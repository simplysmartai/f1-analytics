#!/bin/bash

# F1 Analytics Dashboard - Quick Start Script
# For nexairi.com

echo "🏎️  F1 Analytics Dashboard Setup"
echo "================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================="
echo "✅ Setup complete!"
echo ""
echo "To start the app, run:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "Or use: ./run.sh"
echo "================================="
