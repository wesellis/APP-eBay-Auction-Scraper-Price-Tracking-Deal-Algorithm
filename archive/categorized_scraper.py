"""
Categorized eBay GBA scraper - organizes results by ending soonest, most bid on, and large lots
"""

import requests
from bs4 import BeautifulSoup
import time
import webbrowser
import os
from datetime import datetime
import random
import re

class CategorizedGBAScraper:
    """GBA scraper that organizes results into categories"""
    
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
                r'(\\d+)\\s*bids?',
                r'(\\d+)\\s*bidders?'
            ]
            
            for pattern in bid_patterns:
                match = re.search(pattern, text)
                if match:
                    return int(match.group(1))
                    
            # Check for specific bid elements
            bid_elem = listing.find('span', class_='s-item__bids')
            if bid_elem:
                bid_text = bid_elem.get_text()
                numbers = re.findall(r'\\d+', bid_text)
                if numbers:
                    return int(numbers[0])
                    
        except:
            pass
        return 0
    
    def extract_time_remaining(self, listing):
        \"\"\"Extract time remaining and convert to sortable format\"\"\"
        try:
            time_elem = listing.find('span', class_='s-item__time-left')
            if time_elem:
                time_text = time_elem.get_text(strip=True).lower()
                
                # Convert to minutes for sorting
                if 'd' in time_text:  # days
                    days = int(re.findall(r'(\\d+)d', time_text)[0])
                    return days * 24 * 60, time_text
                elif 'h' in time_text:  # hours
                    hours = int(re.findall(r'(\\d+)h', time_text)[0])
                    return hours * 60, time_text
                elif 'm' in time_text:  # minutes
                    minutes = int(re.findall(r'(\\d+)m', time_text)[0])
                    return minutes, time_text
                    
                return 0, time_text
        except:
            pass
        return 9999, \"Time not specified\"
    
    def scrape_category(self, url, category_name):\n        \"\"\"Scrape a specific category\"\"\"\n        print(f\"🌐 Fetching {category_name}: {url[:80]}...\")\n        \n        try:\n            response = requests.get(url, headers=self.get_headers(), timeout=30)\n            \n            if response.status_code != 200:\n                print(f\"❌ Status {response.status_code}\")\n                return []\n                \n            print(f\"✅ Got {len(response.content)} bytes\")\n            \n            soup = BeautifulSoup(response.content, 'html.parser')\n            \n            # Find listings\n            listings = self.find_listings_multiple_ways(soup)\n            \n            if not listings:\n                print(f\"❌ No listings found for {category_name}\")\n                return []\n            \n            print(f\"📦 Found {len(listings)} potential listings\")\n            \n            # Process listings\n            results = []\n            for i, listing in enumerate(listings[:20]):  # Limit per category\n                try:\n                    title = self.extract_title_multiple_ways(listing)\n                    \n                    if not title or not self.is_gba_item(title):\n                        continue\n                    \n                    # Extract data\n                    price = self.extract_price(listing)\n                    link = self.extract_link(listing)\n                    image = self.extract_image(listing)\n                    time_minutes, time_text = self.extract_time_remaining(listing)\n                    bid_count = self.extract_bid_count(listing)\n                    auction_format = self.check_auction_format(listing)\n                    is_lot = self.is_large_lot(title)\n                    \n                    result = {\n                        'title': title,\n                        'price': price,\n                        'link': link,\n                        'image': image,\n                        'time_left': time_text,\n                        'time_minutes': time_minutes,\n                        'bid_count': bid_count,\n                        'format': auction_format,\n                        'is_lot': is_lot,\n                        'category': category_name\n                    }\n                    \n                    results.append(result)\n                    print(f\"  ✅ {title[:50]}... | {price} | 🔨{bid_count} bids | ⏰{time_text}\")\n                    \n                except Exception as e:\n                    continue\n            \n            return results\n            \n        except Exception as e:\n            print(f\"💥 Error scraping {category_name}: {str(e)[:100]}...\")\n            return []\n    \n    def scrape_all_categories(self):\n        \"\"\"Scrape all categories\"\"\"\n        print(\"🚀 Starting CATEGORIZED eBay GBA Scraper\")\n        print(\"📊 Organizing results by: Ending Soonest, Most Bid On, Large Lots\")\n        print(\"=\" * 70)\n        \n        categories = [\n            {\n                'name': 'Ending Soonest',\n                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=1&LH_Auction=1',\n                'description': 'GBA auctions ending soonest'\n            },\n            {\n                'name': 'Most Bid On',\n                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=12&LH_Auction=1',\n                'description': 'GBA auctions with most bids'\n            },\n            {\n                'name': 'Large Lots',\n                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance+lot+bundle+collection&_sop=1',\n                'description': 'GBA lots, bundles, and collections'\n            },\n            {\n                'name': 'Buy It Now',\n                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=15&LH_BIN=1',\n                'description': 'GBA Buy It Now listings'\n            }\n        ]\n        \n        all_results = {}\n        \n        for i, category in enumerate(categories):\n            print(f\"\\n📍 Category {i+1}/{len(categories)}: {category['name']}\")\n            print(f\"🎯 {category['description']}\")\n            \n            results = self.scrape_category(category['url'], category['name'])\n            all_results[category['name']] = results\n            \n            print(f\"📊 {category['name']}: {len(results)} items found\")\n            \n            if i < len(categories) - 1:\n                wait_time = random.randint(3, 6)\n                print(f\"⏳ Waiting {wait_time} seconds...\")\n                time.sleep(wait_time)\n        \n        return all_results\n    \n    def generate_categorized_html(self, categorized_results):\n        \"\"\"Generate HTML with organized categories\"\"\"\n        \n        total_items = sum(len(items) for items in categorized_results.values())\n        timestamp = datetime.now().strftime(\"%B %d, %Y at %I:%M %p\")\n        \n        # Generate sections for each category\n        sections_html = \"\"\n        \n        category_config = {\n            'Ending Soonest': {\n                'icon': '⏰',\n                'color': '#e74c3c',\n                'description': 'Auctions ending soon - bid before time runs out!'\n            },\n            'Most Bid On': {\n                'icon': '🔥',\n                'color': '#f39c12',\n                'description': 'Popular auctions with lots of bidding activity'\n            },\n            'Large Lots': {\n                'icon': '📦',\n                'color': '#9b59b6',\n                'description': 'Bundles, lots, and collections - great value!'\n            },\n            'Buy It Now': {\n                'icon': '💳',\n                'color': '#27ae60',\n                'description': 'Fixed price items - buy immediately'\n            }\n        }\n        \n        for category_name, items in categorized_results.items():\n            if not items:\n                continue\n                \n            config = category_config.get(category_name, {'icon': '📋', 'color': '#3498db', 'description': ''})\n            \n            # Sort items appropriately\n            if category_name == 'Ending Soonest':\n                items.sort(key=lambda x: x['time_minutes'])\n            elif category_name == 'Most Bid On':\n                items.sort(key=lambda x: x['bid_count'], reverse=True)\n            \n            cards_html = \"\"\n            for item in items:\n                # Special badges\n                badges = \"\"\n                if item['bid_count'] > 0:\n                    badges += f'<span style=\"background: #e74c3c; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px;\">🔨 {item[\"bid_count\"]} bids</span>'\n                if item['is_lot']:\n                    badges += f'<span style=\"background: #9b59b6; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px;\">📦 Lot</span>'\n                if item['format'] == 'Buy It Now':\n                    badges += f'<span style=\"background: #27ae60; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;\">💳 Buy Now</span>'\n                \n                card = f'''\n                <div style=\"background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 15px; cursor: pointer; transition: all 0.3s; border-left: 4px solid {config['color']};\" \n                     onclick=\"window.open('{item['link']}', '_blank')\" \n                     onmouseover=\"this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'\" \n                     onmouseout=\"this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.1)'\">\n                    <div style=\"display: flex; padding: 15px;\">\n                        <img src=\"{item['image']}\" style=\"width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-right: 15px;\" \n                             onerror=\"this.src='https://via.placeholder.com/80x80/f8f9fa/6c757d?text=GBA'\">\n                        <div style=\"flex: 1;\">\n                            <h4 style=\"margin: 0 0 8px 0; color: #2c3e50; font-size: 14px; line-height: 1.3; font-weight: 600;\">{item['title'][:80]}{'...' if len(item['title']) > 80 else ''}</h4>\n                            <div style=\"margin-bottom: 8px;\">{badges}</div>\n                            <div style=\"display: flex; justify-content: space-between; align-items: center;\">\n                                <span style=\"font-size: 16px; font-weight: bold; color: {config['color']};\">{item['price']}</span>\n                                <span style=\"font-size: 12px; color: #7f8c8d;\">⏰ {item['time_left']}</span>\n                            </div>\n                        </div>\n                    </div>\n                </div>\n                '''\n                cards_html += card\n            \n            section_html = f'''\n            <div style=\"margin-bottom: 40px;\">\n                <div style=\"background: linear-gradient(135deg, {config['color']}22, {config['color']}11); border-radius: 15px; padding: 20px; margin-bottom: 20px; border-left: 5px solid {config['color']};\">\n                    <h2 style=\"margin: 0 0 8px 0; color: {config['color']}; font-size: 24px; display: flex; align-items: center;\">\n                        <span style=\"margin-right: 10px; font-size: 28px;\">{config['icon']}</span>\n                        {category_name}\n                        <span style=\"background: {config['color']}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; margin-left: 15px;\">{len(items)}</span>\n                    </h2>\n                    <p style=\"margin: 0; color: #555; font-size: 16px;\">{config['description']}</p>\n                </div>\n                <div style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 15px;\">\n                    {cards_html}\n                </div>\n            </div>\n            '''\n            \n            sections_html += section_html\n        \n        if not sections_html:\n            sections_html = '''\n            <div style=\"text-align: center; padding: 50px; background: rgba(255,255,255,0.1); border-radius: 15px; color: white; margin: 20px;\">\n                <h2>🔍 No GameBoy Advance items found</h2>\n                <p>Try running again in a few minutes - eBay inventory changes frequently!</p>\n            </div>\n            '''\n        \n        html = f'''\n<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>GameBoy Advance Items - Categorized</title>\n    <style>\n        body {{\n            font-family: 'Segoe UI', system-ui, sans-serif;\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            min-height: 100vh;\n            margin: 0;\n            padding: 20px;\n        }}\n        .container {{\n            max-width: 1400px;\n            margin: 0 auto;\n        }}\n        .header {{\n            text-align: center;\n            color: white;\n            margin-bottom: 40px;\n        }}\n        .header h1 {{\n            font-size: clamp(2rem, 5vw, 3rem);\n            margin-bottom: 10px;\n            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);\n        }}\n        .stats {{\n            background: rgba(255,255,255,0.1);\n            padding: 15px 25px;\n            border-radius: 25px;\n            display: inline-block;\n            backdrop-filter: blur(10px);\n        }}\n        .footer {{\n            text-align: center;\n            margin-top: 40px;\n            color: rgba(255,255,255,0.8);\n        }}\n        @media (max-width: 768px) {{\n            .container {{ padding: 10px; }}\n            div[style*=\"grid-template-columns\"] {{ grid-template-columns: 1fr !important; }}\n        }}\n    </style>\n</head>\n<body>\n    <div class=\"container\">\n        <div class=\"header\">\n            <h1>🎮 GameBoy Advance Items</h1>\n            <p style=\"font-size: 1.2rem; margin-bottom: 20px;\">Organized by Category - Live Results</p>\n            <div class=\"stats\">Found {total_items} items • Updated {timestamp}</div>\n        </div>\n        \n        {sections_html}\n        \n        <div class=\"footer\">\n            <p>Powered by Categorized eBay Scraper • Click any item to view on eBay</p>\n            <p>🔄 Run again for latest inventory • 📊 Results organized for easy browsing</p>\n        </div>\n    </div>\n</body>\n</html>\n        '''\n        \n        return html\n    \n    # Include the helper methods from the previous scraper\n    def find_listings_multiple_ways(self, soup):\n        \"\"\"Try multiple ways to find listings\"\"\"\n        selectors = [\n            'div.s-item',\n            'div[data-view]',\n            '.srp-results .s-item',\n            'div[class*=\"s-item\"]',\n            '.s-item'\n        ]\n        \n        for selector in selectors:\n            try:\n                if selector.startswith('.'):\n                    listings = soup.select(selector)\n                elif '[' in selector:\n                    listings = soup.find_all('div', attrs={'data-view': True})\n                else:\n                    listings = soup.find_all('div', class_=lambda x: x and 's-item' in str(x))\n                \n                if listings and len(listings) > 2:\n                    return listings\n            except:\n                continue\n        return []\n    \n    def extract_title_multiple_ways(self, listing):\n        \"\"\"Extract title using multiple methods\"\"\"\n        methods = [\n            lambda: listing.find('h3', class_='s-item__title'),\n            lambda: listing.find('h3'),\n            lambda: listing.find('a', class_='s-item__link'),\n            lambda: listing.find('a')\n        ]\n        \n        for method in methods:\n            try:\n                elem = method()\n                if elem:\n                    title = elem.get_text(strip=True)\n                    if title and len(title) > 10:\n                        title = title.replace('Opens in a new window or tab', '').strip()\n                        title = title.replace('New Listing', '').strip()\n                        return title\n            except:\n                continue\n        return None\n    \n    def extract_price(self, listing):\n        \"\"\"Extract price\"\"\"\n        try:\n            price_elem = listing.find('span', class_='s-item__price')\n            if price_elem:\n                return price_elem.get_text(strip=True)\n        except:\n            pass\n        return \"Price not found\"\n    \n    def extract_link(self, listing):\n        \"\"\"Extract link\"\"\"\n        try:\n            link_elem = listing.find('a')\n            if link_elem and link_elem.get('href'):\n                link = link_elem['href']\n                if not link.startswith('http'):\n                    link = 'https://www.ebay.com' + link\n                return link\n        except:\n            pass\n        return \"#\"\n    \n    def extract_image(self, listing):\n        \"\"\"Extract image\"\"\"\n        try:\n            img_elem = listing.find('img')\n            if img_elem and img_elem.get('src'):\n                image = img_elem['src']\n                if 's-l140' in image:\n                    image = image.replace('s-l140', 's-l300')\n                return image\n        except:\n            pass\n        return \"https://via.placeholder.com/80x80?text=GBA\"\n    \n    def check_auction_format(self, listing):\n        \"\"\"Check auction format\"\"\"\n        try:\n            text = listing.get_text().lower()\n            if 'bid' in text or 'auction' in text:\n                return \"Auction\"\n            elif 'buy it now' in text:\n                return \"Buy It Now\"\n        except:\n            pass\n        return \"Unknown\"\n    \n    def run(self):\n        \"\"\"Main execution\"\"\"\n        results = self.scrape_all_categories()\n        \n        print(\"\\n🎨 Generating categorized HTML...\")\n        html = self.generate_categorized_html(results)\n        \n        filename = 'gba_auctions.html'\n        with open(filename, 'w', encoding='utf-8') as f:\n            f.write(html)\n        \n        print(f\"💾 Saved: {filename}\")\n        \n        # Open in browser\n        try:\n            html_path = os.path.abspath(filename)\n            webbrowser.open(f\"file://{html_path}\")\n            print(f\"🌐 Opening in browser...\")\n        except Exception as e:\n            print(f\"⚠️  Could not auto-open: {e}\")\n        \n        total_items = sum(len(items) for items in results.values())\n        print(\"\\n\" + \"=\" * 70)\n        if total_items > 0:\n            print(f\"✅ SUCCESS! Found {total_items} GameBoy Advance items\")\n            for category, items in results.items():\n                if items:\n                    print(f\"📊 {category}: {len(items)} items\")\n        else:\n            print(\"⚠️  No GBA items found\")\n        print(\"=\" * 70)\n\nif __name__ == \"__main__\":\n    scraper = CategorizedGBAScraper()\n    scraper.run()\n    input(\"\\nPress Enter to exit...\")\n