@echo off
title Debug eBay Title Extraction
color 0E

echo ============================================================
echo   DEBUG: eBay Title Extraction
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo [1/2] Running simple test to see ANY titles...
echo ============================================================
python simple_test.py

echo.
echo [2/2] Running detailed debug of title extraction...
echo ============================================================
python debug_titles.py

echo.
echo ============================================================
echo   Debug Complete!
echo ============================================================
echo Check the generated HTML files to see what eBay returned
pause
