#!/bin/bash
# Job Application Assistant Launcher for macOS/Linux
# Make executable: chmod +x launch.sh
# Run: ./launch.sh

echo "========================================"
echo "  Job Application Assistant"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Display Python version
echo "Python version:"
python3 --version
echo ""

# Check if in correct directory
if [ ! -f "launch.py" ]; then
    echo "ERROR: launch.py not found!"
    echo "Please run this script from the application directory"
    exit 1
fi

# Launch the application
echo "Starting application..."
echo ""

python3 launch.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Error occurred. Check the output above."
    echo "========================================"
    read -p "Press Enter to exit..."
fi
