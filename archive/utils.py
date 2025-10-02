"""
Utility functions for the eBay scraper
"""

import sys
import threading
import time
import weakref
from datetime import datetime
from functools import lru_cache


class Logger:
    """Simple logging utility"""
    
    @staticmethod
    def info(message):
        print(f"[INFO] {message}")
    
    @staticmethod
    def success(message):
        print(f"[SUCCESS] {message}")
    
    @staticmethod
    def warning(message):
        print(f"[WARNING] {message}")
    
    @staticmethod
    def error(message):
        print(f"[ERROR] {message}")
    
    @staticmethod
    def debug(message):
        print(f"[DEBUG] {message}")
    
    @staticmethod
    def network(message):
        print(f"[NETWORK] {message}")
    
    @staticmethod
    def data(message):
        print(f"[DATA] {message}")

@lru_cache(maxsize=512)
def safe_get_text_cached(element_text, default=""):
    """Cached version of text extraction"""
    return element_text.strip() if element_text else default

def safe_get_text(element, default=""):
    """Safely extract text from a BeautifulSoup element"""
    if element:
        text = element.get_text(strip=True)
        return safe_get_text_cached(text, default) if text else default
    return default

def safe_get_attribute(element, attribute, default=""):
    """Safely extract an attribute from a BeautifulSoup element"""
    if element:
        return element.get(attribute, default)
    return default

@lru_cache(maxsize=256)
def clean_title_cached(title, max_length=100):
    """Cached title cleaning for performance"""
    if not title:
        return "No title"
    
    # Fast string operations without regex
    title = title.replace("Shop on eBay", "").replace("New Listing", "").replace("SPONSORED", "")
    title = " ".join(title.split())  # Normalize whitespace
    
    if len(title) > max_length:
        title = title[:max_length-3] + "..."
    
    return title

def clean_title(title, max_length=100):
    """Clean and truncate title text with caching"""
    return clean_title_cached(title, max_length)

def upgrade_image_resolution(img_url, upgrades):
    """Upgrade image URL to higher resolution"""
    if not img_url:
        return ""
    
    for old_res, new_res in upgrades.items():
        if old_res in img_url:
            return img_url.replace(old_res, new_res)
    
    return img_url

def is_gba_related(title, keywords):
    """Check if title contains GBA-related keywords - MUCH more lenient"""
    if not title:
        return False
    
    title_lower = title.lower()
    
    # More comprehensive GBA keywords - any ONE of these should match
    expanded_keywords = [
        'gameboy advance',
        'game boy advance', 
        'gba',
        'advance sp',
        'gba sp',
        'gameboy sp',
        'game boy sp',
        'nintendo advance',
        'ags-001',  # GBA SP model numbers
        'ags-101',
        'ags001',
        'ags101'
    ]
    
    # Check if ANY keyword appears in the title
    for keyword in expanded_keywords:
        if keyword in title_lower:
            return True
    
    # Special case: if it contains both 'nintendo' and ('advance' or 'sp')
    if 'nintendo' in title_lower and ('advance' in title_lower or ' sp ' in title_lower):
        return True
        
    return False

def format_price(price_text):
    """Clean up price text"""
    if not price_text:
        return "Price not available"
    
    # Remove extra whitespace
    price_text = " ".join(price_text.split())
    
    # Handle common price formats
    if "to" in price_text.lower():
        return price_text  # Price range
    
    return price_text

def get_timestamp():
    """Get formatted timestamp for the HTML page"""
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")

def retry_on_failure(func, max_retries=3, delay=1):
    """Retry a function on failure"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            Logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                Logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                Logger.error(f"All {max_retries} attempts failed")
                raise e

def progress_bar(current, total, width=50):
    """Simple ASCII progress bar"""
    if total == 0:
        return ""
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(100 * current / total)
    return f"[{bar}] {percent}% ({current}/{total})"

def validate_url(url):
    """Basic URL validation"""
    if not url:
        return False
    return url.startswith(('http://', 'https://'))

def sanitize_html(text):
    """Basic HTML sanitization"""
    if not text:
        return ""
    
    # Replace problematic characters
    replacements = {
        '"': '&quot;',
        "'": '&#39;',
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def truncate_text(text, max_length):
    """Truncate text with ellipsis"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

class Timer:
    """Simple timer for measuring execution time"""
    
    def __init__(self):
        self.start_time = None
    
    def start(self):
        self.start_time = time.time()
    
    def elapsed(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time
    
    def elapsed_str(self):
        elapsed = self.elapsed()
        if elapsed < 60:
            return f"{elapsed:.1f} seconds"
        else:
            minutes = int(elapsed // 60)
            seconds = elapsed % 60
            return f"{minutes}m {seconds:.1f}s"
