#!/usr/bin/env python3
"""
Test script to verify the Job Application Assistant setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def test_environment():
    """Test if environment is set up correctly"""
    print("\n" + "="*70)
    print("TESTING ENVIRONMENT SETUP")
    print("="*70)

    load_dotenv()
    cv_path = os.getenv("CV_PATH", "cv.pdf")

    tests_passed = 0
    tests_total = 0

    # Test 1: Check Python version
    tests_total += 1
    print("\n1. Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor} (OK)")
        tests_passed += 1
    else:
        print(f"   ✗ Python {sys.version_info.major}.{sys.version_info.minor} (Need 3.8+)")

    # Test 2: Check dependencies
    tests_total += 1
    print("\n2. Checking dependencies...")
    try:
        import openai
        import dotenv
        import PyPDF2
        print("   ✓ All dependencies installed")
        tests_passed += 1
    except ImportError as e:
        print(f"   ✗ Missing dependency: {str(e)}")
        print("   → Run: pip install -r requirements.txt")

    # Test 3: Check .env file
    tests_total += 1
    print("\n3. Checking .env file...")
    if Path('.env').exists():
        print("   ✓ .env file exists")
        tests_passed += 1
    else:
        print("   ✗ .env file not found")
        print("   → Copy .env.example to .env and add your API key")

    # Test 4: Check API key
    tests_total += 1
    print("\n4. Checking OpenAI API key...")
    api_key = os.getenv('OPENAI_API_KEY')

    if api_key:
        if api_key.startswith('sk-'):
            print("   ✓ API key found and looks valid")
            tests_passed += 1
        else:
            print("   ✗ API key doesn't look valid (should start with 'sk-')")
    else:
        print("   ✗ OPENAI_API_KEY not found in .env")
        print("   → Add: OPENAI_API_KEY=sk-your-key-here")

    # Test 5: Check CV file
    tests_total += 1
    print(f"\n5. Checking for CV file ({cv_path})...")
    if Path(cv_path).exists():
        print(f"   ✓ {cv_path} found")
        tests_passed += 1
    else:
        print(f"   ✗ {cv_path} not found")
        print(f"   → Place your CV PDF as '{cv_path}' in this directory")
        print(f"   → Or set CV_PATH=your_cv.pdf in your .env file")

    # Test 6: Test OpenAI connection
    tests_total += 1
    print("\n6. Testing OpenAI API connection...")
    if api_key and api_key.startswith('sk-'):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'OK' if you can read this"}],
                max_tokens=5
            )
            print("   ✓ API connection successful")
            tests_passed += 1
        except Exception as e:
            print(f"   ✗ API connection failed: {str(e)}")
            print("   → Check your API key and internet connection")
    else:
        print("   ⊗ Skipped (no valid API key)")

    # Test 7: Test PDF extraction
    tests_total += 1
    print("\n7. Testing PDF extraction...")
    if Path(cv_path).exists():
        try:
            import PyPDF2
            with open(cv_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

                if len(text) > 100:
                    print(f"   ✓ PDF readable ({len(text)} characters extracted)")
                    print(f"   Preview: {text[:100]}...")
                    tests_passed += 1
                else:
                    print("   ✗ PDF seems empty or unreadable")
        except Exception as e:
            print(f"   ✗ PDF extraction failed: {str(e)}")
    else:
        print("   ⊗ Skipped (no CV file)")

    # Summary
    print("\n" + "="*70)
    print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
    print("="*70)

    if tests_passed == tests_total:
        print("\n🎉 All tests passed! You're ready to use the assistant.")
        print("\nNext steps:")
        print("  1. Run interactive mode: python cli.py")
        print("  2. Or try examples: python examples.py")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nQuick setup checklist:")
        print("  [ ] Install dependencies: pip install -r requirements.txt")
        print("  [ ] Create .env file with OPENAI_API_KEY")
        print(f"  [ ] Place CV as {cv_path} (or set CV_PATH in .env)")
        return False


def test_assistant():
    """Test the assistant with a simple query"""
    print("\n" + "="*70)
    print("TESTING ASSISTANT FUNCTIONALITY")
    print("="*70)
    
    try:
        from job_application_assistant import JobApplicationAssistant

        print("\nInitializing assistant...")
        assistant = JobApplicationAssistant()
        
        print("\nRunning test query...")
        test_job = """
        Machine Learning Engineer
        Requirements: Python, PyTorch, PhD in ML/CS
        """
        
        result = assistant.evaluate_job_fit(test_job)
        
        if 'error' in result:
            print(f"\n✗ Test failed: {result['error']}")
            return False
        else:
            print("\n✓ Test successful!")
            print(f"\nSample output (first 200 chars):")
            print("-" * 70)
            print(result['evaluation'][:200] + "...")
            print("-" * 70)
            print(f"\nTokens used: {result['tokens_used']}")
            return True
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  JOB APPLICATION ASSISTANT - SETUP TEST")
    print("="*70)
    
    # Run environment tests
    env_ok = test_environment()
    
    if not env_ok:
        print("\n⚠️  Fix environment issues before testing the assistant.")
        return
    
    # Ask if user wants to test the assistant
    print("\n" + "-"*70)
    test_run = input("\nRun functional test? (costs ~$0.01, y/n): ").strip().lower()
    
    if test_run == 'y':
        test_assistant()
    else:
        print("\nSkipping functional test.")
        print("You can run it anytime with: python test_setup.py")
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
