#!/usr/bin/env bash
# F1 Analytics Dashboard - Local Development Start Script
# Run this to get the app running instantly

echo "=========================================="
echo "  F1 Analytics Dashboard - Local Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python environment..."
python --version

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run verification
echo ""
echo "Running pre-flight checks..."
python verify_production.py

# Start app
echo ""
echo "Starting F1 Analytics Dashboard..."
echo ""
streamlit run app.py --logger.level=error

