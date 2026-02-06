#!/usr/bin/env python3
"""
Simple Launcher for Job Application Assistant
Automatically starts the best available GUI
"""

import sys
import os

def main():
    print("\n" + "="*70)
    print("  JOB APPLICATION ASSISTANT LAUNCHER")
    print("="*70 + "\n")
    
    # Check for ttkbootstrap
    try:
        import ttkbootstrap
        print("✓ Modern GUI available (ttkbootstrap detected)")
        use_modern = True
    except ImportError:
        print("ℹ Modern GUI not available (install ttkbootstrap for enhanced UI)")
        print("  → pip install ttkbootstrap")
        use_modern = False
    
    # Launch appropriate version
    if use_modern:
        print("\n🚀 Launching Modern GUI...\n")
        try:
            from gui_modern import main as gui_main
            gui_main()
        except Exception as e:
            print(f"\n❌ Error launching modern GUI: {e}")
            print("Falling back to standard GUI...\n")
            from gui import main as gui_main
            gui_main()
    else:
        print("\n🚀 Launching Standard GUI...\n")
        try:
            from gui import main as gui_main
            gui_main()
        except Exception as e:
            print(f"\n❌ Error launching GUI: {e}")
            print("\nPlease ensure all dependencies are installed:")
            print("  pip install -r requirements.txt")
            sys.exit(1)

if __name__ == "__main__":
    main()
