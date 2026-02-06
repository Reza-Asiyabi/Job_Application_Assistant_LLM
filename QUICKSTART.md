# Quick Start Guide

Get up and running with the Job Application Assistant in 5 minutes.

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `PyPDF2` - PDF text extraction

## Step 2: Configure API Key (1 minute)

1. Create a `.env` file in the project directory:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

   Get your API key from: https://platform.openai.com/api-keys

## Step 3: Add Your CV (1 minute)

Place your CV PDF in the project directory and name it `reza_cv.pdf`.

Alternatively, use a custom path when running the assistant.

## Step 4: Test Setup (1 minute)

Run the test script to verify everything works:

```bash
python test_setup.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ .env file exists
- ✓ API key is valid
- ✓ CV file exists
- ✓ API connection works
- ✓ PDF extraction works

## Step 5: Start Using (1 minute)

### Option A: Interactive Mode (Easiest)

```bash
python cli.py
```

Then follow the menu prompts!

### Option B: Command Line

```bash
# Save job description to a file
cat > job.txt << EOF
[Paste job description here]
EOF

# Generate complete application package
python cli.py --job-file job.txt --action full-package --output application.txt
```

### Option C: Python Script

```python
from job_application_assistant import JobApplicationAssistant

assistant = JobApplicationAssistant("reza_cv.pdf")

job_description = """
[Your job description here]
"""

# Get complete package
package = assistant.full_application_package(
    job_description=job_description,
    company_name="Company Name",
    role_title="Role Title"
)

# Save it
assistant.save_results(package, "application.txt")
```

## Common First Tasks

### Evaluate a Job

```bash
python cli.py
# Select: 1. Evaluate job fit
# Paste job description
# Type END
```

### Generate Cover Letter

```bash
python cli.py
# Select: 3. Generate cover letter
# Paste job description
# Type END
# Enter company name
# Enter role title
```

### Get Everything at Once

```bash
python cli.py
# Select: 5. Generate complete application package
# Paste job description
# Type END
# Enter company name and role
# Save to file when prompted
```

## Tips for First Use

1. **Start with evaluation** - Always evaluate fit first before spending time on materials

2. **Use real job postings** - Test with actual roles you're interested in

3. **Review the outputs** - The assistant is smart but you should always review and adjust

4. **Iterate** - Generate, review, and ask for adjustments if needed

5. **Save everything** - Keep a folder of applications for reference

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure `.env` file exists
- Check the API key is in the file
- No quotes or spaces around the key

### "CV file not found"
- Ensure `reza_cv.pdf` is in the same directory
- Or use: `python cli.py /path/to/your/cv.pdf`

### PDF won't read
- Try re-saving the PDF
- Make sure it's not password-protected
- Check it's a real PDF, not a scan image

### API errors
- Check your OpenAI account has credits
- Verify API key is correct
- Check internet connection

## What's Next?

1. **Try the examples**: `python examples.py`
2. **Read the full README**: `README.md`
3. **Customize for your needs**: Edit `job_application_assistant.py`

## Getting Help

- Check `README.md` for detailed documentation
- Run `python test_setup.py` to diagnose issues
- Review the example scripts in `examples.py`

## Cost Information

Using GPT-4o (recommended):
- ~$0.40-0.80 per complete application package
- ~$0.15-0.30 per individual component

Test with GPT-3.5-turbo first if you want to save money (add `--model gpt-3.5-turbo`).

---

**You're ready!** Start with: `python cli.py`
