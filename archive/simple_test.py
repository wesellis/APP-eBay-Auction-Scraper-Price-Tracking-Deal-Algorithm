"""
Simple test to find ANY titles from eBay and show GBA detection
"""

import requests
from bs4 import BeautifulSoup


def simple_test():
    print("🧪 SIMPLE TEST: Finding ANY titles and testing GBA detection")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ Connected to eBay: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='s-item')
        print(f"📦 Found {len(listings)} listings")
        
        print("\\n🔍 EXAMINING FIRST 5 LISTINGS:")
        print("=" * 60)
        
        for i, listing in enumerate(listings[:5], 1):
            print(f"\\nListing {i}:")
            
            # Try to get ANY text from this listing
            all_text = listing.get_text()
            
            # Find the first substantial line
            lines = [line.strip() for line in all_text.split('\\n') if line.strip()]
            title_candidates = [line for line in lines if len(line) > 10]
            
            if title_candidates:
                title = title_candidates[0]
                print(f"  Title: {title[:80]}...")
                
                # Test GBA detection
                title_lower = title.lower()
                gba_keywords = ['gameboy advance', 'game boy advance', 'gba', 'advance sp', 'gba sp']
                
                is_gba = any(keyword in title_lower for keyword in gba_keywords)
                print(f"  Is GBA? {is_gba}")
                
                if is_gba:
                    print(f"  🎮 GBA DETECTED!")
                else:
                    # Show why it wasn't detected
                    found_keywords = [kw for kw in gba_keywords if kw in title_lower]
                    print(f"  Keywords found: {found_keywords}")
            else:
                print(f"  No substantial text found")
                print(f"  Raw text sample: {all_text[:100]}...")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test()
