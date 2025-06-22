@echo off
title GBA Scraper - Debug Mode
color 0E

echo ============================================================
echo   GBA Scraper - Debug Mode
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo [INFO] Testing eBay connection first...
python test_ebay.py

echo.
echo ============================================================
echo [INFO] Now running main scraper with debug output...
echo ============================================================
echo.

python main.py

echo.
echo ============================================================
echo [INFO] Debug session complete
echo ============================================================
pause
