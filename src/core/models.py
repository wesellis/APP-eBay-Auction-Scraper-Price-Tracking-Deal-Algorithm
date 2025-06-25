"""
Data models for scraper components
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ListingData:
    """Structured listing data with optimization features"""
    title: str
    price: str
    link: str
    image: str
    time_left: str
    confidence: float = 0.0
    hash_key: str = ""
    
    def __post_init__(self):
        if not self.hash_key:
            # Generate hash for deduplication
            content = f"{self.title}{self.price}".lower().replace(" ", "")
            self.hash_key = str(hash(content))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for compatibility"""
        return {
            'title': self.title,
            'price': self.price,
            'link': self.link,
            'image': self.image,
            'time_left': self.time_left,
            'confidence': self.confidence
        }
