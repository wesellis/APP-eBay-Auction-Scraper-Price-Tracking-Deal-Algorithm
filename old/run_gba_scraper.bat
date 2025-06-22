@echo off
title GameBoy Advance eBay Auction Scraper
color 0A

echo ========================================
echo  GameBoy Advance eBay Auction Scraper
echo ========================================
echo.

REM Change to the script directory
cd /d "A:\Project\Ebay Scraper"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

echo [INFO] Python found, starting scraper...
echo.

REM Run the scraper
python main.py

REM Check if the HTML file was created
if exist "gba_auctions.html" (
    echo.
    echo [SUCCESS] HTML file created successfully!
    echo [INFO] Opening gba_auctions.html in your default browser...
    start "" "gba_auctions.html"
) else (
    echo.
    echo [WARNING] HTML file was not created
    echo Check the console output above for errors
)

echo.
echo [INFO] Scraper completed. Press any key to exit...
pause >nul
