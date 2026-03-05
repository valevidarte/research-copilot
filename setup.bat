@echo off
REM Research Copilot Setup Script for Windows
REM This script automates the entire setup and run process

setlocal enabledelayedexpansion

echo ============================================================
echo     RESEARCH COPILOT - Automated Setup (Windows)
echo ============================================================

REM Check Python
echo.
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    exit /b 1
)
echo OK - Python found

REM Check .venv
echo.
echo [2/4] Checking virtual environment...
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists
)

REM Activate venv and install requirements
echo.
echo [3/4] Installing dependencies...
call .venv\Scripts\activate.bat
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo OK - Dependencies installed

REM Check .env
echo.
echo [4/4] Checking environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo WARNING: Created .env from template
        echo Please edit .env and add your OpenAI API key (OPENAI_API_KEY=sk-...)
        pause
    )
)

REM Ingest papers if papers directory exists
if exist "papers\" (
    echo.
    echo [Optional] Ingesting papers...
    python src/ingest.py
)

REM Start the app
echo.
echo ============================================================
echo     Starting Research Copilot on http://localhost:8501
echo ============================================================
echo.
streamlit run streamlit_app.py

pause
