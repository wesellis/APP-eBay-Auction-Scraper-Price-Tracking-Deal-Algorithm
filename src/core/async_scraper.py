"""
High-performance async scraper implementation
"""

import asyncio
import random
import time
from typing import List, Optional

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from config import HEADER_SETS, PERF, SCRAPING, SEARCH_TERMS
from utils import (HighPerformanceTimer, Logger, PerformanceMonitor,
                   batch_process)

from .base_scraper import BaseScraper
from .models import ListingData


class AsyncEbayScraper(BaseScraper):
    """High-performance async eBay scraper"""

    def __init__(self):
        super().__init__()
        self.session = None
        self.semaphore = None
        self.monitor = PerformanceMonitor()
        self.timer = HighPerformanceTimer()

        if not AIOHTTP_AVAILABLE:
            raise ImportError(
                "aiohttp is required for async scraping. Install with: pip install aiohttp"
            )

    async def __aenter__(self):
        """Async context manager entry"""
        self.semaphore = asyncio.Semaphore(PERF.max_concurrent_requests)

        connector = aiohttp.TCPConnector(
            limit=PERF.connection_pool_size,
            limit_per_host=8,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        timeout = aiohttp.ClientTimeout(
            total=PERF.read_timeout, connect=PERF.connection_timeout
        )

        self.session = aiohttp.ClientSession(
            connector=connector, timeout=timeout, headers=self._get_next_headers()
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_next_headers(self) -> dict:
        """Rotate through header sets"""
        headers = HEADER_SETS[self._current_header_index % len(HEADER_SETS)]
        self._current_header_index += 1
        return headers

    async def fetch_with_retry(self, url: str) -> Optional[str]:
        """Fetch URL with intelligent retry logic"""
        async with self.semaphore:
            for attempt in range(SCRAPING.max_retries):
                try:
                    # Add jitter to prevent thundering herd
                    if attempt > 0:
                        jitter = random.uniform(0, SCRAPING.jitter_factor)
                        delay = SCRAPING.base_delay * (2**attempt) + jitter
                        await asyncio.sleep(min(delay, SCRAPING.max_delay))

                    async with self.session.get(url) as response:
                        self.monitor.increment("requests_made")

                        if response.status == 200:
                            content = await response.text()
                            return content
                        elif response.status == 429:
                            Logger.warning("Rate limited (429) - waiting...")
                            await asyncio.sleep(10)
                            continue
                        else:
                            Logger.warning(f"HTTP {response.status} for {url[:50]}...")

                except asyncio.TimeoutError:
                    Logger.warning(f"Timeout on attempt {attempt + 1}")
                    self.monitor.increment("requests_failed")
                except Exception as e:
                    Logger.error(f"Request failed: {e}")
                    self.monitor.increment("requests_failed")

            return None

    async def parse_listings_async(self, html_content: str) -> List[ListingData]:
        """Async listing parsing with memory optimization"""
        listings = self.parse_listings_from_html(html_content)

        # Update monitor
        self.monitor.increment("listings_found", len(listings))

        # Small async yield for other tasks
        await asyncio.sleep(0)
        return listings

    async def scrape_search_term(self, search_term: str) -> List[ListingData]:
        """Scrape a single search term async"""
        self.timer.split(f"start_{search_term}")
        Logger.info(f"Searching: {search_term.replace('+', ' ')}")

        try:
            url = self.build_search_url(search_term)
            html_content = await self.fetch_with_retry(url)

            if not html_content:
                Logger.warning(f"No content for: {search_term}")
                return []

            listings = await self.parse_listings_async(html_content)

            elapsed = self.timer.split(f"end_{search_term}")
            Logger.success(f"Found {len(listings)} listings in {elapsed:.2f}s")

            return listings

        except Exception as e:
            Logger.error(f"Error scraping {search_term}: {e}")
            return []

    async def scrape_all_terms(self) -> List[dict]:
        """Main async scraping method"""
        self.timer.start()
        self.monitor.start()

        Logger.info("🚀 Starting optimized async eBay scrape")
        Logger.info("=" * 50)

        try:
            # Create tasks for all search terms
            tasks = [self.scrape_search_term(term) for term in SEARCH_TERMS]

            # Execute all searches concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine all results
            all_listings = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    Logger.error(f"Search {i} failed: {result}")
                    continue

                all_listings.extend(result)

            # Remove duplicates efficiently
            unique_listings = self.remove_duplicates(all_listings)

            # Sort by confidence score
            unique_listings.sort(key=lambda x: x.confidence, reverse=True)

            # Convert to dict format for compatibility
            final_results = []
            for listing in unique_listings[: SCRAPING.max_total_listings]:
                final_results.append(listing.to_dict())

            # Performance summary
            summary = self.monitor.get_summary()
            duplicates_removed = len(all_listings) - len(unique_listings)
            self.monitor.increment("duplicates_removed", duplicates_removed)

            Logger.success(
                f"✅ Scraping complete! Found {len(final_results)} unique auctions"
            )
            Logger.info(
                f"📊 Performance: {summary['requests_made']} requests, "
                f"{duplicates_removed} duplicates removed, "
                f"{self.timer.elapsed_str()} total time"
            )

            return final_results

        except Exception as e:
            Logger.error(f"Scraping failed: {e}")
            return []


async def scrape_gba_auctions_async() -> List[dict]:
    """Main async scraping function"""
    async with AsyncEbayScraper() as scraper:
        return await scraper.scrape_all_terms()


def scrape_gba_auctions() -> List[dict]:
    """Synchronous wrapper for async scraping"""
    try:
        return asyncio.run(scrape_gba_auctions_async())
    except Exception as e:
        Logger.error(f"Async scraping failed: {e}")
        return []
