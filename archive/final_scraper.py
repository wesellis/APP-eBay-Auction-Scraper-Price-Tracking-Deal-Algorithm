"""
Final working eBay scraper - handles current eBay layout and finds any available auctions
"""

import os
import random
import time
import webbrowser
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class FinalEbayScraper:
    """Final version that adapts to current eBay layout"""
    
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
    
    def try_different_searches(self):
        """Try different search strategies to find auctions"""
        
        # Strategy 1: Remove auction filter, then filter in code
        search_configs = [
            {
                'name': 'All GBA items (any format)',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&_sop=1',
                'description': 'All GameBoy Advance listings sorted by ending soonest'
            },
            {
                'name': 'GBA Console search',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=gba+console&_sop=1', 
                'description': 'GBA console listings'
            },
            {
                'name': 'Nintendo GBA',
                'url': 'https://www.ebay.com/sch/i.html?_nkw=nintendo+gameboy+advance&_sop=1',
                'description': 'Nintendo GameBoy Advance items'
            }
        ]
        
        all_results = []
        
        for i, config in enumerate(search_configs):
            print(f"\\n📍 Strategy {i+1}/{len(search_configs)}: {config['name']}")
            print(f"🎯 {config['description']}")
            
            results = self.scrape_url(config['url'])
            all_results.extend(results)
            
            if results:
                print(f"✅ Found {len(results)} GBA items with this strategy!")
            
            if i < len(search_configs) - 1:
                wait_time = random.randint(3, 7)
                print(f"⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        
        return all_results
    
    def scrape_url(self, url):
        """Scrape a specific URL"""
        print(f"🌐 Fetching: {url[:80]}...")
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Status {response.status_code}")
                return []
                
            print(f"✅ Got {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save raw HTML for debugging
            with open('latest_ebay_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved raw HTML to latest_ebay_response.html")
            
            # Try to find ANY listings with multiple approaches
            listings = self.find_listings_multiple_ways(soup)
            
            if not listings:
                print("❌ No listings found")
                return []
            
            print(f"📦 Found {len(listings)} potential listings")
            
            # Process listings
            results = []
            for i, listing in enumerate(listings[:30]):  # Process more listings
                try:
                    # Extract title with multiple methods
                    title = self.extract_title_multiple_ways(listing)
                    
                    if not title:
                        print(f"  {i+1:2d}. ❌ No title")
                        continue
                    
                    print(f"  {i+1:2d}. 📝 {title[:60]}...")
                    
                    # Check if it's a GBA item
                    if self.is_gba_item(title):
                        print(f"       ✅ GBA MATCH!")
                        
                        # Extract other data
                        price = self.extract_price(listing)
                        link = self.extract_link(listing)
                        image = self.extract_image(listing)
                        time_left = self.extract_time_left(listing)
                        auction_format = self.check_auction_format(listing)
                        
                        results.append({
                            'title': title,
                            'price': price,
                            'link': link,
                            'image': image,
                            'time_left': time_left,
                            'format': auction_format
                        })
                        
                        print(f"       💰 {price} | ⏰ {time_left} | 🏷️ {auction_format}")
                    else:
                        print(f"       ❌ Not GBA: {title[:30]}...")
                
                except Exception as e:
                    print(f"  {i+1:2d}. ⚠️  Error: {str(e)[:50]}...")
                    continue
            
            return results
            
        except Exception as e:
            print(f"💥 Error: {str(e)[:100]}...")
            return []
    
    def find_listings_multiple_ways(self, soup):
        """Try multiple ways to find listings"""
        
        selectors = [
            'div.s-item',
            'div[data-view]',
            '.srp-results .s-item',
            'div[class*="s-item"]',
            '.s-item',
            '[data-view*="mi"]',
            'div.srp-results div',
            'li.s-item',
            '.srp-river-results .s-item'
        ]
        
        for selector in selectors:
            try:
                if selector.startswith('.'):
                    listings = soup.select(selector)
                elif '[' in selector:
                    if 'data-view' in selector:
                        listings = soup.find_all('div', attrs={'data-view': True})
                    else:
                        listings = soup.find_all('div', class_=lambda x: x and 's-item' in str(x))
                else:
                    parts = selector.split('.')
                    if len(parts) == 2:
                        tag, class_name = parts
                        listings = soup.find_all(tag, class_=class_name)
                    else:
                        listings = soup.find_all(selector)
                
                if listings and len(listings) > 2:  # Need more than just filters
                    print(f"✅ Found {len(listings)} listings with: {selector}")
                    return listings
                elif listings:
                    print(f"⚠️  Only {len(listings)} listings with: {selector}")
                    
            except Exception as e:
                print(f"⚠️  Selector {selector} failed: {e}")
                continue
        
        # If no good selectors work, try to find ANY structured content
        print("🔍 Trying fallback: looking for any structured content...")
        fallback_listings = soup.find_all('div', class_=True)
        
        # Filter for divs that might be listings
        potential_listings = []
        for div in fallback_listings:
            classes = ' '.join(div.get('class', []))
            if any(term in classes.lower() for term in ['item', 'listing', 'result', 'product']):
                potential_listings.append(div)
        
        if potential_listings:
            print(f"⚡ Found {len(potential_listings)} potential listings via fallback")
            return potential_listings[:50]  # Limit to reasonable number
        
        return []
    
    def extract_title_multiple_ways(self, listing):
        """Try multiple ways to extract title"""
        methods = [
            lambda: listing.find('h3', class_='s-item__title'),
            lambda: listing.find('h3'),
            lambda: listing.find('a', class_='s-item__link'),
            lambda: listing.find('a'),
            lambda: listing.find('span', {'role': 'heading'}),
            lambda: listing.select_one('.s-item__title'),
            lambda: listing.select_one('[data-testid*="title"]'),
            lambda: listing.find('span', class_='BOLD'),
            lambda: listing.find('*', string=lambda text: text and len(text) > 15)
        ]
        
        for method in methods:
            try:
                elem = method()
                if elem:
                    title = elem.get_text(strip=True)
                    if title and len(title) > 10:
                        # Clean up title
                        title = title.replace('Opens in a new window or tab', '').strip()
                        title = title.replace('New Listing', '').strip()
                        if len(title) > 100:
                            title = title[:100] + "..."
                        return title
            except:
                continue
        
        return None
    
    def extract_price(self, listing):
        """Extract price from listing"""
        try:
            price_elem = listing.find('span', class_='s-item__price')
            if price_elem:
                return price_elem.get_text(strip=True)
        except:
            pass
        return "Price not found"
    
    def extract_link(self, listing):
        """Extract link from listing"""
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
        """Extract image from listing"""
        try:
            img_elem = listing.find('img')
            if img_elem and img_elem.get('src'):
                image = img_elem['src']
                if 's-l140' in image:
                    image = image.replace('s-l140', 's-l300')
                return image
        except:
            pass
        return "https://via.placeholder.com/200x150?text=No+Image"
    
    def extract_time_left(self, listing):
        """Extract time left from listing"""
        try:
            time_elem = listing.find('span', class_='s-item__time-left')
            if time_elem:
                return time_elem.get_text(strip=True)
        except:
            pass
        return "Time not specified"
    
    def check_auction_format(self, listing):
        """Check if item is auction or buy it now"""
        try:
            # Look for auction indicators
            text = listing.get_text().lower()
            if 'bid' in text or 'auction' in text:
                return "Auction"
            elif 'buy it now' in text or 'fixed price' in text:
                return "Buy It Now"
        except:
            pass
        return "Unknown"
    
    def generate_html(self, results):
        """Generate HTML results page"""
        if not results:
            cards_html = '''
            <div style="text-align: center; padding: 50px; background: rgba(255,255,255,0.1); border-radius: 15px; color: white; margin: 20px;">
                <h2>🔍 No GameBoy Advance items found</h2>
                <p>This could be due to:</p>
                <ul style="display: inline-block; text-align: left; margin: 20px 0;">
                    <li>No current GBA items available</li>
                    <li>All current auctions may have ended</li>
                    <li>eBay may be showing different layout</li>
                </ul>
                <p><strong>Try running again later - eBay inventory changes frequently!</strong></p>
                <p style="margin-top: 20px; font-size: 14px; opacity: 0.8;">
                    Check latest_ebay_response.html file to see what eBay returned
                </p>
            </div>
            '''
        else:
            cards = []
            for result in results:
                # Add format indicator
                format_badge = ""
                if result['format'] == "Auction":
                    format_badge = '<span style="background: #e74c3c; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin-left: 8px;">🔨 Auction</span>'
                elif result['format'] == "Buy It Now":
                    format_badge = '<span style="background: #27ae60; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; margin-left: 8px;">💳 Buy Now</span>'
                
                card = f'''
                <div style="background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin-bottom: 20px; cursor: pointer; transition: all 0.3s; break-inside: avoid;" 
                     onclick="window.open('{result['link']}', '_blank')" 
                     onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 35px rgba(0,0,0,0.2)'" 
                     onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'">
                    <img src="{result['image']}" style="width: 100%; height: 200px; object-fit: cover;" 
                         onerror="this.src='https://via.placeholder.com/300x200/f8f9fa/6c757d?text=Image+Not+Available'">
                    <div style="padding: 20px;">
                        <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 16px; line-height: 1.4; min-height: 3em;">
                            {result['title']} {format_badge}
                        </h3>
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
    <title>GameBoy Advance Items Found</title>
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
        <h1>🎮 GameBoy Advance Items</h1>
        <p style="font-size: 1.2rem; margin-bottom: 20px;">Found on eBay - Live Results</p>
        <div class="stats">Found {len(results)} items • Updated {timestamp}</div>
    </div>
    <div class="container">
        {cards_html}
    </div>
    <div class="footer">
        <p>Powered by Final eBay Scraper • Click any card to view on eBay</p>
        <p>Mix of auctions and Buy It Now • Run again for latest inventory</p>
    </div>
</body>
</html>
        '''
        
        return html
    
    def run(self):
        """Main execution"""
        print("🚀 Starting FINAL eBay GBA Scraper")
        print("This version adapts to current eBay layout and finds ANY available GBA items")
        print("=" * 70)
        
        results = self.try_different_searches()
        
        # Remove duplicates
        unique_results = []
        seen_titles = set()
        
        for result in results:
            title_key = result['title'].lower().replace(' ', '').replace('-', '')[:40]
            if title_key not in seen_titles:
                unique_results.append(result)
                seen_titles.add(title_key)
        
        removed = len(results) - len(unique_results)
        if removed > 0:
            print(f"\\n🗑️  Removed {removed} duplicates")
        
        print(f"\\n✅ Final result: {len(unique_results)} unique GBA items")
        
        # Generate HTML
        print("\\n🎨 Generating HTML...")
        html = self.generate_html(unique_results)
        
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
        
        print("\\n" + "=" * 70)
        if unique_results:
            print(f"✅ SUCCESS! Found {len(unique_results)} GameBoy Advance items")
            auction_count = sum(1 for r in unique_results if r['format'] == 'Auction')
            buy_now_count = len(unique_results) - auction_count
            print(f"📊 {auction_count} auctions, {buy_now_count} Buy It Now listings")
        else:
            print("⚠️  No GBA items found")
            print("💡 This could mean:")
            print("   • No GBA items currently listed")
            print("   • All recent auctions have ended") 
            print("   • eBay is showing different content")
            print("\\n🔍 Check 'latest_ebay_response.html' to see what eBay returned")
        print("=" * 70)

if __name__ == "__main__":
    scraper = FinalEbayScraper()
    scraper.run()
    input("\\nPress Enter to exit...")
