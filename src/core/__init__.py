"""
Core scraper package initialization
"""

from .base_scraper import BaseScraper
from .models import ListingData

# Import scrapers conditionally
try:
    from .async_scraper import AsyncEbayScraper, scrape_gba_auctions

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

from .standard_scraper import StandardEbayScraper, scrape_gba_auctions_standard

__all__ = [
    "ListingData",
    "BaseScraper",
    "StandardEbayScraper",
    "scrape_gba_auctions_standard",
    "ASYNC_AVAILABLE",
]

if ASYNC_AVAILABLE:
    __all__.extend(["scrape_gba_auctions", "AsyncEbayScraper"])
