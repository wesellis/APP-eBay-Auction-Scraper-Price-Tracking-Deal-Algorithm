@echo off
title GBA Scraper - Robust Test
color 0A

echo ============================================================
echo   Testing ROBUST GBA Scraper with Retry Logic
echo ============================================================
echo.
echo This version handles timeouts and connection issues!
echo.

cd /d "A:\Project\Ebay Scraper"

python robust_scraper.py

echo.
echo ============================================================
echo   Test Complete!
echo ============================================================
pause
