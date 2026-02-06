@echo off
REM Job Application Assistant Launcher for Windows
REM Double-click this file to start the application

echo ========================================
echo Job Application Assistant
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Try to launch
echo Starting application...
echo.

python launch.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo Error occurred. Press any key to exit.
    echo ========================================
    pause
)
