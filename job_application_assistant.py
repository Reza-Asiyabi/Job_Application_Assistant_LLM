"""
Job Application Assistant
A specialized LLM assistant for evaluating job fit and generating application materials.
"""
from __future__ import annotations

import os
import re
import json
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
import pypdf


def _resolve_profile_path(env_var: str, default_name: str) -> Path:
    """Resolve a profile file path from an env var override or the default
    filename next to this module. Relative overrides are taken relative to
    the project directory."""
    override = os.getenv(env_var, "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = Path(__file__).parent / p
        return p
    return Path(__file__).parent / default_name


def get_profile_paths() -> dict:
    """Return the resolved profile file paths as {"instructions", "personal", "legacy"}.

    Overridable via env vars (set them in .env to keep personal files out of git):
      PROFILE_INSTRUCTIONS_PATH  (default: profile_instructions.md)
      PROFILE_PERSONAL_PATH      (default: profile_personal.md)
      PROFILE_PATH               (default: profile.md — legacy single-file fallback)
    """
    load_dotenv()
    return {
        "instructions": _resolve_profile_path("PROFILE_INSTRUCTIONS_PATH", "profile_instructions.md"),
        "personal":     _resolve_profile_path("PROFILE_PERSONAL_PATH",     "profile_personal.md"),
        "legacy":       _resolve_profile_path("PROFILE_PATH",              "profile.md"),
    }


PROMPTS_DIR = Path(__file__).parent / "prompts"


def _render_prompt(name: str, **variables) -> str:
    """Load prompts/<name>.md and substitute {{token}} placeholders.

    Templates are re-read on every call so edits take effect immediately.
    See prompts/README.md for the token reference.
    """
    path = PROMPTS_DIR / f"{name}.md"
    try:
        template = path.read_text(encoding="utf-8")
    except OSError as e:
        raise RuntimeError(
            f"Prompt template not found: {path}\n"
            "Restore the prompts/ directory from the repository."
        ) from e
    for key, value in variables.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template.strip()


def _load_tone(tone: str) -> str:
    """Load the cover-letter tone directive from prompts/tone_<tone>.md.
    Unknown tones fall back to hybrid."""
    key = (tone or "hybrid").strip().lower()
    path = PROMPTS_DIR / f"tone_{key}.md"
    if not path.exists():
        path = PROMPTS_DIR / "tone_hybrid.md"
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as e:
        raise RuntimeError(f"Tone template not found: {path}") from e


def _format_ollama_size(bytes_: int) -> str:
    """Human-readable file size for Ollama model display."""
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


class JobApplicationAssistant:
    """
    An AI assistant for evaluating job fit and generating application materials.
    Supports OpenAI API and local Ollama models.
    """

    def __init__(self, cv_path: str = None, provider: str = "openai",
                 api_key: str = None, base_url: str = None):
        """
        Args:
            cv_path:   Path to the CV PDF file.
            provider:  "openai" (default) or "ollama" (local, no API key needed).
            api_key:   OpenAI API key. If None, read from OPENAI_API_KEY env var.
                       Ignored when provider="ollama".
            base_url:  Override the API base URL. For Ollama, pass
                       "http://localhost:11434/v1" (or your custom host).
        """
        load_dotenv()
        self.provider = provider

        if provider == "ollama":
            actual_base_url = base_url or "http://localhost:11434/v1"
            actual_api_key  = "ollama"   # OpenAI SDK requires a non-empty value
        else:
            actual_base_url = base_url or os.getenv("OPENAI_BASE_URL")
            actual_api_key  = api_key  or os.getenv("OPENAI_API_KEY")
            if not actual_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

        if cv_path is None:
            cv_path = os.getenv("CV_PATH", "cv.pdf")

        client_kwargs: dict = {
            "api_key":     actual_api_key,
            # Retry transient failures (connection errors, 429, 5xx) with
            # exponential backoff — handled by the OpenAI SDK itself.
            "max_retries": 3,
            "timeout":     float(os.getenv("OPENAI_TIMEOUT", "120")),
        }
        if actual_base_url:
            client_kwargs["base_url"] = actual_base_url

        self.client = OpenAI(**client_kwargs)
        self.cv_text = self._extract_cv_text(cv_path)
        self.system_prompt = self._load_system_prompt()
        self.user_name = self._extract_user_name()

        # Stores the most recent fit evaluation so Generate/Package tabs
        # can use it as context without requiring manual re-entry.
        self._last_evaluation: str | None = None
        # Full message list of the most recent generation (including the
        # assistant's reply) — lets refine_output() continue the conversation.
        self._last_conversation: list | None = None

        print(f"  Job Application Assistant initialized ({provider})")
        print(f"  CV loaded: {len(self.cv_text)} characters")

    # ─────────────────────────────────────────────────────────────────────────
    # Ollama helpers (classmethods — usable before instantiation)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def check_ollama_connection(base_url: str = "http://localhost:11434") -> tuple[bool, str]:
        """Ping the Ollama server. Returns (is_running, error_message)."""
        try:
            import requests as _req
            r = _req.get(f"{base_url}/api/tags", timeout=3)
            r.raise_for_status()
            return True, ""
        except Exception as exc:
            msg = str(exc)
            if "Connection refused" in msg or "ConnectionError" in type(exc).__name__:
                return False, (
                    "Cannot connect to Ollama.\n\n"
                    "Make sure Ollama is running:\n"
                    "  ollama serve\n\n"
                    "If you haven't installed it yet:\n"
                    "  https://ollama.com"
                )
            return False, f"Ollama connection error: {msg}"

    @staticmethod
    def list_ollama_models(base_url: str = "http://localhost:11434") -> list[dict]:
        """
        Return installed Ollama models as a list of dicts:
        {"name": str, "size": str, "modified": str}
        Returns [] on any error.
        """
        try:
            import requests as _req
            r = _req.get(f"{base_url}/api/tags", timeout=5)
            r.raise_for_status()
            models = r.json().get("models", [])
            return [
                {
                    "name":     m["name"],
                    "size":     _format_ollama_size(m.get("size", 0)),
                    "modified": m.get("modified_at", "")[:10],
                }
                for m in models
            ]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Initialization helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_cv_text(self, cv_path: str) -> str:
        if not Path(cv_path).exists():
            raise FileNotFoundError(f"CV file not found: {cv_path}")
        text = ""
        try:
            with open(cv_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

    def _load_system_prompt(self) -> str:
        """Load system prompt from profile files (paths from get_profile_paths()).

        Priority:
        1. Both instructions + personal files exist  -> combine them
        2. Only the personal file exists             -> use personal text
        3. Neither exists but the legacy file exists -> legacy fallback
        4. Nothing found                             -> built-in prompt
        """
        paths = get_profile_paths()
        instr_path    = paths["instructions"]
        personal_path = paths["personal"]
        legacy_path   = paths["legacy"]

        has_instr    = instr_path.exists()
        has_personal = personal_path.exists()

        if has_instr and has_personal:
            try:
                instr_text    = instr_path.read_text(encoding="utf-8").strip()
                personal_text = personal_path.read_text(encoding="utf-8").strip()
                combined = instr_text + "\n\n" + personal_text
                print(f"  Profile loaded from {instr_path.name} + {personal_path.name} "
                      f"({len(combined):,} characters)")
                return combined
            except Exception as e:
                print(f"  Warning: could not read split profile files ({e}), trying fallback")

        if has_personal:
            try:
                personal_text = personal_path.read_text(encoding="utf-8").strip()
                if personal_text:
                    print(f"  Profile loaded from {personal_path.name} only ({len(personal_text):,} characters)")
                    return personal_text
            except Exception as e:
                print(f"  Warning: could not read {personal_path.name} ({e}), trying fallback")

        if legacy_path.exists():
            try:
                text = legacy_path.read_text(encoding="utf-8").strip()
                if text:
                    print(f"  Profile loaded from {legacy_path.name} (legacy) ({len(text):,} characters)")
                    return text
            except Exception as e:
                print(f"  Warning: could not read {legacy_path.name} ({e}), using built-in prompt")

        print("  Profile loaded from built-in prompt")
        return self._builtin_system_prompt()

    def _extract_user_name(self) -> str:
        """Extract the candidate's name from the system prompt (looks for 'Name: ...' line)."""
        for line in self.system_prompt.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("name:"):
                name = stripped[5:].strip()
                if name and not name.startswith("["):
                    return name
        return "the candidate"

    def _builtin_system_prompt(self) -> str:
        return """You are a highly specialized career-assistant LLM dedicated to supporting a job candidate with applications.
Your purpose is to strategically evaluate job fit, estimate expected salary, position the candidate optimally, and produce high-quality, human-sounding application materials tailored to each role.
- Think in first principles, be direct, adapt to context. Skip "great question" fluff. Verifiable facts over platitudes.
- Banned phrases: em-dashes, watery language, "it's not about X, it's about Y", "here's the kicker"
- Humanize all your output
- Reason at maximum depth, step by step
- Self-critique every response: rate 1-10, fix weaknesses, iterate. User sees only final version.
- Useful over polite. When wrong, say so and show better.
- Never hallucinate specifics.

You must treat the information in profile.md as ground truth about the candidate.

Meta-Rules: Strategic truth over pleasing language. If a role is a bad fit, say so. Optimize for long-term career trajectory."""

    # ─────────────────────────────────────────────────────────────────────────
    # Core API helper
    # ─────────────────────────────────────────────────────────────────────────

    def _create_completion(self, create_kwargs: dict):
        """chat.completions.create with fallbacks for parameters that newer
        reasoning models reject (temperature must be default; max_tokens was
        replaced by max_completion_tokens). Transient errors are retried by
        the SDK itself (max_retries)."""
        create_kwargs = dict(create_kwargs)
        for _ in range(3):
            try:
                return self.client.chat.completions.create(**create_kwargs)
            except Exception as e:
                msg = str(e)
                if "temperature" in msg and "temperature" in create_kwargs:
                    del create_kwargs["temperature"]
                    continue
                if "max_tokens" in msg and "max_tokens" in create_kwargs:
                    create_kwargs["max_completion_tokens"] = create_kwargs.pop("max_tokens")
                    continue
                raise
        return self.client.chat.completions.create(**create_kwargs)

    def _call_api(self, messages: list, model: str, temperature: float = 0.7,
                  stream_callback=None) -> dict:
        """
        Call the OpenAI chat API, with optional streaming.

        Args:
            messages:         List of message dicts for the API.
            model:            Model identifier string.
            temperature:      Sampling temperature.
            stream_callback:  If provided, stream mode is used and each chunk
                              is passed to stream_callback(chunk: str).

        Returns:
            {"content": str, "tokens_used": int}
        """
        if stream_callback is None:
            response = self._create_completion(dict(
                model=model,
                messages=messages,
                temperature=temperature,
            ))
            content = response.choices[0].message.content or ""
            # Ollama may not return usage — estimate from content length
            try:
                tokens_used = response.usage.total_tokens
            except (AttributeError, TypeError):
                tokens_used = len(content) // 4
            self._last_conversation = messages + [{"role": "assistant", "content": content}]
            return {"content": content, "tokens_used": tokens_used}

        # Streaming path
        create_kwargs = dict(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        # stream_options is an OpenAI extension — Ollama ignores it gracefully
        # but some older SDK versions raise TypeError, so we handle that too
        if self.provider != "ollama":
            try:
                create_kwargs["stream_options"] = {"include_usage": True}
                stream = self._create_completion(create_kwargs)
            except TypeError:
                del create_kwargs["stream_options"]
                stream = self._create_completion(create_kwargs)
        else:
            stream = self._create_completion(create_kwargs)

        collected = []
        tokens_used = 0
        try:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    collected.append(delta)
                    stream_callback(delta)
                try:
                    if chunk.usage is not None:
                        tokens_used = chunk.usage.total_tokens
                except AttributeError:
                    pass  # Ollama does not always include usage in stream chunks
        except Exception as stream_err:
            error_msg = f"\n\n[Stream interrupted: {stream_err}]"
            stream_callback(error_msg)
            collected.append(error_msg)

        content = "".join(collected)
        # Fall back to character estimate if Ollama didn't report token count
        if tokens_used == 0 and content:
            tokens_used = len(content) // 4
        self._last_conversation = messages + [{"role": "assistant", "content": content}]
        return {"content": content, "tokens_used": tokens_used}

    # ─────────────────────────────────────────────────────────────────────────
    # CV context builder
    # ─────────────────────────────────────────────────────────────────────────

    def _create_cv_context(self) -> str:
        return (
            f"## {self.user_name.upper()}'S CV\n\n"
            "Below is the full text extracted from the candidate's CV. "
            "Use this as the authoritative source for specific project details, "
            "publications, technical skills, job titles, dates, and achievements.\n\n"
            f"CV TEXT:\n---\n{self.cv_text}\n---"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Public methods
    # ─────────────────────────────────────────────────────────────────────────

    def evaluate_job_fit(self, job_description: str, model: str = "gpt-4o",
                         stream_callback=None) -> dict:
        """
        Evaluate strategic fit for a specific job.

        Args:
            job_description:  The complete job posting text.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"evaluation": str, "model": str, "tokens_used": int,
             "score": int|None, "verdict": str, "salary": str}
            score/verdict/salary are parsed from the structured first line
            (SCORE: NN/100 | VERDICT: ... | SALARY: ...) when present.
        """
        cv_context = self._create_cv_context()
        user_prompt = _render_prompt(
            "evaluate_job_fit",
            cv_context=cv_context,
            job_description=job_description,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.3,
            stream_callback=stream_callback,
        )
        self._last_evaluation = result["content"]
        return {
            "evaluation":  result["content"],
            "model":       model,
            "tokens_used": result["tokens_used"],
            **self._parse_verdict_line(result["content"]),
        }

    @staticmethod
    def _parse_verdict_line(evaluation: str) -> dict:
        """Parse the machine-readable header line of an evaluation.

        Expected shape (first non-empty line):
            SCORE: 78/100 | VERDICT: Conditional | SALARY: £65,000-80,000
        Returns {"score": int|None, "verdict": str, "salary": str} —
        empty values when the line is absent (e.g. old evaluations).
        """
        out = {"score": None, "verdict": "", "salary": ""}
        for line in evaluation.splitlines():
            line = line.strip().lstrip("*# ").rstrip("*")
            if not line:
                continue
            if line.upper().startswith("SCORE"):
                m = re.search(r"SCORE:\s*(\d{1,3})\s*/\s*100", line, re.IGNORECASE)
                if m:
                    out["score"] = max(0, min(100, int(m.group(1))))
                m = re.search(r"VERDICT:\s*([^|]+?)\s*(?:\||$)", line, re.IGNORECASE)
                if m:
                    out["verdict"] = m.group(1).strip()
                m = re.search(r"SALARY:\s*(.+?)\s*$", line, re.IGNORECASE)
                if m:
                    out["salary"] = m.group(1).strip()
            break  # only inspect the first non-empty line
        return out

    def refine_output(self, instruction: str, model: str = "gpt-4o",
                      stream_callback=None) -> dict:
        """
        Refine the most recent generation with a follow-up instruction,
        continuing the same conversation instead of regenerating from scratch.
        Chained refinements keep extending the same conversation.

        Args:
            instruction:      What to change ("shorter", "more technical",
                              "mention project X", ...).
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"refined": str, "model": str, "tokens_used": int}

        Raises:
            ValueError if nothing has been generated yet.
        """
        if not self._last_conversation:
            raise ValueError("Nothing to refine yet — generate something first.")
        user_prompt = _render_prompt("refine", instruction=instruction)
        messages = self._last_conversation + [{"role": "user", "content": user_prompt}]
        result = self._call_api(
            messages=messages,
            model=model,
            temperature=0.5,
            stream_callback=stream_callback,
        )
        return {
            "refined":     result["content"],
            "model":       model,
            "tokens_used": result["tokens_used"],
        }

    @staticmethod
    def _limit_note(word_limit: int | None) -> str:
        if not word_limit:
            return ""
        return (
            f"\nHARD LENGTH CONSTRAINT: the output must be at most {word_limit} words. "
            "This overrides any other length guidance above. Count carefully — "
            "application portals reject over-length answers."
        )

    def generate_cv_summary(self, job_description: str, fit_evaluation: str = None,
                             word_limit: int = None,
                             model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Generate a tailored CV summary for a specific role.

        Args:
            job_description:  The complete job posting text.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"summary": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        eval_block = (
            f"## STRATEGIC FIT EVALUATION (use this to decide what to emphasize)\n\n{fit_evaluation}"
            if fit_evaluation
            else "## NOTE\nNo prior evaluation — infer the best positioning directly from the job description and CV."
        )

        user_prompt = _render_prompt(
            "cv_summary",
            cv_context=cv_context,
            job_description=job_description,
            eval_block=eval_block,
            limit_note=self._limit_note(word_limit),
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.5,
            stream_callback=stream_callback,
        )
        return {
            "summary":     result["content"],
            "model":       model,
            "tokens_used": result["tokens_used"],
        }

    def generate_cover_letter(self, job_description: str, fit_evaluation: str = None,
                               company_name: str = None, role_title: str = None,
                               tone: str = "hybrid", word_limit: int = None,
                               model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Generate a tailored cover letter for a specific role.

        Args:
            job_description:  The complete job posting text.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            company_name:     Company name (extracted from JD if not provided).
            role_title:       Role title (extracted from JD if not provided).
            tone:             Framing angle — "hybrid" (default), "research", or "engineering".
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"cover_letter": str, "model": str, "tokens_used": int}
        """
        cv_context   = self._create_cv_context()
        company_info = f"Company: {company_name}" if company_name else "[Extract company from job description]"
        role_info    = f"Role: {role_title}"       if role_title    else "[Extract role title from job description]"
        eval_block   = (
            f"## STRATEGIC FIT EVALUATION (use this to decide angle and emphasis)\n\n{fit_evaluation}"
            if fit_evaluation
            else "## NOTE\nNo prior evaluation — infer the best positioning directly from the job description and CV."
        )
        tone_instruction = _load_tone(tone)

        user_prompt = _render_prompt(
            "cover_letter",
            cv_context=cv_context,
            job_description=job_description,
            eval_block=eval_block,
            company_info=company_info,
            role_info=role_info,
            tone_instruction=tone_instruction,
            limit_note=self._limit_note(word_limit),
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            stream_callback=stream_callback,
        )
        return {
            "cover_letter": result["content"],
            "model":        model,
            "tokens_used":  result["tokens_used"],
        }

    def answer_application_question(self, job_description: str, question: str,
                                    fit_evaluation: str = None, word_limit: int = None,
                                    model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Answer a specific application or interview question.

        Args:
            job_description:  The complete job posting text.
            question:         The specific question to answer.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"question": str, "answer": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        eval_block = (
            f"## STRATEGIC FIT EVALUATION\n\n{fit_evaluation}"
            if fit_evaluation else ""
        )

        user_prompt = _render_prompt(
            "application_question",
            cv_context=cv_context,
            job_description=job_description,
            eval_block=eval_block,
            question=question,
            limit_note=self._limit_note(word_limit),
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.4,
            stream_callback=stream_callback,
        )
        return {
            "question":    question,
            "answer":      result["content"],
            "model":       model,
            "tokens_used": result["tokens_used"],
        }

    def generate_interview_prep(self, job_description: str, fit_evaluation: str = None,
                                model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Generate comprehensive interview preparation materials.

        Args:
            job_description:  The complete job posting text.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"interview_prep": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        eval_block = (
            f"## STRATEGIC FIT EVALUATION\n\n{fit_evaluation}"
            if fit_evaluation
            else "## NOTE\nNo prior evaluation — infer positioning from job description and CV."
        )

        user_prompt = _render_prompt(
            "interview_prep",
            cv_context=cv_context,
            job_description=job_description,
            eval_block=eval_block,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.6,
            stream_callback=stream_callback,
        )
        return {
            "interview_prep": result["content"],
            "model":          model,
            "tokens_used":    result["tokens_used"],
        }

    def generate_linkedin_message(self, job_description: str, recruiter_name: str = None,
                                   fit_evaluation: str = None, model: str = "gpt-4o",
                                   stream_callback=None) -> dict:
        """
        Generate a concise LinkedIn outreach message to a recruiter or hiring manager.

        Args:
            job_description:  The complete job posting text or role context.
            recruiter_name:   Optional recruiter first name for personalisation.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"linkedin_message": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        eval_block = (
            f"## STRATEGIC FIT EVALUATION\n\n{fit_evaluation}"
            if fit_evaluation
            else "## NOTE\nNo prior evaluation — infer the best angle from job description and CV."
        )
        greeting = f"Hi {recruiter_name}," if recruiter_name else "Hi [Name],"

        user_prompt = _render_prompt(
            "linkedin_message",
            cv_context=cv_context,
            job_description=job_description,
            eval_block=eval_block,
            greeting=greeting,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.7,
            stream_callback=stream_callback,
        )
        return {
            "linkedin_message": result["content"],
            "model":            model,
            "tokens_used":      result["tokens_used"],
        }

    def generate_followup_email(self, job_description: str, interviewer_name: str = None,
                                interview_notes: str = None, model: str = "gpt-4o",
                                stream_callback=None) -> dict:
        """
        Generate a concise thank-you / follow-up email after an interview.

        Args:
            job_description:  The job posting or role context.
            interviewer_name: Optional name of the interviewer(s) for personalisation.
            interview_notes:  Optional notes on what was discussed — used to add a
                              specific reference that makes the email feel genuine.
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"followup_email": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()

        interviewer_block = (
            f"Interviewer name(s): {interviewer_name}"
            if interviewer_name
            else "Interviewer name: unknown — use a generic but warm greeting"
        )
        notes_block = (
            f"Key things discussed during the interview:\n{interview_notes}"
            if interview_notes
            else "No specific interview notes provided — reference something plausible from the role."
        )

        user_prompt = _render_prompt(
            "followup_email",
            cv_context=cv_context,
            job_description=job_description,
            interviewer_block=interviewer_block,
            notes_block=notes_block,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.6,
            stream_callback=stream_callback,
        )
        return {
            "followup_email": result["content"],
            "model":          model,
            "tokens_used":    result["tokens_used"],
        }

    def analyze_ats_fit(self, job_description: str, content: str,
                        model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Analyse how well a piece of content (CV summary, cover letter, etc.)
        matches the job description from an ATS / keyword perspective.

        Args:
            job_description: The full job posting text.
            content:         The generated material to evaluate (cover letter, CV summary…).
            model:           OpenAI model to use.
            stream_callback: Optional callable(str) for streaming chunks.

        Returns:
            {"ats_analysis": str, "model": str, "tokens_used": int}
        """
        user_prompt = _render_prompt(
            "ats_analysis",
            job_description=job_description,
            content=content,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.2,
            stream_callback=stream_callback,
        )
        return {
            "ats_analysis": result["content"],
            "model":        model,
            "tokens_used":  result["tokens_used"],
        }

    def extract_job_details(self, job_description: str, model: str = "gpt-4o") -> dict:
        """
        Extract company name, role title, and location from a job description.

        Args:
            job_description:  The job posting text (first 3000 chars used).
            model:            OpenAI model to use.

        Returns:
            {"company": str, "role": str, "location": str}
            Falls back to empty strings on any failure.
        """
        user_prompt = (
            "Extract the following from this job description. "
            "Reply ONLY with valid JSON — no prose, no markdown fences.\n\n"
            'JSON schema: {"company": "<company name or empty>", '
            '"role": "<job title or empty>", "location": "<city/country or Remote or empty>"}\n\n'
            f"JOB DESCRIPTION:\n{job_description[:3000]}"
        )

        try:
            response = self._create_completion(dict(
                model=model,
                messages=[
                    {"role": "system", "content": "You extract structured information from job descriptions. Output only valid JSON."},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=120,
            ))
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if the model adds them despite instructions
            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
            # Extract first JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                return {
                    "company":  parsed.get("company",  ""),
                    "role":     parsed.get("role",     ""),
                    "location": parsed.get("location", ""),
                }
        except Exception:
            pass
        return {"company": "", "role": "", "location": ""}

    def analyze_rejection(self, company_name: str = None, role_title: str = None,
                          rejection_message: str = None, application_materials: str = None,
                          model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Analyse a job rejection and provide actionable learning.

        Args:
            company_name:          Company that rejected the candidate.
            role_title:            Role applied for.
            rejection_message:     The rejection email / message text (optional).
            application_materials: Generated cover letter / CV summary submitted (optional).
            model:                 OpenAI model to use.
            stream_callback:       Optional callable(str) for streaming chunks.

        Returns:
            {"rejection_analysis": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()

        role_ctx = f"{role_title} at {company_name}" if role_title and company_name else \
                   (company_name or role_title or "this role")

        materials_block = (
            f"## APPLICATION MATERIALS SUBMITTED\n\n{application_materials}"
            if application_materials
            else "## APPLICATION MATERIALS\nNot provided — reason from context only."
        )
        rejection_block = (
            f"## REJECTION MESSAGE\n\n{rejection_message}"
            if rejection_message
            else "## REJECTION MESSAGE\nNot provided — analyse based on profile and role fit only."
        )

        user_prompt = _render_prompt(
            "rejection_analysis",
            cv_context=cv_context,
            role_ctx=role_ctx,
            materials_block=materials_block,
            rejection_block=rejection_block,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.3,
            stream_callback=stream_callback,
        )
        return {
            "rejection_analysis": result["content"],
            "model":              model,
            "tokens_used":        result["tokens_used"],
        }

    def generate_salary_negotiation(self, offer_details: str, job_description: str = None,
                                     model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Analyse a received offer and generate counter-offer strategy + negotiation email.

        Args:
            offer_details:   The received offer text (salary, bonus, equity, benefits, etc.).
            job_description: Optional job posting for context.
            model:           OpenAI model to use.
            stream_callback: Optional callable(str) for streaming chunks.

        Returns:
            {"salary_negotiation": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        jd_block = f"## JOB DESCRIPTION (for context)\n\n{job_description}" if job_description else ""

        user_prompt = _render_prompt(
            "salary_negotiation",
            cv_context=cv_context,
            offer_details=offer_details,
            jd_block=jd_block,
        )

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            temperature=0.3,
            stream_callback=stream_callback,
        )
        return {
            "salary_negotiation": result["content"],
            "model":              model,
            "tokens_used":        result["tokens_used"],
        }

    def full_application_package(self, job_description: str, company_name: str = None,
                                  role_title: str = None, model: str = "gpt-4o") -> dict:
        """
        Generate a complete application package (for Python API / CLI use).
        The GUI uses sequential streaming calls instead of this method.

        Returns:
            Dict with evaluation, cv_summary, cover_letter, and token counts.
        """
        print("\n" + "=" * 70)
        print("GENERATING COMPLETE APPLICATION PACKAGE")
        print("=" * 70)

        eval_result    = self.evaluate_job_fit(job_description, model=model)
        eval_text      = eval_result.get("evaluation", "")

        summary_result = self.generate_cv_summary(job_description, eval_text, model=model)

        letter_result  = self.generate_cover_letter(
            job_description, eval_text, company_name, role_title, model=model
        )

        total_tokens = (
            eval_result.get("tokens_used",   0) +
            summary_result.get("tokens_used", 0) +
            letter_result.get("tokens_used",  0)
        )

        return {
            "job_description":    job_description,
            "company_name":       company_name,
            "role_title":         role_title,
            "evaluation":         eval_text,
            "cv_summary":         summary_result.get("summary"),
            "cover_letter":       letter_result.get("cover_letter"),
            "model":              model,
            "total_tokens_used":  total_tokens,
        }

    def save_results(self, results: dict, output_path: str):
        """Save results to a .txt or .json file."""
        output_file = Path(output_path)
        if output_file.suffix == ".json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                for key, value in results.items():
                    if value and key not in ("model", "tokens_used", "total_tokens_used"):
                        f.write(f"\n{'=' * 70}\n{key.upper().replace('_', ' ')}\n{'=' * 70}\n\n")
                        f.write(str(value))
                        f.write("\n")
        print(f"\n  Results saved to: {output_path}")


def main():
    """Example usage of the Job Application Assistant."""
    assistant = JobApplicationAssistant()

    job_description = """
    Machine Learning Engineer - Computer Vision

    We're looking for an experienced ML engineer to work on production computer vision systems.

    Requirements:
    - PhD or Master's in Computer Science, Machine Learning, or related field
    - 3+ years experience with PyTorch or TensorFlow
    - Strong background in computer vision and deep learning
    - Experience deploying models to production
    - Python expertise

    Nice to have:
    - Experience with satellite/remote sensing data
    - Publications in top-tier ML conferences
    """

    results = assistant.full_application_package(
        job_description=job_description,
        company_name="Example Tech Company",
        role_title="Machine Learning Engineer - Computer Vision",
    )

    print(f"\n{results['evaluation']}\n")
    print(f"\nCV SUMMARY:\n{results['cv_summary']}\n")
    print(f"\nCOVER LETTER:\n{results['cover_letter']}\n")
    print(f"\nTotal tokens used: {results['total_tokens_used']}")
    assistant.save_results(results, "application_output.txt")


if __name__ == "__main__":
    main()
