"""
Optimized configuration for eBay scraper with performance improvements
"""

import concurrent.futures
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class PerformanceConfig:
    """Performance-related configuration"""
    # Async settings
    max_concurrent_requests: int = 8
    connection_pool_size: int = 20
    connection_timeout: int = 10
    read_timeout: int = 15
    
    # Memory optimization
    max_memory_usage_mb: int = 200
    enable_streaming: bool = True
    chunk_size: int = 8192
    
    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_entries: int = 1000

@dataclass
class ScrapingConfig:
    """Scraping behavior configuration"""
    # Request limits
    max_listings_per_search: int = 20
    max_total_listings: int = 100
    max_retries: int = 3
    
    # Delays (optimized)
    base_delay: float = 0.5
    max_delay: float = 10.0
    jitter_factor: float = 0.1
    
    # Quality thresholds
    min_title_length: int = 10
    max_title_length: int = 120
    similarity_threshold: float = 0.85

# Search configuration - optimized for performance
SEARCH_TERMS = [
    "gameboy+advance+console",
    "gba+console+sp",
    "game+boy+advance",
    "nintendo+gba"
]

# Enhanced GBA keywords with weights
GBA_KEYWORDS = {
    # High confidence keywords
    'gameboy advance': 1.0,
    'game boy advance': 1.0,
    'gba': 0.9,
    'gba sp': 1.0,
    'advance sp': 1.0,
    
    # Medium confidence
    'nintendo gba': 0.8,
    'ags-001': 0.9,  # GBA SP model
    'ags-101': 0.9,  # GBA SP backlit
    
    # Lower confidence but still relevant
    'handheld console': 0.3,
    'portable gaming': 0.2
}

# Optimized headers with rotation
HEADER_SETS = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1'
    }
]

# Optimized CSS selectors with fallback chain
SELECTOR_CHAINS = {
    'listing_container': [
        'div.s-item',
        'div[data-view="mi:1686"]',
        '.srp-results .s-item',
        'div.srp-river-results div'
    ],
    'title': [
        'h3.s-item__title span[role="heading"]',
        'h3.s-item__title',
        'a.s-item__link span',
        '.s-item__title span',
        '.s-item__title'
    ],
    'price': [
        'span.s-item__price span.notranslate',
        'span.s-item__price',
        '.s-item__price .notranslate',
        '.s-item__price'
    ],
    'link': [
        'a.s-item__link[href]',
        '.s-item__link[href]'
    ],
    'image': [
        'img.s-item__image[src]',
        '.s-item__image img[src]',
        'img[src]'
    ],
    'time_left': [
        'span.s-item__time-left',
        '.s-item__time-left',
        '.s-item__time-end'
    ]
}

# Performance instances
PERF = PerformanceConfig()
SCRAPING = ScrapingConfig()

# Output settings
OUTPUT_FILENAME = 'gba_auctions.html'
BACKUP_FILENAME = 'gba_auctions_backup.html'

# Image optimization
DEFAULT_IMAGE = 'https://via.placeholder.com/300x200/f8f9fa/6c757d?text=No+Image'
IMAGE_UPGRADES = {
    's-l140': 's-l400',
    's-l225': 's-l500',
    's-l300': 's-l640'
}

# Environment detection
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() == 'true'
DEVELOPMENT_MODE = os.environ.get('ENV', 'prod') == 'dev'

# Thread pool configuration
MAX_WORKERS = min(PERF.max_concurrent_requests, (os.cpu_count() or 1) * 2)
