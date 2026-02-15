#!/bin/bash

echo "========================================"
echo " TRUST ISSUES - Building Extension"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/3] Cleaning old builds..."
rm -rf node_modules
rm -rf dist
rm -f package-lock.json

echo ""
echo "[2/3] Installing dependencies..."
npm install --legacy-peer-deps

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: npm install failed!"
    echo ""
    echo "Try manually:"
    echo "  npm install --legacy-peer-deps --force"
    exit 1
fi

echo ""
echo "[3/3] Building extension..."
npm run build

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo " BUILD COMPLETE!"
echo "========================================"
echo ""
echo "Extension built in: frontend/dist"
echo ""
echo "Next steps:"
echo "1. Open Chrome: chrome://extensions/"
echo "2. Enable 'Developer mode'"
echo "3. Click 'Load unpacked'"
echo "4. Select the 'dist' folder"
echo ""
