# Job Application Assistant for Reza

A highly specialized AI assistant built with OpenAI's GPT models to help Reza evaluate job fit and generate high-quality, tailored application materials for ML/AI roles.

## Features

- **Job Fit Evaluation**: Strategic analysis of how well a role matches Reza's background
- **CV Summary Generation**: Tailored summaries that highlight relevant strengths for each role
- **Cover Letter Writing**: Human-sounding, professional cover letters customized per position
- **Application Questions**: Smart answers to common application questions
- **Complete Package Generation**: All materials in one go

All outputs are:
- ✅ Natural and human-sounding (no AI jargon)
- ✅ Strategically positioned for the specific role
- ✅ Based on actual CV content
- ✅ Honest about fit and gaps
- ✅ Professionally written but not stiff

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Reza's CV in PDF format

### 2. Installation

```bash
# Clone or download the files to a directory
cd job-application-assistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# .env file should contain:
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 4. Add Your CV

Place your CV PDF in the project directory and name it `reza_cv.pdf`, or use a custom path (see usage below).

## Usage

### Option 1: Interactive CLI (Recommended)

Run the interactive command-line interface:

```bash
python cli.py
```

You'll see a menu with options:
1. Evaluate job fit
2. Generate CV summary
3. Generate cover letter
4. Answer application question
5. Generate complete application package
6. Exit

Simply paste the job description when prompted and select what you need.

### Option 2: Command Line (Direct)

Generate materials directly from the command line:

```bash
# Evaluate job fit
python cli.py --job-file job.txt --action evaluate --output evaluation.txt

# Generate CV summary
python cli.py --job-file job.txt --action cv-summary --output summary.txt

# Generate cover letter
python cli.py --job-file job.txt --action cover-letter \
  --company "DeepMind" --role "Research Engineer" --output cover_letter.txt

# Generate complete package
python cli.py --job-file job.txt --action full-package \
  --company "DeepMind" --role "Research Engineer" --output application_package.txt
```

### Option 3: Python Script

Use the assistant programmatically:

```python
from job_application_assistant import JobApplicationAssistant

# Initialize
assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")

# Read job description
job_description = """
[Paste job description here]
"""

# Evaluate fit
evaluation = assistant.evaluate_job_fit(job_description)
print(evaluation['evaluation'])

# Generate CV summary
summary = assistant.generate_cv_summary(job_description)
print(summary['summary'])

# Generate cover letter
cover_letter = assistant.generate_cover_letter(
    job_description=job_description,
    company_name="Example Company",
    role_title="Machine Learning Engineer"
)
print(cover_letter['cover_letter'])

# Or get everything at once
package = assistant.full_application_package(
    job_description=job_description,
    company_name="Example Company",
    role_title="ML Engineer"
)

# Save results
assistant.save_results(package, "complete_application.txt")
```

## Advanced Usage

### Custom CV Path

```bash
python cli.py /path/to/your/cv.pdf
```

### Different OpenAI Model

```bash
python cli.py --model gpt-4-turbo
```

Available models:
- `gpt-4o` (default, recommended)
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo` (faster, cheaper, but lower quality)

### Save Output in Different Formats

```python
# JSON format
assistant.save_results(results, "output.json")

# Text format
assistant.save_results(results, "output.txt")
```

## API Methods

### `JobApplicationAssistant`

Main class for the assistant.

**Initialization:**
```python
assistant = JobApplicationAssistant(cv_path: str)
```

**Methods:**

1. **`evaluate_job_fit(job_description, model='gpt-4o')`**
   - Evaluates how well the role matches Reza's profile
   - Returns: dict with evaluation, model, tokens_used

2. **`generate_cv_summary(job_description, model='gpt-4o')`**
   - Generates a tailored 3-4 sentence CV summary
   - Returns: dict with summary, model, tokens_used

3. **`generate_cover_letter(job_description, company_name=None, role_title=None, model='gpt-4o')`**
   - Generates a complete cover letter
   - Returns: dict with cover_letter, model, tokens_used

4. **`answer_application_question(job_description, question, model='gpt-4o')`**
   - Answers a specific application question
   - Returns: dict with question, answer, model, tokens_used

5. **`full_application_package(job_description, company_name=None, role_title=None, model='gpt-4o')`**
   - Generates evaluation + CV summary + cover letter
   - Returns: dict with all materials and total_tokens_used

6. **`save_results(results, output_path)`**
   - Saves results to file (auto-detects format from extension)
   - Supports .txt and .json

## How It Works

### The System Prompt

The assistant uses your detailed career profile as its system prompt, which defines:

- Your identity, background, and career stage
- Technical skill profile (weighted realistically)
- Career goals and preferences
- Writing style requirements
- Strategic positioning guidelines

### The CV Context

For every query, the assistant:
1. Extracts text from your CV PDF
2. Includes the full CV content in the context
3. References specific projects, publications, and achievements
4. Ensures all claims are grounded in your actual experience

### Strategic Evaluation

The assistant doesn't just match keywords. It:
- Assesses **true fit** vs surface-level match
- Identifies **gaps and risks** honestly
- Finds **hidden advantages** from your unique background
- Recommends **strategic positioning** for each role
- Tells you if you **shouldn't apply** when fit is weak

## Cost Estimates

Using `gpt-4o` (recommended):
- Job fit evaluation: ~$0.15-0.30 per job
- CV summary: ~$0.10-0.20 per job
- Cover letter: ~$0.15-0.30 per job
- Complete package: ~$0.40-0.80 per job

Using `gpt-4-turbo`:
- About 30% more expensive but similar quality

Using `gpt-3.5-turbo`:
- About 90% cheaper but noticeably lower quality

*Costs are approximate and depend on job description length and CV size.*

## Tips for Best Results

### Job Descriptions
- Include the full job posting (responsibilities, requirements, nice-to-haves)
- Include company information if available
- Copy the exact text rather than summarizing

### Company/Role Information
- Provide company name and role title when you have them
- The assistant can extract these from the JD, but explicit info is better
- Include any additional context about the company or team if relevant

### Iterative Refinement
- Generate materials, review them, then ask for adjustments
- You can ask for different tones or emphasis
- Request changes to specific sections

### Multiple Roles
- Save each application package with descriptive filenames
- Example: `deepmind_research_engineer_application.txt`
- Keep a folder of applications for reference

## Troubleshooting

### "OPENAI_API_KEY not found"
- Ensure `.env` file exists in the project directory
- Check that the API key is correctly formatted
- No quotes needed around the key in `.env`

### "CV file not found"
- Check the file path is correct
- Ensure the PDF is readable (not corrupted or encrypted)
- Try absolute path: `python cli.py /full/path/to/cv.pdf`

### PDF extraction issues
- Some PDFs with complex formatting may not extract well
- Try re-saving the PDF or using a different PDF tool
- Check extracted text by running the test script (see below)

### Rate limits
- If you hit OpenAI rate limits, wait a few minutes
- Consider using gpt-3.5-turbo for testing
- Batch process applications with delays between them

## Testing Your Setup

Create a simple test:

```python
from job_application_assistant import JobApplicationAssistant

# Test initialization
assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")

# Test with a simple job description
test_job = """
Machine Learning Engineer
Requirements: Python, PyTorch, PhD preferred
"""

# Generate evaluation
result = assistant.evaluate_job_fit(test_job)

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print("✓ Setup successful!")
    print(f"\nSample output:\n{result['evaluation'][:200]}...")
```

## File Structure

```
job-application-assistant/
├── job_application_assistant.py  # Main assistant class
├── cli.py                         # Interactive CLI
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment file
├── .env                          # Your API key (create this)
├── reza_cv.pdf                   # Your CV (add this)
└── README.md                     # This file
```

## Privacy & Security

- Your CV and all data stay local (only API calls to OpenAI)
- API calls include CV content and job descriptions
- OpenAI's API doesn't train on your data (as of their current policy)
- Keep your `.env` file secure and never commit it to version control

## Support & Customization

### Customizing the System Prompt

Edit the `_load_system_prompt()` method in `job_application_assistant.py` to update:
- Career goals
- Skill emphasis
- Writing style preferences
- Evaluation criteria

### Adding New Features

The architecture is modular. You can easily add:
- LinkedIn message generation
- Email follow-up templates
- Skill gap analysis
- Interview preparation
- Resume reformatting

### Model Selection

Different models for different needs:
- **gpt-4o**: Best quality, recommended for final materials
- **gpt-4-turbo**: Good balance of speed and quality
- **gpt-3.5-turbo**: Fast and cheap for testing and drafts

## Examples

### Example 1: Quick Evaluation

```bash
# Save job description to file
cat > job.txt << EOF
Senior ML Engineer at Tech Company
Requirements: PyTorch, Computer Vision, PhD
Remote, UK-based preferred
EOF

# Get evaluation
python cli.py --job-file job.txt --action evaluate
```

### Example 2: Complete Application

```python
assistant = JobApplicationAssistant("reza_cv.pdf")

job = open("deepmind_jd.txt").read()

package = assistant.full_application_package(
    job_description=job,
    company_name="DeepMind",
    role_title="Research Engineer"
)

assistant.save_results(package, "deepmind_application.txt")
```

### Example 3: Answer Multiple Questions

```python
questions = [
    "Why do you want to work at our company?",
    "Describe a challenging ML project you've worked on",
    "Where do you see yourself in 5 years?"
]

for i, q in enumerate(questions):
    result = assistant.answer_application_question(job_description, q)
    assistant.save_results(result, f"answer_{i+1}.txt")
```

## License

This is a personal tool. Modify and use as needed.

## Changelog

**v1.0** - Initial release
- Job fit evaluation
- CV summary generation
- Cover letter generation
- Application question answering
- Interactive CLI
- Command-line interface
- Python API
