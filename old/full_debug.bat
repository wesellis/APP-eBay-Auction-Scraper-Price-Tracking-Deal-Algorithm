@echo off
title eBay Scraper - Full Debug Suite
color 0A

echo ============================================================
echo   eBay Scraper - Full Debug Suite  
echo ============================================================
echo.

cd /d "A:\Project\Ebay Scraper"

echo [1/3] Running aggressive debug to see raw eBay data...
echo ============================================================
python aggressive_debug.py

echo.
echo [2/3] Running simple scraper (no filtering)...
echo ============================================================
python simple_scraper.py

echo.
echo [3/3] Running main scraper with enhanced debug...
echo ============================================================
python main.py

echo.
echo ============================================================
echo   Debug Suite Complete!
echo ============================================================
echo.
echo Check these files:
echo   • ebay_debug.html (raw eBay HTML)
echo   • simple_results.html (unfiltered results)  
echo   • gba_auctions.html (main scraper results)
echo.
pause
