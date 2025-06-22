@echo off
title GBA Scraper - Fixed Filtering Test
color 0A

echo ============================================================
echo   GBA Scraper - Testing Fixed Filtering
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo [1/2] Testing the filtering function...
echo ============================================================
python test_filtering.py

echo.
echo [2/2] Running main scraper with fixed filtering...
echo ============================================================
python main.py

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
echo.
echo If filtering test shows GBA items are detected,
echo the main scraper should now find results!
echo.
pause
