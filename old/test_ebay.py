"""
Simple test script to see what eBay is returning
"""

import requests
from bs4 import BeautifulSoup

def test_ebay_response():
    print("Testing eBay response...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Simple search
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&LH_Auction=1&_sop=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all possible listing containers
            possible_selectors = [
                'div.s-item',
                'div[data-view]',
                '.srp-results .s-item',
                '.srp-results div'
            ]
            
            for selector in possible_selectors:
                if selector.startswith('.'):
                    items = soup.select(selector)
                else:
                    items = soup.find_all('div', class_=selector.replace('div.', ''))
                
                print(f"Selector '{selector}': Found {len(items)} items")
                
                if items:
                    # Print first few titles
                    for i, item in enumerate(items[:5]):
                        title_selectors = ['h3', 'a', 'span.BOLD', '.s-item__title']
                        title = None
                        
                        for title_sel in title_selectors:
                            if title_sel.startswith('.'):
                                title_elem = item.select_one(title_sel)
                            else:
                                title_elem = item.find(title_sel)
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                break
                        
                        if title:
                            print(f"  {i+1}. {title[:80]}...")
                    break
            
            # Save raw HTML for inspection
            with open('ebay_raw.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Raw HTML saved to 'ebay_raw.html'")
            
        else:
            print(f"Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ebay_response()
