#!/bin/bash

set -e  # Exit on error

# Choose Python command
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Python is not installed or not in PATH."
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping install."
fi

# Run the main script
if [ -f "main.py" ]; then
    echo "Running main.py..."
    python main.py
else
    echo "main.py not found."
    exit 1
fi
