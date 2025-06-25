"""
Core utilities and helper functions
"""

import time
import hashlib
import threading
from datetime import datetime
from typing import Optional, Any, Tuple, Dict
from functools import lru_cache, wraps

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
            self._last_flush = time.time()
    
    def _log(self, level: str, message: str) -> None:
        """Internal logging with minimal formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
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
    
    def network(self, message: str) -> None:
        self._log("NET", message)
    
    def data(self, message: str) -> None:
        self._log("DATA", message)

# Global logger instance
Logger = PerformanceLogger()

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
def safe_get_text_cached(element_text: str, default: str = "") -> str:
    """Cached text extraction for performance"""
    return element_text.strip() if element_text else default

def safe_get_text(element, default: str = "") -> str:
    """Safely extract text from BeautifulSoup element"""
    if element:
        text = element.get_text(strip=True)
        return safe_get_text_cached(text, default) if text else default
    return default

def safe_get_attribute(element, attribute: str, default: str = "") -> str:
    """Safely extract attribute from BeautifulSoup element"""
    if element:
        return element.get(attribute, default)
    return default

def get_timestamp() -> str:
    """Get formatted timestamp for display"""
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")

def sanitize_html(text: str) -> str:
    """Fast HTML sanitization using translation table"""
    if not text:
        return ""
    
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
    
    def split(self, label: str = "") -> float:
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
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            Logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
            time.sleep(delay)
