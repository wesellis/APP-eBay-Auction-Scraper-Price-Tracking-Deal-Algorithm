"""
Back to basics - focused on finding GBA auctions ending soon that actually work
"""

import os
import random
import time
import webbrowser
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class WorkingGBAScraperFocused:
    """Simple scraper focused on auctions ending soon"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def is_gba_item(self, title):
        """Simple GBA detection"""
        if not title:
            return False
            
        title_lower = title.lower()
        
        # Skip obvious filters
        if any(word in title_lower for word in ['filter', 'apply', 'brand', 'condition']):
            return False
            
        # GBA keywords
        gba_words = ['gameboy advance', 'game boy advance', 'gba', 'advance sp', 'gba sp']
        return any(word in title_lower for word in gba_words)
    
    def scrape_ending_soon(self):
        """Scrape auctions ending soonest"""
        print("🎯 Focusing on GBA AUCTIONS ENDING SOON")
        print("=" * 50)
        
        # Direct auction search ending soonest
        url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&LH_Auction=1&_sop=1"
        
        print(f"🔍 Searching: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"📡 Status: {response.status_code}")
            print(f"📊 Got: {len(response.content)} bytes")
            
            if response.status_code != 200:
                print("❌ Failed to get eBay page")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find listings
            listings = []
            selectors = ['div.s-item', 'div[data-view]', '.s-item']
            
            for selector in selectors:
                if selector.startswith('.'):
                    found = soup.select(selector)
                else:
                    found = soup.find_all('div', attrs={'data-view': True}) if 'data-view' in selector else soup.find_all('div', class_='s-item')
                
                if found and len(found) > 5:  # Need more than just filters
                    listings = found
                    print(f"✅ Found {len(listings)} listings with: {selector}")
                    break
            
            if not listings:
                print("❌ No listings found!")
                return []
            
            # Process listings and extract titles
            results = []
            print("\\n🔄 Processing listings...")
            
            for i, listing in enumerate(listings[:25]):  # Check more listings
                try:
                    # Try multiple ways to get title
                    title = None
                    
                    # Method 1: h3 tag
                    h3_elem = listing.find('h3')
                    if h3_elem:
                        title = h3_elem.get_text(strip=True)
                    
                    # Method 2: a tag
                    if not title or len(title) < 10:
                        a_elem = listing.find('a')
                        if a_elem:
                            title = a_elem.get_text(strip=True)
                    
                    # Method 3: any text content
                    if not title or len(title) < 10:
                        all_text = listing.get_text(strip=True)
                        lines = all_text.split('\\n')
                        for line in lines[:3]:  # Check first few lines
                            if len(line) > 15 and not any(skip in line.lower() for skip in ['shipping', 'bid', 'time left', 'buy it now']):
                                title = line.strip()
                                break
                    
                    if not title:
                        continue
                    
                    # Clean title
                    title = title.replace('Opens in a new window or tab', '').strip()
                    title = title.replace('New Listing', '').strip()
                    
                    print(f"  {i+1:2d}. {title[:70]}...")
                    
                    # Check if GBA
                    if self.is_gba_item(title):
                        print(f"       🎮 GBA AUCTION FOUND!")
                        
                        # Get other details
                        price = "No price"
                        try:
                            price_elem = listing.find('span', class_='s-item__price')
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                        except:
                            pass
                        
                        link = "#"
                        try:
                            link_elem = listing.find('a')
                            if link_elem and link_elem.get('href'):
                                link = link_elem['href']
                                if not link.startswith('http'):
                                    link = 'https://www.ebay.com' + link
                        except:
                            pass
                        
                        time_left = "Ending soon"
                        try:
                            time_elem = listing.find('span', class_='s-item__time-left')
                            if time_elem:
                                time_left = time_elem.get_text(strip=True)
                        except:
                            pass
                        
                        image = "https://via.placeholder.com/200x150?text=GBA"
                        try:
                            img_elem = listing.find('img')
                            if img_elem and img_elem.get('src'):
                                image = img_elem['src']
                                if 's-l140' in image:
                                    image = image.replace('s-l140', 's-l300')
                        except:
                            pass
                        
                        results.append({
                            'title': title,
                            'price': price,
                            'link': link,
                            'image': image,
                            'time_left': time_left
                        })
                        
                        print(f"       💰 {price} | ⏰ {time_left}")
                    
                except Exception as e:
                    continue
            
            print(f"\\n🎯 FOUND {len(results)} GBA AUCTIONS ENDING SOON!")
            return results
            
        except Exception as e:
            print(f"💥 Error: {e}")
            return []
    
    def generate_simple_html(self, results):
        """Generate simple HTML focused on ending soon"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        if not results:
            content = '''
            <div style="text-align: center; padding: 50px; background: #2d2d2d; border-radius: 15px; color: white; margin: 20px;">
                <h2>⏰ No GBA Auctions Ending Soon</h2>
                <p>This could mean:</p>
                <ul style="display: inline-block; text-align: left; margin: 20px 0;">
                    <li>All recent GBA auctions have ended</li>
                    <li>No new auctions listed recently</li>
                    <li>Try again in a few hours</li>
                </ul>
                <p><strong>Check back regularly - new auctions appear frequently!</strong></p>
            </div>
            '''
        else:
            cards = []
            for i, item in enumerate(results, 1):
                card = f'''
                <div style="background: #2d2d2d; border-radius: 15px; overflow: hidden; margin-bottom: 25px; cursor: pointer; transition: all 0.3s; border: 2px solid #444;" 
                     onclick="window.open('{item['link']}', '_blank')" 
                     onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='#ff6b6b'" 
                     onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='#444'">
                    
                    <div style="position: relative;">
                        <img src="{item['image']}" style="width: 100%; height: 250px; object-fit: cover;" 
                             onerror="this.src='https://via.placeholder.com/300x250/444/fff?text=GBA+Auction'">
                        <div style="position: absolute; top: 15px; left: 15px; background: #ff6b6b; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                            #{i} ENDING SOON
                        </div>
                        <div style="position: absolute; bottom: 15px; right: 15px; background: rgba(0,0,0,0.8); color: white; padding: 8px 12px; border-radius: 15px; font-size: 13px;">
                            ⏰ {item['time_left']}
                        </div>
                    </div>
                    
                    <div style="padding: 25px;">
                        <h3 style="margin: 0 0 15px 0; color: #fff; font-size: 18px; line-height: 1.4;">{item['title']}</h3>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #ff6b6b;">{item['price']}</div>
                            <div style="background: #ff6b6b; color: white; padding: 12px 20px; border-radius: 25px; font-weight: bold;">
                                BID NOW →
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
    <title>GBA Auctions Ending Soon</title>
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
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 40px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            border-radius: 20px;
            color: white;
        }}
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .urgent {{
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            display: inline-block;
            font-weight: bold;
            font-size: 18px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: #2d2d2d;
            border-radius: 15px;
            color: #ccc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ GBA Auctions Ending Soon</h1>
            <p style="font-size: 1.3rem; margin-bottom: 20px;">GameBoy Advance auctions you need to bid on NOW!</p>
            <div class="urgent">Found {len(results)} auctions • Updated {timestamp}</div>
        </div>
        
        {content}
        
        <div class="footer">
            <p>🎮 Focused on GBA auctions ending soonest • Click any auction to bid on eBay</p>
            <p>⚡ Run again frequently - auctions end quickly!</p>
        </div>
    </div>
</body>
</html>
        '''
        
        return html
    
    def run(self):
        """Main execution"""
        results = self.scrape_ending_soon()
        
        print("\\n🎨 Generating focused HTML...")
        html = self.generate_simple_html(results)
        
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
        
        print("\\n" + "=" * 50)
        if results:
            print(f"🎯 SUCCESS! Found {len(results)} GBA auctions ending soon")
            print("⚡ These auctions are ending soonest - bid quickly!")
        else:
            print("⏰ No GBA auctions ending soon right now")
            print("💡 Try again in a few hours - new auctions appear regularly")
        print("=" * 50)

if __name__ == "__main__":
    scraper = WorkingGBAScraperFocused()
    scraper.run()
    input("\\nPress Enter to exit...")
