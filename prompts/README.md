# Prompt Templates

Every task prompt the assistant sends to the LLM lives here as an editable file.
Edit these to tune what the AI produces — no code changes needed. Changes take
effect on the next generation (files are re-read on every call).

`{{token}}` placeholders are filled in at runtime. Leave them where they are
(or move them around), but don't rename them.

| File | Used by | Tokens |
|---|---|---|
| `evaluate_job_fit.md` | Evaluate page | `cv_context`, `job_description` |
| `cv_summary.md` | Generate → CV Summary | `cv_context`, `job_description`, `eval_block` |
| `cover_letter.md` | Generate → Cover Letter | `cv_context`, `job_description`, `eval_block`, `company_info`, `role_info`, `tone_instruction` |
| `tone_hybrid.md` / `tone_research.md` / `tone_engineering.md` | Cover letter tone directive (inserted as `tone_instruction`) | — |
| `application_question.md` | Q&A page | `cv_context`, `job_description`, `eval_block`, `question` |
| `interview_prep.md` | Interview page | `cv_context`, `job_description`, `eval_block` |
| `linkedin_message.md` | Generate → LinkedIn | `cv_context`, `job_description`, `eval_block`, `greeting` |
| `followup_email.md` | Interview → Follow-up | `cv_context`, `job_description`, `interviewer_block`, `notes_block` |
| `ats_analysis.md` | ATS check | `job_description`, `content` |
| `rejection_analysis.md` | History → Analyze rejection | `cv_context`, `role_ctx`, `materials_block`, `rejection_block` |
| `salary_negotiation.md` | Salary negotiation dialog | `cv_context`, `offer_details`, `jd_block` |

Token meanings:
- `cv_context` — the full text extracted from the CV PDF, with a header
- `eval_block` — the prior fit evaluation (or a "no prior evaluation" note)
- `company_info` / `role_info` — "Company: X" / "Role: Y" lines
- `greeting` — "Hi <name>," or "Hi [Name],"
- `interviewer_block` / `notes_block` / `materials_block` / `rejection_block` /
  `jd_block` / `role_ctx` — optional context blocks built from user input

The AI's overall behavior/voice rules live in `../profile_instructions.md`, and the
candidate's facts in the personal profile file — these templates only control the
per-task instructions.
