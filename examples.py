#!/usr/bin/env python3
"""
Simple example demonstrating basic usage of the Job Application Assistant
"""

from job_application_assistant import JobApplicationAssistant


def example_1_quick_evaluation():
    """Example 1: Quick job fit evaluation"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Quick Job Fit Evaluation")
    print("="*70)
    
    # Initialize assistant
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    
    # Sample job description
    job_description = """
    Senior Machine Learning Engineer - Earth Observation
    Location: London, UK
    
    We're building cutting-edge ML models for satellite imagery analysis.
    
    Requirements:
    - PhD in Computer Science, Machine Learning, or related field
    - Strong experience with PyTorch and deep learning
    - Background in computer vision or remote sensing
    - Experience with geospatial data processing
    - Strong publication record preferred
    
    Responsibilities:
    - Design and implement novel ML architectures for EO data
    - Work with SAR and optical satellite imagery
    - Collaborate with product teams on deployment
    - Publish research findings
    """
    
    # Get evaluation
    result = assistant.evaluate_job_fit(job_description)
    
    print("\n" + result['evaluation'])
    print(f"\nTokens used: {result['tokens_used']}")


def example_2_cv_summary():
    """Example 2: Generate tailored CV summary"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Generate CV Summary")
    print("="*70)
    
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    
    job_description = """
    Applied Research Scientist - Computer Vision
    Tech Company, Cambridge UK
    
    Looking for a researcher with deep ML expertise to work on production CV systems.
    Requirements: PhD, PyTorch, strong publication record, industry interest.
    """
    
    result = assistant.generate_cv_summary(job_description)
    
    print("\nGenerated CV Summary:")
    print("-" * 70)
    print(result['summary'])
    print("-" * 70)
    print(f"\nTokens used: {result['tokens_used']}")


def example_3_cover_letter():
    """Example 3: Generate cover letter"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Generate Cover Letter")
    print("="*70)
    
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    
    job_description = """
    Machine Learning Engineer - Geospatial AI
    SatelliteAI Inc., Remote (UK-based)
    
    We're revolutionizing Earth observation with deep learning.
    
    Requirements:
    - Strong ML background (PhD preferred)
    - Experience with PyTorch
    - Knowledge of remote sensing or geospatial data
    - Ability to work independently and in teams
    
    You'll be:
    - Building ML models for satellite imagery
    - Optimizing models for production
    - Working with our science and engineering teams
    """
    
    result = assistant.generate_cover_letter(
        job_description=job_description,
        company_name="SatelliteAI Inc.",
        role_title="Machine Learning Engineer - Geospatial AI"
    )
    
    print("\nGenerated Cover Letter:")
    print("-" * 70)
    print(result['cover_letter'])
    print("-" * 70)
    print(f"\nTokens used: {result['tokens_used']}")


def example_4_complete_package():
    """Example 4: Generate complete application package"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Complete Application Package")
    print("="*70)
    
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    
    job_description = """
    Senior ML Researcher
    AI Research Lab, Edinburgh
    
    Join our team working on next-generation machine learning for Earth observation.
    
    Requirements:
    - PhD in ML/CV/related field
    - Publications in top-tier venues
    - Strong PyTorch skills
    - Experience with vision models
    - Interest in geospatial applications
    """
    
    # Generate everything
    package = assistant.full_application_package(
        job_description=job_description,
        company_name="AI Research Lab",
        role_title="Senior ML Researcher"
    )
    
    # Save to file
    assistant.save_results(package, "example_complete_package.txt")
    
    print("\n✓ Complete package generated and saved to: example_complete_package.txt")
    print(f"✓ Total tokens used: {package['total_tokens_used']}")
    
    # Print preview
    print("\n" + "="*70)
    print("PREVIEW - CV Summary")
    print("="*70)
    print(package['cv_summary'])


def example_5_answer_question():
    """Example 5: Answer application question"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Answer Application Question")
    print("="*70)
    
    assistant = JobApplicationAssistant(cv_path="reza_cv.pdf")
    
    job_description = """
    Research Engineer - ML
    Tech Company
    Requirements: PhD, ML expertise, Python/PyTorch
    """
    
    question = "Describe a challenging machine learning project you've worked on and how you approached it."
    
    result = assistant.answer_application_question(
        job_description=job_description,
        question=question
    )
    
    print(f"\nQuestion: {result['question']}")
    print("\nAnswer:")
    print("-" * 70)
    print(result['answer'])
    print("-" * 70)
    print(f"\nTokens used: {result['tokens_used']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  JOB APPLICATION ASSISTANT - USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        ("Quick Evaluation", example_1_quick_evaluation),
        ("CV Summary", example_2_cv_summary),
        ("Cover Letter", example_3_cover_letter),
        ("Complete Package", example_4_complete_package),
        ("Answer Question", example_5_answer_question)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("6. Run all examples")
    print("7. Exit")
    
    choice = input("\nSelect example to run (1-7): ").strip()
    
    if choice == '7':
        return
    elif choice == '6':
        for name, func in examples:
            try:
                func()
                input("\nPress Enter to continue to next example...")
            except Exception as e:
                print(f"\n❌ Error in {name}: {str(e)}")
    elif choice in ['1', '2', '3', '4', '5']:
        try:
            examples[int(choice)-1][1]()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    main()
