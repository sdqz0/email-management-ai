#!/bin/bash

# Installation script for Email Management AI Agent

echo "Installing Email Management AI Agent..."

# Check if Python 3.10+ is installed
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3.10 or higher is required but not found."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Setting up directories..."
mkdir -p src/static/uploads

echo "Installation complete!"
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Navigate to the src directory: cd src"
echo "3. Run the application: python app.py"
echo "4. Open your browser and go to http://localhost:5000"
