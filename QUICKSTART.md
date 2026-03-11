# Quick Start

Get up and running in 5 minutes.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure your environment

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
CV_PATH=your_cv.pdf
```

Get your API key at: https://platform.openai.com/api-keys

## 3. Add your profile and CV

- **`profile.md`** — Fill in your personal information (name, skills, career goals, key projects). Every `[YOUR ...]` placeholder needs to be replaced with your actual details. This is what the AI uses to generate grounded, specific outputs.
- **CV PDF** — Place your CV in the project directory. Set the filename in `CV_PATH` inside `.env`.

## 4. Verify setup

```bash
python test_setup.py
```

## 5. Launch

```bash
python launch.py          # GUI (recommended)
python cli.py             # Command-line
```

---

## CLI quick reference

**Interactive menu:**
```bash
python cli.py
```

**Direct commands:**
```bash
python cli.py --job-file job.txt --action evaluate
python cli.py --job-file job.txt --action full-package --company "Acme" --role "ML Engineer" --output out.txt
```

Actions: `evaluate` · `cv-summary` · `cover-letter` · `full-package`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not found` | Check `.env` file exists and has the key |
| `CV file not found` | Check `CV_PATH` in `.env` matches your actual filename |
| PDF won't read | Make sure the PDF is text-based, not a scanned image |
| API errors | Check your OpenAI account has credits |

Run `python test_setup.py` for a full diagnostic.
