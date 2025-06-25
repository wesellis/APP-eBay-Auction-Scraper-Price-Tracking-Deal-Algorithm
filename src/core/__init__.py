"""
Core scraper package initialization
"""

from .models import ListingData
from .base_scraper import BaseScraper

# Import scrapers conditionally
try:
    from .async_scraper import scrape_gba_auctions, AsyncEbayScraper
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

from .standard_scraper import scrape_gba_auctions_standard, StandardEbayScraper

__all__ = [
    'ListingData', 'BaseScraper', 'StandardEbayScraper',
    'scrape_gba_auctions_standard', 'ASYNC_AVAILABLE'
]

if ASYNC_AVAILABLE:
    __all__.extend(['scrape_gba_auctions', 'AsyncEbayScraper'])
