#!/bin/bash
# Research Copilot Setup Script for macOS/Linux
# This script automates the entire setup and run process

set -e  # Exit on error

echo "============================================================"
echo "     RESEARCH COPILOT - Automated Setup (macOS/Linux)"
echo "============================================================"

# Check Python
echo ""
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.10+"
    exit 1
fi
python3 --version
echo "OK - Python found"

# Check/create virtual environment
echo ""
echo "[2/4] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate venv and install requirements
echo ""
echo "[3/4] Installing dependencies..."
source venv/bin/activate
pip install --quiet -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "OK - Dependencies installed"

# Check .env
echo ""
echo "[4/4] Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "WARNING: Created .env from template"
        echo "Please edit .env and add your OpenAI API key (OPENAI_API_KEY=sk-...)"
        read -p "Press Enter to continue..."
    fi
fi

# Ingest papers if papers directory exists
if [ -d "papers" ]; then
    echo ""
    echo "[Optional] Ingesting papers..."
    python src/ingest.py
fi

# Start the app
echo ""
echo "============================================================"
echo "     Starting Research Copilot on http://localhost:8501"
echo "============================================================"
echo ""
streamlit run streamlit_app.py
