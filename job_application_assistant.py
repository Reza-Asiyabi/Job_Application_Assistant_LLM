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
import PyPDF2


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

        client_kwargs: dict = {"api_key": actual_api_key}
        if actual_base_url:
            client_kwargs["base_url"] = actual_base_url

        self.client = OpenAI(**client_kwargs)
        self.cv_text = self._extract_cv_text(cv_path)
        self.system_prompt = self._load_system_prompt()
        self.user_name = self._extract_user_name()

        # Stores the most recent fit evaluation so Generate/Package tabs
        # can use it as context without requiring manual re-entry.
        self._last_evaluation: str | None = None

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
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

    def _load_system_prompt(self) -> str:
        """Load system prompt from profile files.

        Priority:
        1. Both profile_instructions.md + profile_personal.md exist  -> combine them
        2. Only profile_personal.md exists                            -> use personal text (with note)
        3. Neither exists but profile.md exists                       -> legacy fallback
        4. Nothing found                                              -> built-in prompt
        """
        base = Path(__file__).parent
        instr_path    = base / "profile_instructions.md"
        personal_path = base / "profile_personal.md"
        legacy_path   = base / "profile.md"

        has_instr    = instr_path.exists()
        has_personal = personal_path.exists()

        if has_instr and has_personal:
            try:
                instr_text    = instr_path.read_text(encoding="utf-8").strip()
                personal_text = personal_path.read_text(encoding="utf-8").strip()
                combined = instr_text + "\n\n" + personal_text
                print(f"  Profile loaded from profile_instructions.md + profile_personal.md "
                      f"({len(combined):,} characters)")
                return combined
            except Exception as e:
                print(f"  Warning: could not read split profile files ({e}), trying fallback")

        if has_personal:
            try:
                personal_text = personal_path.read_text(encoding="utf-8").strip()
                if personal_text:
                    print(f"  Profile loaded from profile_personal.md only ({len(personal_text):,} characters)")
                    return personal_text
            except Exception as e:
                print(f"  Warning: could not read profile_personal.md ({e}), trying fallback")

        if legacy_path.exists():
            try:
                text = legacy_path.read_text(encoding="utf-8").strip()
                if text:
                    print(f"  Profile loaded from profile.md (legacy) ({len(text):,} characters)")
                    return text
            except Exception as e:
                print(f"  Warning: could not read profile.md ({e}), using built-in prompt")

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
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content or ""
            # Ollama may not return usage — estimate from content length
            try:
                tokens_used = response.usage.total_tokens
            except (AttributeError, TypeError):
                tokens_used = len(content) // 4
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
                stream = self.client.chat.completions.create(**create_kwargs)
            except TypeError:
                del create_kwargs["stream_options"]
                stream = self.client.chat.completions.create(**create_kwargs)
        else:
            stream = self.client.chat.completions.create(**create_kwargs)

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
            {"evaluation": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        user_prompt = f"""{cv_context}

## JOB DESCRIPTION TO EVALUATE

{job_description}

---

Provide a comprehensive, honest job fit evaluation. Structure it exactly as follows:

1. FIT ASSESSMENT
State: Strong fit / Partial fit / Weak fit.
Then in 2-3 sentences: why. Be direct. No hedging.

2. MATCH ANALYSIS
- Core strengths that directly align with this role's requirements (cite specific CV evidence)
- Unique advantages this candidate brings that the JD may not have explicitly asked for but will value
- Read the JD carefully: some "preferred" requirements are disguised must-haves. Flag those.

3. GAPS AND RISKS
- Missing or under-represented skills/experience — be specific, name them
- Concerns from the employer's perspective (e.g. seniority mismatch, industry gap, missing credentials)
- Any genuine red flags. If none, say so.

4. COMPANY AND ROLE CONTEXT
- What does this company/team likely care about most? What does "great" look like in this role?
- Stage of company (startup / scale-up / enterprise) and what that means for the candidate
- Any signals in the JD about culture, pace, technical depth expectations

5. SALARY ESTIMATE
- Expected salary range for this candidate in this role
- Justify the range: company stage, location premium, role seniority, specialisation signals
- Flag clearly if the role appears to be underpaying for the candidate's level

6. STRATEGIC POSITIONING
- Which role archetype best fits (derive this from the profile's Section 4 archetypes)
- Exactly what to emphasize in the application — specific skills, specific projects
- What to downplay or reframe — be tactical, not evasive
- One sentence: the single strongest angle for this application

7. APPLICATION RECOMMENDATION
Yes / Conditional / No — followed by clear reasoning.
If Conditional: state exactly what conditions would change the answer.

Be honest. Be specific. Reference actual CV details throughout. A candidate reading this should come away knowing exactly what to do."""

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
        }

    def generate_cv_summary(self, job_description: str, fit_evaluation: str = None,
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

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION

{job_description}

---

{eval_block}

---

Write a CV/profile summary for this candidate, tailored specifically to this role.

STYLE REFERENCE — these examples show the correct LENGTH and TONE. Do not copy the content; adapt the approach to this candidate's actual background:

Example A (research-to-industry transition framing):
"ML researcher transitioning into AI safety and alignment research. Proven track record designing interpretable deep learning architectures across high-impact projects. Expertise in building models that maintain reliability under distribution shift, grounded in end-to-end empirical research from architecture design through publication. Rapid adapter to new research domains with a record of clear cross-disciplinary communication."

Example B (engineering/product framing):
"ML engineer with a strong record building and shipping production geospatial data pipelines from multi-source Earth Observation data. Delivered operational solutions across projects spanning government agencies, universities, and national research bodies. Work focuses on reliable, scalable pipelines that translate complex satellite data into decision-ready analytics — from data ingestion through cloud deployment."

Example C (applied scientist framing):
"Applied ML Scientist with deep experience developing domain-aware, deployable deep learning systems. Track record taking research innovations to production in collaboration with engineering and product teams. Broad technical range across physics-informed learning, LLMs, and multimodal models, with hands-on delivery on high-stakes projects."

REQUIREMENTS:
- 3-5 sentences. Natural flow — not a bulleted list in prose form.
- First sentence: immediately establish WHAT the candidate does + at what level. Specific > generic.
- If the CV contains quantifiable achievements relevant to this role, include one.
- Use the evaluation context to choose what to foreground for THIS specific role.
- Consistent first-person voice (implied "I" or explicit) — do not mix.
- No banned language. No hollow adjectives. No AI-isms.
- Output ONLY the summary text — no header, no explanation."""

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

    # Tone framing instructions for cover letter variations
    _COVER_LETTER_TONES = {
        "hybrid": (
            "Use a BALANCED / HYBRID framing — weigh research depth and engineering impact equally. "
            "Neither the academic angle nor the production angle should dominate."
        ),
        "research": (
            "Use a RESEARCH-LED framing:\n"
            "- Open by foregrounding publications, domain expertise, or methodological depth as the key differentiator\n"
            "- Emphasise intellectual contribution, novel approaches, and academic credibility\n"
            "- Frame projects in terms of research impact, not just delivery\n"
            "- Tone: peer-to-peer scientific — confident about research contributions, not apologetic about academia"
        ),
        "engineering": (
            "Use an ENGINEERING-LED framing:\n"
            "- Open by foregrounding shipped systems, production deployments, or quantified engineering outcomes\n"
            "- Emphasise scale, reliability, performance, and practical delivery speed\n"
            "- Frame projects in terms of systems built, problems solved at scale, and measurable business results\n"
            "- Tone: engineering-first — results over methods, action-oriented, production-ready"
        ),
    }

    def generate_cover_letter(self, job_description: str, fit_evaluation: str = None,
                               company_name: str = None, role_title: str = None,
                               tone: str = "hybrid",
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
        tone_instruction = self._COVER_LETTER_TONES.get(tone or "hybrid",
                                                         self._COVER_LETTER_TONES["hybrid"])

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION

{job_description}

---

{eval_block}

---

{company_info}
{role_info}

## TONE / FRAMING DIRECTIVE

{tone_instruction}

Write a cover letter. Apply the TONE DIRECTIVE above as the primary framing decision.

STRUCTURE:
1. Opening paragraph — hook, company, role, why now:
   - First sentence must compel the reader to keep going. It is NOT an introduction — it is a hook.
   - Name the company and role explicitly.
   - Give ONE specific, genuine reason this company/role is interesting right now — reference something real from the JD (a product, a technical challenge, a stated mission).
   - End the paragraph with a one-sentence value proposition: what does this candidate uniquely bring?

2. Middle (1-2 paragraphs) — evidence:
   - 1-2 concrete examples from the CV. Use the impact formula: "Built [what] for [who/context], which [outcome/result]."
   - Outcomes over process. Numbers over adjectives. Name the actual projects/organisations.
   - Frame in terms of transferable value to THIS role specifically.
   - If there is a relevant gap, bridge it confidently in one sentence: "While I haven't worked directly with X, my work on Y gave me deep grounding in the underlying principles" — never hide, never grovel.

3. Closing paragraph:
   - One forward-looking sentence expressing genuine interest in discussing further.
   - Confident, not pushy. Not "I would be grateful for any opportunity".
   - Sign off: "Warm regards," then a line break, then the candidate's full name exactly as given in the profile.

REQUIREMENTS:
- 4-5 tight paragraphs, 350-450 words total. Every sentence earns its place.
- Apply the tone directive as the framing lens throughout.
- Human voice — reads like a sharp person wrote it on their best day, not an AI filling a template.
- No banned language. No hollow adjectives.
- Draw only from CV facts — never fabricate metrics or project details.
- Output the letter only — no header, no label, no explanation."""

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
                                    fit_evaluation: str = None, model: str = "gpt-4o",
                                    stream_callback=None) -> dict:
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

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION

{job_description}

---

{eval_block}

## APPLICATION QUESTION

{question}

---

First, identify the question type, then write the answer accordingly.

QUESTION TYPE GUIDE:
- "Why this company / why this role?" → Show specific knowledge of the company. Reference something real: their product, their technical approach, their stated mission. Connect it to a genuine aspect of the candidate's direction. Avoid generic "I've always been passionate about X."
- "Tell me about yourself / walk me through your background" → Lead with the most relevant part of the candidate's story for THIS role. 3-4 sentences max. End with why this role is the natural next step.
- "Describe a time you..." (competency/STAR) → Full STAR structure: Situation (brief), Task (what was at stake), Action (what the candidate specifically did — not "we"), Result (concrete outcome). Use a real CV example.
- "What is your greatest weakness / area for development?" → Name a real, plausible weakness. Show self-awareness and what the candidate is actively doing about it. Don't give the insulting fake answer ("I work too hard").
- "Where do you see yourself in 5 years?" → Be honest about direction. Connect it to why this role is a meaningful step, not a dead end.
- Technical question → Lead with the direct answer. Then add depth: approach, trade-offs considered, real examples from CV.
- Short-answer field (100-250 words) → Be crisp. No padding. Every sentence adds something.
- Long-answer / essay → Use clear structure. No headers needed, but logical flow with a strong opening sentence.

REQUIREMENTS:
- Draw directly from the CV — no generic answers that could come from anyone
- Tailor to this specific role and company
- Natural, confident language — not a rehearsed speech, not AI-formal
- Appropriate length for the question format
- If there's a genuine gap relevant to the question, acknowledge it briefly and bridge confidently
- No banned language, no hollow buzzwords, no inflated claims
- Output the answer only — no label, no preamble"""

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

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION

{job_description}

---

{eval_block}

---

Generate comprehensive interview preparation for this specific role. Structure as five parts:

PART 1: TECHNICAL QUESTIONS AND ANSWERS
Generate 6-8 technical questions this interview panel is likely to ask, based on the JD requirements.
- Prioritise questions that test the most critical skills listed in the JD
- For each: write the question, then a strong specific answer grounded in the candidate's actual CV (real projects, real numbers where available)
- Include at least one question that probes for depth beyond the CV's surface claims

PART 2: BEHAVIORAL QUESTIONS (STAR FORMAT)
Generate 5-6 behavioral questions covering: cross-functional collaboration, handling ambiguity, technical leadership, delivering under constraints, failure and recovery, influencing without authority, handling a disagreement with a senior stakeholder.
For each: write the question, then a complete STAR answer (Situation — brief; Task — what was at stake; Action — what this candidate specifically did, not "we"; Result — concrete outcome) drawn from actual CV experience.

PART 3: QUESTIONS THE CANDIDATE SHOULD ASK
Generate 6-7 sharp questions for the candidate to ask. Each question should:
- Signal genuine curiosity and strategic thinking, not box-checking
- Probe something the candidate genuinely needs to know: technical decisions, team dynamics, research-to-production balance, what success looks like at 6 months, why the last person in this role left/moved on
- Be specific to this company and role — nothing generic
- NOT be answerable from the JD alone

PART 4: MOTIVATION AND FIT QUESTIONS
Generate 4-5 "why us / why this role" questions the interviewer is likely to ask.
For each: write the question and a strong, honest answer grounded in the candidate's actual career direction and motivations — not generic enthusiasm. Connect specifically to this company's mission, stage, or technical approach.

PART 5: HANDLING DIFFICULT TERRITORY
Identify 3-4 potential weak spots for this candidate in this specific role (gaps from Section 3 of the evaluation, or profile areas that won't map cleanly).
For each: write the likely tough question the interviewer will ask, then a confident, honest bridging answer — acknowledge the gap, don't hide it, then immediately pivot to what the candidate does have that addresses the underlying need.

Every answer must sound like a confident, senior person — not a rehearsed script.
Be specific. Reference actual CV content throughout. Generic prep is useless."""

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

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION / ROLE CONTEXT

{job_description}

---

{eval_block}

---

Write a LinkedIn outreach message from the candidate to a recruiter or hiring manager.

Greeting to use: {greeting}

CRITICAL — THE FIRST SENTENCE:
The first sentence is make or break. It determines whether the message gets read or deleted.
- It must be a statement, not a question, not a compliment to the recruiter
- It must be about something specific: a product the company makes, a technical problem they're working on, a recent announcement, something in the JD that is genuinely interesting
- It must not start with "I" or reference the candidate at all
- BAD: "I came across your posting and was excited by the opportunity"
- BAD: "I hope you're doing well"
- GOOD: "The work [Company] is doing on [specific technical area from JD] is one of the few serious attempts to [what it's trying to solve] — and it's rare to see it done with [specific approach mentioned in JD]."

STRUCTURE:
1. Hook sentence (about them / the work)
2. 1-2 sentences on fit: the single most compelling angle. Be concrete — name a skill, a project, a result. One strong specific beats three vague claims.
3. One low-friction call to action: "happy to share more if useful" or "open to a quick chat if timing works" — not a formal application request

REQUIREMENTS:
- 100-150 words absolute maximum. LinkedIn messages get skimmed.
- Conversational and confident — sounds like a real person, not a cover letter
- Sign off with the candidate's full name as given in the profile
- No banned language. No hollow phrases.

Output ONLY the message text, ready to copy-paste."""

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

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION / ROLE CONTEXT

{job_description}

---

{interviewer_block}

{notes_block}

---

Write a short thank-you / follow-up email from the candidate to the interviewer(s) after a job interview.

Requirements:
- 150-200 words — concise and respectful of the reader's time
- Warm but not groveling — confident, genuine, professional
- Reference ONE specific thing from the conversation (use the notes above if provided)
- Reaffirm interest in the role with a brief, concrete reason — not generic enthusiasm
- Clear, low-friction closing — express readiness for next steps without being pushy
- Sign off with the candidate's full name as given in the profile

Do NOT:
- Open with "I wanted to reach out" or "I hope this email finds you well"
- Be excessively effusive ("It was AMAZING to meet you")
- Summarise the entire interview
- Add hollow filler phrases

Output ONLY the email text (subject line first, then body), ready to send."""

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
        user_prompt = f"""## JOB DESCRIPTION

{job_description}

---

## CONTENT TO EVALUATE

{content}

---

Perform an ATS (Applicant Tracking System) keyword analysis of the content above against the job description.

Produce a structured report with these exact sections:

MATCH SCORE
Give a single score from 0–100 reflecting keyword and requirement coverage. Format: "Score: XX/100"
One sentence of plain-language interpretation (e.g. "Strong match — most critical requirements are addressed.").

KEYWORDS PRESENT
List the key skills, tools, qualifications, and phrases from the JD that appear in the content.
Group as bullet points. Be specific — use the exact terms from the JD.

KEYWORDS MISSING
List important skills, tools, qualifications, and phrases from the JD that are absent from the content.
Focus on must-haves and strong-signals. Ignore minor or generic phrases.

SUGGESTED ADDITIONS
For each missing keyword that the candidate plausibly has (based on the content's context), suggest a concrete sentence or phrase that could be inserted to address the gap.
If a keyword is genuinely absent from the candidate's profile, say so rather than fabricating.

Keep the report concise and actionable. No filler."""

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
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You extract structured information from job descriptions. Output only valid JSON."},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=120,
            )
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

        user_prompt = f"""{cv_context}

## ROLE APPLIED FOR

{role_ctx}

---

{materials_block}

---

{rejection_block}

---

Analyse this rejection and produce a structured report with three sections:

LIKELY CAUSES
Based on the candidate's profile, the materials (if provided), and the rejection message (if provided):
- What most likely caused the rejection? Be direct and specific.
- Was it a fit issue (skills, experience, seniority), a presentation issue (how they were positioned), a process issue (timing, competition), or something else?
- If the rejection message gives clues, extract them explicitly.

WHAT TO DO DIFFERENTLY
Concrete, actionable changes for next applications:
- If it's a skill gap: what specifically to address and how
- If it's a positioning issue: what angle to use instead
- If it's a presentation issue: what to change in the materials
- Maximum 4-5 bullet points, each with a specific action

WHAT WAS STRONG
Identify the aspects of this candidate's application or profile that were likely strong for this role.
This is not consolation — it's data for where to focus future applications.

Be honest, direct, and constructive. No platitudes. The goal is to extract maximum learning from this rejection."""

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

        user_prompt = f"""{cv_context}

## OFFER RECEIVED

{offer_details}

{jd_block}

---

Analyse this offer and produce a salary negotiation brief with three sections:

OFFER ASSESSMENT
- Is this offer fair for this candidate's profile, experience level, and market?
- Rating: Strong / Fair / Low — with clear reasoning
- What specifically makes it strong, fair, or low? Reference salary benchmarks from the profile (Section 5) and the role signals.
- What elements beyond base salary are worth negotiating (equity, bonus, start date, remote, title, review timeline)?

COUNTER-OFFER STRATEGY
- Recommended counter: specific number or range (not vague "above market")
- Reasoning: why this number is justified and defensible
- Priority order of what to push on: what matters most vs. what's a nice-to-have
- What to accept without pushback if they won't move on salary
- What would make this offer unacceptable regardless of other terms

NEGOTIATION SCRIPT
Write a 150-200 word negotiation email or message the candidate can send.
- Opens by expressing genuine interest in the role — not desperation
- States the counter clearly and confidently — no apology for asking
- Gives 1-2 brief, factual reasons for the counter (market rate, experience level, competing offers if applicable)
- Leaves the door open without groveling
- Signs off with the candidate's full name as given in the profile

Be direct. Give specific numbers. Don't hedge with "it depends" — the candidate needs actionable guidance."""

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

        eval_result    = self.evaluate_job_fit(job_description, model)
        eval_text      = eval_result.get("evaluation", "")

        summary_result = self.generate_cv_summary(job_description, eval_text, model)

        letter_result  = self.generate_cover_letter(
            job_description, eval_text, company_name, role_title, model
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
