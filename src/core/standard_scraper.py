"""
Enhanced standard synchronous scraper with performance improvements
"""

import time
from typing import List

import requests

from config import HEADER_SETS, SCRAPING, SEARCH_TERMS
from utils import HighPerformanceTimer, Logger, retry_with_backoff

from .base_scraper import BaseScraper
from .models import ListingData


class StandardEbayScraper(BaseScraper):
    """Enhanced standard scraper with connection pooling and caching"""

    def __init__(self):
        super().__init__()
        # Optimized session with connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10, pool_maxsize=20, max_retries=3
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(HEADER_SETS[0])  # Use first header set

        self.timer = HighPerformanceTimer()
        self._cache = {}  # Simple response cache
        self.total_found = 0

    def fetch_page(self, url: str) -> str:
        """Optimized page fetching with caching"""
        # Check cache first
        cache_key = hash(url)
        if cache_key in self._cache:
            Logger.debug("Cache hit for URL")
            return self._cache[cache_key]

        try:
            Logger.network(f"Fetching: {url[:80]}...")
            response = self.session.get(url, timeout=15, stream=True)

            Logger.data(f"Response status: {response.status_code}")

            if response.status_code == 200:
                content = response.text
                # Cache successful responses (limit cache size)
                if len(self._cache) < 50:
                    self._cache[cache_key] = content
                return content
            elif response.status_code == 429:
                Logger.warning("Rate limited by eBay - waiting longer...")
                time.sleep(10)
                return None
            else:
                Logger.error(f"HTTP {response.status_code}")
                return None

        except requests.RequestException as e:
            Logger.error(f"Request failed: {e}")
            return None

    def scrape_search_term(self, search_term: str) -> List[ListingData]:
        """Scrape listings for a single search term"""
        Logger.info(f"Searching for: {search_term.replace('+', ' ')}")

        try:
            url = self.build_search_url(search_term)
            html_content = retry_with_backoff(
                lambda: self.fetch_page(url),
                max_retries=SCRAPING.max_retries,
                base_delay=SCRAPING.base_delay,
            )

            if not html_content:
                Logger.warning(f"No content retrieved for: {search_term}")
                return []

            listings = self.parse_listings_from_html(html_content)
            self.total_found += len(listings)

            return listings

        except Exception as e:
            Logger.error(f"Error scraping {search_term}: {e}")
            return []

    def scrape_all_terms(self) -> List[dict]:
        """Scrape all configured search terms"""
        self.timer.start()
        Logger.info("Starting eBay GBA auction scrape")
        Logger.info("=" * 50)

        all_listings = []

        for i, search_term in enumerate(SEARCH_TERMS):
            try:
                listings = self.scrape_search_term(search_term)
                all_listings.extend(listings)

                # Progress update
                progress = f"({i+1}/{len(SEARCH_TERMS)})"
                Logger.info(f"Progress {progress}: {len(listings)} items found")

                # Delay between searches to be respectful
                if i < len(SEARCH_TERMS) - 1:
                    Logger.info(f"Waiting {SCRAPING.base_delay * 2} seconds...")
                    time.sleep(SCRAPING.base_delay * 2)

            except KeyboardInterrupt:
                Logger.warning("Scraping interrupted by user")
                break
            except Exception as e:
                Logger.error(f"Unexpected error: {e}")
                continue

        # Remove duplicates
        unique_listings = self.remove_duplicates(all_listings)

        # Sort by confidence
        unique_listings.sort(key=lambda x: x.confidence, reverse=True)

        # Convert to dict format
        final_results = []
        for listing in unique_listings[: SCRAPING.max_total_listings]:
            final_results.append(listing.to_dict())

        removed = len(all_listings) - len(unique_listings)
        Logger.success(
            f"Scraping complete! Found {len(final_results)} unique GBA auctions"
        )
        if removed > 0:
            Logger.info(f"Removed {removed} duplicate listings")
        Logger.info(f"Total time: {self.timer.elapsed_str()}")

        return final_results


def scrape_gba_auctions_standard() -> List[dict]:
    """Standard synchronous scraping function"""
    scraper = StandardEbayScraper()
    return scraper.scrape_all_terms()
