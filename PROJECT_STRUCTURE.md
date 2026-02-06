# Project Structure

## File Overview

```
job-application-assistant/
│
├── Core Files
│   ├── job_application_assistant.py    # Main assistant class (core logic)
│   ├── cli.py                          # Interactive command-line interface
│   ├── requirements.txt                # Python dependencies
│   └── .env                           # Your API key (create from .env.example)
│
├── Documentation
│   ├── README.md                       # Complete documentation
│   ├── QUICKSTART.md                   # 5-minute setup guide
│   └── PROJECT_STRUCTURE.md            # This file
│
├── Examples & Testing
│   ├── examples.py                     # Usage examples
│   ├── test_setup.py                   # Setup verification script
│   └── .env.example                    # Template for environment variables
│
└── Your Files (to add)
    ├── reza_cv.pdf                     # Your CV (required)
    └── .env                            # Your API configuration (required)
```

## File Descriptions

### Core Application Files

#### `job_application_assistant.py` (Main Class)
**Purpose**: Core assistant logic and API integration

**Key Components**:
- `JobApplicationAssistant` class
- PDF text extraction
- OpenAI API integration
- System prompt management
- CV context building

**Main Methods**:
- `evaluate_job_fit()` - Analyze job-candidate match
- `generate_cv_summary()` - Create tailored CV summaries
- `generate_cover_letter()` - Write custom cover letters
- `answer_application_question()` - Respond to app questions
- `full_application_package()` - Generate all materials at once
- `save_results()` - Save outputs to file

**When to modify**:
- To change the system prompt
- To add new output types
- To customize API parameters
- To change CV parsing logic

---

#### `cli.py` (Command-Line Interface)
**Purpose**: User-friendly interface for the assistant

**Features**:
- Interactive menu system
- Command-line argument support
- Batch processing capability
- Multiple input/output modes

**Usage modes**:
1. Interactive: `python cli.py`
2. Direct command: `python cli.py --job-file job.txt --action evaluate`
3. Custom CV path: `python cli.py /path/to/cv.pdf`

**When to modify**:
- To add new menu options
- To change UI flow
- To add new command-line flags

---

#### `requirements.txt` (Dependencies)
**Purpose**: Python package dependencies

**Packages**:
- `openai>=1.12.0` - OpenAI API client
- `python-dotenv>=1.0.0` - Environment variables
- `PyPDF2>=3.0.0` - PDF text extraction

**Installation**:
```bash
pip install -r requirements.txt
```

---

#### `.env` (Configuration)
**Purpose**: Store API keys and sensitive configuration

**Required variables**:
```
OPENAI_API_KEY=sk-your-key-here
```

**Security**: 
- Never commit to version control
- Keep this file private
- Use `.env.example` as template

---

### Documentation Files

#### `README.md` (Main Documentation)
**Contains**:
- Complete feature overview
- Installation instructions
- Usage examples for all methods
- API reference
- Troubleshooting guide
- Cost estimates
- Tips and best practices

**Audience**: Anyone using the assistant

---

#### `QUICKSTART.md` (Quick Setup)
**Contains**:
- 5-minute setup guide
- Essential commands
- Common first tasks
- Basic troubleshooting

**Audience**: First-time users who want to get started quickly

---

#### `PROJECT_STRUCTURE.md` (This File)
**Contains**:
- File organization
- Purpose of each file
- When to modify what
- Development guide

**Audience**: Developers or advanced users customizing the tool

---

### Example & Testing Files

#### `examples.py` (Usage Examples)
**Contains**:
- 5 working examples showing different use cases
- Demonstration of all main features
- Code you can copy and adapt

**Examples**:
1. Quick job fit evaluation
2. CV summary generation
3. Cover letter writing
4. Complete application package
5. Answering application questions

**Usage**:
```bash
python examples.py
```

---

#### `test_setup.py` (Setup Verification)
**Contains**:
- Environment validation tests
- Dependency checks
- API connection test
- PDF extraction test
- Optional functional test

**Tests performed**:
1. Python version check
2. Dependencies installed
3. .env file exists
4. API key validity
5. CV file exists
6. API connection works
7. PDF readable

**Usage**:
```bash
python test_setup.py
```

**When to use**:
- Initial setup verification
- Troubleshooting issues
- After updating dependencies

---

#### `.env.example` (Environment Template)
**Purpose**: Template showing required environment variables

**Usage**:
```bash
cp .env.example .env
# Then edit .env with your actual API key
```

---

### User Files (You Need to Add)

#### `reza_cv.pdf` (Your CV)
**Purpose**: Your curriculum vitae in PDF format

**Requirements**:
- Must be a readable PDF (not scanned image)
- Should contain your complete CV text
- Will be extracted and included in all queries

**Location**: 
- Default: Same directory as scripts
- Custom: Specify path when initializing assistant

**How it's used**:
- Extracted to text on initialization
- Included in every API call for context
- Used to ground all recommendations in actual experience

---

#### `.env` (Your Configuration)
**Purpose**: Your actual API key and settings

**Create from**:
```bash
cp .env.example .env
```

**Then add your key**:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## Workflow Diagrams

### Typical Usage Flow

```
┌─────────────────────┐
│  User Input         │
│  (Job Description)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  CLI or Script      │
│  Receives Input     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Assistant Class    │
│  - Loads CV         │
│  - Builds prompt    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  OpenAI API         │
│  - GPT-4o           │
│  - System prompt    │
│  - CV context       │
│  - Job description  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Response           │
│  - Evaluation       │
│  - CV summary       │
│  - Cover letter     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Save to File       │
│  or Display         │
└─────────────────────┘
```

### Data Flow

```
┌─────────────┐
│   CV PDF    │
└──────┬──────┘
       │ PyPDF2 extraction
       ▼
┌─────────────┐      ┌──────────────┐
│  CV Text    │──────│ System Prompt│
└──────┬──────┘      └──────┬───────┘
       │                    │
       │     Combined       │
       └────────┬───────────┘
                │
                ▼
         ┌────────────┐      ┌──────────────┐
         │   Prompt   │──────│ Job Description│
         │  Context   │      └──────────────┘
         └─────┬──────┘
               │
               ▼
         ┌────────────┐
         │ OpenAI API │
         └─────┬──────┘
               │
               ▼
         ┌────────────┐
         │   Output   │
         └────────────┘
```

## Customization Guide

### Adding New Output Types

To add a new type of output (e.g., LinkedIn message):

1. **Add method to `job_application_assistant.py`**:
```python
def generate_linkedin_message(self, job_description: str, model: str = "gpt-4o") -> dict:
    cv_context = self._create_cv_context()
    
    user_prompt = f"""{cv_context}
    
    ## JOB DESCRIPTION
    {job_description}
    
    Write a professional LinkedIn message to the hiring manager...
    """
    
    response = self.client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    
    return {
        "message": response.choices[0].message.content,
        "model": model,
        "tokens_used": response.usage.total_tokens
    }
```

2. **Add to CLI menu in `cli.py`**:
```python
# In interactive_mode function, add menu option:
print("6. Generate LinkedIn message")

# Add handling:
elif choice == '6':
    result = assistant.generate_linkedin_message(job_description)
    # ... display and save logic
```

3. **Add example in `examples.py`**:
```python
def example_linkedin_message():
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    result = assistant.generate_linkedin_message(job_description)
    print(result['message'])
```

### Modifying the System Prompt

The system prompt is in `job_application_assistant.py` in the `_load_system_prompt()` method.

**To modify**:
1. Edit the string in that method
2. Test with a few examples
3. Iterate based on output quality

**Key sections to customize**:
- Career goals and preferences
- Technical skill weights
- Writing style requirements
- Evaluation criteria

### Changing API Models

**In code**:
```python
# Default model
assistant = JobApplicationAssistant("reza_cv.pdf")
result = assistant.evaluate_job_fit(job, model="gpt-4-turbo")

# Or set default in the class
```

**In CLI**:
```bash
python cli.py --model gpt-4-turbo
```

**Available models**:
- `gpt-4o` (recommended, best quality)
- `gpt-4-turbo` (good quality, bit cheaper)
- `gpt-4` (older, more expensive)
- `gpt-3.5-turbo` (cheapest, lower quality)

### Adding Output Formats

Currently supports: `.txt` and `.json`

To add markdown format:

```python
# In save_results method of job_application_assistant.py

elif output_file.suffix == '.md':
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Application Materials\n\n")
        for key, value in results.items():
            if value and key not in ['model', 'tokens_used']:
                f.write(f"## {key.title()}\n\n{value}\n\n")
```

## Development Tips

### Testing Changes

Always test with:
```bash
python test_setup.py  # Verify setup
python examples.py    # Test functionality
```

### API Cost Control

Monitor costs with:
```python
result = assistant.evaluate_job_fit(job)
print(f"Tokens used: {result['tokens_used']}")
# Estimate: ~$0.01 per 1000 tokens for gpt-4o
```

### Debugging

Enable verbose output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or add print statements in the assistant methods to see what's being sent to the API.

### Version Control

**Recommended `.gitignore`**:
```
.env
*.pdf
reza_cv.pdf
__pycache__/
*.pyc
output*.txt
application*.txt
```

## Support

- **Issues with setup**: Run `python test_setup.py`
- **Questions about usage**: Check `README.md`
- **Quick start**: See `QUICKSTART.md`
- **Code examples**: Run `python examples.py`

## Future Enhancements

Possible additions:
- [ ] LinkedIn message generation
- [ ] Email follow-up templates
- [ ] Interview preparation Q&A
- [ ] Resume reformatting
- [ ] Skill gap analysis
- [ ] Multiple CV support
- [ ] Batch processing of multiple jobs
- [ ] Web interface
- [ ] Results database/tracking

---

**Last updated**: 2026-02-04
