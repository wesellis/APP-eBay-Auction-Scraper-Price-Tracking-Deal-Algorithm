"""
Debug version to see exactly what titles eBay is returning
"""

import requests
from bs4 import BeautifulSoup

def debug_title_extraction():
    print("🔍 DEBUG: Let's see what titles eBay is actually returning...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response size: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print("Failed to get eBay page")
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find listings
        listings = soup.find_all('div', class_='s-item')
        print(f"Found {len(listings)} listings")
        
        print("\\n" + "="*80)
        print("EXTRACTING TITLES FROM FIRST 10 LISTINGS:")
        print("="*80)
        
        for i, listing in enumerate(listings[:10], 1):
            print(f"\\nListing {i}:")
            print("-" * 40)
            
            # Try multiple title extraction methods
            methods = {
                'h3.s-item__title': lambda: listing.find('h3', class_='s-item__title'),
                'h3': lambda: listing.find('h3'),
                'a.s-item__link': lambda: listing.find('a', class_='s-item__link'),
                'a': lambda: listing.find('a'),
                'span.BOLD': lambda: listing.find('span', class_='BOLD'),
                'any_text': lambda: listing
            }
            
            for method_name, method in methods.items():
                try:
                    if method_name == 'any_text':
                        # Get all text and find meaningful lines
                        all_text = listing.get_text(strip=True)
                        lines = [line.strip() for line in all_text.split('\\n') if line.strip()]
                        meaningful_lines = [line for line in lines if len(line) > 15 and 
                                          not any(skip in line.lower() for skip in ['shipping', 'bid', 'buy it now', 'time left'])]
                        if meaningful_lines:
                            print(f"  {method_name}: {meaningful_lines[0][:60]}...")
                    else:
                        elem = method()
                        if elem:
                            title = elem.get_text(strip=True)
                            if title and len(title) > 5:
                                title_clean = title.replace('Opens in a new window or tab', '').strip()
                                print(f"  {method_name}: {title_clean[:60]}...")
                except Exception as e:
                    print(f"  {method_name}: ERROR - {e}")
            
            # Show raw HTML snippet for this listing
            print(f"  Raw HTML snippet: {str(listing)[:200]}...")
        
        # Save full HTML for manual inspection
        with open('full_debug_ebay.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\\n💾 Full HTML saved to 'full_debug_ebay.html'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_title_extraction()
