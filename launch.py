#!/usr/bin/env python3
"""Launcher for the Job Application Assistant GUI.
"""

import sys


def main():
    try:
        from gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"\nError launching GUI: {e}")
        print("Try a different version if available.")
        sys.exit(1)


if __name__ == "__main__":
    main()
