"""
High-performance async eBay scraper with intelligent error handling and optimization
"""

import asyncio
import aiohttp
import time
import random
from typing import List, Dict, Optional, Set, Tuple
from bs4 import BeautifulSoup
from dataclasses import dataclass

try:
    from config_optimized import (
        SEARCH_TERMS, GBA_KEYWORDS, HEADER_SETS, SELECTOR_CHAINS,
        PERF, SCRAPING, IMAGE_UPGRADES, DEFAULT_IMAGE
    )
    from utils_optimized import (
        Logger, cache, performance_timer, calculate_similarity,
        is_gba_related, clean_title, upgrade_image_resolution,
        format_price, batch_process, HighPerformanceTimer,
        retry_with_backoff, memory_manager
    )
except ImportError:
    # Fallback imports for standalone operation
    from config import *
    from utils import *

@dataclass
class ListingData:
    """Optimized listing data structure"""
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

class AsyncEbayScraper:
    """High-performance async eBay scraper"""
    
    def __init__(self):
        self.session = None
        self.semaphore = asyncio.Semaphore(PERF.max_concurrent_requests)
        self.monitor = PerformanceMonitor()
        self.timer = HighPerformanceTimer()
        self._current_header_index = 0
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=PERF.connection_pool_size,
            limit_per_host=8,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=PERF.read_timeout,
            connect=PERF.connection_timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_next_headers()
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_next_headers(self) -> Dict[str, str]:
        """Rotate through header sets for variety"""
        headers = HEADER_SETS[self._current_header_index % len(HEADER_SETS)]
        self._current_header_index += 1
        return headers
    
    def _build_search_url(self, search_term: str) -> str:
        """Build optimized eBay search URL"""
        base_url = "https://www.ebay.com/sch/i.html"
        # Add random element to avoid caching
        random_param = random.randint(1000, 9999)
        return f"{base_url}?_nkw={search_term}&LH_Auction=1&_sop=1&_rnd={random_param}"
    
    async def _fetch_with_retry(self, url: str) -> Optional[str]:
        """Fetch URL with intelligent retry logic"""
        async with self.semaphore:  # Limit concurrent requests
            for attempt in range(SCRAPING.max_retries):
                try:
                    # Add jitter to prevent thundering herd
                    if attempt > 0:
                        jitter = random.uniform(0, SCRAPING.jitter_factor)
                        delay = SCRAPING.base_delay * (2 ** attempt) + jitter
                        await asyncio.sleep(min(delay, SCRAPING.max_delay))
                    
                    async with self.session.get(url) as response:
                        self.monitor.increment('requests_made')
                        
                        if response.status == 200:
                            content = await response.text()
                            return content
                        elif response.status == 429:
                            # Rate limited - wait longer
                            Logger.warning(f"Rate limited (429) - waiting...")
                            await asyncio.sleep(10)
                            continue
                        else:
                            Logger.warning(f"HTTP {response.status} for {url[:50]}...")
                            
                except asyncio.TimeoutError:
                    Logger.warning(f"Timeout on attempt {attempt + 1}")
                    self.monitor.increment('requests_failed')
                except Exception as e:
                    Logger.error(f"Request failed: {e}")
                    self.monitor.increment('requests_failed')
            
            return None
    
    def _find_element_with_selectors(self, container, selector_chain: List[str]) -> Optional[any]:
        """Optimized element finding with fallback chain"""
        for selector in selector_chain:
            try:
                if selector.startswith(('.', '#')):
                    element = container.select_one(selector)
                else:
                    parts = selector.split('.')
                    if len(parts) == 2:
                        tag, class_name = parts
                        element = container.find(tag, class_=class_name)
                    else:
                        element = container.find(selector)
                
                if element:
                    return element
            except Exception:
                continue
        return None
    
    @performance_timer
    def _extract_listing_data(self, listing_soup) -> Optional[ListingData]:
        """Optimized listing data extraction"""
        try:
            # Extract title
            title_elem = self._find_element_with_selectors(listing_soup, SELECTOR_CHAINS['title'])
            if not title_elem:
                return None
            
            raw_title = title_elem.get_text(strip=True)
            title = clean_title(raw_title, SCRAPING.max_title_length)
            
            if len(title) < SCRAPING.min_title_length:
                return None
            
            # Check GBA relevance with confidence
            is_relevant, confidence = is_gba_related(title, GBA_KEYWORDS)
            if not is_relevant:
                return None
            
            # Extract other fields
            price_elem = self._find_element_with_selectors(listing_soup, SELECTOR_CHAINS['price'])
            price = format_price(price_elem.get_text(strip=True) if price_elem else "")
            
            link_elem = self._find_element_with_selectors(listing_soup, SELECTOR_CHAINS['link'])
            link = link_elem.get('href', '') if link_elem else ''
            
            img_elem = self._find_element_with_selectors(listing_soup, SELECTOR_CHAINS['image'])
            img_src = ''
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src') or ''
            img_src = upgrade_image_resolution(img_src, IMAGE_UPGRADES) or DEFAULT_IMAGE
            
            time_elem = self._find_element_with_selectors(listing_soup, SELECTOR_CHAINS['time_left'])
            time_left = time_elem.get_text(strip=True) if time_elem else 'Ending soon'
            
            return ListingData(
                title=title,
                price=price,
                link=link,
                image=img_src,
                time_left=time_left,
                confidence=confidence
            )
            
        except Exception as e:
            Logger.debug(f"Error extracting listing: {e}")
            return None
    
    async def _parse_listings_async(self, html_content: str) -> List[ListingData]:
        """Async listing parsing with memory optimization"""
        try:
            # Use lxml parser for speed if available, fallback to html.parser
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find listing containers
            listings = []
            for selector in SELECTOR_CHAINS['listing_container']:
                if selector.startswith('.'):
                    found = soup.select(selector)
                else:
                    found = soup.find_all('div', class_=selector.replace('div.', ''))
                
                if found:
                    listings = found[:SCRAPING.max_listings_per_search]
                    break
            
            if not listings:
                Logger.warning("No listing containers found")
                return []
            
            Logger.debug(f"Found {len(listings)} raw listings")
            
            # Process listings in batches for memory efficiency
            processed_listings = []
            for batch in batch_process(listings, batch_size=5):
                batch_results = []
                for listing in batch:
                    # Skip sponsored content
                    if listing.find(text=lambda t: t and 'sponsored' in t.lower()):
                        continue
                    
                    listing_data = self._extract_listing_data(listing)
                    if listing_data:
                        batch_results.append(listing_data)
                        self.monitor.increment('listings_found')
                
                processed_listings.extend(batch_results)
                
                # Small async yield for other tasks
                await asyncio.sleep(0)
            
            Logger.success(f"Extracted {len(processed_listings)} valid GBA listings")
            return processed_listings
            
        except Exception as e:
            Logger.error(f"Error parsing listings: {e}")
            return []
    
    async def _scrape_search_term(self, search_term: str) -> List[ListingData]:
        """Scrape a single search term async"""
        self.timer.split(f"start_{search_term}")
        Logger.info(f"Searching: {search_term.replace('+', ' ')}")
        
        try:
            url = self._build_search_url(search_term)
            html_content = await self._fetch_with_retry(url)
            
            if not html_content:
                Logger.warning(f"No content for: {search_term}")
                return []
            
            listings = await self._parse_listings_async(html_content)
            
            elapsed = self.timer.split(f"end_{search_term}")
            Logger.success(f"Found {len(listings)} listings in {elapsed:.2f}s")
            
            return listings
            
        except Exception as e:
            Logger.error(f"Error scraping {search_term}: {e}")
            return []
    
    def _remove_duplicates_optimized(self, listings: List[ListingData]) -> List[ListingData]:
        """Optimized duplicate removal using hash-based detection"""
        if not listings:
            return listings
        
        seen_hashes = set()
        unique_listings = []
        
        # First pass: exact hash matches
        for listing in listings:
            if listing.hash_key not in seen_hashes:
                seen_hashes.add(listing.hash_key)
                unique_listings.append(listing)
            else:
                self.monitor.increment('duplicates_removed')
        
        # Second pass: similarity-based deduplication for remaining items
        if len(unique_listings) > 1:
            final_listings = [unique_listings[0]]  # Keep first item
            
            for listing in unique_listings[1:]:
                is_duplicate = False
                
                for existing in final_listings:
                    similarity = calculate_similarity(listing.title, existing.title)
                    if similarity > SCRAPING.similarity_threshold:
                        is_duplicate = True
                        self.monitor.increment('duplicates_removed')
                        # Keep the one with higher confidence
                        if listing.confidence > existing.confidence:
                            final_listings.remove(existing)
                            final_listings.append(listing)
                        break
                
                if not is_duplicate:
                    final_listings.append(listing)
            
            return final_listings
        
        return unique_listings
    
    async def scrape_all_terms(self) -> List[Dict]:
        """Main scraping method - async version"""
        self.timer.start()
        self.monitor.start()
        
        Logger.info("🚀 Starting optimized async eBay scrape")
        Logger.info("=" * 50)
        
        try:
            # Create tasks for all search terms
            tasks = [
                self._scrape_search_term(term) 
                for term in SEARCH_TERMS
            ]
            
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
            unique_listings = self._remove_duplicates_optimized(all_listings)
            
            # Sort by confidence score
            unique_listings.sort(key=lambda x: x.confidence, reverse=True)
            
            # Convert to dict format for compatibility
            final_results = []
            for listing in unique_listings[:SCRAPING.max_total_listings]:
                final_results.append({
                    'title': listing.title,
                    'price': listing.price,
                    'link': listing.link,
                    'image': listing.image,
                    'time_left': listing.time_left,
                    'confidence': listing.confidence
                })
            
            # Performance summary
            summary = self.monitor.get_summary()
            Logger.success(f"✅ Scraping complete! Found {len(final_results)} unique auctions")
            Logger.info(f"📊 Performance: {summary['requests_made']} requests, "
                       f"{summary['duplicates_removed']} duplicates removed, "
                       f"{self.timer.elapsed_str()} total time")
            
            return final_results
            
        except Exception as e:
            Logger.error(f"Scraping failed: {e}")
            return []
        finally:
            # Cleanup
            memory_manager.cleanup()

async def scrape_gba_auctions() -> List[Dict]:
    """Main async scraping function"""
    async with AsyncEbayScraper() as scraper:
        return await scraper.scrape_all_terms()

# Backward compatibility function for sync usage
def scrape_auctions_sync() -> List[Dict]:
    """Synchronous wrapper for async scraping"""
    try:
        return asyncio.run(scrape_gba_auctions())
    except Exception as e:
        Logger.error(f"Async scraping failed: {e}")
        return []
