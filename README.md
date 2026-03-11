# Job Application Assistant

An AI assistant with a desktop GUI and command-line interface to help evaluate job fit and generate tailored application materials — powered by OpenAI's GPT models and your personal profile.

## What It Does

- **Job Fit Evaluation** — Strategic analysis with gap assessment, salary estimate, and application recommendation (Yes / Conditional / No)
- **CV Summary** — 3-5 sentence tailored summaries for each role
- **Cover Letter** — Human-sounding, role-specific letters grounded in your actual CV
- **Interview Prep** — Technical Q&A, STAR behavioral answers, and questions to ask the interviewer
- **LinkedIn Message** — Short outreach messages to recruiters
- **Application Q&A** — Answers to specific application form questions
- **Complete Package** — Everything above at once (30–60 seconds)

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your environment
cp .env.example .env
# Edit .env: add OPENAI_API_KEY and set CV_PATH to your CV filename

# 3. Fill in your profile
# Edit profile.md — replace every [YOUR ...] placeholder with your actual info

# 4. Verify setup
python test_setup.py

# 5. Launch
python launch.py        # GUI (recommended)
python cli.py           # Command-line
```

See [QUICKSTART.md](QUICKSTART.md) for a more detailed walkthrough.

---

## Personalizing for Your Use

Two files define who you are. **Both must be filled in before the tool works well.**

### `profile.md` — Your professional profile

This is the AI's system prompt. Open it and replace every `[YOUR ...]` section:

| Section | What to fill in |
|---------|----------------|
| **Identity** | Full name, current role, location, work authorization |
| **Education** | Degrees, universities, dates, fellowships |
| **Technical Skills** | Specific tools and frameworks you actually use |
| **Career Intent** | Target role types, company preferences, priorities |
| **Role Archetypes** | Positioning strategy for each type of role you apply to |
| **Salary Benchmarks** | Market ranges for your level and location |
| **Key Projects** | 3–5 projects you'll reference in interviews and letters |

The more specific and accurate this file is, the better every output will be.

### `.env` — Your configuration

```bash
OPENAI_API_KEY=sk-your-api-key-here
CV_PATH=your_cv.pdf          # filename of your CV PDF in the project directory
```

---

## Usage

### GUI (Recommended)

```bash
python launch.py
```

Seven pages accessible from the sidebar: **Setup → Evaluate → Generate → Q&A → Package → Interview → History**

See [GUI_GUIDE.md](GUI_GUIDE.md) for a full walkthrough.

### CLI — Interactive

```bash
python cli.py
```

### CLI — Command-line arguments

```bash
python cli.py --job-file job.txt --action evaluate
python cli.py --job-file job.txt --action cv-summary
python cli.py --job-file job.txt --action cover-letter --company "Acme" --role "ML Engineer"
python cli.py --job-file job.txt --action full-package --output application.txt
```

### Python API

```python
from job_application_assistant import JobApplicationAssistant

assistant = JobApplicationAssistant()  # reads CV_PATH from .env

result = assistant.evaluate_job_fit(job_description)
result = assistant.generate_cv_summary(job_description)
result = assistant.generate_cover_letter(job_description, company_name="Acme", role_title="ML Engineer")
result = assistant.generate_interview_prep(job_description)
result = assistant.generate_linkedin_message(job_description, recruiter_name="Sarah")
result = assistant.answer_application_question(job_description, question="Why this role?")
result = assistant.full_application_package(job_description, company_name="Acme", role_title="ML Engineer")

assistant.save_results(result, "application.txt")
```

See `examples.py` for runnable examples of every method.

---

## Configuration

### `.env` variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `CV_PATH` | No | `cv.pdf` | Path to your CV PDF |
| `OPENAI_BASE_URL` | No | OpenAI default | Override API endpoint |

### Model options

| Model | Quality | Cost |
|-------|---------|------|
| `gpt-4o` | Recommended | $$$ |
| `gpt-4-turbo` | Good | $$ |
| `gpt-3.5-turbo` | Budget / testing | $ |

Selectable in the GUI Setup page or passed to any API method.

---

## Cost estimates (gpt-4o)

- Evaluation: ~$0.15–0.30 per job
- CV summary / cover letter: ~$0.10–0.30 each
- Complete package: ~$0.40–0.80

Use `gpt-3.5-turbo` for testing (~90% cheaper).

---

## Recommended workflow

```
1. Paste job posting → Evaluate tab
2. If Weak fit → skip
3. If Strong/Partial → Package tab → generate everything
4. Review, edit lightly, save
5. Apply
```

---

## Troubleshooting

```bash
python test_setup.py    # full diagnostic
python cli.py --help    # CLI options
```

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not found` | Create `.env` with your key |
| `CV file not found` | Check `CV_PATH` in `.env` matches your filename |
| GUI won't start | Run `python cli.py` as fallback |
| Empty output | Check API key has credits; try again |

---

## Privacy

CV content and job descriptions are sent to OpenAI for processing. Keep `.env` out of version control (already in `.gitignore`).

---

## File reference

| File | Purpose |
|------|---------|
| `profile.md` | Your professional profile — the AI's system prompt. **Edit this.** |
| `.env` | API key and CV path. **Edit this.** |
| `job_application_assistant.py` | Core assistant class |
| `gui_v2.py` | Desktop GUI |
| `cli.py` | Command-line interface |
| `launch.py` | GUI launcher |
| `examples.py` | Runnable API examples |
| `test_setup.py` | Setup verification |
