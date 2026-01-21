@echo off
REM Run F1 Analytics Dashboard

if not exist "venv" (
    echo Virtual environment not found!
    echo Run setup.bat first
    pause
    exit
)

echo Starting F1 Analytics Dashboard...
call venv\Scripts\activate
streamlit run app.py
