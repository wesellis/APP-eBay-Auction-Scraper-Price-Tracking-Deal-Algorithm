"""
Text processing and analysis utilities
"""

import threading
import time
from difflib import SequenceMatcher
from functools import lru_cache
from typing import Any, Dict, Generator, List, Tuple


class SmartCache:
    """High-performance cache with TTL and size limits"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Any:
        with self._lock:
            if key not in self._cache:
                return None

            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                return None

            return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            # Cleanup if at capacity
            if len(self._cache) >= self.max_size:
                self._cleanup_expired()
                if len(self._cache) >= self.max_size:
                    # Remove oldest entries
                    oldest_keys = sorted(self._timestamps.items(), key=lambda x: x[1])[
                        :10
                    ]
                    for old_key, _ in oldest_keys:
                        del self._cache[old_key]
                        del self._timestamps[old_key]

            self._cache[key] = value
            self._timestamps[key] = time.time()

    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key
            for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
            del self._timestamps[key]


# Global cache instance
cache = SmartCache()


@lru_cache(maxsize=256)
def clean_title_cached(title: str, max_length: int = 120) -> str:
    """Cached title cleaning for performance"""
    if not title:
        return "No title"

    # Fast string operations
    title = (
        title.replace("Shop on eBay", "")
        .replace("New Listing", "")
        .replace("SPONSORED", "")
    )
    title = " ".join(title.split())  # Normalize whitespace

    if len(title) > max_length:
        title = title[: max_length - 3] + "..."

    return title


def clean_title(title: str, max_length: int = 120) -> str:
    """Clean and truncate title text with caching"""
    return clean_title_cached(title, max_length)


def upgrade_image_resolution(img_url: str, upgrades: Dict[str, str]) -> str:
    """Upgrade image URL to higher resolution with caching"""
    if not img_url:
        return ""

    # Check cache first
    cache_key = f"img_{hash(img_url)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    result = img_url
    for old_res, new_res in upgrades.items():
        if old_res in result:
            result = result.replace(old_res, new_res)
            break

    cache.set(cache_key, result)
    return result


def is_gba_related(title: str, keywords: Dict[str, float]) -> Tuple[bool, float]:
    """Enhanced GBA relevance detection with confidence scoring"""
    if not title:
        return False, 0.0

    # Check cache first
    cache_key = f"gba_{hash(title.lower())}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    title_lower = title.lower()
    max_confidence = 0.0

    # Score against all keywords
    for keyword, weight in keywords.items():
        if keyword in title_lower:
            max_confidence = max(max_confidence, weight)

    # Special rules for compound matches
    if "nintendo" in title_lower and (
        "advance" in title_lower or " sp " in title_lower
    ):
        max_confidence = max(max_confidence, 0.7)

    # AGS model numbers
    if any(
        model in title_lower for model in ["ags-001", "ags-101", "ags001", "ags101"]
    ):
        max_confidence = max(max_confidence, 0.9)

    result = (max_confidence > 0.3, max_confidence)
    cache.set(cache_key, result)
    return result


def format_price(price_text: str) -> str:
    """Clean and format price text"""
    if not price_text:
        return "Price not available"

    # Simple cleanup
    return " ".join(price_text.split())


def calculate_similarity(text1: str, text2: str) -> float:
    """Optimized text similarity calculation"""
    if not text1 or not text2:
        return 0.0

    # Use faster algorithm for long strings
    if len(text1) > 100 or len(text2) > 100:
        # Hash-based similarity for performance
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    # Use SequenceMatcher for shorter strings
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def batch_process(
    items: List[Any], batch_size: int = 10
) -> Generator[List[Any], None, None]:
    """Process items in batches for memory efficiency"""
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
