#!/usr/bin/env python3
"""Launcher for the Job Application Assistant GUI."""

import sys


def main():
    try:
        from gui_v2 import main as gui_main
        gui_main()
    except Exception as e:
        print(f"\nError launching GUI: {e}")
        print("Ensure dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
