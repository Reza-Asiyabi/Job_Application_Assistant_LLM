#!/usr/bin/env python3
"""
Interactive CLI for Job Application Assistant
Provides a user-friendly command-line interface for the assistant
"""

import argparse
import sys
from pathlib import Path
from job_application_assistant import JobApplicationAssistant


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("  JOB APPLICATION ASSISTANT FOR REZA")
    print("  Specialized AI for evaluating fit and generating application materials")
    print("="*70 + "\n")


def get_multiline_input(prompt: str) -> str:
    """
    Get multi-line input from user.
    
    Args:
        prompt: Prompt to display
        
    Returns:
        Multi-line input string
    """
    print(prompt)
    print("(Enter your text. Type 'END' on a new line when finished)\n")
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    return '\n'.join(lines)


def interactive_mode(assistant: JobApplicationAssistant):
    """
    Run interactive mode with menu-driven interface.
    
    Args:
        assistant: Initialized JobApplicationAssistant instance
    """
    while True:
        print("\n" + "-"*70)
        print("MENU - What would you like to do?")
        print("-"*70)
        print("1. Evaluate job fit")
        print("2. Generate CV summary")
        print("3. Generate cover letter")
        print("4. Answer application question")
        print("5. Generate complete application package")
        print("6. Exit")
        print("-"*70)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '6':
            print("\n👋 Thank you for using Job Application Assistant!")
            break
        
        if choice not in ['1', '2', '3', '4', '5']:
            print("\n❌ Invalid choice. Please select 1-6.")
            continue
        
        # Get job description (needed for all operations)
        job_description = get_multiline_input("\n📋 Paste the job description:")
        
        if not job_description.strip():
            print("\n❌ Job description cannot be empty.")
            continue
        
        # Execute based on choice
        if choice == '1':
            # Evaluate job fit
            result = assistant.evaluate_job_fit(job_description)
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n" + "="*70)
                print("JOB FIT EVALUATION")
                print("="*70)
                print(f"\n{result['evaluation']}\n")
                print(f"Tokens used: {result['tokens_used']}")
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Enter filename (default: evaluation.txt): ").strip() or "evaluation.txt"
                    assistant.save_results(result, filename)
        
        elif choice == '2':
            # Generate CV summary
            result = assistant.generate_cv_summary(job_description)
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n" + "="*70)
                print("CV SUMMARY")
                print("="*70)
                print(f"\n{result['summary']}\n")
                print(f"Tokens used: {result['tokens_used']}")
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Enter filename (default: cv_summary.txt): ").strip() or "cv_summary.txt"
                    assistant.save_results(result, filename)
        
        elif choice == '3':
            # Generate cover letter
            company = input("\nCompany name (optional, press Enter to skip): ").strip() or None
            role = input("Role title (optional, press Enter to skip): ").strip() or None
            
            result = assistant.generate_cover_letter(job_description, company, role)
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n" + "="*70)
                print("COVER LETTER")
                print("="*70)
                print(f"\n{result['cover_letter']}\n")
                print(f"Tokens used: {result['tokens_used']}")
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Enter filename (default: cover_letter.txt): ").strip() or "cover_letter.txt"
                    assistant.save_results(result, filename)
        
        elif choice == '4':
            # Answer application question
            question = get_multiline_input("\n❓ Enter the application question:")
            
            if not question.strip():
                print("\n❌ Question cannot be empty.")
                continue
            
            result = assistant.answer_application_question(job_description, question)
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n" + "="*70)
                print("ANSWER TO APPLICATION QUESTION")
                print("="*70)
                print(f"\nQuestion: {result['question']}\n")
                print(f"Answer: {result['answer']}\n")
                print(f"Tokens used: {result['tokens_used']}")
                
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Enter filename (default: question_answer.txt): ").strip() or "question_answer.txt"
                    assistant.save_results(result, filename)
        
        elif choice == '5':
            # Generate complete package
            company = input("\nCompany name (optional, press Enter to skip): ").strip() or None
            role = input("Role title (optional, press Enter to skip): ").strip() or None
            
            result = assistant.full_application_package(job_description, company, role)
            
            if 'error' in result:
                print(f"\n❌ Error: {result['error']}")
            else:
                print("\n" + "="*70)
                print("COMPLETE APPLICATION PACKAGE GENERATED")
                print("="*70)
                print(f"\nTotal tokens used: {result['total_tokens_used']}")
                
                # Display summary
                print("\n📊 Package includes:")
                print("  ✓ Job fit evaluation")
                print("  ✓ Tailored CV summary")
                print("  ✓ Custom cover letter")
                
                save = input("\nSave complete package to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Enter filename (default: complete_application.txt): ").strip() or "complete_application.txt"
                    assistant.save_results(result, filename)


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Job Application Assistant for Reza - AI-powered job application support"
    )
    
    parser.add_argument(
        'cv_path',
        nargs='?',
        default='reza_cv.pdf',
        help='Path to CV PDF file (default: reza_cv.pdf)'
    )
    
    parser.add_argument(
        '--model',
        default='gpt-4o',
        help='OpenAI model to use (default: gpt-4o)'
    )
    
    parser.add_argument(
        '--job-file',
        help='Path to file containing job description (skip interactive mode)'
    )
    
    parser.add_argument(
        '--action',
        choices=['evaluate', 'cv-summary', 'cover-letter', 'full-package'],
        help='Action to perform (requires --job-file)'
    )
    
    parser.add_argument(
        '--company',
        help='Company name (for cover letter)'
    )
    
    parser.add_argument(
        '--role',
        help='Role title (for cover letter)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check if CV exists
    if not Path(args.cv_path).exists():
        print(f"❌ Error: CV file not found: {args.cv_path}")
        print("\nPlease ensure your CV PDF is in the correct location.")
        print(f"Expected: {args.cv_path}")
        sys.exit(1)
    
    # Initialize assistant
    try:
        assistant = JobApplicationAssistant(cv_path=args.cv_path)
    except Exception as e:
        print(f"❌ Error initializing assistant: {str(e)}")
        print("\nPlease check:")
        print("1. .env file exists with OPENAI_API_KEY")
        print("2. CV PDF is readable")
        sys.exit(1)
    
    # Non-interactive mode
    if args.job_file and args.action:
        try:
            with open(args.job_file, 'r', encoding='utf-8') as f:
                job_description = f.read()
        except Exception as e:
            print(f"❌ Error reading job file: {str(e)}")
            sys.exit(1)
        
        # Execute action
        if args.action == 'evaluate':
            result = assistant.evaluate_job_fit(job_description)
        elif args.action == 'cv-summary':
            result = assistant.generate_cv_summary(job_description)
        elif args.action == 'cover-letter':
            result = assistant.generate_cover_letter(
                job_description, args.company, args.role
            )
        elif args.action == 'full-package':
            result = assistant.full_application_package(
                job_description, args.company, args.role
            )
        
        # Handle result
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Save or print
        if args.output:
            assistant.save_results(result, args.output)
        else:
            print("\n" + "="*70)
            print("RESULTS")
            print("="*70)
            for key, value in result.items():
                if key not in ['model', 'tokens_used', 'total_tokens_used'] and value:
                    print(f"\n{key.upper()}:\n{value}\n")
    
    else:
        # Interactive mode
        interactive_mode(assistant)


if __name__ == "__main__":
    main()
