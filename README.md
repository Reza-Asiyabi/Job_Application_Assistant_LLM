# Job Application Assistant

**An AI-powered desktop tool for evaluating job fit and generating tailored application materials.**

Built for people who apply strategically — not by spray and pray. Paste a job description, get a frank evaluation, and generate a cover letter, CV summary, interview prep, and LinkedIn message grounded in your actual CV and profile. Runs on OpenAI (cloud) or Ollama (fully local, no API key, no cost, offline).

---

## What It Does

| Feature | What you get |
|---|---|
| **Job Fit Evaluation** | Strong / Partial / Weak rating · gap analysis · salary estimate · application recommendation (Yes / Conditional / No) |
| **CV Summary** | 3–5 sentence tailored summary for each role type |
| **Cover Letter** | Human-sounding, role-specific letters in three tones: Hybrid / Research-led / Engineering-led |
| **Interview Prep** | Technical Q&A with CV-grounded answers · STAR behavioral stories · questions to ask · how to handle your weak spots |
| **LinkedIn Message** | 100–150 word outreach messages that don't read like cover letters |
| **Application Q&A** | Answers to specific application form questions, with question-type detection |
| **Complete Package** | Evaluation + CV summary + cover letter in one pass |
| **Follow-Up Email** | Post-interview thank-you emails referencing specific conversation points |
| **Salary Negotiation** | Offer fairness assessment · counter-offer strategy · ready-to-send negotiation email |
| **ATS Keyword Check** | Score your CV summary or cover letter against the JD for keyword coverage |
| **Rejection Analysis** | What likely went wrong · what to do differently · what was genuinely strong |
| **Application Tracker** | Full pipeline tracker (Watching → Applied → Interview → Offer → Rejected) with funnel statistics |
| **History** | All generated materials saved, searchable, filterable, exportable |

---

## Screenshots

The GUI has a dark navy theme with a sidebar for navigation. Key pages:

- **Setup** — configure CV, model, and provider (OpenAI or Ollama)
- **Evaluate** — paste a JD, get a strategic fit analysis
- **Generate** — CV summaries, cover letters (with tone options), LinkedIn messages, ATS check, salary negotiation
- **Interview** — interview prep + follow-up email generator + quiz mode
- **Tracker** — application pipeline with stats bar and funnel metrics
- **Stats** — conversion funnel, response/interview/offer rates, all-time token usage

---

## Requirements

- Python 3.9+
- A CV in PDF format (text-based, not scanned)
- **Either** an OpenAI API key **or** Ollama installed locally (free)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Reza-Asiyabi/Job_Application_Assistant_LLM.git
cd Job_Application_Assistant_LLM

# Install dependencies
pip install -r requirements.txt
```

Optional dependencies (install if you want these features):
```bash
pip install openpyxl        # XLSX import for the Application Tracker
pip install requests beautifulsoup4   # Import job descriptions from URLs
```

---

## Quick Start — OpenAI (Cloud)

**1. Get an API key**

Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and create a key.

**2. Set up your environment**

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
CV_PATH=your_cv.pdf
```

**3. Add your CV**

Place your CV PDF in the project directory. Set `CV_PATH` to match the filename.

**4. Fill in your profile**

Use the Profile Wizard in the GUI (Setup Wizard button on the Profile page), or manually edit `profile_personal.md` — replacing every `[YOUR ...]` placeholder with your real information.

**5. Launch**

```bash
python launch.py     # GUI (recommended)
python cli.py        # Command-line
```

---

## Quick Start — Ollama (Local, Free, Offline)

Ollama runs AI models on your own machine. **No API key. No cost. No data leaves your computer.**

### Step 1 — Install Ollama

**Windows:**
Download and run the installer from [ollama.com/download](https://ollama.com/download).

**macOS:**
```bash
brew install ollama
```
Or download from [ollama.com/download](https://ollama.com/download).

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2 — Start the Ollama server

After installing, start Ollama:

```bash
ollama serve
```

Keep this running in the background. On Windows, Ollama starts automatically after installation and runs in the system tray.

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```
You should see a JSON response. If you get "Connection refused", run `ollama serve` first.

### Step 3 — Pull a model

Download a model to your machine. This is a one-time download per model.

```bash
ollama pull qwen2.5:7b        # Recommended — strong instruction following (~5 GB)
ollama pull llama3.2:11b      # Good quality, balanced (~8 GB)
ollama pull mistral-nemo      # Good for writing tasks (~7 GB)
ollama pull llama3.2          # Fast and light (~2 GB)
```

Downloads are large (2–10 GB). Make sure you have enough disk space.

List your installed models:
```bash
ollama list
```

### Step 4 — Configure the app

**In the GUI:**
1. Launch the app: `python launch.py`
2. Go to **Setup** page
3. Under **Provider & Model**, select **Ollama (local, no API key)**
4. The URL should auto-fill to `http://localhost:11434`
5. Click **Check** — it should show `● Connected — N models installed`
6. Select your model from the list (double-click or click "Use Model")
7. Click **Initialize Assistant**

**Or pull a new model directly from the app:**
- Click **Pull…** in the Ollama section
- Type the model name (e.g. `qwen2.5:7b`)
- Watch the download progress in real time

That's it. No `.env` file needed. No API key. Works offline.

### Recommended Ollama Models

For job application materials, you need a model that follows instructions precisely, maintains structured output, and writes natural English. Not all models are equally good at this.

| Model | Pull command | Download size | RAM needed | Best for |
|---|---|---|---|---|
| **qwen2.5:7b** ⭐ Recommended | `ollama pull qwen2.5:7b` | ~4.7 GB | ~6 GB | Best instruction following for the size; strong writing quality |
| **qwen2.5:14b** | `ollama pull qwen2.5:14b` | ~9 GB | ~12 GB | Best local quality overall; noticeably better cover letters |
| **llama3.2:11b** | `ollama pull llama3.2:11b` | ~8 GB | ~10 GB | Excellent all-rounder; good STAR story generation |
| **mistral-nemo** | `ollama pull mistral-nemo` | ~7.1 GB | ~8 GB | Good at writing tasks; solid cover letter tone |
| **phi4** | `ollama pull phi4` | ~9.1 GB | ~10 GB | Strong reasoning; good for evaluation and ATS analysis |
| **deepseek-r1:8b** | `ollama pull deepseek-r1:8b` | ~5 GB | ~6 GB | Good structured output; explicit reasoning visible |
| **llama3.2** (3B) | `ollama pull llama3.2` | ~2 GB | ~3 GB | Fast; acceptable for short outputs; not great for cover letters |
| **gemma3:4b** | `ollama pull gemma3:4b` | ~3.3 GB | ~4 GB | Fast and capable for its size |

**Recommendations by use case:**

- **Best overall quality:** `qwen2.5:14b` or `llama3.2:11b` — if your machine has 12 GB+ RAM
- **Best balance of speed and quality:** `qwen2.5:7b` — works well on most modern laptops with 8 GB RAM
- **Low RAM / fast machine:** `llama3.2` (3B) or `gemma3:4b` — acceptable quality, much faster
- **Analytical tasks** (evaluations, ATS check): `phi4` or `deepseek-r1:8b`
- **Writing tasks** (cover letters, LinkedIn): `qwen2.5:7b` or `mistral-nemo`

> **Note:** Ollama models are significantly smaller than GPT-4o. Expect output quality roughly equivalent to GPT-3.5-turbo. Cover letters and evaluations are usable but may require more editing than the cloud version. Structured outputs (STAR stories, multi-part evaluations) work better with 7B+ models.

**Check available models and pull new ones:**
```bash
ollama list              # list installed models
ollama pull <name>       # download a model
ollama rm <name>         # remove a model
ollama show <name>       # show model info
```

Browse the full library at [ollama.com/library](https://ollama.com/library).

---

## Your Profile — The Most Important Setup Step

The tool generates application materials by combining your CV with your personal profile. **The quality of the output is directly proportional to the quality of your profile.**

### What your profile contains

`profile_personal.md` defines who you are — your background, technical skills, career goals, salary expectations, best projects, STAR stories, and what you're genuinely interested in. The AI uses this as ground truth for every output.

`profile_instructions.md` defines how the AI behaves — writing tone, banned phrases, quality bar, output rules. You usually don't need to change this.

### Option A — Profile Setup Wizard (recommended for new users)

1. Launch the app: `python launch.py`
2. Go to **Profile** page
3. Click **Setup Wizard**
4. Fill in 10 guided steps:
   - Identity & Background
   - Education
   - Technical Skills
   - Career Goals & Positioning
   - Experience & Key Projects
   - Salary Benchmarks & Awards
   - Career Narrative (your "connecting thread" story)
   - Domains of Interest & Target Companies
   - Honest Gaps & STAR Stories
   - Search Logistics & Portfolio
5. Click **✓ Save Profile** — done

The wizard generates a complete, properly formatted `profile_personal.md`.

### Option B — Edit directly

Open `profile_personal.md` in any text editor and replace every `[YOUR ...]` placeholder with your real information. Save. The app reloads it immediately on the Profile page.

Key sections that have the most impact on output quality:
- **Section 4 (Role Archetypes)** — which angle to use for each type of role
- **Section 7 (Key Projects)** — specific projects with outcomes and numbers
- **Section 8 (Career Narrative)** — your "why" story
- **Section 11 (STAR Stories)** — pre-prepared behavioral interview answers

### Checking your profile

On the Profile page, after saving, a warning banner appears if any `[YOUR ...]` placeholders were left unfilled. This tells you exactly which sections still need attention.

---

## Using the GUI

Launch with:
```bash
python launch.py
```

### Page-by-page guide

**⚙ Setup**
- Select your provider: OpenAI (requires API key) or Ollama (local, free)
- Add multiple CV versions and switch between them at runtime
- Initialize the assistant (one-time per session, or auto-initializes on launch)
- Preview extracted CV text to verify your PDF parsed correctly
- View the initialization log for debugging

**◎ Evaluate**
- Paste a job description (or click **URL** to import directly from a job posting URL)
- Click **⟶ Evaluate Fit** to get a full strategic analysis
- Output: fit rating, match analysis, gaps, company context, salary estimate, positioning strategy, and application recommendation

**✦ Generate**
- Paste a job description
- Fill in optional Company and Role fields for better output
- Generate: **CV Summary**, **Cover Letter** (with Hybrid / Research-led / Engineering-led tone options), **LinkedIn** message
- **ATS Check** — score your generated content against the JD
- **Salary Negotiate** — paste a received offer and get a negotiation brief

**◇ Q & A**
- Paste a JD and type a specific application question
- The AI detects the question type (motivation, competency, STAR, technical, weakness) and responds accordingly

**▣ Package**
- Paste a JD, fill in company and role
- Generates evaluation + CV summary + cover letter in sequence
- The three outputs are stitched into one ready-to-use document

**◉ Interview**
- Paste a JD to generate a 5-part interview prep:
  - Technical questions with CV-grounded answers
  - STAR behavioral questions and answers
  - Questions to ask the interviewer
  - Motivation / "why us" questions
  - How to handle your specific weak spots
- **Follow-Up Email** — add interviewer name and notes from the conversation; generates a post-interview thank-you email
- **⚡ Quiz Mode** — flashcard-style quiz on the generated questions

**☰ History**
- All generated materials are saved automatically
- Search and filter by type, status, company
- Add personal notes per entry (auto-saved)
- Set application status (Applied / Interview / Offer / Rejected)
- **Analyze Rejection** — for Rejected entries, paste the rejection email and get a learning analysis
- Export as CSV or JSON
- "+ Add to Tracker" — pre-fills the Tracker from a history entry

**◐ Profile**
- Two-tab editor: **Personal Profile** (your info) and **AI Instructions** (AI behavior)
- **Setup Wizard** — guided 10-step form
- Placeholder warning banner shows any unfilled `[YOUR ...]` sections after saving

**▤ Tracker**
- Full application pipeline tracker with 9 statuses
- **Pipeline Stats Bar** — shows counts per status; click to filter the table
- **Conversion Funnel** — interview rate and offer rate based on `peak_stage` (so rejected-after-interview entries correctly count as "reached interview")
- Add, edit, delete entries; sort by any column
- Date fields: Applied, Interview, Decision
- Import from CSV or XLSX (any column naming convention)
- Export to CSV

**◑ Stats**
- Current active pipeline by status
- Conversion funnel: response rate, interview rate, offer rate
- Generated materials count by type
- All-time token usage and estimated cost (shows "Local (free)" for Ollama)
- Current session stats

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Primary action on current page (evaluate / generate / save) |
| `Ctrl+S` | Save output for current page |
| `Ctrl+1` – `Ctrl+9` | Navigate to sidebar pages 1–9 |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo in any text area |
| `A–` / `A+` | Decrease / increase font size (header buttons) |
| `☀ / 🌙` | Toggle dark / light theme (header button) |

---

## Using the CLI

### Interactive menu

```bash
python cli.py
```

Presents a numbered menu:
1. Evaluate job fit
2. Generate CV summary
3. Generate cover letter
4. Answer application question
5. Generate complete package
6. Generate interview prep
7. Generate LinkedIn / recruiter message
8. Exit

Results stream in real time. After each result, you can save to a file.

### Command-line arguments (non-interactive)

```bash
# Evaluate a job description
python cli.py --job-file job.txt --action evaluate

# Generate a cover letter
python cli.py --job-file job.txt --action cover-letter --company "Acme" --role "ML Engineer"

# Generate a CV summary and save it
python cli.py --job-file job.txt --action cv-summary --output summary.txt

# Generate interview prep
python cli.py --job-file job.txt --action interview-prep

# Generate a LinkedIn message with recruiter name
python cli.py --job-file job.txt --action linkedin --recruiter "Sarah"

# Answer a specific question
python cli.py --job-file job.txt --action qa --question "Why do you want this role?"

# Full package (evaluation + CV summary + cover letter)
python cli.py --job-file job.txt --action full-package --company "Acme" --role "ML Engineer" --output package.txt
```

All actions stream output to the terminal in real time. Pass `--output` to save directly to a file instead.

### Batch processing

Evaluate an entire folder of job descriptions at once:

```bash
# Evaluate all .txt files in a folder
python cli.py --batch-dir ./jobs/ --action evaluate

# Generate cover letters for all, save to a results folder
python cli.py --batch-dir ./jobs/ --action cover-letter --output-dir ./letters/

# Full package for each job
python cli.py --batch-dir ./jobs/ --action full-package --output-dir ./results/
```

Creates one output file per input, plus a `batch_summary.csv` with status and token counts.

---

## Python API

```python
from job_application_assistant import JobApplicationAssistant

# OpenAI (reads OPENAI_API_KEY from environment)
assistant = JobApplicationAssistant(cv_path="your_cv.pdf")

# Ollama (local, no API key needed)
assistant = JobApplicationAssistant(
    cv_path="your_cv.pdf",
    provider="ollama",
    base_url="http://localhost:11434/v1"
)
```

Available methods:

```python
# Job fit evaluation
result = assistant.evaluate_job_fit(job_description)
print(result["evaluation"])

# CV summary (tailored to role)
result = assistant.generate_cv_summary(job_description)
print(result["summary"])

# Cover letter (tone: "hybrid" | "research" | "engineering")
result = assistant.generate_cover_letter(
    job_description,
    company_name="Acme Corp",
    role_title="ML Engineer",
    tone="hybrid"
)
print(result["cover_letter"])

# Interview preparation
result = assistant.generate_interview_prep(job_description)
print(result["interview_prep"])

# LinkedIn outreach message
result = assistant.generate_linkedin_message(
    job_description,
    recruiter_name="Sarah"
)
print(result["linkedin_message"])

# Application question answer
result = assistant.answer_application_question(
    job_description,
    question="Describe a time you led a cross-functional project."
)
print(result["answer"])

# Follow-up email after interview
result = assistant.generate_followup_email(
    job_description,
    interviewer_name="Dr. Smith",
    interview_notes="Discussed the PG-CBM project and model interpretability."
)
print(result["followup_email"])

# Salary negotiation brief
result = assistant.generate_salary_negotiation(
    offer_details="Base: £75,000 + 10% bonus + 0.05% equity",
    job_description=job_description
)
print(result["salary_negotiation"])

# ATS keyword analysis
result = assistant.analyze_ats_fit(job_description, cover_letter_text)
print(result["ats_analysis"])

# Rejection analysis
result = assistant.analyze_rejection(
    company_name="Acme Corp",
    role_title="ML Engineer",
    rejection_message="We have decided to move forward with other candidates.",
    application_materials=cover_letter_text
)
print(result["rejection_analysis"])

# Complete package (evaluation + CV summary + cover letter)
result = assistant.full_application_package(
    job_description,
    company_name="Acme Corp",
    role_title="ML Engineer"
)

# Save any result to a file
assistant.save_results(result, "application.txt")
```

All methods support streaming via `stream_callback`:
```python
result = assistant.generate_cover_letter(
    job_description,
    stream_callback=lambda chunk: print(chunk, end="", flush=True)
)
```

---

## Configuration Reference

### `.env` file (OpenAI only)

```bash
OPENAI_API_KEY=sk-your-key-here   # Required for OpenAI
CV_PATH=your_cv.pdf               # Optional (default: cv.pdf)
OPENAI_BASE_URL=                  # Optional: override API endpoint
```

Ollama users do not need a `.env` file.

### `config.json` (auto-generated, gitignored)

Stores your preferences across sessions:
- Multiple CV profiles (name → path)
- Active provider (OpenAI or Ollama)
- Ollama URL and last-used model
- Last-selected OpenAI model
- Window geometry and font size
- Theme preference (dark / light)

### Multiple CV support

You can register multiple CV versions (Research CV, Engineering CV, etc.) in the Setup page. Switch between them without restarting. Each loads instantly and reinitialises the assistant.

---

## OpenAI Models

| Model | Quality | Notes |
|---|---|---|
| `gpt-4o` | ⭐ Best | Recommended for final applications |
| `gpt-4-turbo` | High | Good alternative to gpt-4o |
| `gpt-3.5-turbo` | Budget | Good for testing and drafts (~90% cheaper) |

**Estimated costs per action (gpt-4o):**
- Evaluation: ~$0.10–0.25
- CV summary / cover letter: ~$0.08–0.20
- Interview prep (5 parts): ~$0.25–0.50
- Complete package: ~$0.30–0.60

---

## Privacy

**OpenAI mode:** Your CV content, profile, and job descriptions are sent to OpenAI's servers for processing. This is the same as using ChatGPT. Review [OpenAI's privacy policy](https://openai.com/privacy).

**Ollama mode:** Everything runs on your machine. Nothing is transmitted externally. Your CV, profile, and job descriptions never leave your computer. Suitable for sensitive applications.

Files that are never committed to version control (in `.gitignore`):
- `.env` (API key)
- `history.json` (your generated materials)
- `applications.json` (your tracker data)
- `config.json` (your preferences including CV paths)
- `drafts.json` (auto-saved drafts)
- Your CV PDF

---

## Troubleshooting

```bash
python test_setup.py    # Full diagnostic (OpenAI mode)
```

### Common issues

| Problem | Solution |
|---|---|
| `OPENAI_API_KEY not found` | Create `.env` with your key from [platform.openai.com](https://platform.openai.com/api-keys) |
| `CV file not found` | Check `CV_PATH` in `.env` matches your CV filename exactly |
| Very short CV text extracted | Your PDF may be scanned. Use a text-based PDF. Use "Preview CV Text" on Setup page to verify. |
| `Cannot connect to Ollama` | Run `ollama serve` in a terminal first |
| `model not found` error | Pull the model first: `ollama pull <model-name>` |
| Ollama output quality poor | Use a larger model (7B+). `qwen2.5:7b` is the recommended minimum. |
| GUI won't start | Run `python cli.py` as fallback; check Python version (3.9+) |
| Streaming stops mid-response | Check network stability (OpenAI); check RAM availability (Ollama) |
| Import from URL fails | Many sites (LinkedIn, Workday) require login. Copy-paste the JD manually instead. |

---

## File Reference

| File | Purpose |
|---|---|
| `launch.py` | GUI launcher — run this to start |
| `gui.py` | Full desktop GUI (dark theme, 10 sidebar pages) |
| `cli.py` | Command-line interface (interactive + argument modes + batch) |
| `job_application_assistant.py` | Core assistant class — all generation logic |
| `profile_instructions.md` | AI behavior rules — writing tone, quality bar, banned phrases |
| `profile_personal.md` | **Your personal profile template** — fill this in |
| `import_tracker.py` | CLI tool to import a CSV/XLSX tracking spreadsheet |
| `test_setup.py` | Setup verifier for OpenAI mode |
| `examples.py` | Runnable API examples |
| `.env.example` | Template for environment configuration |

Generated files (gitignored, stored locally):
| File | Contents |
|---|---|
| `history.json` | All generated materials with metadata |
| `applications.json` | Your application tracker data |
| `config.json` | User preferences (models, CV paths, theme) |
| `drafts.json` | Auto-saved JD input drafts |

---

## Recommended Workflow

```
1. Paste job posting → Evaluate page
   If "Weak fit" → skip (save your time)
   If "Strong / Partial fit" → continue

2. Generate → CV Summary + Cover Letter (pick the right tone)
   Run ATS Check to verify keyword coverage
   Review, adjust lightly — the output is a strong first draft

3. Interview → Generate Interview Prep
   Use Quiz Mode to test yourself before the interview

4. Tracker → add the application
   Update status as it progresses

5. If rejected → History → Analyze Rejection
   Extract what to do differently next time
```

---

## Contributing

Issues and pull requests are welcome. For significant changes, open an issue first to discuss.

The codebase is a single Python project:
- `job_application_assistant.py` — all AI logic (add new generation methods here)
- `gui.py` — the entire GUI (tkinter, one file by design)
- `cli.py` — the CLI interface

---

*Built with Python · tkinter · OpenAI API · Ollama*
