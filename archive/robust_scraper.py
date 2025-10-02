"""
Ultra-robust eBay scraper with retry logic and better error handling
"""

import os
import random
import time
import webbrowser
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class RobustEbayScraper:
    """A scraper that handles timeouts and errors gracefully"""
    
    def __init__(self):
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        
    def get_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
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
    
    def fetch_with_retry(self, url, max_retries=3):
        """Fetch URL with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"🌐 Attempt {attempt + 1}/{max_retries}: Connecting to eBay...")
                
                session = requests.Session()
                session.headers.update(self.get_headers())
                
                # Longer timeout and more patience
                response = session.get(url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    print(f"✅ Success! Got {len(response.content)} bytes")
                    return response
                elif response.status_code == 429:
                    print(f"⚠️  Rate limited (429), waiting {(attempt + 1) * 10} seconds...")
                    time.sleep((attempt + 1) * 10)
                else:
                    print(f"⚠️  Status {response.status_code}, retrying...")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"💥 Unexpected error: {str(e)[:100]}...")
                if attempt < max_retries - 1:
                    time.sleep(5)
        
        print(f"❌ Failed after {max_retries} attempts")
        return None
    
    def scrape_ebay(self, search_term):
        """Scrape eBay for a specific search term"""
        url = f"https://www.ebay.com/sch/i.html?_nkw={search_term}&LH_Auction=1&_sop=1"
        
        print(f"\\n🔍 Searching: {search_term.replace('+', ' ')}")
        print(f"📡 URL: {url[:80]}...")
        
        response = self.fetch_with_retry(url)
        if not response:
            print(f"❌ Could not fetch data for {search_term}")
            return []
            
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listings - try multiple selectors
            all_listings = []
            selectors_to_try = [
                'div.s-item',
                'div[data-view]',
                '.srp-results .s-item',
                'div[class*="s-item"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    if selector.startswith('.'):
                        listings = soup.select(selector)
                    elif '[' in selector:
                        listings = soup.find_all('div', attrs={'data-view': True})
                    else:
                        listings = soup.find_all('div', class_=selector.replace('div.', ''))
                    
                    if listings:
                        all_listings = listings
                        print(f"✅ Found {len(listings)} listings with: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️  Selector {selector} failed: {e}")
                    continue
            
            if not all_listings:
                print("❌ No listings found with any selector")
                # Save HTML for debugging
                with open('debug_no_listings.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("💾 Saved debug HTML to debug_no_listings.html")
                return []
            
            # Process each listing
            results = []
            processed = 0
            
            print(f"🔄 Processing {min(len(all_listings), 15)} listings...")
            
            for i, listing in enumerate(all_listings[:15]):
                try:
                    # Extract title - try multiple ways
                    title = None
                    title_selectors = [
                        ('h3', None),
                        ('a', None), 
                        ('span', {'role': 'heading'}),
                        ('.s-item__title', None),
                        ('*', {'class': lambda x: x and 's-item__title' in str(x)})
                    ]
                    
                    for sel, attrs in title_selectors:
                        try:
                            if sel.startswith('.'):
                                elem = listing.select_one(sel)
                            else:
                                elem = listing.find(sel, attrs) if attrs else listing.find(sel)
                            
                            if elem:
                                title = elem.get_text(strip=True)
                                if title and len(title) > 10 and 'shop on ebay' not in title.lower():
                                    break
                        except:
                            continue
                    
                    if not title:
                        print(f"  {i+1:2d}. ❌ No title found")
                        continue
                    
                    # Clean title
                    title = title.replace('Opens in a new window or tab', '').strip()
                    if len(title) > 100:
                        title = title[:100] + "..."
                    
                    print(f"  {i+1:2d}. 📝 {title[:50]}...")
                    
                    # Check if GBA related
                    if self.is_gba_item(title):
                        print(f"       ✅ GBA MATCH!")
                        
                        # Get price
                        price = "Price not found"
                        try:
                            price_elem = listing.find('span', class_='s-item__price')
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                        except:
                            pass
                        
                        # Get link
                        link = "#"
                        try:
                            link_elem = listing.find('a')
                            if link_elem and link_elem.get('href'):
                                link = link_elem['href']
                                if not link.startswith('http'):
                                    link = 'https://www.ebay.com' + link
                        except:
                            pass
                        
                        # Get image
                        image = "https://via.placeholder.com/200x150?text=No+Image"
                        try:
                            img_elem = listing.find('img')
                            if img_elem and img_elem.get('src'):
                                image = img_elem['src']
                                if 's-l140' in image:
                                    image = image.replace('s-l140', 's-l300')
                        except:
                            pass
                        
                        # Get time left
                        time_left = "Ending soon"
                        try:
                            time_elem = listing.find('span', class_='s-item__time-left')
                            if time_elem:
                                time_left = time_elem.get_text(strip=True)
                        except:
                            pass
                        
                        results.append({
                            'title': title,
                            'price': price,
                            'link': link,
                            'image': image,
                            'time_left': time_left
                        })
                        
                        processed += 1
                        print(f"       💰 {price} | ⏰ {time_left}")
                    else:
                        print(f"       ❌ Not GBA related")
                
                except Exception as e:
                    print(f"  {i+1:2d}. ⚠️  Error: {str(e)[:50]}...")
                    continue
            
            print(f"📦 Found {processed} GBA items from {search_term}")
            return results
            
        except Exception as e:
            print(f"💥 Error parsing HTML: {str(e)[:100]}...")
            return []
    
    def scrape_all(self):
        """Scrape all search terms"""
        print("🚀 Starting ROBUST eBay GBA Scraper")
        print("=" * 60)
        
        # Simpler search terms
        search_terms = [
            "gameboy+advance",
            "gba+console"
        ]
        
        all_results = []
        
        for i, term in enumerate(search_terms):
            print(f"\\n📍 Search {i+1}/{len(search_terms)}")
            results = self.scrape_ebay(term)
            all_results.extend(results)
            
            # Wait between searches
            if i < len(search_terms) - 1:
                wait_time = random.randint(5, 10)
                print(f"⏳ Waiting {wait_time} seconds before next search...")
                time.sleep(wait_time)
        
        # Remove duplicates
        unique_results = []
        seen_titles = set()
        
        for result in all_results:
            title_key = result['title'].lower().replace(' ', '').replace('-', '')[:50]
            if title_key not in seen_titles:
                unique_results.append(result)
                seen_titles.add(title_key)
        
        removed = len(all_results) - len(unique_results)
        if removed > 0:
            print(f"\\n🗑️  Removed {removed} duplicates")
        
        print(f"\\n✅ Final result: {len(unique_results)} unique GBA auctions")
        return unique_results
    
    def generate_html(self, results):
        """Generate HTML results page"""
        if not results:
            cards_html = '''
            <div style="text-align: center; padding: 50px; background: rgba(255,255,255,0.1); border-radius: 15px; color: white; margin: 20px;">
                <h2>🔍 No GameBoy Advance auctions found</h2>
                <p>This could be due to:</p>
                <ul style="display: inline-block; text-align: left; margin: 20px 0;">
                    <li>No current GBA auctions ending soon</li>
                    <li>Network connectivity issues</li>
                    <li>eBay temporarily blocking requests</li>
                </ul>
                <p><strong>Try running again in 5-10 minutes!</strong></p>
            </div>
            '''
        else:
            cards = []
            for result in results:
                card = f'''
                <div style="background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin-bottom: 20px; cursor: pointer; transition: all 0.3s; break-inside: avoid;" 
                     onclick="window.open('{result['link']}', '_blank')" 
                     onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 35px rgba(0,0,0,0.2)'" 
                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'">
                    <img src="{result['image']}" style="width: 100%; height: 200px; object-fit: cover;" 
                         onerror="this.src='https://via.placeholder.com/300x200/f8f9fa/6c757d?text=Image+Not+Available'">
                    <div style="padding: 20px;">
                        <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 16px; line-height: 1.4; min-height: 3em;">{result['title']}</h3>
                        <p style="margin: 8px 0; font-size: 20px; font-weight: bold; color: #e74c3c;">{result['price']}</p>
                        <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">⏰ {result['time_left']}</p>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ecf0f1; text-align: center;">
                            <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 10px 20px; border-radius: 25px; font-size: 14px; font-weight: 600; display: inline-block;">View on eBay →</span>
                        </div>
                    </div>
                </div>
                '''
                cards.append(card)
            
            cards_html = '\\n'.join(cards)
        
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f'''
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
            font-size: clamp(2rem, 5vw, 3rem);
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
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255,255,255,0.8);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 GameBoy Advance Auctions</h1>
        <p style="font-size: 1.2rem; margin-bottom: 20px;">Ending Soon - Live Results</p>
        <div class="stats">Found {len(results)} auctions • Updated {timestamp}</div>
    </div>
    <div class="container">
        {cards_html}
    </div>
    <div class="footer">
        <p>Powered by Robust eBay Scraper • Click any card to view on eBay</p>
        <p>Data refreshed automatically • Run scraper again for latest results</p>
    </div>
</body>
</html>
        '''
        
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
        try:
            html_path = os.path.abspath(filename)
            webbrowser.open(f"file://{html_path}")
            print(f"🌐 Opening in browser...")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"💡 Please manually open: {filename}")
        
        print("\\n" + "=" * 60)
        if results:
            print(f"✅ SUCCESS! Found {len(results)} GameBoy Advance auctions")
        else:
            print("⚠️  No results found - try again in a few minutes")
        print("=" * 60)

if __name__ == "__main__":
    scraper = RobustEbayScraper()
    scraper.run()
    input("\\nPress Enter to exit...")
