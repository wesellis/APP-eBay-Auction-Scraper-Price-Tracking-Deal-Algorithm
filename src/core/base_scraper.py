"""
Base scraper class with common functionality
"""

import random
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from config import (DEFAULT_IMAGE, GBA_KEYWORDS, IMAGE_UPGRADES, SCRAPING,
                    SELECTOR_CHAINS)
from utils import (Logger, calculate_similarity, clean_title, format_price,
                   is_gba_related)

from .models import ListingData


class BaseScraper:
    """Base scraper with common functionality"""

    def __init__(self):
        self._current_header_index = 0

    def build_search_url(self, search_term: str) -> str:
        """Build eBay search URL with randomization"""
        base_url = "https://www.ebay.com/sch/i.html"
        # Add random element to avoid caching
        random_param = random.randint(1000, 9999)
        return f"{base_url}?_nkw={search_term}&LH_Auction=1&_sop=1&_rnd={random_param}"

    def find_element_with_selectors(self, container, selector_chain: List[str]):
        """Find element using fallback selector chain"""
        for selector in selector_chain:
            try:
                if selector.startswith((".", "#")):
                    element = container.select_one(selector)
                else:
                    parts = selector.split(".")
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

    def extract_listing_data(self, listing_soup) -> Optional[ListingData]:
        """Extract data from a single listing with confidence scoring"""
        try:
            # Extract title
            title_elem = self.find_element_with_selectors(
                listing_soup, SELECTOR_CHAINS["title"]
            )
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
            price_elem = self.find_element_with_selectors(
                listing_soup, SELECTOR_CHAINS["price"]
            )
            price = format_price(price_elem.get_text(strip=True) if price_elem else "")

            link_elem = self.find_element_with_selectors(
                listing_soup, SELECTOR_CHAINS["link"]
            )
            link = link_elem.get("href", "") if link_elem else ""

            img_elem = self.find_element_with_selectors(
                listing_soup, SELECTOR_CHAINS["image"]
            )
            img_src = ""
            if img_elem:
                img_src = img_elem.get("src") or img_elem.get("data-src") or ""

            # Upgrade image resolution
            from utils.text_processing import upgrade_image_resolution

            img_src = upgrade_image_resolution(img_src, IMAGE_UPGRADES) or DEFAULT_IMAGE

            time_elem = self.find_element_with_selectors(
                listing_soup, SELECTOR_CHAINS["time_left"]
            )
            time_left = time_elem.get_text(strip=True) if time_elem else "Ending soon"

            return ListingData(
                title=title,
                price=price,
                link=link,
                image=img_src,
                time_left=time_left,
                confidence=confidence,
            )

        except Exception as e:
            Logger.debug(f"Error extracting listing: {e}")
            return None

    def parse_listings_from_html(self, html_content: str) -> List[ListingData]:
        """Parse listings from HTML content"""
        try:
            # Use lxml parser for speed if available
            try:
                soup = BeautifulSoup(html_content, "lxml")
            except:
                soup = BeautifulSoup(html_content, "html.parser")

            # Find listing containers
            listings = []
            for selector in SELECTOR_CHAINS["listing_container"]:
                if selector.startswith("."):
                    found = soup.select(selector)
                else:
                    found = soup.find_all("div", class_=selector.replace("div.", ""))

                if found:
                    listings = found[: SCRAPING.max_listings_per_search]
                    break

            if not listings:
                Logger.warning("No listing containers found")
                return []

            Logger.debug(f"Found {len(listings)} raw listings")

            # Process listings
            processed_listings = []
            for listing in listings:
                # Skip sponsored content
                if listing.find(text=lambda t: t and "sponsored" in t.lower()):
                    continue

                listing_data = self.extract_listing_data(listing)
                if listing_data:
                    processed_listings.append(listing_data)

            Logger.success(f"Extracted {len(processed_listings)} valid GBA listings")
            return processed_listings

        except Exception as e:
            Logger.error(f"Error parsing listings: {e}")
            return []

    def remove_duplicates(self, listings: List[ListingData]) -> List[ListingData]:
        """Remove duplicates using hash and similarity detection"""
        if not listings:
            return listings

        seen_hashes = set()
        unique_listings = []

        # First pass: exact hash matches
        for listing in listings:
            if listing.hash_key not in seen_hashes:
                seen_hashes.add(listing.hash_key)
                unique_listings.append(listing)

        # Second pass: similarity-based deduplication
        if len(unique_listings) > 1:
            final_listings = [unique_listings[0]]

            for listing in unique_listings[1:]:
                is_duplicate = False

                for existing in final_listings:
                    similarity = calculate_similarity(listing.title, existing.title)
                    if similarity > SCRAPING.similarity_threshold:
                        is_duplicate = True
                        # Keep the one with higher confidence
                        if listing.confidence > existing.confidence:
                            final_listings.remove(existing)
                            final_listings.append(listing)
                        break

                if not is_duplicate:
                    final_listings.append(listing)

            return final_listings

        return unique_listings
