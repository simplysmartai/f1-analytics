@echo off
REM F1 Analytics Dashboard - Quick Start Script for Windows

echo F1 Analytics Dashboard Setup
echo =================================
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo =================================
echo Setup complete!
echo.
echo To start the app, run: run.bat
echo =================================
pause
