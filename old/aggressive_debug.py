"""
Aggressive debug script to see what titles eBay is returning
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_ebay_listings():
    print("=" * 60)
    print("AGGRESSIVE EBAY DEBUG - EXTRACTING ALL TITLES")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&LH_Auction=1&_sop=1"
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed with status {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try all possible selectors for listings
        listing_selectors = [
            'div.s-item',
            'div[data-view]', 
            '.srp-results .s-item',
            '.srp-river-results .s-item',
            'div[class*="s-item"]'
        ]
        
        all_listings = []
        for selector in listing_selectors:
            try:
                if selector.startswith('.'):
                    items = soup.select(selector)
                else:
                    items = soup.find_all('div', attrs={'data-view': True}) if 'data-view' in selector else soup.find_all('div', class_=selector.replace('div.', ''))
                
                print(f"Selector '{selector}': {len(items)} items")
                if items:
                    all_listings = items
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        if not all_listings:
            print("No listings found with any selector!")
            return
        
        print(f"\\nProcessing {len(all_listings)} listings...")
        print("-" * 60)
        
        # Try all possible title selectors
        title_selectors = [
            'h3.s-item__title',
            'a.s-item__link', 
            'span.BOLD',
            '.s-item__title',
            'h3',
            'a[href*="itm"]',
            'span[role="heading"]'
        ]
        
        found_titles = []
        
        for i, listing in enumerate(all_listings[:20]):  # Process first 20
            title_found = False
            
            for title_sel in title_selectors:
                try:
                    if title_sel.startswith('.'):
                        title_elem = listing.select_one(title_sel)
                    elif title_sel.startswith('h3') or title_sel.startswith('a') or title_sel.startswith('span'):
                        if '.' in title_sel:
                            tag, class_name = title_sel.split('.', 1)
                            title_elem = listing.find(tag, class_=class_name)
                        elif '[' in title_sel:
                            # Handle attribute selectors like a[href*="itm"]
                            if 'href*=' in title_sel:
                                title_elem = listing.find('a', href=lambda x: x and 'itm' in x)
                            else:
                                title_elem = listing.find(title_sel.split('[')[0])
                        else:
                            title_elem = listing.find(title_sel)
                    else:
                        title_elem = listing.find(title_sel)
                    
                    if title_elem:
                        title_text = title_elem.get_text(strip=True)
                        if title_text and len(title_text) > 5:  # Valid title
                            found_titles.append({
                                'index': i+1,
                                'selector': title_sel,
                                'title': title_text
                            })
                            print(f"{i+1:2d}. [{title_sel}] {title_text[:80]}...")
                            title_found = True
                            break
                            
                except Exception as e:
                    continue
            
            if not title_found:
                # Try to extract any text from the listing
                all_text = listing.get_text(strip=True)
                if all_text:
                    lines = [line.strip() for line in all_text.split('\\n') if line.strip()]
                    if lines:
                        print(f"{i+1:2d}. [RAW TEXT] {lines[0][:80]}...")
        
        print(f"\\n" + "=" * 60)
        print(f"SUMMARY: Found {len(found_titles)} titles")
        
        # Check for GBA-related terms
        gba_terms = ['gameboy', 'game boy', 'gba', 'advance', 'nintendo']
        gba_matches = []
        
        for item in found_titles:
            title_lower = item['title'].lower()
            if any(term in title_lower for term in gba_terms):
                gba_matches.append(item)
        
        print(f"GBA-related items: {len(gba_matches)}")
        
        if gba_matches:
            print("\\nGBA-RELATED ITEMS FOUND:")
            print("-" * 40)
            for item in gba_matches:
                print(f"  • {item['title'][:60]}...")
        
        # Save debug HTML
        with open('ebay_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\\nDebug HTML saved to 'ebay_debug.html'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ebay_listings()
