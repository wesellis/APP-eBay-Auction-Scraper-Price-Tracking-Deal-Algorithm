"""
Enhanced categorized eBay GBA scraper with dark mode, equal columns, and total price calculation
"""

import requests
from bs4 import BeautifulSoup
import time
import webbrowser
import os
from datetime import datetime
import random
import re

class EnhancedGBAScraper:
    """Enhanced GBA scraper with dark mode and better pricing"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
    def get_headers(self):
        """Get headers for requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def is_gba_item(self, title):
        """Check if title is GBA related"""
        if not title or len(title) < 5:
            return False
            
        title_lower = title.lower()
        
        # Filter out obvious non-items
        filter_terms = ['apply', 'filter', 'region code', 'brand', 'condition', 'price range', 'buying format']
        if any(term in title_lower for term in filter_terms):
            return False
            
        gba_keywords = [
            'gameboy advance', 'game boy advance', 'gba', 'advance sp',
            'gba sp', 'gameboy sp', 'game boy sp', 'nintendo advance',
            'ags-001', 'ags-101', 'ags001', 'ags101', 'nintendo gba'
        ]
        
        for keyword in gba_keywords:
            if keyword in title_lower:
                return True
                
        # Special case: nintendo + (advance or sp)
        if 'nintendo' in title_lower and ('advance' in title_lower or ' sp ' in title_lower):
            return True
            
        return False
    
    def is_large_lot(self, title):
        """Check if item is a large lot or bundle"""
        title_lower = title.lower()
        lot_keywords = ['lot', 'bundle', 'collection', 'bulk', 'multiple', 'games', 'accessories']
        return any(keyword in title_lower for keyword in lot_keywords)
    
    def extract_bid_count(self, listing):
        """Extract number of bids from listing"""
        try:
            # Look for bid count in various formats
            text = listing.get_text().lower()
            
            # Match patterns like "5 bids", "12 bid", "1 bid"
            bid_patterns = [
                r'(\d+)\s*bids?',
                r'(\d+)\s*bidders?'
            ]
            
            for pattern in bid_patterns:
                match = re.search(pattern, text)
                if match:
                    return int(match.group(1))
                    
            # Check for specific bid elements
            bid_elem = listing.find('span', class_='s-item__bids')
            if bid_elem:
                bid_text = bid_elem.get_text()
                numbers = re.findall(r'\d+', bid_text)
                if numbers:
                    return int(numbers[0])
                    
        except:
            pass
        return 0
    
    def extract_time_remaining(self, listing):
        """Extract time remaining and convert to sortable format"""
        try:
            time_elem = listing.find('span', class_='s-item__time-left')
            if time_elem:
                time_text = time_elem.get_text(strip=True).lower()
                
                # Convert to minutes for sorting
                if 'd' in time_text:  # days
                    days = int(re.findall(r'(\d+)d', time_text)[0])
                    return days * 24 * 60, time_text
                elif 'h' in time_text:  # hours
                    hours = int(re.findall(r'(\d+)h', time_text)[0])
                    return hours * 60, time_text
                elif 'm' in time_text:  # minutes
                    minutes = int(re.findall(r'(\d+)m', time_text)[0])
                    return minutes, time_text
                    
                return 0, time_text
        except:
            pass
        return 9999, "Time not specified"
    
    def extract_shipping_cost(self, listing):
        """Extract shipping cost from listing"""
        try:
            # Look for shipping cost in various formats
            text = listing.get_text()
            
            # Common shipping patterns
            shipping_patterns = [
                r'\+\s*\$(\d+\.?\d*)\s*shipping',
                r'shipping:\s*\$(\d+\.?\d*)',
                r'\$(\d+\.?\d*)\s*ship',
                r'ships?\s*for\s*\$(\d+\.?\d*)'
            ]
            
            for pattern in shipping_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return float(match.group(1))
            
            # Check for free shipping
            if 'free shipping' in text.lower():
                return 0.0
                
        except:
            pass
        return None  # Unknown shipping
    
    def calculate_total_price(self, price_text, shipping_cost):
        """Calculate total price including shipping"""
        try:
            # Extract numeric price
            price_numbers = re.findall(r'\$?(\d+\.?\d*)', price_text)
            if price_numbers:
                base_price = float(price_numbers[0])
                
                if shipping_cost is not None:
                    total = base_price + shipping_cost
                    if shipping_cost == 0:
                        return f"${total:.2f} (Free Ship)", total
                    else:
                        return f"${total:.2f} (+${shipping_cost:.2f} ship)", total
                else:
                    return f"${base_price:.2f} (Ship TBD)", base_price
        except:
            pass
        return price_text, 0
    
    def scrape_category(self, url, category_name):
        """Scrape a specific category"""
        print(f"🌐 Fetching {category_name}: {url[:80]}...")
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Status {response.status_code}")
                return []
                
            print(f"✅ Got {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listings
            listings = self.find_listings_multiple_ways(soup)
            
            if not listings:
                print(f"❌ No listings found for {category_name}")
                return []
            
            print(f"📦 Found {len(listings)} potential listings")
            
            # Process listings
            results = []
            for i, listing in enumerate(listings[:15]):  # Limit per category
                try:
                    title = self.extract_title_multiple_ways(listing)
                    
                    if not title or not self.is_gba_item(title):
                        continue
                    
                    # Extract data
                    price_text = self.extract_price(listing)
                    shipping_cost = self.extract_shipping_cost(listing)
                    total_price_text, total_value = self.calculate_total_price(price_text, shipping_cost)
                    
                    link = self.extract_link(listing)
                    image = self.extract_image(listing)
                    time_minutes, time_text = self.extract_time_remaining(listing)
                    bid_count = self.extract_bid_count(listing)
                    auction_format = self.check_auction_format(listing)
                    is_lot = self.is_large_lot(title)
                    
                    result = {
                        'title': title,
                        'price': price_text,
                        'total_price': total_price_text,
                        'total_value': total_value,
                        'shipping': shipping_cost,
                        'link': link,
                        'image': image,
                        'time_left': time_text,
                        'time_minutes': time_minutes,
                        'bid_count': bid_count,
                        'format': auction_format,
                        'is_lot': is_lot,
                        'category': category_name
                    }
                    
                    results.append(result)
                    print(f"  ✅ {title[:40]}... | {total_price_text} | 🔨{bid_count} bids | ⏰{time_text}")
                    
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            print(f"💥 Error scraping {category_name}: {str(e)[:100]}...")
            return []
    
    def scrape_all_categories(self):
        """Scrape all categories"""
        print("🚀 Starting ENHANCED eBay GBA Scraper")
        print("🌙 Dark mode | 📊 Equal columns | 💰 Total price with shipping")
        print("=" * 70)
        
        categories = [
            {
                'name': 'Ending Soonest',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=1&LH_Auction=1',
                'description': 'GBA auctions ending soonest'
            },
            {
                'name': 'Most Bid On',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=12&LH_Auction=1',
                'description': 'GBA auctions with most bids'
            },
            {
                'name': 'Large Lots',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance+lot+bundle+collection&_sop=1',
                'description': 'GBA lots, bundles, and collections'
            },
            {
                'name': 'Buy It Now',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=15&LH_BIN=1',
                'description': 'GBA Buy It Now listings'
            }
        ]
        
        all_results = {}
        
        for i, category in enumerate(categories):
            print(f"\n📍 Category {i+1}/{len(categories)}: {category['name']}")
            print(f"🎯 {category['description']}")
            
            results = self.scrape_category(category['url'], category['name'])
            all_results[category['name']] = results
            
            print(f"📊 {category['name']}: {len(results)} items found")
            
            if i < len(categories) - 1:
                wait_time = random.randint(3, 6)
                print(f"⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        
        return all_results
    
    def generate_dark_mode_html(self, categorized_results):
        """Generate dark mode HTML with equal columns and total pricing"""
        
        total_items = sum(len(items) for items in categorized_results.values())
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Generate sections for each category
        sections_html = ""
        
        category_config = {
            'Ending Soonest': {
                'icon': '⏰',
                'color': '#ff6b6b',
                'description': 'Auctions ending soon - bid before time runs out!'
            },
            'Most Bid On': {
                'icon': '🔥',
                'color': '#ffa726',
                'description': 'Popular auctions with lots of bidding activity'
            },
            'Large Lots': {
                'icon': '📦',
                'color': '#ab47bc',
                'description': 'Bundles, lots, and collections - great value!'
            },
            'Buy It Now': {
                'icon': '💳',
                'color': '#66bb6a',
                'description': 'Fixed price items - buy immediately'
            }
        }
        
        for category_name, items in categorized_results.items():
            if not items:
                continue
                
            config = category_config.get(category_name, {'icon': '📋', 'color': '#42a5f5', 'description': ''})
            
            # Sort items appropriately
            if category_name == 'Ending Soonest':
                items.sort(key=lambda x: x['time_minutes'])
            elif category_name == 'Most Bid On':
                items.sort(key=lambda x: x['bid_count'], reverse=True)
            elif category_name == 'Buy It Now':
                items.sort(key=lambda x: x['total_value'])
            
            cards_html = ""
            for item in items:
                # Special badges
                badges = ""
                if item['bid_count'] > 0:
                    badges += f'<span class="badge bid-badge">🔨 {item["bid_count"]} bids</span>'
                if item['is_lot']:
                    badges += f'<span class="badge lot-badge">📦 Lot</span>'
                if item['format'] == 'Buy It Now':
                    badges += f'<span class="badge buy-badge">💳 Buy Now</span>'
                
                card = f'''
                <div class="item-card" onclick="window.open('{item['link']}', '_blank')">
                    <div class="card-header" style="border-left: 4px solid {config['color']};">
                        <img src="{item['image']}" class="item-image" 
                             onerror="this.src='https://via.placeholder.com/100x100/555/fff?text=GBA'">
                        <div class="item-info">
                            <h4 class="item-title">{item['title'][:65]}{'...' if len(item['title']) > 65 else ''}</h4>
                            <div class="badges">{badges}</div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="price-section">
                            <div class="total-price" style="color: {config['color']};">{item['total_price']}</div>
                            <div class="base-price">Base: {item['price']}</div>
                        </div>
                        <div class="time-section">
                            <span class="time-left">⏰ {item['time_left']}</span>
                        </div>
                    </div>
                </div>
                '''
                cards_html += card
            
            section_html = f'''
            <div class="category-section">
                <div class="category-header" style="border-left: 5px solid {config['color']};">
                    <h2 style="color: {config['color']};">
                        <span class="category-icon">{config['icon']}</span>
                        {category_name}
                        <span class="item-count" style="background: {config['color']};">{len(items)}</span>
                    </h2>
                    <p class="category-description">{config['description']}</p>
                </div>
                <div class="items-grid">
                    {cards_html}
                </div>
            </div>
            '''
            
            sections_html += section_html
        
        if not sections_html:
            sections_html = '''
            <div class="no-results">
                <h2>🔍 No GameBoy Advance items found</h2>
                <p>Try running again in a few minutes - eBay inventory changes frequently!</p>
            </div>
            '''
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameBoy Advance Items - Dark Mode</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #121212;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #1e1e1e, #2d2d2d);
            border-radius: 15px;
            border: 1px solid #333;
        }}
        
        .header h1 {{
            font-size: clamp(2rem, 5vw, 3rem);
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
            background-size: 400% 400%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 3s ease infinite;
        }}
        
        @keyframes gradient {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        .stats {{
            background: #2d2d2d;
            padding: 15px 25px;
            border-radius: 25px;
            display: inline-block;
            border: 1px solid #444;
        }}
        
        .category-section {{
            margin-bottom: 50px;
        }}
        
        .category-header {{
            background: #1e1e1e;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 1px solid #333;
        }}
        
        .category-header h2 {{
            font-size: 28px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        
        .category-icon {{
            margin-right: 15px;
            font-size: 32px;
        }}
        
        .item-count {{
            color: white !important;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 16px;
            margin-left: 20px;
            font-weight: 600;
        }}
        
        .category-description {{
            color: #b0b0b0;
            font-size: 16px;
            margin: 0;
        }}
        
        .items-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }}
        
        @media (max-width: 1400px) {{
            .items-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        
        @media (max-width: 1000px) {{
            .items-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        @media (max-width: 600px) {{
            .items-grid {{ grid-template-columns: 1fr; }}
        }}
        
        .item-card {{
            background: #1e1e1e;
            border-radius: 12px;
            border: 1px solid #333;
            cursor: pointer;
            transition: all 0.3s ease;
            overflow: hidden;
        }}
        
        .item-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-color: #555;
        }}
        
        .card-header {{
            padding: 15px;
            display: flex;
            gap: 15px;
        }}
        
        .item-image {{
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 8px;
            background: #333;
        }}
        
        .item-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .item-title {{
            color: #f0f0f0;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
            line-height: 1.3;
        }}
        
        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        
        .badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .bid-badge {{ background: #ff6b6b; color: white; }}
        .lot-badge {{ background: #ab47bc; color: white; }}
        .buy-badge {{ background: #66bb6a; color: white; }}
        
        .card-footer {{
            padding: 15px;
            background: #252525;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #333;
        }}
        
        .price-section {{
            flex: 1;
        }}
        
        .total-price {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .base-price {{
            font-size: 12px;
            color: #888;
        }}
        
        .time-section {{
            text-align: right;
        }}
        
        .time-left {{
            font-size: 12px;
            color: #b0b0b0;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            background: #1e1e1e;
            border-radius: 15px;
            border: 1px solid #333;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: #1e1e1e;
            border-radius: 15px;
            border: 1px solid #333;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 GameBoy Advance Items</h1>
            <p style="font-size: 1.2rem; margin-bottom: 20px; color: #b0b0b0;">Dark Mode • Equal Columns • Total Pricing</p>
            <div class="stats">Found {total_items} items • Updated {timestamp}</div>
        </div>
        
        {sections_html}
        
        <div class="footer">
            <p>🌙 Enhanced Dark Mode Scraper • Click any item to view on eBay</p>
            <p>💰 Prices include shipping when available • 📊 Equal column layout for easy browsing</p>
        </div>
    </div>
</body>
</html>
        '''
        
        return html
    
    # Include helper methods (same as before but keeping them here for completeness)
    def find_listings_multiple_ways(self, soup):
        """Try multiple ways to find listings"""
        selectors = [
            'div.s-item',
            'div[data-view]',
            '.srp-results .s-item',
            'div[class*="s-item"]',
            '.s-item'
        ]
        
        for selector in selectors:
            try:
                if selector.startswith('.'):
                    listings = soup.select(selector)
                elif '[' in selector:
                    listings = soup.find_all('div', attrs={'data-view': True})
                else:
                    listings = soup.find_all('div', class_=lambda x: x and 's-item' in str(x))
                
                if listings and len(listings) > 2:
                    return listings
            except:
                continue
        return []
    
    def extract_title_multiple_ways(self, listing):
        """Extract title using multiple methods"""
        methods = [
            lambda: listing.find('h3', class_='s-item__title'),
            lambda: listing.find('h3'),
            lambda: listing.find('a', class_='s-item__link'),
            lambda: listing.find('a')
        ]
        
        for method in methods:
            try:
                elem = method()
                if elem:
                    title = elem.get_text(strip=True)
                    if title and len(title) > 10:
                        title = title.replace('Opens in a new window or tab', '').strip()
                        title = title.replace('New Listing', '').strip()
                        return title
            except:
                continue
        return None
    
    def extract_price(self, listing):
        """Extract price"""
        try:
            price_elem = listing.find('span', class_='s-item__price')
            if price_elem:
                return price_elem.get_text(strip=True)
        except:
            pass
        return "Price not found"
    
    def extract_link(self, listing):
        """Extract link"""
        try:
            link_elem = listing.find('a')
            if link_elem and link_elem.get('href'):
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.ebay.com' + link
                return link
        except:
            pass
        return "#"
    
    def extract_image(self, listing):
        """Extract image"""
        try:
            img_elem = listing.find('img')
            if img_elem and img_elem.get('src'):
                image = img_elem['src']
                if 's-l140' in image:
                    image = image.replace('s-l140', 's-l300')
                return image
        except:
            pass
        return "https://via.placeholder.com/80x80/555/fff?text=GBA"
    
    def check_auction_format(self, listing):
        """Check auction format"""
        try:
            text = listing.get_text().lower()
            if 'bid' in text or 'auction' in text:
                return "Auction"
            elif 'buy it now' in text:
                return "Buy It Now"
        except:
            pass
        return "Unknown"
    
    def run(self):
        """Main execution"""
        results = self.scrape_all_categories()
        
        print("\n🌙 Generating dark mode HTML with equal columns...")
        html = self.generate_dark_mode_html(results)
        
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
            print(f"⚠️  Could not auto-open: {e}")
        
        total_items = sum(len(items) for items in results.values())
        print("\n" + "=" * 70)
        if total_items > 0:
            print(f"✅ SUCCESS! Found {total_items} GameBoy Advance items")
            for category, items in results.items():
                if items:
                    print(f"📊 {category}: {len(items)} items")
        else:
            print("⚠️  No GBA items found")
        print("=" * 70)

if __name__ == "__main__":
    scraper = EnhancedGBAScraper()
    scraper.run()
    input("\nPress Enter to exit...")
