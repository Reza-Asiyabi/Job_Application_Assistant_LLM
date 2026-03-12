#!/usr/bin/env python3
"""
Interactive CLI for Job Application Assistant
Provides a user-friendly command-line interface for the assistant
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from job_application_assistant import JobApplicationAssistant


def print_banner():
    print("\n" + "="*70)
    print("  JOB APPLICATION ASSISTANT")
    print("  AI for evaluating fit and generating application materials")
    print("="*70 + "\n")


def get_multiline_input(prompt: str) -> str:
    """Get multi-line input; type END on a new line to finish."""
    print(prompt)
    print("(Enter your text. Type 'END' on a new line when finished)\n")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    return '\n'.join(lines)


def stream_cb(chunk: str):
    """Print each streamed token immediately."""
    print(chunk, end="", flush=True)


def print_section(title: str):
    print("\n" + "="*70)
    print(title)
    print("="*70)


def ask_save(assistant, result, default_name: str):
    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input(f"Enter filename (default: {default_name}): ").strip() or default_name
        assistant.save_results(result, filename)


def interactive_mode(assistant: JobApplicationAssistant, model: str):
    while True:
        print("\n" + "-"*70)
        print("MENU — What would you like to do?")
        print("-"*70)
        print("1. Evaluate job fit")
        print("2. Generate CV summary")
        print("3. Generate cover letter")
        print("4. Answer application question")
        print("5. Generate complete application package")
        print("6. Generate interview prep")
        print("7. Generate LinkedIn / recruiter message")
        print("8. Exit")
        print("-"*70)

        choice = input("\nEnter your choice (1-8): ").strip()

        if choice == '8':
            print("\nGoodbye.")
            break

        if choice not in ('1', '2', '3', '4', '5', '6', '7'):
            print("\nInvalid choice. Please select 1-8.")
            continue

        job_description = get_multiline_input("\nPaste the job description:")
        if not job_description.strip():
            print("\nJob description cannot be empty.")
            continue

        if choice == '1':
            print_section("JOB FIT EVALUATION")
            result = assistant.evaluate_job_fit(
                job_description, model=model,
                stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "evaluation.txt")

        elif choice == '2':
            print_section("CV SUMMARY")
            result = assistant.generate_cv_summary(
                job_description, model=model,
                stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "cv_summary.txt")

        elif choice == '3':
            company = input("\nCompany name (Enter to skip): ").strip() or None
            role    = input("Role title (Enter to skip): ").strip() or None
            print_section("COVER LETTER")
            result = assistant.generate_cover_letter(
                job_description, company_name=company, role_title=role,
                model=model, stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "cover_letter.txt")

        elif choice == '4':
            question = get_multiline_input("\nEnter the application question:")
            if not question.strip():
                print("\nQuestion cannot be empty.")
                continue
            print_section("ANSWER TO APPLICATION QUESTION")
            result = assistant.answer_application_question(
                job_description, question, model=model,
                stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "question_answer.txt")

        elif choice == '5':
            company = input("\nCompany name (Enter to skip): ").strip() or None
            role    = input("Role title (Enter to skip): ").strip() or None
            print("\nGenerating complete package (this makes multiple API calls)...")
            result = assistant.full_application_package(
                job_description, company, role, model=model)
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print_section("COMPLETE APPLICATION PACKAGE")
                for key, value in result.items():
                    if key not in ('model', 'tokens_used', 'total_tokens_used') and value:
                        print(f"\n{key.upper()}:\n{value}\n")
                print(f"Total tokens used: {result.get('total_tokens_used', '—')}")
                ask_save(assistant, result, "complete_application.txt")

        elif choice == '6':
            print_section("INTERVIEW PREP")
            result = assistant.generate_interview_prep(
                job_description, model=model,
                stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "interview_prep.txt")

        elif choice == '7':
            recruiter = input("\nRecruiter name (Enter to skip): ").strip() or None
            print_section("LINKEDIN / RECRUITER MESSAGE")
            result = assistant.generate_linkedin_message(
                job_description, recruiter_name=recruiter,
                model=model, stream_callback=stream_cb)
            print()
            if 'error' in result:
                print(f"\nError: {result['error']}")
            else:
                print(f"\nTokens used: {result['tokens_used']}")
                ask_save(assistant, result, "linkedin_message.txt")


def run_batch(assistant, batch_dir: str, output_dir: str, action: str, model: str):
    """Evaluate (or run another action on) all .txt files in batch_dir."""
    import glob as _glob
    from collections import Counter

    batch_path  = Path(batch_dir)
    out_path    = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files = sorted(batch_path.glob("*.txt"))
    if not files:
        print(f"No .txt files found in: {batch_path}")
        return

    print(f"\nBatch mode — {len(files)} files  |  action: {action}  |  model: {model}")
    print(f"Output directory: {out_path}\n")
    print("─" * 70)

    results_summary = []

    for i, jd_file in enumerate(files, 1):
        stem = jd_file.stem
        print(f"\n[{i}/{len(files)}]  {jd_file.name}")
        try:
            jd = jd_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ERROR reading file: {e}")
            continue

        try:
            if action == "evaluate":
                r = assistant.evaluate_job_fit(jd, model=model)
                content = r.get("evaluation", "")
                toks    = r.get("tokens_used", 0)
            elif action == "cv-summary":
                r = assistant.generate_cv_summary(jd, model=model)
                content = r.get("summary", "")
                toks    = r.get("tokens_used", 0)
            elif action == "cover-letter":
                r = assistant.generate_cover_letter(jd, model=model)
                content = r.get("cover_letter", "")
                toks    = r.get("tokens_used", 0)
            elif action == "full-package":
                r = assistant.full_application_package(jd, model=model)
                content = "\n\n".join(f"{k.upper()}\n{'─'*40}\n{v}"
                                      for k, v in r.items()
                                      if k not in ("model", "tokens_used", "total_tokens_used") and v)
                toks    = r.get("total_tokens_used", 0)
            else:
                print(f"  Batch action '{action}' not supported. Use: evaluate, cv-summary, cover-letter, full-package")
                return
        except Exception as e:
            print(f"  ERROR: {e}")
            results_summary.append({"file": jd_file.name, "status": "ERROR", "tokens": 0})
            continue

        out_file = out_path / f"{stem}_{action}.txt"
        out_file.write_text(content, encoding="utf-8")
        print(f"  ✓  {toks:,} tokens  →  {out_file.name}")
        results_summary.append({"file": jd_file.name, "status": "OK", "tokens": toks})

    # Summary report
    total_toks = sum(r["tokens"] for r in results_summary)
    n_ok  = sum(1 for r in results_summary if r["status"] == "OK")
    n_err = sum(1 for r in results_summary if r["status"] == "ERROR")
    print("\n" + "═" * 70)
    print(f"  Batch complete: {n_ok} succeeded, {n_err} failed, {total_toks:,} tokens used")
    print(f"  Results saved to: {out_path}")

    # Write summary CSV
    import csv as _csv
    summary_file = out_path / "batch_summary.csv"
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=["file", "status", "tokens"])
        w.writeheader()
        w.writerows(results_summary)
    print(f"  Summary CSV: {summary_file.name}\n")


def main():
    load_dotenv()
    default_cv_path = os.getenv("CV_PATH", "cv.pdf")

    parser = argparse.ArgumentParser(
        description="Job Application Assistant — AI-powered job application support"
    )
    parser.add_argument(
        'cv_path', nargs='?', default=default_cv_path,
        help=f'Path to CV PDF file (default: {default_cv_path})')
    parser.add_argument(
        '--model', default='gpt-4o',
        help='OpenAI model to use (default: gpt-4o)')
    parser.add_argument(
        '--job-file',
        help='Path to file containing job description (enables non-interactive mode)')
    parser.add_argument(
        '--action',
        choices=['evaluate', 'cv-summary', 'cover-letter', 'full-package',
                 'interview-prep', 'linkedin', 'qa'],
        help='Action to perform (requires --job-file)')
    parser.add_argument('--company', help='Company name (for cover-letter, full-package)')
    parser.add_argument('--role',    help='Role title (for cover-letter, full-package)')
    parser.add_argument('--recruiter', help='Recruiter name (for linkedin)')
    parser.add_argument('--question',  help='Application question text (for qa)')
    parser.add_argument('--output',    help='Output file path')
    parser.add_argument('--batch-dir',  help='Directory of .txt job description files (batch mode)')
    parser.add_argument('--output-dir', help='Output directory for batch results (default: batch-dir/results)')

    args = parser.parse_args()

    print_banner()

    if not Path(args.cv_path).exists():
        print(f"Error: CV file not found: {args.cv_path}")
        sys.exit(1)

    try:
        assistant = JobApplicationAssistant(cv_path=args.cv_path)
    except Exception as e:
        print(f"Error initialising assistant: {e}")
        print("\nCheck: .env file exists with OPENAI_API_KEY, and CV PDF is readable.")
        sys.exit(1)

    # ── Batch mode ───────────────────────────────────────────────────────────
    if args.batch_dir:
        batch_action = args.action or "evaluate"
        output_dir   = args.output_dir or str(Path(args.batch_dir) / "results")
        run_batch(assistant, args.batch_dir, output_dir, batch_action, args.model)
        return

    # ── Non-interactive mode ──────────────────────────────────────────────────
    if args.job_file and args.action:
        try:
            job_description = Path(args.job_file).read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading job file: {e}")
            sys.exit(1)

        # Streaming goes to stdout live; result dict also contains the full text
        cb = stream_cb if not args.output else None

        if args.action == 'evaluate':
            if cb:
                print_section("JOB FIT EVALUATION")
            result = assistant.evaluate_job_fit(
                job_description, model=args.model, stream_callback=cb)

        elif args.action == 'cv-summary':
            if cb:
                print_section("CV SUMMARY")
            result = assistant.generate_cv_summary(
                job_description, model=args.model, stream_callback=cb)

        elif args.action == 'cover-letter':
            if cb:
                print_section("COVER LETTER")
            result = assistant.generate_cover_letter(
                job_description, company_name=args.company, role_title=args.role,
                model=args.model, stream_callback=cb)

        elif args.action == 'full-package':
            print("Generating complete package (multiple API calls)…")
            result = assistant.full_application_package(
                job_description, args.company, args.role, model=args.model)

        elif args.action == 'interview-prep':
            if cb:
                print_section("INTERVIEW PREP")
            result = assistant.generate_interview_prep(
                job_description, model=args.model, stream_callback=cb)

        elif args.action == 'linkedin':
            if cb:
                print_section("LINKEDIN / RECRUITER MESSAGE")
            result = assistant.generate_linkedin_message(
                job_description, recruiter_name=args.recruiter,
                model=args.model, stream_callback=cb)

        elif args.action == 'qa':
            if not args.question:
                print("Error: --question is required for the 'qa' action.")
                sys.exit(1)
            if cb:
                print_section("APPLICATION QUESTION ANSWER")
            result = assistant.answer_application_question(
                job_description, args.question,
                model=args.model, stream_callback=cb)

        if cb:
            print()  # newline after streamed output

        if 'error' in result:
            print(f"\nError: {result['error']}")
            sys.exit(1)

        if args.output:
            assistant.save_results(result, args.output)
        elif not cb:
            # Non-streaming path (--output was set, cb was None; already saved above)
            # or full-package which doesn't stream
            print_section("RESULTS")
            for key, value in result.items():
                if key not in ('model', 'tokens_used', 'total_tokens_used') and value:
                    print(f"\n{key.upper()}:\n{value}\n")

    else:
        interactive_mode(assistant, model=args.model)


if __name__ == "__main__":
    main()
