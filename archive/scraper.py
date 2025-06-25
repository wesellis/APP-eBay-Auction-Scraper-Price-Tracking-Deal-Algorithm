"""
eBay scraping functionality
"""

import requests
from bs4 import BeautifulSoup
import time
from functools import lru_cache
from config import *
from utils import Logger, safe_get_text, safe_get_attribute, clean_title, upgrade_image_resolution, is_gba_related, format_price, retry_on_failure

class EbayScraper:
    """Main scraper class for eBay auctions"""
    
    def __init__(self):
        # Optimized session with connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(HEADERS)
        self.total_found = 0
        self._cache = {}  # Simple response cache
    
    def build_search_url(self, search_term):
        """Build eBay search URL for auctions ending soon"""
        base_url = "https://www.ebay.com/sch/i.html"
        params = {
            '_nkw': search_term,
            'LH_Auction': '1',  # Auctions only
            '_sop': '1'  # Sort by ending soonest
        }
        
        # Build URL manually to avoid encoding issues
        url = f"{base_url}?_nkw={search_term}&LH_Auction=1&_sop=1"
        return url
    
    def fetch_page(self, url):
        """Optimized page fetching with caching"""
        # Check cache first
        cache_key = hash(url)
        if cache_key in self._cache:
            Logger.debug("Cache hit for URL")
            return self._cache[cache_key]
        
        try:
            Logger.network(f"Fetching: {url[:80]}...")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
            
            Logger.data(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content
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
    
    def find_element_by_selectors(self, container, selectors):
        """Try multiple selectors to find an element"""
        for selector in selectors:
            if selector.startswith('.') or selector.startswith('#'):
                # CSS selector
                element = container.select_one(selector)
            else:
                # Class-based search
                if '.' in selector:
                    tag, class_name = selector.split('.', 1)
                    element = container.find(tag, class_=class_name)
                else:
                    element = container.find(selector)
            
            if element:
                return element
        return None
    
    def extract_listing_data(self, listing_soup):
        """Extract data from a single listing"""
        try:
            # Find title
            title_elem = self.find_element_by_selectors(listing_soup, SELECTORS['title'])
            title = safe_get_text(title_elem)
            title = clean_title(title, MAX_TITLE_LENGTH)
            
            # Debug: Test the filtering function directly
            if title and title != "No title":
                is_gba = is_gba_related(title, GBA_KEYWORDS)
                if is_gba:
                    Logger.success(f"GBA MATCH: {title[:50]}...")
                else:
                    Logger.debug(f"Not GBA: {title[:40]}...")
                    return None
            else:
                Logger.debug("No valid title found")
                return None
            
            # Find price
            price_elem = self.find_element_by_selectors(listing_soup, SELECTORS['price'])
            price = format_price(safe_get_text(price_elem))
            
            # Find link
            link_elem = self.find_element_by_selectors(listing_soup, SELECTORS['link'])
            link = safe_get_attribute(link_elem, 'href')
            
            # Find image
            img_elem = self.find_element_by_selectors(listing_soup, SELECTORS['image'])
            img_src = safe_get_attribute(img_elem, 'src') or safe_get_attribute(img_elem, 'data-src')
            img_src = upgrade_image_resolution(img_src, IMAGE_RESOLUTION_UPGRADE)
            
            if not img_src:
                img_src = DEFAULT_IMAGE
            
            # Find time left
            time_elem = self.find_element_by_selectors(listing_soup, SELECTORS['time_left'])
            time_left = safe_get_text(time_elem) or "Ending soon"
            
            Logger.success(f"PROCESSING: {title[:50]}... - {price}")
            
            return {
                'title': title,
                'price': price,
                'link': link,
                'image': img_src,
                'time_left': time_left
            }
            
        except Exception as e:
            Logger.warning(f"Error extracting listing data: {e}")
            return None
    
    def parse_listings(self, html_content):
        """Optimized listing parsing with better parser selection"""
        try:
            # Use lxml parser for better performance if available
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different selectors for listings
            listings = []
            for selector in SELECTORS['listings']:
                if selector.startswith('.'):
                    found = soup.select(selector)
                else:
                    found = soup.find_all('div', class_=selector.replace('div.', ''))
                
                if found:
                    listings = found
                    break
            
            Logger.data(f"Found {len(listings)} raw listings")
            
            # Debug: Show first few raw titles found
            if len(listings) > 0:
                Logger.debug("Sample raw titles found:")
                for i, listing in enumerate(listings[:5]):
                    for title_selector in SELECTORS['title']:
                        title_elem = self.find_element_by_selectors(listing, [title_selector])
                        if title_elem:
                            raw_title = title_elem.get_text(strip=True)
                            if raw_title and len(raw_title) > 5:
                                Logger.debug(f"  {i+1}. {raw_title[:70]}...")
                                break
            
            processed_listings = []
            for i, listing in enumerate(listings[:MAX_LISTINGS_PER_SEARCH]):
                # Skip sponsored/ad listings
                if listing.find(text=lambda text: text and 'SPONSORED' in text.upper()):
                    continue
                
                listing_data = self.extract_listing_data(listing)
                if listing_data:
                    processed_listings.append(listing_data)
                    Logger.success(f"Added: {listing_data['title'][:50]}...")
                
                # Small delay between processing items
                if i % 5 == 0:
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            Logger.data(f"Processed {len(processed_listings)} GBA listings")
            return processed_listings
            
        except Exception as e:
            Logger.error(f"Error parsing listings: {e}")
            return []
    
    def scrape_search_term(self, search_term):
        """Scrape listings for a single search term"""
        Logger.info(f"Searching for: {search_term.replace('+', ' ')}")
        
        try:
            url = self.build_search_url(search_term)
            html_content = retry_on_failure(
                lambda: self.fetch_page(url),
                max_retries=MAX_RETRIES,
                delay=RETRY_DELAY
            )
            
            if not html_content:
                Logger.warning(f"No content retrieved for: {search_term}")
                return []
            
            listings = self.parse_listings(html_content)
            self.total_found += len(listings)
            
            return listings
            
        except Exception as e:
            Logger.error(f"Error scraping {search_term}: {e}")
            return []
    
    def scrape_all_terms(self):
        """Scrape all configured search terms"""
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
                    Logger.info(f"Waiting {DELAY_BETWEEN_SEARCHES} seconds...")
                    time.sleep(DELAY_BETWEEN_SEARCHES)
                    
            except KeyboardInterrupt:
                Logger.warning("Scraping interrupted by user")
                break
            except Exception as e:
                Logger.error(f"Unexpected error: {e}")
                continue
        
        # Remove duplicates based on title similarity
        unique_listings = self.remove_duplicates(all_listings)
        
        Logger.success(f"Scraping complete! Found {len(unique_listings)} unique GBA auctions")
        return unique_listings
    
    def remove_duplicates(self, listings):
        """Remove duplicate listings based on title similarity"""
        if not listings:
            return listings
        
        unique_listings = []
        seen_titles = set()
        
        for listing in listings:
            # Create a simplified title for comparison
            simple_title = listing['title'].lower().replace(' ', '').replace('-', '')
            
            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                if self.titles_similar(simple_title, seen_title):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_listings.append(listing)
                seen_titles.add(simple_title)
        
        removed = len(listings) - len(unique_listings)
        if removed > 0:
            Logger.info(f"Removed {removed} duplicate listings")
        
        return unique_listings
    
    def titles_similar(self, title1, title2, threshold=0.8):
        """Check if two titles are similar (simple approach)"""
        # Simple similarity check - could be improved with more sophisticated algorithms
        shorter = min(len(title1), len(title2))
        if shorter == 0:
            return False
        
        # Count common characters
        common = sum(1 for a, b in zip(title1, title2) if a == b)
        similarity = common / shorter
        
        return similarity >= threshold
