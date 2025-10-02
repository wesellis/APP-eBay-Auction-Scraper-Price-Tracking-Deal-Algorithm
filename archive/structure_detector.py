"""
Modern eBay structure detector - finds current selectors that actually work
"""

import re

import requests
from bs4 import BeautifulSoup


def find_current_ebay_structure():
    print("🕵️ DETECTING CURRENT EBAY HTML STRUCTURE...")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📡 Status: {response.status_code}")
        print(f"📊 Response size: {len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"❌ Failed with status {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save the raw HTML for inspection
        with open('current_ebay_structure.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 Saved full HTML to 'current_ebay_structure.html'")
        
        # Try many different selectors to find listings
        selectors_to_try = [
            ('div.s-item', 'Standard s-item divs'),
            ('div[data-view]', 'Data-view divs'),
            ('li.s-item', 'List item s-items'),
            ('.srp-results div', 'SRP results divs'),
            ('[data-testid*="item"]', 'Test ID items'),
            ('.item', 'Generic item class'),
            ('div[class*="item"]', 'Any div with item in class'),
            ('li[class*="item"]', 'Any li with item in class'),
            ('[id*="item"]', 'Any element with item in ID'),
            ('div.listing', 'Listing divs'),
            ('article', 'Article elements'),
            ('div[data-id]', 'Elements with data-id'),
            ('div.result', 'Result divs')
        ]
        
        print(f"\\n🔍 TESTING {len(selectors_to_try)} DIFFERENT SELECTORS:")
        print("-" * 60)
        
        for selector, description in selectors_to_try:
            try:
                if selector.startswith('[') and not selector.startswith('.'):
                    # Attribute selector
                    if 'data-view' in selector:
                        elements = soup.find_all('div', attrs={'data-view': True})
                    elif 'data-testid' in selector:
                        elements = soup.find_all(attrs={'data-testid': re.compile(r'item')})
                    elif 'data-id' in selector:
                        elements = soup.find_all('div', attrs={'data-id': True})
                    elif 'id*=' in selector:
                        elements = soup.find_all(attrs={'id': re.compile(r'item')})
                    else:
                        elements = soup.select(selector)
                elif selector.startswith('.'):
                    elements = soup.select(selector)
                else:
                    # Class-based search
                    if 'class*=' in selector:
                        tag = selector.split('[')[0]
                        if tag == 'div':
                            elements = soup.find_all('div', class_=re.compile(r'item'))
                        elif tag == 'li':
                            elements = soup.find_all('li', class_=re.compile(r'item'))
                        else:
                            elements = []
                    else:
                        parts = selector.split('.')
                        if len(parts) == 2:
                            tag, class_name = parts
                            elements = soup.find_all(tag, class_=class_name)
                        else:
                            elements = soup.find_all(selector)
                
                print(f"  {selector:<25} | {description:<25} | Found: {len(elements)}")
                
                # If we found some elements, let's examine them
                if elements and len(elements) > 5:
                    print(f"    ✅ PROMISING! Let's examine first few...")
                    
                    for i, elem in enumerate(elements[:3], 1):
                        # Try to extract meaningful text
                        text = elem.get_text(strip=True)
                        if text:
                            lines = [line.strip() for line in text.split('\\n') if line.strip() and len(line) > 10]
                            if lines:
                                first_line = lines[0]
                                print(f"      Item {i}: {first_line[:60]}...")
                                
                                # Check if it looks like a GBA item
                                if any(gba in first_line.lower() for gba in ['gameboy', 'gba', 'advance']):
                                    print(f"        🎮 CONTAINS GBA KEYWORDS!")
                    print()
                    
            except Exception as e:
                print(f"  {selector:<25} | ERROR: {str(e)[:30]}...")
        
        # Also try to find any links that might be items
        print("\\n🔗 LOOKING FOR ITEM LINKS:")
        print("-" * 30)
        
        all_links = soup.find_all('a', href=True)
        item_links = [link for link in all_links if 'itm' in link.get('href', '') or '/i/' in link.get('href', '')]
        
        print(f"Found {len(item_links)} potential item links")
        
        for i, link in enumerate(item_links[:5], 1):
            link_text = link.get_text(strip=True)
            if link_text and len(link_text) > 10:
                print(f"  Link {i}: {link_text[:60]}...")
                if any(gba in link_text.lower() for gba in ['gameboy', 'gba', 'advance']):
                    print(f"    🎮 GBA LINK FOUND!")
        
        # Look for any structured data
        print("\\n📊 LOOKING FOR STRUCTURED DATA:")
        print("-" * 35)
        
        # JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        print(f"JSON-LD scripts: {len(json_scripts)}")
        
        # Data attributes
        data_attrs = soup.find_all(attrs=lambda x: x and any(attr.startswith('data-') for attr in x.keys()))
        print(f"Elements with data attributes: {len(data_attrs)}")
        
        # Try to find the main content area
        main_areas = [
            soup.find('main'),
            soup.find('div', id='mainContent'),
            soup.find('div', class_=re.compile(r'results')),
            soup.find('div', class_=re.compile(r'listing')),
            soup.find('section')
        ]
        
        for i, area in enumerate(main_areas):
            if area:
                print(f"Main area {i+1}: {area.name} with {len(area.find_all())} child elements")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    find_current_ebay_structure()
