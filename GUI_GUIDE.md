# GUI Guide

The GUI (`gui_v2.py`) is a dark, modern desktop interface launched via `python launch.py`.

## Navigation

The left sidebar has seven pages accessed by clicking the labels:

| Symbol | Page | Purpose |
|--------|------|---------|
| `^` | Setup | Configure CV path, model, initialize assistant |
| `*` | Evaluate | Paste a job description and get a fit assessment |
| `+` | Generate | Create CV summaries and cover letters |
| `?` | Q & A | Answer specific application questions |
| `#` | Package | Generate evaluation + CV summary + cover letter at once |
| `~` | Interview | Generate full interview prep materials |
| `=` | History | View and manage past applications |

---

## Setup Page

1. Set the path to your CV PDF (or use the Browse button)
2. Choose your OpenAI model (`gpt-4o` recommended)
3. Click **Initialize** — the assistant loads your CV and profile

The assistant auto-initializes on launch if `CV_PATH` is set in `.env`.

---

## Evaluate Page

1. Paste the full job description into the text area
2. Click **Evaluate Fit**
3. The assistant streams back a structured analysis:
   - Fit assessment (Strong / Partial / Weak)
   - Match analysis with specific CV references
   - Gaps and risks
   - Salary estimate
   - Strategic positioning advice
   - Application recommendation (Yes / Conditional / No)

The evaluation is stored as context and used automatically in subsequent Generate/Interview/Package calls.

---

## Generate Page

1. Paste the job description
2. Optionally enter company name and role title (improves output quality)
3. Click **CV Summary** or **Cover Letter**
4. Output streams in real time — review, copy, or save

If you ran Evaluate first, that context is used automatically.

---

## Q & A Page

For application forms that ask specific questions:

1. Paste the job description
2. Type the application question
3. Click **Answer** — get a CV-grounded, role-specific response

---

## Package Page

Generates evaluation + CV summary + cover letter in one go.

1. Paste the job description
2. Enter company and role (optional but recommended)
3. Click **Generate Package**
4. Wait 30–60 seconds for all three sections to stream in

Use this when you've decided to apply and want everything at once.

---

## Interview Page

1. Paste the job description
2. Click **Generate Interview Prep**
3. Receive four sections:
   - **Technical Q&A** — role-specific technical questions with CV-grounded answers
   - **Behavioral Q&A** — STAR-format answers drawn from your actual experience
   - **Questions to ask them** — smart, specific questions for the interviewer
   - **Culture/motivation Q&A** — "why this company" answers tied to your real goals

---

## History Page

Every generation is automatically saved to `history.json`. The History page lets you:
- Browse past applications by company/role
- View saved outputs
- Mark status: Applied / Interview / Offer / Rejected
- Delete entries

---

## Tips

- **Always evaluate first** — a Weak fit means skip it; a Strong/Partial means proceed
- **Use the Package tab for serious applications** — ensures a consistent narrative
- **Token count** is shown in the status bar — use `gpt-3.5-turbo` for testing, `gpt-4o` for real applications
- **Copy button** copies the full output to clipboard, ready to paste
