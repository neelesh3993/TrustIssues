@echo off
echo ========================================
echo  TRUST ISSUES - Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo [2/3] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo WARNING: Dependencies not installed
    echo Installing now...
    pip install -r requirements.txt
)

echo.
echo [3/3] Starting server...
echo.
echo Backend will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
