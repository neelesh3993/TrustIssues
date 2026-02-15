@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   TRUST ISSUES - Complete Startup
echo ========================================
echo.

cd /d "%~dp0"

REM Check if .env file has real API keys
echo [1/5] Checking API keys...
findstr /C:"your_" backend\.env >nul 2>&1
if !errorlevel! equ 0 (
    echo.
    echo ================================================
    echo   ERROR: API KEYS NOT CONFIGURED!
    echo ================================================
    echo.
    echo You still have placeholder keys in backend\.env
    echo.
    echo Please edit backend\.env and add REAL keys:
    echo   1. Get Gemini API: https://makersuite.google.com/app/apikey
    echo   2. Get NewsAPI: https://newsapi.org/
    echo   3. Replace "your_..._here" with actual keys
    echo.
    pause
    exit /b 1
)
echo ✓ API keys appear to be configured

echo.
echo [2/5] Starting backend server...
cd backend
start "Trust Issues Backend" cmd /k "python -m uvicorn app.main:app --reload"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo [3/5] Testing backend connection...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if !errorlevel! neq 0 (
    echo.
    echo ================================================
    echo   WARNING: Backend not responding!
    echo ================================================
    echo.
    echo The backend server might not have started yet.
    echo Check the backend terminal window for errors.
    echo.
    echo Common issues:
    echo   - API keys invalid or missing
    echo   - Port 8000 already in use
    echo   - Python packages not installed
    echo.
    echo Press any key to continue anyway, or Ctrl+C to abort...
    pause >nul
) else (
    echo ✓ Backend is healthy and responding!
)

echo.
echo [4/5] Opening diagnostic tool...
cd ..
start "" test_backend.html

echo.
echo [5/5] Setup complete!
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Check the diagnostic tool that just opened
echo    - All tests should be GREEN ✓
echo.
echo 2. Build the extension:
echo    cd frontend
echo    npm run build
echo.
echo 3. Load in Chrome:
echo    chrome://extensions/
echo    → Enable "Developer mode"
echo    → Click "Load unpacked"
echo    → Select frontend\dist folder
echo.
echo 4. Test it:
echo    → Visit any news website
echo    → Click extension icon
echo    → Click "Scan Now"
echo    → Wait 10-15 seconds
echo.
echo Backend is running in the other window.
echo DO NOT CLOSE IT while using the extension!
echo.
pause
