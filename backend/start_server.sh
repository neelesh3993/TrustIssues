#!/bin/bash

echo "========================================"
echo " TRUST ISSUES - Starting Backend Server"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

echo "[1/3] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

python3 --version

echo ""
echo "[2/3] Checking dependencies..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "WARNING: Dependencies not installed"
    echo "Installing now..."
    pip3 install -r requirements.txt
fi

echo ""
echo "[3/3] Starting server..."
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
