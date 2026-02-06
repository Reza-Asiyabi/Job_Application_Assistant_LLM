# Job Application Assistant for Reza

A highly specialized AI assistant with **Command-Line** and **Graphical User Interfaces** to help evaluate job fit and generate high-quality, tailored application materials for ML/AI roles.

## 🎯 What's Included

### Core Application
- **Python API** - Full programmatic access
- **Command-Line Interface** - Interactive terminal interface
- **Graphical User Interface** - Modern, user-friendly GUI (NEW!)
- All powered by OpenAI's GPT models with Reza's custom profile

### Three Ways to Use

1. **GUI (Easiest)** ⭐
   ```bash
   python launch.py
   # Or: python gui_modern.py
   ```

2. **Interactive CLI**
   ```bash
   python cli.py
   ```

3. **Python Scripts**
   ```python
   from job_application_assistant import JobApplicationAssistant
   assistant = JobApplicationAssistant("reza_cv.pdf")
   ```

## 🚀 Quick Start

### Option 1: GUI (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your-key-here

# 3. Add your CV as *.pdf

# 4. Launch!
python launch.py

# Or on Windows: double-click launch.bat
# Or on Mac/Linux: ./launch.sh
```

That's it! The GUI will guide you through the rest.

### Option 2: Command Line

```bash
# Same setup (steps 1-3 above)

# Launch interactive CLI
python cli.py

# Or run directly
python cli.py --job-file job.txt --action full-package
```

## 📦 Complete File List

### Main Applications
- `gui_modern.py` - Modern GUI with ttkbootstrap (best experience)
- `gui.py` - Standard GUI with tkinter (fallback)
- `cli.py` - Interactive command-line interface
- `job_application_assistant.py` - Core assistant class
- `launch.py` - Smart launcher (auto-detects best GUI)
- `launch.bat` - Windows launcher (double-click)
- `launch.sh` - Mac/Linux launcher (executable)

### Documentation
- `README.md` - Main documentation (this file)
- `QUICKSTART.md` - 5-minute setup guide
- `GUI_GUIDE.md` - Complete GUI user guide
- `PROJECT_STRUCTURE.md` - File structure and customization

### Examples & Testing
- `examples.py` - Usage examples
- `test_setup.py` - Setup verification

### Configuration
- `requirements.txt` - Python dependencies
- `.env` - Your API key
- `reza_cv.pdf` - Reza's CV

## ✨ Features

### Job Fit Evaluation
- Strategic analysis with honest gap assessment
- Identifies hidden advantages from Reza's unique background
- Recommends whether to apply

### CV Summary Generation
- Tailored 3-4 sentence summaries
- Highlights relevant strengths for each role
- Natural, professional language

### Cover Letter Writing
- Human-sounding, no AI jargon
- Specific examples from Reza's CV
- Strategically positioned for each role

### Complete Package
- All materials at once (30-60 seconds)
- Consistent narrative across all documents
- Ready to submit (Not really!)

## 🖥️ GUI Features

### Modern Interface
- Clean, professional design
- Intuitive navigation with tabs
- Real-time progress indicators
- Token usage and cost tracking

### Five Main Tabs

1. **⚙️ Setup** - Configure CV, API, and initialize
2. **📊 Evaluate** - Analyze job fit before applying
3. **✍️ Generate** - Create CV summaries and cover letters
4. **📦 Package** - Generate everything at once
5. **📜 History** - View past applications (coming soon!!)

### User-Friendly Features
- Paste job descriptions directly
- Browse for CV file
- Save results with one click
- Copy to clipboard easily
- Progress bars for long operations
- Status updates in real-time

## 💻 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet**: Required for OpenAI API calls
- **OpenAI API Key**: From https://platform.openai.com

## 📖 Usage Guide

### Using the GUI

**First Time Setup:**
1. Launch: `python launch.py`
2. Go to Setup tab
3. Browse for your CV
4. Select model (recommend gpt-4o)
5. Click "Initialize Assistant"

**Evaluate a Job:**
1. Go to Evaluate tab
2. Paste job description
3. Click "Evaluate Fit"
4. Review detailed analysis
5. Save if needed

**Generate Materials:**
1. Go to Generate tab
2. Paste job description
3. Add company name and role (optional)
4. Click "CV Summary" or "Cover Letter"
5. Review and save

**Complete Package:**
1. Go to Package tab
2. Paste job description
3. Add company and role info
4. Click "Generate Complete Package"
5. Wait 30-60 seconds
6. Save or copy results

### Using the CLI

**Interactive Mode:**
```bash
python cli.py
# Follow menu prompts
```

**Command Line:**
```bash
# Evaluate
python cli.py --job-file job.txt --action evaluate

# Generate CV summary
python cli.py --job-file job.txt --action cv-summary

# Complete package
python cli.py --job-file job.txt --action full-package \
  --company "DeepMind" --role "Research Engineer"
```

### Using Python API

```python
from job_application_assistant import JobApplicationAssistant

# Initialize
assistant = JobApplicationAssistant("reza_cv.pdf")

# Evaluate fit
evaluation = assistant.evaluate_job_fit(job_description)
print(evaluation['evaluation'])

# Generate materials
summary = assistant.generate_cv_summary(job_description)
cover_letter = assistant.generate_cover_letter(
    job_description, 
    company_name="Company", 
    role_title="Role"
)

# Complete package
package = assistant.full_application_package(
    job_description,
    company_name="Company",
    role_title="Role"
)

# Save
assistant.save_results(package, "application.txt")
```

## 💰 Cost Estimates

Using **gpt-4o** (recommended):
- Job fit evaluation: **$0.15-0.30** per job
- CV summary: **$0.10-0.20** per job
- Cover letter: **$0.15-0.30** per job
- Complete package: **$0.40-0.80** per job

Using **gpt-3.5-turbo** (budget):
- About **90% cheaper** but noticeably lower quality
- Good for testing, use gpt-4o for final versions

## 🎨 GUI Screenshots (Conceptual)

### Setup Tab
- CV path configuration
- Model selection dropdown
- Initialize button
- Status output area

### Evaluate Tab
- Job description input
- Evaluate button
- Results display
- Save/copy buttons

### Generate Tab
- Split view: input on left, output on right
- Job description input
- Company/role fields
- Generate buttons (CV summary, cover letter)
- Save/copy/clear buttons

### Package Tab
- Job description input
- Company and role fields
- Large generate button
- Progress bar
- Complete package output
- Export options

## 🔧 Configuration

### Environment Variables (.env)

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Model Options

- `gpt-5.2` - Best quality, $$$$
- `gpt-4o` - Better quality, recommended, $$$
- `gpt-4-turbo` - Good balance, $$
- `gpt-4` - Older, more expensive, $$$
- `gpt-3.5-turbo` - Budget option, $

Set in GUI (Setup tab) or when calling methods.

## 🚨 Troubleshooting

### GUI won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Try standard GUI
python gui.py

# Or use CLI instead
python cli.py
```

### "API Key Not Found"

1. Create `.env` file in project directory
2. Add: `OPENAI_API_KEY=sk-your-key`
3. No quotes needed
4. Restart application

### "CV File Not Found"

1. Place CV as `*.pdf` in project directory
2. Or use Browse button in GUI
3. Or specify path: `python cli.py /path/to/cv.pdf`

### Empty Output

1. Check internet connection
2. Verify API key has credits
3. Try again (occasional API issues)
4. Check model selection

### More Help

Run diagnostics:
```bash
python test_setup.py
```

## 📚 Documentation

- **README.md** (this file) - Overview and quick start
- **QUICKSTART.md** - Step-by-step setup guide
- **GUI_GUIDE.md** - Complete GUI documentation
- **PROJECT_STRUCTURE.md** - Technical details and customization

## 🎯 Best Practices

### For Best Results

1. **Always evaluate first** - Don't waste time on bad fits
2. **Include full job descriptions** - More context = better output
3. **Provide company/role info** - Makes materials more specific
4. **Review and edit** - AI is smart but not perfect
5. **Save everything** - Keep organized by company

### Recommended Workflow

```
1. Get job posting
2. GUI: Evaluate tab → Check fit
3. If good fit → Package tab → Generate all materials
4. Review and customize
5. Save with clear filename
6. Apply!
```

### File Organization

```
job_applications/
├── company_a/
│   ├── evaluation.txt
│   ├── package.txt
│   └── notes.txt
├── company_b/
│   └── package.txt
└── ...
```

## 🔄 Updates

```bash
# Get latest version
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Test
python test_setup.py
```

## 🤝 Which Interface Should I Use?

### Use GUI if you:
- ✅ Want visual interface
- ✅ Process jobs one at a time
- ✅ Like to review as you go
- ✅ Prefer clicking over typing
- ✅ Are new to the system

### Use CLI if you:
- ✅ Prefer keyboard/terminal
- ✅ Want to script/automate
- ✅ Work on remote systems
- ✅ Process many jobs in batches
- ✅ Integrate with other tools

### Use Python API if you:
- ✅ Want full control
- ✅ Build custom workflows
- ✅ Integrate into larger systems
- ✅ Need programmatic access
- ✅ Automate complex tasks

**You can use all three!** They all work with the same CV and configuration.

## 🎓 Learning Path

### Day 1: Get Started
1. Install and configure (5 min)
2. Run test setup (2 min)
3. Launch GUI and explore (10 min)
4. Try evaluation on a real job (5 min)

### Day 2: Create Materials
1. Generate CV summary (3 min)
2. Generate cover letter (3 min)
3. Try complete package (5 min)
4. Review and understand output (10 min)

### Week 1: Master the Tool
1. Process 5-10 jobs
2. Experiment with different models
3. Learn what makes good vs bad output
4. Develop your workflow

### Ongoing: Optimize
1. Track success rates
2. Refine your CV based on feedback
3. Customize prompts if needed
4. Share insights

## 🌟 Pro Tips

1. **Test with cheaper model first**
   - Use gpt-3.5-turbo to test
   - Switch to gpt-4o or gpt-5.2 for final version
   - Saves money while learning

2. **Save evaluations**
   - Reuse for similar roles
   - Compare different approaches
   - Learn what the AI focuses on

3. **Customize after generation**
   - Add personal touches
   - Include specific examples
   - Adjust tone if needed

4. **Use Package for serious applications**
   - Ensures consistency
   - Saves time
   - Gets everything at once

5. **Keep history**
   - Save all materials
   - Track what worked
   - Reference for future applications

## 📊 Feature Comparison

| Feature | GUI | CLI | Python API |
|---------|-----|-----|------------|
| Evaluate fit | ✅ | ✅ | ✅ |
| CV summary | ✅ | ✅ | ✅ |
| Cover letter | ✅ | ✅ | ✅ |
| Complete package | ✅ | ✅ | ✅ |
| Visual interface | ✅ | ❌ | ❌ |
| Batch processing | ❌ | ✅ | ✅ |
| Automation | ❌ | ✅ | ✅ |
| Progress bars | ✅ | ❌ | ❌ |
| Easy for beginners | ✅ | ⚠️ | ❌ |
| Scriptable | ❌ | ✅ | ✅ |
| Real-time status | ✅ | ✅ | ❌ |

## 🔐 Privacy & Security

- ✅ All data stays local except API calls
- ✅ OpenAI doesn't train on your data (per their policy)
- ✅ CV and materials stay on your computer
- ⚠️ API calls include CV content and job descriptions
- 🔒 Keep `.env` file secure
- 🔒 Never commit `.env` to version control

## 📝 License

Personal use. Modify as needed.

## 🙏 Credits

Built by Reza for his job search journey. Powered by OpenAI's GPT models.

## 📞 Support

- **Setup issues**: Run `python test_setup.py`
- **GUI help**: See `GUI_GUIDE.md`
- **CLI help**: Run `python cli.py --help`
- **Examples**: Run `python examples.py`

---

**Version**: 1.0 with GUI

**Last Updated**: 2026-02-04

**Recommended Start**: `python launch.py` 🚀

Enjoy your job search! 🎯
