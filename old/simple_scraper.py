"""
Super simple eBay scraper - no filtering, just get anything
"""

import requests
from bs4 import BeautifulSoup
import webbrowser
import os

def simple_scrape():
    print("SIMPLE SCRAPER - Getting ANY eBay listings...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = "https://www.ebay.com/sch/i.html?_nkw=gameboy+advance&LH_Auction=1"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to get eBay page")
            return
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find ANY listings
        listings = soup.find_all('div', class_='s-item')
        print(f"Found {len(listings)} listings")
        
        results = []
        
        for i, listing in enumerate(listings[:10]):
            try:
                # Try multiple ways to get title
                title = None
                for selector in ['h3', 'a']:
                    elem = listing.find(selector)
                    if elem:
                        title = elem.get_text(strip=True)
                        if title and len(title) > 10:
                            break
                
                # Try to get price
                price = "No price"
                price_elem = listing.find('span', class_='s-item__price')
                if price_elem:
                    price = price_elem.get_text(strip=True)
                
                # Try to get link
                link = "#"
                link_elem = listing.find('a')
                if link_elem:
                    link = link_elem.get('href', '#')
                
                # Try to get image
                image = "https://via.placeholder.com/200x150?text=No+Image"
                img_elem = listing.find('img')
                if img_elem:
                    image = img_elem.get('src', image)
                
                if title:
                    results.append({
                        'title': title,
                        'price': price,
                        'link': link,
                        'image': image
                    })
                    print(f"{i+1}. {title[:60]}... - {price}")
                    
            except Exception as e:
                print(f"Error processing listing {i}: {e}")
                continue
        
        # Generate simple HTML
        if results:
            html = generate_simple_html(results)
            with open('simple_results.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"\\nGenerated simple_results.html with {len(results)} items")
            
            # Open in browser
            html_path = os.path.abspath('simple_results.html')
            webbrowser.open(f"file://{html_path}")
            print("Opening in browser...")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error: {e}")

def generate_simple_html(results):
    cards = ""
    for result in results:
        cards += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 15px; border-radius: 8px; background: white;">
            <img src="{result['image']}" style="width: 200px; height: 150px; object-fit: cover; float: left; margin-right: 15px;">
            <h3>{result['title']}</h3>
            <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">{result['price']}</p>
            <a href="{result['link']}" target="_blank" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">View on eBay</a>
            <div style="clear: both;"></div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple eBay Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #333; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Simple eBay Scraper Results</h1>
        {cards}
    </body>
    </html>
    """

if __name__ == "__main__":
    simple_scrape()
