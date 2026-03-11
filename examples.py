#!/usr/bin/env python3
"""Usage examples for the Job Application Assistant."""

from job_application_assistant import JobApplicationAssistant

SAMPLE_JD = """
Senior Machine Learning Engineer — Earth Observation
London, UK

We're building deep learning models for satellite imagery analysis.

Requirements:
- PhD in Computer Science, Machine Learning, or related field
- Strong experience with PyTorch and deep learning
- Background in computer vision or remote sensing
- Experience with geospatial data (SAR, multispectral)
- Strong publication record preferred

Responsibilities:
- Design and implement ML architectures for EO data
- Collaborate with product teams on deployment
- Publish research findings
"""


def example_1_evaluate():
    """Example 1: Evaluate job fit."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Job Fit Evaluation")
    print("="*60)
    assistant = JobApplicationAssistant()
    result = assistant.evaluate_job_fit(SAMPLE_JD)
    print(result["evaluation"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_2_cv_summary():
    """Example 2: Generate a tailored CV summary."""
    print("\n" + "="*60)
    print("EXAMPLE 2: CV Summary")
    print("="*60)
    assistant = JobApplicationAssistant()
    result = assistant.generate_cv_summary(SAMPLE_JD)
    print(result["summary"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_3_cover_letter():
    """Example 3: Generate a cover letter."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Cover Letter")
    print("="*60)
    assistant = JobApplicationAssistant()
    result = assistant.generate_cover_letter(
        job_description=SAMPLE_JD,
        company_name="SatelliteAI Inc.",
        role_title="Senior Machine Learning Engineer"
    )
    print(result["cover_letter"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_4_interview_prep():
    """Example 4: Generate interview preparation materials."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Interview Preparation")
    print("="*60)
    assistant = JobApplicationAssistant()
    result = assistant.generate_interview_prep(SAMPLE_JD)
    print(result["interview_prep"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_5_linkedin_message():
    """Example 5: Generate a LinkedIn outreach message."""
    print("\n" + "="*60)
    print("EXAMPLE 5: LinkedIn Message")
    print("="*60)
    assistant = JobApplicationAssistant()
    result = assistant.generate_linkedin_message(
        job_description=SAMPLE_JD,
        recruiter_name="Sarah"
    )
    print(result["linkedin_message"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_6_answer_question():
    """Example 6: Answer an application question."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Application Question Answer")
    print("="*60)
    assistant = JobApplicationAssistant()
    question = "Describe a challenging ML project you've worked on and how you approached it."
    result = assistant.answer_application_question(
        job_description=SAMPLE_JD,
        question=question
    )
    print(f"Q: {result['question']}\n")
    print(result["answer"])
    print(f"\nTokens used: {result['tokens_used']}")


def example_7_complete_package():
    """Example 7: Generate and save a complete application package."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Complete Application Package")
    print("="*60)
    assistant = JobApplicationAssistant()
    package = assistant.full_application_package(
        job_description=SAMPLE_JD,
        company_name="SatelliteAI Inc.",
        role_title="Senior Machine Learning Engineer"
    )
    assistant.save_results(package, "example_output.txt")
    print(f"Package saved to: example_output.txt")
    print(f"Total tokens used: {package['total_tokens_used']}")
    print("\n--- CV Summary Preview ---")
    print(package["cv_summary"])


EXAMPLES = [
    ("Job Fit Evaluation",      example_1_evaluate),
    ("CV Summary",              example_2_cv_summary),
    ("Cover Letter",            example_3_cover_letter),
    ("Interview Preparation",   example_4_interview_prep),
    ("LinkedIn Message",        example_5_linkedin_message),
    ("Answer Question",         example_6_answer_question),
    ("Complete Package",        example_7_complete_package),
]


def main():
    print("\n" + "="*60)
    print("  JOB APPLICATION ASSISTANT — EXAMPLES")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(EXAMPLES, 1):
        print(f"  {i}. {name}")
    print(f"  {len(EXAMPLES)+1}. Run all")
    print(f"  {len(EXAMPLES)+2}. Exit")

    choice = input(f"\nSelect (1-{len(EXAMPLES)+2}): ").strip()

    if choice == str(len(EXAMPLES)+2):
        return
    elif choice == str(len(EXAMPLES)+1):
        for name, func in EXAMPLES:
            try:
                func()
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\nError in '{name}': {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(EXAMPLES):
        try:
            EXAMPLES[int(choice)-1][1]()
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print("\nInvalid choice.")


if __name__ == "__main__":
    main()
