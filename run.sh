#!/bin/bash

# Activate virtual environment and run the app

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

echo "🏎️  Starting F1 Analytics Dashboard..."
source venv/bin/activate
streamlit run app.py
