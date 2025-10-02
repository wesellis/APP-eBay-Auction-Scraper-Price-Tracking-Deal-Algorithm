"""
Core configuration for eBay scraper with performance optimization
"""

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PerformanceConfig:
    """Performance-related settings"""

    max_concurrent_requests: int = 8
    connection_pool_size: int = 20
    connection_timeout: int = 10
    read_timeout: int = 15
    max_memory_usage_mb: int = 200
    enable_streaming: bool = True
    chunk_size: int = 8192
    enable_cache: bool = True
    cache_ttl_seconds: int = 300
    max_cache_entries: int = 1000


@dataclass
class ScrapingConfig:
    """Scraping behavior settings"""

    max_listings_per_search: int = 20
    max_total_listings: int = 100
    max_retries: int = 3
    base_delay: float = 0.5
    max_delay: float = 10.0
    jitter_factor: float = 0.1
    min_title_length: int = 10
    max_title_length: int = 120
    similarity_threshold: float = 0.85


# Search terms optimized for relevance
SEARCH_TERMS = [
    "gameboy+advance+console",
    "gba+console+sp",
    "game+boy+advance",
    "nintendo+gba",
]

# Enhanced GBA keywords with confidence weights
GBA_KEYWORDS = {
    # High confidence
    "gameboy advance": 1.0,
    "game boy advance": 1.0,
    "gba": 0.9,
    "gba sp": 1.0,
    "advance sp": 1.0,
    # Medium confidence
    "nintendo gba": 0.8,
    "ags-001": 0.9,  # GBA SP model numbers
    "ags-101": 0.9,
    "ags001": 0.9,
    "ags101": 0.9,
    # Lower confidence but relevant
    "handheld console": 0.3,
    "portable gaming": 0.2,
}

# Rotating headers for variety
HEADER_SETS = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
    },
]

# CSS selectors with fallback chains
SELECTOR_CHAINS = {
    "listing_container": [
        "div.s-item",
        'div[data-view="mi:1686"]',
        ".srp-results .s-item",
        "div.srp-river-results div",
    ],
    "title": [
        'h3.s-item__title span[role="heading"]',
        "h3.s-item__title",
        "a.s-item__link span",
        ".s-item__title span",
        ".s-item__title",
    ],
    "price": [
        "span.s-item__price span.notranslate",
        "span.s-item__price",
        ".s-item__price .notranslate",
        ".s-item__price",
    ],
    "link": ["a.s-item__link[href]", ".s-item__link[href]"],
    "image": ["img.s-item__image[src]", ".s-item__image img[src]", "img[src]"],
    "time_left": ["span.s-item__time-left", ".s-item__time-left", ".s-item__time-end"],
}

# Image optimization settings
DEFAULT_IMAGE = "https://via.placeholder.com/300x200/f8f9fa/6c757d?text=No+Image"
IMAGE_UPGRADES = {"s-l140": "s-l400", "s-l225": "s-l500", "s-l300": "s-l640"}

# Environment settings
DEBUG_MODE = os.environ.get("DEBUG", "false").lower() == "true"
DEVELOPMENT_MODE = os.environ.get("ENV", "prod") == "dev"

# Performance instances
PERF = PerformanceConfig()
SCRAPING = ScrapingConfig()

# Thread pool configuration
MAX_WORKERS = min(PERF.max_concurrent_requests, (os.cpu_count() or 1) * 2)

# Output settings
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_OUTPUT_FILE = "gba_auctions.html"
BACKUP_OUTPUT_FILE = "gba_auctions_backup.html"
