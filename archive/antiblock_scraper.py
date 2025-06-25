"""
Anti-blocking GBA scraper that handles 503 errors and uses multiple strategies
"""

import requests
from bs4 import BeautifulSoup
import time
import webbrowser
import os
from datetime import datetime
import random

class AntiBlockGBAScraper:
    """GBA scraper with anti-blocking measures"""
    
    def __init__(self):
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        self.session = requests.Session()
        
    def get_headers(self):
        """Get random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        }
        
    def try_request_with_backoff(self, url, max_attempts=3):
        """Try request with exponential backoff"""
        for attempt in range(max_attempts):
            try:
                print(f"🌐 Attempt {attempt + 1}/{max_attempts}: Connecting...")
                
                # Use fresh headers each time
                self.session.headers.update(self.get_headers())
                
                # Add random delay to seem more human
                if attempt > 0:
                    delay = (2 ** attempt) + random.uniform(1, 3)
                    print(f"⏳ Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
                
                response = self.session.get(url, timeout=30, allow_redirects=True)
                
                print(f"📡 Status: {response.status_code}")
                print(f"📊 Response size: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 503:
                    print("⚠️  eBay is blocking us (503) - trying different approach...")
                elif response.status_code == 429:
                    print("⚠️  Rate limited (429) - waiting longer...")
                    time.sleep(10)
                else:
                    print(f"⚠️  Unexpected status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                print(f"🔌 Connection error on attempt {attempt + 1}")
            except Exception as e:
                print(f"💥 Error: {str(e)[:100]}...")
                
        return None
    
    def try_multiple_search_strategies(self):
        """Try different search URLs to avoid blocking"""
        
        strategies = [
            {
                'name': 'Direct GBA Auction Search',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&LH_Auction=1&_sop=1'
            },
            {
                'name': 'Broader GBA Search (any format)',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=1'
            },
            {
                'name': 'GBA Console Search',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gba+console&_sop=1'
            },
            {
                'name': 'Nintendo GBA Search',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=nintendo+gba&_sop=1'
            }
        ]
        
        for i, strategy in enumerate(strategies):
            print(f"\\n📍 Strategy {i+1}/{len(strategies)}: {strategy['name']}")
            print(f"🔗 URL: {strategy['url']}")
            
            response = self.try_request_with_backoff(strategy['url'])
            
            if response:
                results = self.parse_response(response, strategy['name'])
                if results:
                    print(f"✅ Success with {strategy['name']}!")
                    return results
                else:
                    print(f"❌ No GBA items found with {strategy['name']}")
            else:
                print(f"❌ Failed to get response for {strategy['name']}")
            
            # Wait between strategies
            if i < len(strategies) - 1:
                wait_time = random.uniform(5, 10)
                print(f"⏳ Waiting {wait_time:.1f} seconds before next strategy...")
                time.sleep(wait_time)
        
        return []
    
    def is_gba_item(self, title):
        """Check if title is GBA related"""
        if not title or len(title) < 5:
            return False
            
        title_lower = title.lower()
        
        # Skip obvious filters and navigation
        skip_terms = ['filter', 'apply', 'brand', 'condition', 'price range', 'buying format', 'category', 'shop on ebay']
        if any(term in title_lower for term in skip_terms):
            return False
            
        # GBA keywords
        gba_keywords = [
            'gameboy advance', 'game boy advance', 'gba', 'advance sp', 'gba sp',
            'gameboy sp', 'game boy sp', 'nintendo advance', 'ags-001', 'ags-101'
        ]
        
        return any(keyword in title_lower for keyword in gba_keywords)
    
    def extract_auction_info(self, listing):
        """Extract auction information with multiple fallback methods"""
        result = {
            'title': None,
            'price': 'Price not found',
            'link': '#',
            'image': 'https://via.placeholder.com/200x150/333/fff?text=GBA',
            'time_left': 'Time unknown',
            'is_auction': False
        }
        
        try:
            # Try multiple methods to extract title
            title_methods = [
                lambda: listing.find('h3', class_='s-item__title'),
                lambda: listing.find('h3'),
                lambda: listing.find('a', class_='s-item__link'),
                lambda: listing.select_one('[data-testid*="title"]'),
                lambda: listing.find('span', class_='BOLD')
            ]
            
            for method in title_methods:
                try:
                    elem = method()
                    if elem:
                        title = elem.get_text(strip=True)
                        if title and len(title) > 10:
                            # Clean title
                            title = title.replace('Opens in a new window or tab', '').strip()
                            title = title.replace('New Listing', '').strip()
                            if len(title) > 100:
                                title = title[:100] + "..."
                            result['title'] = title
                            break
                except:
                    continue
            
            # If still no title, try getting any substantial text
            if not result['title']:
                text_content = listing.get_text(strip=True)
                lines = [line.strip() for line in text_content.split('\\n') if line.strip()]
                for line in lines[:5]:
                    if len(line) > 15 and not any(skip in line.lower() for skip in ['shipping', 'buy it now', 'bid', 'time left']):
                        result['title'] = line[:100]
                        break
            
            # Extract price
            try:
                price_elem = listing.find('span', class_='s-item__price')
                if price_elem:
                    result['price'] = price_elem.get_text(strip=True)
            except:
                pass
            
            # Extract link
            try:
                link_elem = listing.find('a')
                if link_elem and link_elem.get('href'):
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = 'https://www.ebay.com' + link
                    result['link'] = link
            except:
                pass
            
            # Extract image
            try:
                img_elem = listing.find('img')
                if img_elem and img_elem.get('src'):
                    image = img_elem['src']
                    if 's-l140' in image:
                        image = image.replace('s-l140', 's-l300')
                    result['image'] = image
            except:
                pass
            
            # Extract time left
            try:
                time_elem = listing.find('span', class_='s-item__time-left')
                if time_elem:
                    result['time_left'] = time_elem.get_text(strip=True)
            except:
                pass
            
            # Check if it's an auction
            listing_text = listing.get_text().lower()
            result['is_auction'] = 'bid' in listing_text or 'auction' in listing_text
            
        except Exception as e:
            pass
            
        return result
    
    def parse_response(self, response, strategy_name):
        """Parse eBay response and extract GBA items"""
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save for debugging
            with open(f'debug_{strategy_name.lower().replace(" ", "_")}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Find listings with multiple selectors
            listings = []
            selectors = [
                'div.s-item',
                'div[data-view]',
                '.srp-results .s-item',
                'div[class*="s-item"]'
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith('.'):
                        found = soup.select(selector)
                    elif '[' in selector:
                        found = soup.find_all('div', attrs={'data-view': True})
                    else:
                        found = soup.find_all('div', class_=lambda x: x and 's-item' in str(x))
                    
                    if found and len(found) > 3:
                        listings = found
                        print(f"✅ Found {len(listings)} listings using: {selector}")
                        break
                except:
                    continue
            
            if not listings:
                print("❌ No listings found with any selector")
                return []
            
            # Process listings
            results = []
            print(f"\\n🔄 Processing {min(len(listings), 20)} listings...")
            
            for i, listing in enumerate(listings[:20]):
                try:
                    info = self.extract_auction_info(listing)
                    
                    if info['title'] and self.is_gba_item(info['title']):
                        results.append(info)
                        auction_type = "🔨 AUCTION" if info['is_auction'] else "💳 BUY NOW"
                        print(f"  ✅ GBA FOUND: {info['title'][:50]}...")
                        print(f"     {auction_type} | {info['price']} | ⏰ {info['time_left']}")
                    
                except Exception as e:
                    continue
            
            print(f"\\n📊 Found {len(results)} GBA items total")
            return results
            
        except Exception as e:
            print(f"💥 Error parsing response: {e}")
            return []
    
    def generate_results_html(self, results):
        """Generate HTML for results"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        if not results:
            content = '''
            <div style="text-align: center; padding: 60px; background: #2d2d2d; border-radius: 20px; color: white;">
                <h2>🚫 eBay is Blocking Our Requests</h2>
                <p style="font-size: 18px; margin: 20px 0;">This is temporary! eBay uses anti-bot protection.</p>
                <div style="background: #ff6b6b; padding: 20px; border-radius: 15px; margin: 30px 0;">
                    <h3 style="margin: 0 0 10px 0;">💡 What to do:</h3>
                    <ul style="text-align: left; display: inline-block;">
                        <li>Wait 10-15 minutes and try again</li>
                        <li>Try using a VPN if available</li>
                        <li>eBay blocking is temporary and will reset</li>
                    </ul>
                </div>
                <p>GBA auctions are still there - we just need to wait for access!</p>
            </div>
            '''
        else:
            cards = []
            auctions = [r for r in results if r['is_auction']]
            buy_nows = [r for r in results if not r['is_auction']]
            
            # Sort auctions by urgency (shorter time = more urgent)
            all_items = auctions + buy_nows
            
            for i, item in enumerate(all_items, 1):
                auction_badge = "🔨 AUCTION" if item['is_auction'] else "💳 BUY IT NOW"
                badge_color = "#ff6b6b" if item['is_auction'] else "#4caf50"
                
                card = f'''
                <div style="background: #2d2d2d; border-radius: 15px; overflow: hidden; margin-bottom: 20px; cursor: pointer; transition: all 0.3s; border: 2px solid #444;" 
                     onclick="window.open('{item['link']}', '_blank')" 
                     onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='{badge_color}'" 
                     onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='#444'">
                    
                    <div style="display: flex; padding: 20px;">
                        <img src="{item['image']}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 10px; margin-right: 20px;" 
                             onerror="this.src='https://via.placeholder.com/120x120/444/fff?text=GBA'">
                        
                        <div style="flex: 1;">
                            <div style="background: {badge_color}; color: white; padding: 5px 12px; border-radius: 15px; display: inline-block; font-size: 12px; font-weight: bold; margin-bottom: 10px;">
                                {auction_badge}
                            </div>
                            <h3 style="margin: 0 0 10px 0; color: #fff; font-size: 16px; line-height: 1.4;">{item['title']}</h3>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 20px; font-weight: bold; color: {badge_color};">{item['price']}</div>
                                <div style="color: #ccc; font-size: 14px;">⏰ {item['time_left']}</div>
                            </div>
                        </div>
                    </div>
                </div>
                '''
                cards.append(card)
            
            content = '\\n'.join(cards)
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GBA Items Found - Anti-Block Scraper</title>
    <style>
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #1a1a1a;
            color: #fff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 20px;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats {{
            background: rgba(255,255,255,0.1);
            padding: 15px 25px;
            border-radius: 25px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Anti-Block GBA Scraper</h1>
            <p style="font-size: 1.2rem; margin-bottom: 20px;">Fighting eBay's blocking to find your GBA items!</p>
            <div class="stats">Found {len(results)} items • {timestamp}</div>
        </div>
        
        {content}
        
        <div style="text-align: center; margin-top: 40px; padding: 20px; background: #2d2d2d; border-radius: 15px; color: #ccc;">
            <p>🛡️ This scraper uses anti-blocking techniques • Click any item to view on eBay</p>
            <p>If blocked, wait 10-15 minutes and try again - it's temporary!</p>
        </div>
    </div>
</body>
</html>
        '''
        
        return html
    
    def run(self):
        """Main execution"""
        print("🛡️ Starting Anti-Block GBA Scraper")
        print("🎯 Fighting eBay's blocking to find GBA items!")
        print("=" * 60)
        
        results = self.try_multiple_search_strategies()
        
        print("\\n🎨 Generating results HTML...")
        html = self.generate_results_html(results)
        
        filename = 'gba_auctions.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"💾 Saved: {filename}")
        
        # Open in browser
        try:
            html_path = os.path.abspath(filename)
            webbrowser.open(f"file://{html_path}")
            print(f"🌐 Opening in browser...")
        except:
            pass
        
        print("\\n" + "=" * 60)
        if results:
            auctions = len([r for r in results if r['is_auction']])
            buy_nows = len(results) - auctions
            print(f"✅ SUCCESS! Found {len(results)} GBA items")
            print(f"🔨 {auctions} auctions | 💳 {buy_nows} Buy It Now")
        else:
            print("🚫 eBay is currently blocking requests")
            print("💡 This is temporary - try again in 10-15 minutes")
        print("=" * 60)

if __name__ == "__main__":
    scraper = AntiBlockGBAScraper()
    scraper.run()
    input("\\nPress Enter to exit...")
