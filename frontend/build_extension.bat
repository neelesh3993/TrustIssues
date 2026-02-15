@echo off
echo ========================================
echo  TRUST ISSUES - Building Extension
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Cleaning old builds...
if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
)
if exist dist (
    echo Removing dist...
    rmdir /s /q dist
)
if exist package-lock.json (
    del package-lock.json
)

echo.
echo [2/3] Installing dependencies...
call npm install --legacy-peer-deps

if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    echo.
    echo Try manually:
    echo   npm install --legacy-peer-deps --force
    pause
    exit /b 1
)

echo.
echo [3/3] Building extension...
call npm run build

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  BUILD COMPLETE!
echo ========================================
echo.
echo Extension built in: frontend\dist
echo.
echo Next steps:
echo 1. Open Chrome: chrome://extensions/
echo 2. Enable "Developer mode"
echo 3. Click "Load unpacked"
echo 4. Select the "dist" folder
echo.
pause
