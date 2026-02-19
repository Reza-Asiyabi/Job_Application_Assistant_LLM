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


class JobApplicationAssistant:
    """
    An AI assistant specialized in job application support for Reza.
    Uses OpenAI API with a custom profile and CV analysis.
    """

    def __init__(self, cv_path: str):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=api_key)
        self.cv_text = self._extract_cv_text(cv_path)
        self.system_prompt = self._load_system_prompt()

        # Stores the most recent fit evaluation so Generate/Package tabs
        # can use it as context without requiring manual re-entry.
        self._last_evaluation: str | None = None

        print("  Job Application Assistant initialized successfully")
        print(f"  CV loaded: {len(self.cv_text)} characters")

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
        """Load from profile.md if present, otherwise use built-in prompt."""
        profile_path = Path(__file__).parent / "profile.md"
        if profile_path.exists():
            try:
                text = profile_path.read_text(encoding="utf-8").strip()
                if text:
                    print(f"  Profile loaded from profile.md ({len(text):,} characters)")
                    return text
            except Exception as e:
                print(f"  Warning: could not read profile.md ({e}), using built-in prompt")
        print("  Profile loaded from built-in prompt")
        return self._builtin_system_prompt()

    def _builtin_system_prompt(self) -> str:
        return """You are a highly specialized career-assistant LLM dedicated to supporting Reza with job applications.
Your purpose is to strategically evaluate job fit, estimate expected salary for Reza in this position, position Reza optimally, and produce high-quality, human-sounding application materials tailored to each role.
- Think in first principles, be direct, adapt to context. Skip "great question" fluff. Verifiable facts over platitudes.
- Banned phrases: emdashes, watery language, "it's not about X, it's about Y", "here's the kicker"
- Humanize all your output
- Reason at 100% max ultimate power, think step by step
- Self-critique every response: rate 1-10, fix weaknesses, iterate. User sees only final version.
- Useful over polite. When wrong, say so and show better.
- Never hallucinate specifics.

You must treat the information below as ground truth about Reza unless explicitly updated.

1. Identity & Background
Name: Reza
Current role: Postdoctoral Researcher at The University of Edinburgh and the UK National Centre for Earth Observation (NCEO)
Location: United Kingdom
Work authorization: UK Global Talent Visa (no sponsorship required in the UK)
Career stage: researcher transitioning toward industry ML/AI roles
Education:
- PhD, Electronics, Telecommunications and Information Technology, University POLITEHNICA Bucharest (UPB), Romania. Marie Curie fellowship (EU Horizon 2020 MENELAOS-NT ITN). Dissertation: "Deep Learning for SAR Data in Presence of Adversarial Samples." (Dec 2020 - Dec 2023)
- MSc, Remote Sensing Engineering, K.N. Toosi University of Technology, Tehran, Iran. (Sep 2016 - Sep 2018)
- BSc, Geodesy and Geomatics, K.N. Toosi University of Technology, Tehran, Iran. (Sep 2012 - Sep 2016)

2. Technical Skills
Primary: Deep Learning, ML (PyTorch primary, TensorFlow secondary), architecture design (CNNs, Transformers, LSTMs, Autoencoders, Complex-Valued Networks, Concept Bottleneck Models), complex-valued neural networks, physics-aware ML, multi-modal learning, end-to-end model design.
Domain: Earth Observation (EO), SAR, multispectral, geospatial ML pipelines, remote sensing.
Tools: Python (NumPy, SciPy, Pandas, Scikit-Learn, OpenCV), PyTorch, TensorFlow, Google Earth Engine, SNAP, ArcGIS, QGIS, ENVI.

3. Career Direction: transitioning to industry ML/AI roles. Preference: remain in UK. Target: roles that reward depth.

4. CV Highlights: 500+ Google Scholar citations. Projects with ESA, Stanford, Edinburgh, NCEO. PG-CBM architecture. GAIL fellowship (2025-present). Marie Curie fellowship (2020-2023).

9. Meta-Rules: Strategic truth over pleasing language. If a role is a bad fit, say so. Optimize for long-term career trajectory."""

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
            return {
                "content":     response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
            }

        # Streaming path
        create_kwargs = dict(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        try:
            create_kwargs["stream_options"] = {"include_usage": True}
            stream = self.client.chat.completions.create(**create_kwargs)
        except TypeError:
            # Older SDK version without stream_options support
            del create_kwargs["stream_options"]
            stream = self.client.chat.completions.create(**create_kwargs)

        collected = []
        tokens_used = 0
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                delta = chunk.choices[0].delta.content
                collected.append(delta)
                stream_callback(delta)
            if hasattr(chunk, "usage") and chunk.usage is not None:
                tokens_used = chunk.usage.total_tokens

        return {"content": "".join(collected), "tokens_used": tokens_used}

    # ─────────────────────────────────────────────────────────────────────────
    # CV context builder
    # ─────────────────────────────────────────────────────────────────────────

    def _create_cv_context(self) -> str:
        return (
            "## REZA'S COMPLETE CV\n\n"
            "Below is the full text extracted from Reza's CV. "
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

Provide a comprehensive job fit evaluation with this structure:

1. **FIT ASSESSMENT**: Strong fit / Partial fit / Weak fit (with clear reasoning)

2. **MATCH ANALYSIS**:
   - Core strengths that align
   - Relevant experience from CV
   - Unique advantages Reza brings

3. **GAPS AND RISKS**:
   - Missing skills or experience
   - Potential concerns from employer perspective
   - Any red flags

4. **SALARY ESTIMATE**:
   - Expected salary range for Reza in this role
   - Reasoning: company stage, location, seniority signals, role type

5. **STRATEGIC POSITIONING**:
   - Which archetype to use: Research Scientist / Applied ML Engineer / Geospatial AI / Hybrid
   - What to emphasize in the application
   - What to downplay or reframe

6. **APPLICATION RECOMMENDATION**: Yes / Conditional / No — with clear reasoning.

Be honest, strategic, and specific. Reference actual CV details where relevant."""

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
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

Write a compelling CV summary tailored for this specific role. Follow these examples:

Example 1:
"ML researcher transitioning from applied AI to AI safety and alignment research. Proven track record designing interpretable, robust deep learning architectures across projects with the European Space Agency, Stanford and Edinburgh Universities, and the UK National Centre for Earth Observation (NCEO). Expertise in building interpretable neural networks, investigating adversarial robustness, and developing domain-constrained models that maintain reliability under distribution shift. Experienced in end-to-end empirical ML research using PyTorch, from architecture design through experimental workflows to publication. Demonstrated ability to rapidly adapt to new research domains, implement ideas quickly, and communicate complex technical concepts clearly across interdisciplinary teams."

Example 2:
"Geospatial ML/AI engineer with strong experience building and operating geospatial data products from multi-source Earth Observation data, including SAR, multispectral, hyperspectral, and LiDAR. I design end-to-end workflows spanning data ingestion, preprocessing, feature extraction, ML-based analysis, and publication to production-ready geospatial services. Delivered operational solutions across projects with the European Space Agency (ESA), Stanford and Edinburgh Universities, and the UK National Centre for Earth Observation (NCEO). My work focuses on reliable, well-documented, and scalable geospatial pipelines using Python, EO/GIS tools and cloud-based infrastructure, translating complex satellite data into clear maps, dashboards, and decision-ready analytics."

Example 3:
"Applied ML/AI Scientist with extensive experience developing interpretable, scalable, and domain-aware deep learning systems. Experienced in transforming research innovations into deployable AI solutions across high-impact projects with the European Space Agency, Stanford University, and the University of Edinburgh. Skilled in PyTorch with expertise spanning physics-informed learning, LLMs, and multimodal model design. Hands-on experience applying deep learning to complex, high-dimensional data and building robust, production-ready models. Adapt quickly to new technical environments and enjoy collaborating closely with product and engineering teams to translate business requirements into deployable ML solutions."

Requirements:
- 3-5 natural, flowing sentences — similar length to the examples
- Use the evaluation to decide what to emphasize and what to downplay for THIS role
- No generic buzzwords, no hollow AI phrases
- Must sound like Reza: sharp, precise, confident, human"""

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
            stream_callback=stream_callback,
        )
        return {
            "summary":     result["content"],
            "model":       model,
            "tokens_used": result["tokens_used"],
        }

    def generate_cover_letter(self, job_description: str, fit_evaluation: str = None,
                               company_name: str = None, role_title: str = None,
                               model: str = "gpt-4o", stream_callback=None) -> dict:
        """
        Generate a tailored cover letter for a specific role.

        Args:
            job_description:  The complete job posting text.
            fit_evaluation:   Prior fit evaluation text for strategic context.
            company_name:     Company name (extracted from JD if not provided).
            role_title:       Role title (extracted from JD if not provided).
            model:            OpenAI model to use.
            stream_callback:  Optional callable(str) for streaming chunks.

        Returns:
            {"cover_letter": str, "model": str, "tokens_used": int}
        """
        cv_context = self._create_cv_context()
        company_info = f"Company: {company_name}" if company_name else "[Extract company from job description]"
        role_info    = f"Role: {role_title}"       if role_title    else "[Extract role title from job description]"
        eval_block   = (
            f"## STRATEGIC FIT EVALUATION (use this to decide angle and emphasis)\n\n{fit_evaluation}"
            if fit_evaluation
            else "## NOTE\nNo prior evaluation — infer the best positioning directly from the job description and CV."
        )

        user_prompt = f"""{cv_context}

## JOB DESCRIPTION

{job_description}

---

{eval_block}

---

{company_info}
{role_info}

Write a compelling cover letter. Follow these examples as reference for tone, structure, and length:

Example 1:
"Dear Mistral AI Hiring Team, I am an AI/ML researcher with a PhD and over five years of experience developing scalable deep learning systems for complex, high-dimensional, real-world data. I am excited to apply for the Research Engineer - Machine Learning position at Mistral AI, where my expertise in multimodal, physics-informed, and production-ready AI aligns closely with your mission. Throughout my career, I have bridged cutting-edge AI research with deployable solutions. At the University of Edinburgh, I designed Process-Guided Concept Bottleneck Models (PG-CBM), a modular, physics-aware architecture that improved robustness and interpretability for real-world data. Across projects with the European Space Agency and Stanford University, I built end-to-end ML pipelines for processing massive multimodal Earth Observation datasets. What excites me most about Mistral AI is the opportunity to work at the intersection of research and production, where I can turn prototypes into scalable, production-grade components. I would be thrilled to bring my experience in large-scale ML, multimodal modeling, and research-to-production engineering to Mistral AI. Warm regards, Reza M. Asiyabi"

Example 2:
"Dear Nyxium Team, I am a Geospatial AI and Machine Learning researcher with a PhD and several years of experience building applied spatial-ML systems from Earth observation data. I am excited to apply for the Geospatial AI Engineer role because Nyxium's focus on turning complex geospatial data into practical decision-making tools strongly aligns with how I approach applied AI and where I want to take the next step of my career. In my current role at the University of Edinburgh and the UK National Centre for Earth Observation (NCEO), I design and implement end-to-end geospatial ML systems. A recent example: the Process-Guided Concept Bottleneck Model (PG-CBM), a modular AI framework for estimating forest attributes from multi-sensor EO data, where explainability was a first-class design goal. Through collaborations with ESA, Stanford, Edinburgh, and NCEO, I have worked extensively with SAR, multispectral, hyperspectral, and LiDAR data at scale. What attracts me to Nyxium is the opportunity to build geospatial intelligence systems that directly inform real-world decisions. I would welcome the opportunity to contribute my experience to Nyxium's platform. Warm regards, Reza M. Asiyabi"

Requirements:
- 4-5 tight paragraphs, 350-500 words — similar structure and length to the examples
- Use the evaluation to decide the strategic angle, what to emphasize, what to downplay
- Opening: name the specific company and role; state one genuine reason for interest; give a clear value proposition. NEVER open with "I am writing to apply for..."
- Middle: 1-2 concrete, specific examples from the CV with outcomes
- Closing: forward-looking, confident, not pushy or groveling
- Professional but human — reads like a smart person wrote it, not a template
- No hollow buzzwords, no exaggerated claims, no AI-sounding phrases
- Sign off as: Warm regards, Reza M. Asiyabi"""

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

Provide a strong, specific answer to this application question.

Requirements:
- Draw directly from Reza's CV experiences — no generic answers
- Tailor the answer to this specific role and company
- Natural, human language — confident, not a rehearsed speech
- Appropriate length: concise for short questions, structured for open-ended ones
- Honest: acknowledge gaps if directly relevant, but position strengths prominently
- No hollow buzzwords or inflated claims"""

        result = self._call_api(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            model=model,
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

Generate comprehensive interview preparation for Reza for this specific role. Structure it as four parts:

PART 1: TECHNICAL QUESTIONS AND ANSWERS
Generate 5-7 technical questions this interview panel is likely to ask, based on the job requirements.
For each question, write a strong, specific answer grounded in Reza's actual CV — real projects, real architectures, real results.
Not hypothetical. Draw from PG-CBM, SAR deep learning, EO pipelines, ESA/Stanford/NCEO work where relevant.

PART 2: BEHAVIORAL QUESTIONS (STAR FORMAT)
Generate 4-5 behavioral questions focused on: cross-functional collaboration, handling ambiguity, technical leadership, shipping under constraints, failure and recovery.
For each question: write the question, then a complete STAR answer (Situation, Task, Action, Result) drawn from Reza's actual experience.

PART 3: QUESTIONS REZA SHOULD ASK THEM
Generate 5-6 sharp, intelligent questions for Reza to ask the interviewer. These should:
- Signal genuine technical curiosity and strategic thinking
- Probe team culture, technical stack decisions, research-to-production balance, and what "good" looks like in this role
- Avoid generic questions like "what does a typical day look like"
- Be specific to this company and role

PART 4: CULTURE AND MOTIVATION QUESTIONS
Generate 3-4 questions about "why this company / why this role" that the interviewer might ask.
For each: write the question and a strong, honest answer connecting Reza's actual motivations and career direction to this specific company's mission.

Every answer must sound like a confident, senior technical person — not a rehearsed script.
Be specific. Reference actual CV content throughout."""

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

Write a short LinkedIn outreach message from Reza to a recruiter or hiring manager for this role.

Greeting to use: {greeting}

Requirements:
- Maximum 200-250 words — brevity is critical for LinkedIn
- Opens with something specific about the company or role, NOT "I came across your posting" or generic openers
- 1-2 sentences on why Reza is a strong fit — pick the most compelling angle, be concrete
- A clear, low-friction call to action (a quick call, expressing interest — not "please consider my application")
- Warm, professional tone — confident, conversational, not stiff
- Reads like Reza wrote it: precise, not flashy
- Sign off as: Reza M. Asiyabi

Do NOT:
- Use hollow phrases like "passionate about", "excited to leverage", "synergies"
- Write it like a mini cover letter
- Be excessively formal

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
    assistant = JobApplicationAssistant(cv_path="Reza_CV.pdf")

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
