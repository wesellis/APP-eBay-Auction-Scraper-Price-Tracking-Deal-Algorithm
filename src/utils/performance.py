"""
Memory management and performance monitoring utilities
"""

import threading
import weakref
import time
from typing import Dict, Any

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

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.metrics = {
            'requests_made': 0,
            'requests_failed': 0,
            'listings_found': 0,
            'duplicates_removed': 0,
            'cache_hits': 0,
            'total_time': 0
        }
        self.start_time = None
    
    def start(self):
        self.start_time = time.perf_counter()
    
    def increment(self, metric: str, value: int = 1):
        self.metrics[metric] += value
    
    def get_summary(self) -> Dict:
        if self.start_time:
            self.metrics['total_time'] = time.perf_counter() - self.start_time
        return self.metrics.copy()

# Global instances
memory_manager = MemoryManager()
