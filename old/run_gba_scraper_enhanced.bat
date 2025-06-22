@echo off
title GBA Auction Scraper - Enhanced Launcher
color 0A

echo ============================================================
echo   GameBoy Advance eBay Auction Scraper - Enhanced Launcher
echo ============================================================
echo.
echo [INFO] Checking system requirements...

REM Change to the script directory
cd /d "A:\Project\Ebay Scraper"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.6+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python found
python --version

REM Check if required packages are installed
echo.
echo [INFO] Checking required packages...

python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] requests package not found, installing...
    pip install requests
)

python -c "import bs4" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] beautifulsoup4 package not found, installing...
    pip install beautifulsoup4
)

echo [SUCCESS] All dependencies are ready!
echo.

REM Check if all required files exist
echo [INFO] Checking required files...

set "missing_files="
if not exist "main.py" set "missing_files=%missing_files% main.py"
if not exist "config.py" set "missing_files=%missing_files% config.py"
if not exist "scraper.py" set "missing_files=%missing_files% scraper.py"
if not exist "html_generator.py" set "missing_files=%missing_files% html_generator.py"
if not exist "utils.py" set "missing_files=%missing_files% utils.py"

if not "%missing_files%"=="" (
    echo [ERROR] Missing required files:%missing_files%
    echo Please make sure all scraper files are in this directory
    pause
    exit /b 1
)

echo [SUCCESS] All required files found!
echo.

echo ============================================================
echo   Starting GameBoy Advance Auction Scraper...
echo ============================================================
echo.

REM Run the scraper
python main.py

REM Check results
echo.
if exist "gba_auctions.html" (
    echo ============================================================
    echo   SCRAPING COMPLETED SUCCESSFULLY!
    echo ============================================================
    echo.
    echo [SUCCESS] HTML results file created: gba_auctions.html
    echo [INFO] File size: 
    for %%F in ("gba_auctions.html") do echo %%~zF bytes
    echo.
    echo [INFO] Opening results in your default browser...
    timeout /t 2 >nul
    start "" "gba_auctions.html"
    echo.
    echo [INFO] You can also manually open: gba_auctions.html
    echo [INFO] Run this batch file again anytime for fresh results!
) else (
    echo ============================================================
    echo   SCRAPING COMPLETED WITH ISSUES
    echo ============================================================
    echo.
    echo [WARNING] HTML file was not created
    echo [INFO] This could be due to:
    echo   - No GBA auctions found ending soon
    echo   - Network connectivity issues
    echo   - eBay temporarily blocking requests
    echo.
    echo [INFO] Try running again in a few minutes
)

echo.
echo ============================================================
echo   Press any key to exit...
echo ============================================================
pause >nul
