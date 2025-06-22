"""
Configuration settings for the eBay scraper
"""

# Search configuration
SEARCH_TERMS = [
    "gameboy+advance+console",
    "game+boy+advance+gba", 
    "gba+console+handheld",
    "gameboy+advance+sp",
    "gba+sp+console"
]

# Keywords to filter for GBA items - made less strict
GBA_KEYWORDS = [
    'gameboy advance', 
    'game boy advance', 
    'gba', 
    'advance sp',
    'gba sp',
    'nintendo gba',
    'handheld console',
    'portable gaming'
]

# Request headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Scraping settings
REQUEST_TIMEOUT = 15
MAX_LISTINGS_PER_SEARCH = 15
DELAY_BETWEEN_SEARCHES = 2
DELAY_BETWEEN_REQUESTS = 0.5
DEBUG_MODE = True  # Show more detailed output

# Output settings
OUTPUT_FILENAME = 'gba_auctions.html'
MAX_TITLE_LENGTH = 100

# Image settings
DEFAULT_IMAGE = 'https://via.placeholder.com/200x150?text=No+Image'
IMAGE_RESOLUTION_UPGRADE = {
    's-l140': 's-l300',
    's-l225': 's-l400'
}

# CSS selectors for different page layouts
SELECTORS = {
    'listings': [
        'div.s-item',
        'div[data-view="mi:1686"]',
        '.srp-results .s-item'
    ],
    'title': [
        'h3.s-item__title',
        'a.s-item__link',
        'span.BOLD',
        '.s-item__title'
    ],
    'price': [
        'span.s-item__price',
        'span.notranslate',
        '.s-item__price'
    ],
    'link': [
        'a.s-item__link',
        '.s-item__link'
    ],
    'image': [
        'img.s-item__image',
        '.s-item__image img',
        'img'
    ],
    'time_left': [
        'span.s-item__time-left',
        '.s-item__time-left'
    ]
}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5
