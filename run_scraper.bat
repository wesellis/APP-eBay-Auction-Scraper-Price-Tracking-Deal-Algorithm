@echo off
title GameBoy Advance Auction Scraper
color 0A

echo ============================================================
echo   GameBoy Advance eBay Auction Scraper  
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.6+
    pause
    exit /b 1
)

REM Install dependencies if needed
python -c "import requests, bs4" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing required packages...
    pip install requests beautifulsoup4
)

echo [INFO] Starting GameBoy Advance auction scraper...
echo.

REM Run the FINAL SOLUTION that provides value even when eBay blocks
python final_solution.py

REM Check if HTML was created and open it
if exist "gba_auctions.html" (
    echo.
    echo [SUCCESS] Results saved to gba_auctions.html
    echo [INFO] Opening in browser...
    start "" "gba_auctions.html"
) else (
    echo [WARNING] No HTML file created
)

echo.
echo Press any key to exit...
pause >nul
