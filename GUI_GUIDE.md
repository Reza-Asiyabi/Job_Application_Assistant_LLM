# GUI User Guide

Complete guide for the Job Application Assistant graphical user interface.

## Overview

The Job Application Assistant comes with two GUI options:

1. **`gui.py`** - Standard GUI using tkinter (works everywhere)
2. **`gui_modern.py`** - Modern, beautiful GUI using ttkbootstrap (recommended)

Both provide the same functionality with a user-friendly interface.

## Installation

### Standard GUI (gui.py)

No additional dependencies needed beyond the base requirements:

```bash
pip install -r requirements.txt
python gui.py
```

### Modern GUI (gui_modern.py) - Recommended

Install with ttkbootstrap for enhanced visuals:

```bash
pip install -r requirements.txt
python gui_modern.py
```

If ttkbootstrap isn't available, it will automatically fall back to standard theme.

## Quick Start

### 1. Launch the Application

```bash
# Standard version
python gui.py

# Modern version (recommended)
python gui_modern.py
```

### 2. Setup Tab (First Time)

**On first launch:**

1. **CV Path**: The application looks for `reza_cv.pdf` by default
   - If your CV is elsewhere, click "Browse" to select it
   
2. **Model Selection**: Choose your OpenAI model
   - `gpt-4o` - Best quality, recommended
   - `gpt-4-turbo` - Good balance
   - `gpt-3.5-turbo` - Budget option
   
3. **API Status**: Check your API key is detected
   - Green ✅ = Ready
   - Red ❌ = Need to configure .env file
   
4. Click "🚀 Initialize Assistant"

5. Once initialized, you'll see:
   ```
   ✅ Assistant initialized
   ✅ CV loaded: reza_cv.pdf
   ✅ Model: gpt-4o
   🎉 Ready to process applications!
   ```

### 3. Using the Application

After initialization, all other tabs become functional.

## Feature Guide

### 📊 Evaluate Tab

**Purpose**: Analyze how well a job matches your profile

**How to use:**

1. Paste the job description in the input box
2. Click "🔍 Evaluate Fit"
3. Wait 10-30 seconds
4. Review the detailed evaluation
5. Save or copy the results

**What you get:**
- Fit assessment (Strong/Partial/Weak)
- Match analysis
- Gaps and risks
- Strategic positioning advice
- Application recommendation

**Tips:**
- Include the full job posting for best results
- The evaluation is honest - it will tell you if it's a weak fit
- Use this before spending time on other materials

### ✍️ Generate Tab

**Purpose**: Create individual application materials

**How to use:**

1. **Left side - Input:**
   - Paste job description
   - Optionally add company name and role title
   
2. **Choose what to generate:**
   - "📝 CV Summary" - 3-4 sentence professional summary
   - "✉️ Cover Letter" - Full cover letter
   
3. **Right side - Output:**
   - Review generated content
   - Edit if needed
   - Save, copy, or clear

**Split-panel design:**
- Input on left stays visible
- Generate multiple versions easily
- Compare different approaches

### 📦 Package Tab

**Purpose**: Generate everything at once

**How to use:**

1. Paste job description
2. Add company name and role (optional but recommended)
3. Click "🚀 Generate Complete Package"
4. Wait 30-60 seconds (progress bar shows activity)
5. Get all three deliverables:
   - Job fit evaluation
   - CV summary
   - Cover letter

**When to use:**
- When you're serious about an application
- To get a complete picture quickly
- For consistent materials

**Output includes:**
- Header with company, role, timestamp
- Complete evaluation
- Tailored CV summary
- Custom cover letter
- All formatted and ready to use

### 📜 History Tab

**Purpose**: View past applications (coming soon)

**Planned features:**
- Log of all generated materials
- Quick access to previous applications
- Search and filter
- Export history

## Tips & Best Practices

### For Best Results

1. **Full Job Descriptions**
   - Copy the entire posting, not just requirements
   - Include responsibilities, nice-to-haves, company info
   - More context = better output

2. **Company and Role Info**
   - Always provide when available
   - Makes cover letters more specific
   - Helps with positioning

3. **Review and Edit**
   - The AI is smart but not perfect
   - Always review outputs
   - Make personal touches
   - Verify all claims

4. **Iterative Approach**
   - Start with evaluation
   - If fit is good, generate materials
   - Generate, review, adjust as needed

### Workflow Recommendations

**Standard Workflow:**
```
1. Evaluate Tab: Check fit
2. If good fit → Generate Tab: CV summary first
3. Review and refine
4. Generate Tab: Cover letter
5. Save all materials
```

**Quick Workflow:**
```
1. Package Tab: Generate everything
2. Review complete package
3. Save or export
4. Make final edits outside GUI
```

**Batch Processing:**
```
1. Collect multiple job descriptions
2. Evaluate each in Evaluate tab
3. For good fits, go to Package tab
4. Generate and save each application
5. Organize saved files by company
```

## Interface Features

### Modern GUI Highlights

**Enhanced Design:**
- Clean, professional appearance
- Color-coded sections
- Smooth animations
- Better readability

**Status Indicators:**
- Real-time progress updates
- Token usage tracking
- Cost estimates
- Connection status

**User Experience:**
- Intuitive navigation
- Keyboard shortcuts work naturally
- Copy/paste friendly
- Responsive layout

### Common Controls

**Text Areas:**
- Scroll for long content
- Select all: Ctrl+A (Cmd+A on Mac)
- Copy: Ctrl+C (Cmd+C on Mac)
- Paste: Ctrl+V (Cmd+V on Mac)

**Buttons:**
- Hover for visual feedback
- Click to execute
- Some show progress indicators

**Status Bar (Bottom):**
- Left: Current operation status
- Right: Token usage and cost estimate

## Troubleshooting

### "Please initialize first"

**Problem**: Trying to use features without initializing

**Solution**:
1. Go to Setup tab
2. Check CV path is correct
3. Verify API key status
4. Click "Initialize Assistant"

### Empty or No Output

**Problem**: Generated content is blank

**Solution**:
1. Check internet connection
2. Verify API key has credits
3. Try again (occasional API issues)
4. Check console for error messages

### Slow Generation

**Problem**: Taking longer than expected

**Solution**:
- Normal wait times:
  - Evaluation: 10-30 seconds
  - CV Summary: 10-20 seconds
  - Cover Letter: 15-30 seconds
  - Complete Package: 30-60 seconds
- Longer wait usually means:
  - Long job description
  - Network latency
  - API load

### Application Won't Start

**Problem**: GUI window doesn't appear

**Solution**:
1. Check Python version: `python --version` (need 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Try standard GUI if modern fails: `python gui.py`
4. Check console for error messages

### Can't Find CV

**Problem**: CV file not found error

**Solution**:
1. Place CV as `reza_cv.pdf` in same directory as scripts
2. Or use Browse button to select CV location
3. Ensure file is actual PDF (not renamed file)

## Keyboard Shortcuts

**Text Editing:**
- `Ctrl+A` / `Cmd+A` - Select all
- `Ctrl+C` / `Cmd+C` - Copy
- `Ctrl+V` / `Cmd+V` - Paste
- `Ctrl+X` / `Cmd+X` - Cut
- `Ctrl+Z` / `Cmd+Z` - Undo

**Navigation:**
- `Tab` - Move between fields
- `Shift+Tab` - Move backward
- `Enter` - Activate focused button (sometimes)

## Cost Management

### Monitoring Costs

**Token Display:**
- Shows after each operation
- Format: "Tokens: X,XXX | Est. Cost: $X.XX"

**Typical Costs (GPT-4o):**
- Evaluation: $0.15-0.30
- CV Summary: $0.10-0.20
- Cover Letter: $0.15-0.30
- Complete Package: $0.40-0.80

### Saving Money

1. **Use gpt-3.5-turbo for testing**
   - 90% cheaper
   - Good for experimenting
   - Switch to gpt-4o for final versions

2. **Generate only what you need**
   - Don't generate unnecessarily
   - Use evaluation first to filter

3. **Reuse evaluations**
   - Save evaluation results
   - No need to re-evaluate same job

## File Management

### Saving Results

**Naming Convention:**
```
application_YYYYMMDD_HHMM.txt
```

**Recommended Structure:**
```
job_applications/
├── company_name/
│   ├── evaluation_20260204.txt
│   ├── cv_summary_20260204.txt
│   ├── cover_letter_20260204.txt
│   └── complete_package_20260204.txt
```

### Backup Strategy

1. Save all generated materials
2. Keep organized by company/role
3. Add notes about customizations
4. Reference when applying to similar roles

## Advanced Usage

### Customizing Output

**After Generation:**
1. Copy text to your editor
2. Make personal adjustments
3. Add specific details
4. Format as needed

**Iterating:**
1. Generate initial version
2. Review
3. Adjust job description input
4. Regenerate if needed

### Batch Operations

**Multiple Applications:**
1. Prepare list of job descriptions
2. Go through Evaluate tab first
3. Filter for good fits
4. Generate packages for each
5. Save with clear filenames

### Integration with Other Tools

**Export to:**
- Word: Save as .txt, open in Word
- Google Docs: Copy and paste
- Email: Copy directly
- LinkedIn: Adapt cover letter to message

## GUI Architecture

### Two-Version Strategy

**Why two versions?**

1. **gui.py (Standard)**
   - Works everywhere
   - No extra dependencies
   - Fallback option
   - Reliable

2. **gui_modern.py (Modern)**
   - Better aesthetics
   - Enhanced UX
   - Modern themes
   - Recommended when possible

### Threading Model

**Non-Blocking Operations:**
- API calls run in background threads
- GUI remains responsive
- Progress indicators show activity
- Can't start multiple operations simultaneously (by design)

### State Management

**Initialization:**
- Assistant object persists
- CV loaded once
- Settings maintained across tabs

**Per-Operation:**
- Independent API calls
- Results don't interfere
- Clean state for each generation

## Comparison: CLI vs GUI

### When to Use CLI

- Batch processing many jobs
- Automation/scripting
- Quick one-off operations
- Remote/SSH access
- Integration with other scripts

### When to Use GUI

- Interactive exploration
- Reviewing multiple options
- Visual comparison
- Learning the system
- Occasional use
- Prefer visual feedback

### Can Use Both

- CLI for automation
- GUI for review and refinement
- Both read same .env and CV
- Results are identical

## Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Test
python test_setup.py
```

### Checking Version

Look at the header title or:
```bash
# Check file modification date
ls -l gui*.py
```

## Getting Help

### In-Application

1. Setup tab shows detailed status
2. Error messages in status bar
3. Status area shows operation progress

### External Resources

- README.md - Complete documentation
- QUICKSTART.md - Setup guide
- test_setup.py - Diagnostic tool
- examples.py - Code examples

### Common Issues

See **Troubleshooting** section above for solutions to:
- Initialization problems
- Empty outputs
- Slow performance
- File not found errors

## Future Features

**Planned Enhancements:**

1. **History Tab**
   - Full application history
   - Search and filter
   - Quick reload

2. **Templates**
   - Save customized prompts
   - Company-specific templates
   - Reusable configurations

3. **Batch Mode**
   - Process multiple jobs at once
   - Queue management
   - Parallel processing

4. **Export Options**
   - Direct Word export
   - PDF generation
   - Email formatting

5. **Analytics**
   - Success rate tracking
   - Cost analysis
   - Quality metrics

---

**Last Updated**: 2026-02-04

**Version**: 1.0

**Recommended**: Use `gui_modern.py` for the best experience!
