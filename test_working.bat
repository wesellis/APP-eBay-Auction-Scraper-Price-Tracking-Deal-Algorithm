@echo off
title GBA Scraper - Test Run
color 0A

echo ============================================================
echo   Testing the WORKING GBA Scraper
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo [INFO] Running the simplified working scraper...
echo This version shows step-by-step what's happening...
echo.

python working_scraper.py

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
pause
