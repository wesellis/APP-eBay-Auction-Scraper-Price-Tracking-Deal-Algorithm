@echo off
title Quick GBA Scraper Launch
color 0A

REM Quick launcher - just run and open results
cd /d "A:\Project\Ebay Scraper"

echo Starting GBA Auction Scraper...
python main.py

REM Auto-open HTML if it exists
if exist "gba_auctions.html" (
    start "" "gba_auctions.html"
)

timeout /t 3 >nul
