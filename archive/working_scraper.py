"""
Simplified, working eBay scraper that actually processes listings
"""

import os
import time
import webbrowser
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class WorkingEbayScraper:
    """A scraper that actually works"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def is_gba_item(self, title):
        """Check if title is GBA related"""
        if not title:
            return False
            
        title_lower = title.lower()
        gba_keywords = [
            'gameboy advance', 'game boy advance', 'gba', 'advance sp',
            'gba sp', 'gameboy sp', 'game boy sp', 'nintendo advance',
            'ags-001', 'ags-101', 'ags001', 'ags101'
        ]
        
        for keyword in gba_keywords:
            if keyword in title_lower:
                return True
                
        # Special case: nintendo + (advance or sp)
        if 'nintendo' in title_lower and ('advance' in title_lower or ' sp ' in title_lower):
            return True
            
        return False
    
    def scrape_ebay(self, search_term):
        """Scrape eBay for a specific search term"""
        url = f"https://www.ebay.com/sch/i.html?_nkw={search_term}&LH_Auction=1&_sop=1"
        
        print(f"🔍 Searching: {search_term.replace('+', ' ')}")
        print(f"📡 URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Failed: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listings - try multiple selectors
            all_listings = []
            selectors_to_try = [
                'div.s-item',
                'div[data-view*="mi"]',
                '.srp-results .s-item'
            ]
            
            for selector in selectors_to_try:
                if selector.startswith('.'):
                    listings = soup.select(selector)
                else:
                    listings = soup.find_all('div', class_=selector.replace('div.', ''))
                
                if listings:
                    all_listings = listings
                    print(f"✅ Found {len(listings)} listings with selector: {selector}")
                    break
            
            if not all_listings:
                print("❌ No listings found with any selector")
                return []
            
            # Process each listing
            results = []
            processed = 0
            
            for i, listing in enumerate(all_listings[:20]):  # Process first 20
                try:
                    # Extract title - try multiple ways
                    title = None
                    title_selectors = ['h3', 'a', 'span[role="heading"]']
                    
                    for sel in title_selectors:
                        if sel.startswith('span'):
                            elem = listing.find('span', role='heading')
                        else:
                            elem = listing.find(sel)
                        
                        if elem:
                            title = elem.get_text(strip=True)
                            if title and len(title) > 10:
                                break
                    
                    if not title:
                        continue
                    
                    # Clean title
                    title = title.replace('Opens in a new window or tab', '').strip()
                    if len(title) > 100:
                        title = title[:100] + "..."
                    
                    print(f"  📝 {i+1}. {title[:60]}...")
                    
                    # Check if GBA related
                    if self.is_gba_item(title):
                        print(f"    ✅ GBA MATCH!")
                        
                        # Get price
                        price = "Price not found"
                        price_elem = listing.find('span', class_='s-item__price')
                        if price_elem:
                            price = price_elem.get_text(strip=True)
                        
                        # Get link
                        link = "#"
                        link_elem = listing.find('a')
                        if link_elem and link_elem.get('href'):
                            link = link_elem['href']
                        
                        # Get image
                        image = "https://via.placeholder.com/200x150?text=No+Image"
                        img_elem = listing.find('img')
                        if img_elem and img_elem.get('src'):
                            image = img_elem['src']
                            # Upgrade image quality
                            if 's-l140' in image:
                                image = image.replace('s-l140', 's-l300')
                        
                        # Get time left
                        time_left = "Ending soon"
                        time_elem = listing.find('span', class_='s-item__time-left')
                        if time_elem:
                            time_left = time_elem.get_text(strip=True)
                        
                        results.append({
                            'title': title,
                            'price': price,
                            'link': link,
                            'image': image,
                            'time_left': time_left
                        })
                        
                        processed += 1
                        print(f"    💰 {price} | ⏰ {time_left}")
                    else:
                        print(f"    ❌ Not GBA related")
                
                except Exception as e:
                    print(f"    ⚠️  Error processing listing {i+1}: {e}")
                    continue
            
            print(f"📦 Found {processed} GBA items from {search_term}")
            return results
            
        except Exception as e:
            print(f"💥 Error scraping {search_term}: {e}")
            return []
    
    def scrape_all(self):
        """Scrape all search terms"""
        print("🚀 Starting WORKING eBay GBA Scraper")
        print("=" * 60)
        
        search_terms = [
            "gameboy+advance",
            "game+boy+advance+sp", 
            "gba+console"
        ]
        
        all_results = []
        
        for term in search_terms:
            results = self.scrape_ebay(term)
            all_results.extend(results)
            
            if len(search_terms) > 1:
                print("⏳ Waiting 3 seconds...")
                time.sleep(3)
        
        # Remove duplicates
        unique_results = []
        seen_titles = set()
        
        for result in all_results:
            title_key = result['title'].lower().replace(' ', '')[:50]
            if title_key not in seen_titles:
                unique_results.append(result)
                seen_titles.add(title_key)
        
        removed = len(all_results) - len(unique_results)
        if removed > 0:
            print(f"🗑️  Removed {removed} duplicates")
        
        print(f"✅ Final result: {len(unique_results)} unique GBA auctions")
        return unique_results
    
    def generate_html(self, results):
        """Generate simple but beautiful HTML"""
        if not results:
            cards_html = """
            <div style="text-align: center; padding: 50px; background: rgba(255,255,255,0.1); border-radius: 15px; color: white;">
                <h2>No GameBoy Advance auctions found</h2>
                <p>Try running again in a few minutes!</p>
            </div>
            """
        else:
            cards = []
            for result in results:
                card = f"""
                <div style="background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin-bottom: 20px; cursor: pointer; transition: transform 0.3s;" 
                     onclick="window.open('{result['link']}', '_blank')" 
                     onmouseover="this.style.transform='translateY(-5px)'" 
                     onmouseout="this.style.transform='translateY(0)'">
                    <img src="{result['image']}" style="width: 100%; height: 200px; object-fit: cover;">
                    <div style="padding: 20px;">
                        <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 16px; line-height: 1.4;">{result['title']}</h3>
                        <p style="margin: 5px 0; font-size: 18px; font-weight: bold; color: #e74c3c;">{result['price']}</p>
                        <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">{result['time_left']}</p>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ecf0f1;">
                            <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600;">View on eBay →</span>
                        </div>
                    </div>
                </div>
                """
                cards.append(card)
            
            cards_html = '\\n'.join(cards)
        
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameBoy Advance Auctions</title>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            columns: 4;
            column-gap: 25px;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats {{
            background: rgba(255,255,255,0.1);
            padding: 15px 25px;
            border-radius: 25px;
            display: inline-block;
            backdrop-filter: blur(10px);
        }}
        @media (max-width: 1200px) {{ .container {{ columns: 3; }} }}
        @media (max-width: 900px) {{ .container {{ columns: 2; }} }}
        @media (max-width: 600px) {{ .container {{ columns: 1; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 GameBoy Advance Auctions</h1>
        <div class="stats">Found {len(results)} auctions • Updated {timestamp}</div>
    </div>
    <div class="container">
        {cards_html}
    </div>
    <div style="text-align: center; margin-top: 40px; color: rgba(255,255,255,0.8);">
        <p>Powered by Working eBay Scraper • Click any card to view on eBay</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def run(self):
        """Main execution"""
        results = self.scrape_all()
        
        print("\\n🎨 Generating HTML...")
        html = self.generate_html(results)
        
        filename = 'gba_auctions.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"💾 Saved: {filename}")
        
        # Open in browser
        html_path = os.path.abspath(filename)
        webbrowser.open(f"file://{html_path}")
        print(f"🌐 Opening in browser...")
        
        print("\\n" + "=" * 60)
        print(f"✅ COMPLETE! Found {len(results)} GameBoy Advance auctions")
        print("=" * 60)

if __name__ == "__main__":
    scraper = WorkingEbayScraper()
    scraper.run()
    input("\\nPress Enter to exit...")
