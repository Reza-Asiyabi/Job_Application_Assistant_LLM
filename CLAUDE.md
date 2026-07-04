# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Purpose

AI-powered job application assistant. Evaluates job postings and generates tailored
application materials (CV summaries, cover letters, interview prep, LinkedIn messages,
follow-up emails, salary negotiation briefs) by combining the user's CV PDF and personal
profile with an LLM (OpenAI API or local Ollama).

## Commands

```bash
pip install -r requirements.txt   # openai, python-dotenv, pypdf
python test_setup.py              # setup verifier (deps, .env, API key, CV file)
python launch.py                  # launch GUI
python cli.py                     # CLI, interactive menu
python cli.py --job-file job.txt --action evaluate --output result.txt
python import_tracker.py file.xlsx  # standalone tracker import
```

Optional deps: `openpyxl` (xlsx import), `requests` + `beautifulsoup4` (URL import, Ollama).

## Architecture

### Core Data Flow

```
.env (OPENAI_API_KEY, CV_PATH, PROFILE_*_PATH)  +  config.json (GUI prefs)
    ↓
JobApplicationAssistant (job_application_assistant.py)
    ├── Extracts text from CV PDF via pypdf
    ├── System prompt = profile_instructions.md + personal profile file (combined)
    │   (paths from get_profile_paths(); fallbacks: personal-only → profile.md → built-in)
    ├── Extracts user name from the "Name:" line → self.user_name
    └── Per request: [system_prompt] + rendered prompts/<task>.md template → chat API
                     (templates re-read every call — edits take effect immediately)
    ↓
GUI (gui.py) / CLI (cli.py) — thin interfaces over the same assistant class
```

### Key Files

- **`job_application_assistant.py`** — All business logic. Task prompts live in
  `prompts/*.md` (loaded per call via `_render_prompt()` with `{{token}}` placeholders —
  see `prompts/README.md`; cover-letter tone directives in `prompts/tone_*.md` via
  `_load_tone()`). Public methods: `evaluate_job_fit`,
  `generate_cv_summary`, `generate_cover_letter` (tones: hybrid/research/engineering),
  `answer_application_question`, `generate_interview_prep`, `generate_linkedin_message`,
  `generate_followup_email`, `analyze_ats_fit`, `extract_job_details`, `analyze_rejection`,
  `generate_salary_negotiation`, `full_application_package`, `save_results`.
  Also: `get_profile_paths()` (module-level), Ollama static helpers
  (`check_ollama_connection`, `list_ollama_models`).

- **`gui.py`** (~4,400 lines) — The only GUI. Class `JobAssistantV3` + `ProfileWizard`
  (guided profile generator). Ten sidebar pages: Setup, Evaluate, Generate, Q&A, Package,
  Interview, History, Profile, Stats, Tracker. Dark/light themes, autosave drafts,
  streaming output, quiz mode, salary negotiation dialog, rejection analysis. Standard
  `tkinter` only. All API calls run in background threads; UI updates go through
  `root.after()`.

- **`cli.py`** — Interactive menu + argparse mode. **`launch.py`** — wrapper calling
  `gui.main()`. **`import_tracker.py`** — standalone xlsx/csv → applications.json import.

### Profile system (the soul of the app)

- System prompt = `profile_instructions.md` (AI behavior rules) + personal profile file
  (user facts), concatenated. Both editable on the GUI Profile page.
- Paths are overridable via `.env`: `PROFILE_INSTRUCTIONS_PATH`, `PROFILE_PERSONAL_PATH`,
  `PROFILE_PATH` (legacy). The tracked `profile_personal.md` / `profile.md` are generic
  templates with `[YOUR ...]` placeholders; users point `PROFILE_PERSONAL_PATH` at a
  private, gitignored copy.
- Changes to profile files affect tone, strategy, and emphasis in every output.

### Configuration & data files (all gitignored)

- **`.env`** — `OPENAI_API_KEY` (required for OpenAI), `CV_PATH` (default `cv.pdf`),
  `OPENAI_BASE_URL`, `OPENAI_TIMEOUT`, `PROFILE_*_PATH` overrides.
- **`config.json`** — GUI prefs: `cv_profiles` (multiple CVs), `active_cv_name`, `model`,
  `openai_models` (selectable model list), geometry, font size, theme, provider,
  Ollama URL/model.
- **`history.json`** — generated materials log (History page). **`applications.json`** —
  structured tracker pipeline. **`drafts.json`** — autosaved page inputs.

### Providers & models

- `JobApplicationAssistant(provider="openai"|"ollama", base_url=...)`. Ollama needs no key.
- Selectable OpenAI models come from `config.json` `"openai_models"`
  (default: `DEFAULT_OPENAI_MODELS` in gui.py). Model is passed per call; the assistant
  method defaults (`gpt-4o`) are just fallbacks.
- `_create_completion()` transparently retries without `temperature` / with
  `max_completion_tokens` for reasoning models that reject those params; the OpenAI client
  is constructed with `max_retries=3` and a timeout.

## Important Design Notes

- **No test suite** — `test_setup.py` is a setup verifier, not unit tests.
- **Streaming** — `_call_api()` takes an optional `stream_callback(str)`. GUI streams;
  CLI and `full_application_package()` mostly block.
- **`_last_evaluation`** — the assistant caches the latest fit evaluation; GUI pages pass
  it automatically as context to generate/Q&A/interview calls.
- **Keyword args** — always call the generate_* methods with keyword arguments; several
  share long optional-parameter lists (a positional `model` once landed in `tone`).
- **Privacy** — this repo is public. Never commit personal data: real profiles, CV PDFs,
  history/applications/config JSONs are all gitignored. `Improvement_Plan.md` is a local
  working document.
- **`Improvement_Plan.md`** — the current roadmap (tiered checklist). Update markers as
  items ship.
