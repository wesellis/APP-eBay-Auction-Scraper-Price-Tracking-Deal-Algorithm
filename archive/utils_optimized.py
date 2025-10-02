"""
Optimized utilities with performance improvements and memory management
"""

import hashlib
import logging
import threading
import time
import weakref
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from functools import lru_cache, wraps
from typing import Any, Dict, Generator, List, Optional, Tuple


class PerformanceLogger:
    """High-performance logger with minimal overhead"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._log_cache = {}
            self._last_flush = time.time()
    
    def _log(self, level: str, message: str) -> None:
        """Internal logging with minimal formatting"""
        if time.time() - self._last_flush > 1.0:  # Flush every second
            self._flush_cache()
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def _flush_cache(self):
        """Flush any cached logs"""
        self._last_flush = time.time()
        self._log_cache.clear()
    
    def info(self, message: str) -> None:
        self._log("INFO", message)
    
    def success(self, message: str) -> None:
        self._log("✓", message)
    
    def warning(self, message: str) -> None:
        self._log("⚠", message)
    
    def error(self, message: str) -> None:
        self._log("✗", message)
    
    def debug(self, message: str) -> None:
        self._log("DEBUG", message)

# Global logger instance
Logger = PerformanceLogger()

class MemoryManager:
    """Memory usage monitoring and optimization"""
    
    def __init__(self, max_memory_mb: int = 200):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._refs = weakref.WeakSet()
    
    def register_object(self, obj):
        """Register object for memory tracking"""
        self._refs.add(obj)
    
    def cleanup(self):
        """Force cleanup of tracked objects"""
        import gc
        gc.collect()

class SmartCache:
    """High-performance cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
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
                    oldest_keys = sorted(self._timestamps.items(), key=lambda x: x[1])[:10]
                    for old_key, _ in oldest_keys:
                        del self._cache[old_key]
                        del self._timestamps[old_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
            del self._timestamps[key]

# Global cache instance
cache = SmartCache()

def performance_timer(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            Logger.debug(f"{func.__name__} took {elapsed:.3f}s")
    return wrapper

@lru_cache(maxsize=512)
def safe_get_text(element_text: str, default: str = "") -> str:
    """Optimized text extraction with caching"""
    if not element_text:
        return default
    return element_text.strip()

@lru_cache(maxsize=256)
def safe_get_attribute(element_attrs: str, attribute: str, default: str = "") -> str:
    """Optimized attribute extraction with caching"""
    # This would need to be adapted based on how attributes are passed
    return default

def clean_title(title: str, max_length: int = 120) -> str:
    """Optimized title cleaning"""
    if not title:
        return "No title"
    
    # Use cache key
    cache_key = f"title_{hash(title)}_{max_length}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Fast cleaning without regex
    title = title.replace("Shop on eBay", "").replace("New Listing", "").replace("SPONSORED", "")
    title = " ".join(title.split())  # Normalize whitespace
    
    if len(title) > max_length:
        title = title[:max_length-3] + "..."
    
    cache.set(cache_key, title)
    return title

def upgrade_image_resolution(img_url: str, upgrades: Dict[str, str]) -> str:
    """Optimized image URL upgrading"""
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
    if 'nintendo' in title_lower and ('advance' in title_lower or ' sp ' in title_lower):
        max_confidence = max(max_confidence, 0.7)
    
    # AGS model numbers
    if any(model in title_lower for model in ['ags-001', 'ags-101', 'ags001', 'ags101']):
        max_confidence = max(max_confidence, 0.9)
    
    result = (max_confidence > 0.3, max_confidence)
    cache.set(cache_key, result)
    return result

def format_price(price_text: str) -> str:
    """Optimized price formatting"""
    if not price_text:
        return "Price not available"
    
    # Simple cleanup without regex
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

def batch_process(items: List[Any], batch_size: int = 10) -> Generator[List[Any], None, None]:
    """Process items in batches for memory efficiency"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def get_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")

def sanitize_html(text: str) -> str:
    """Fast HTML sanitization"""
    if not text:
        return ""
    
    # Use translation table for speed
    translation = str.maketrans({
        '"': '&quot;',
        "'": '&#39;',
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;'
    })
    
    return text.translate(translation)

class HighPerformanceTimer:
    """High-resolution timer for performance measurement"""
    
    def __init__(self):
        self.start_time = None
        self.splits = []
    
    def start(self):
        self.start_time = time.perf_counter()
        self.splits = []
    
    def split(self, label: str = ""):
        if self.start_time is None:
            return 0
        elapsed = time.perf_counter() - self.start_time
        self.splits.append((label, elapsed))
        return elapsed
    
    def elapsed(self) -> float:
        if self.start_time is None:
            return 0
        return time.perf_counter() - self.start_time
    
    def elapsed_str(self) -> str:
        elapsed = self.elapsed()
        if elapsed < 1:
            return f"{elapsed*1000:.1f}ms"
        elif elapsed < 60:
            return f"{elapsed:.2f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            return f"{minutes}m {seconds:.1f}s"

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Optimized retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            Logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
            time.sleep(delay)

# Memory manager instance
memory_manager = MemoryManager()
