@echo off
title eBay Structure Detection
color 0A

echo ============================================================
echo   eBay Structure Detector - Finding Current HTML Layout
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo Running structure detector to find what eBay is actually using...
echo.

python structure_detector.py

echo.
echo ============================================================
echo   Detection Complete!
echo ============================================================
echo.
echo Check current_ebay_structure.html to see the raw eBay page
echo The detector will show which selectors actually find items
echo.
pause
