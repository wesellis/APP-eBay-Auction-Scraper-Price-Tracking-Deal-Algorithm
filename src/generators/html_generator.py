"""
HTML generation for the auction results
"""

from utils import get_timestamp, sanitize_html, Logger

class HTMLGenerator:
    """Generate beautiful HTML pages for auction results"""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self):
        """Main HTML template with modern styling"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameBoy Advance Auctions Ending Soon</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 20px;
        }}
        
        .header h1 {{
            font-size: clamp(2rem, 5vw, 3rem);
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: clamp(1rem, 3vw, 1.2rem);
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .stats {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            display: inline-block;
            backdrop-filter: blur(10px);
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            columns: 4;
            column-gap: 25px;
            column-fill: balance;
        }}
        
        @media (max-width: 1200px) {{ .container {{ columns: 3; }} }}
        @media (max-width: 900px) {{ .container {{ columns: 2; }} }}
        @media (max-width: 600px) {{ .container {{ columns: 1; }} }}
        
        .auction-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            margin-bottom: 25px;
            break-inside: avoid;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
        }}
        
        .auction-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }}
        
        .card-image-container {{
            position: relative;
            overflow: hidden;
            background: #f8f9fa;
        }}
        
        .card-image {{
            width: 100%;
            height: auto;
            min-height: 200px;
            object-fit: cover;
            transition: transform 0.3s ease;
            display: block;
        }}
        
        .auction-card:hover .card-image {{
            transform: scale(1.05);
        }}
        
        .time-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            background: rgba(231, 76, 60, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }}
        
        .card-content {{
            padding: 24px;
        }}
        
        .card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 12px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 4.2rem;
        }}
        
        .card-price {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #e74c3c;
            margin-bottom: 8px;
        }}
        
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid #ecf0f1;
        }}
        
        .bid-info {{
            font-size: 0.9rem;
            color: #7f8c8d;
        }}
        
        .view-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .view-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .no-results {{
            text-align: center;
            color: white;
            font-size: 1.3rem;
            margin-top: 60px;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}
        
        .loading {{
            text-align: center;
            color: white;
            font-size: 1.1rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
        }}
        
        .card-image[src=""] {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        .auction-card:focus {{
            outline: 3px solid rgba(255,255,255,0.8);
            outline-offset: 2px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GameBoy Advance Auctions</h1>
        <div class="subtitle">Ending Soon - Live Results</div>
        <div class="stats">
            Found {auction_count} auctions • Updated {timestamp}
        </div>
    </div>
    
    <div class="container">
        {auction_cards}
    </div>
    
    <div class="footer">
        <p>Powered by Python eBay Scraper • Data refreshed automatically</p>
        <p>Click any card to view the auction on eBay</p>
    </div>
    
    <script>
        document.querySelectorAll('.auction-card').forEach((card, index) => {{
            card.addEventListener('click', function(e) {{
                e.preventDefault();
                const link = this.getAttribute('data-link');
                if (link) {{
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {{
                        this.style.transform = '';
                        window.open(link, '_blank');
                    }}, 100);
                }}
            }});
            
            card.setAttribute('tabindex', '0');
            card.addEventListener('keydown', function(e) {{
                if (e.key === 'Enter' || e.key === ' ') {{
                    e.preventDefault();
                    this.click();
                }}
            }});
        }});
        
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.auction-card');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {{
                    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 100);
            }});
        }});
        
        document.querySelectorAll('.card-image').forEach(img => {{
            img.addEventListener('error', function() {{
                this.src = 'https://via.placeholder.com/300x200/f8f9fa/6c757d?text=Image+Not+Available';
                this.style.opacity = '0.7';
            }});
        }});
    </script>
</body>
</html>"""
    
    def generate_card_html(self, auction):
        """Generate HTML for a single auction card"""
        # Sanitize data
        title = sanitize_html(auction.get('title', 'No Title'))
        price = sanitize_html(auction.get('price', 'Price not available'))
        link = auction.get('link', '#')
        image = auction.get('image', 'https://via.placeholder.com/300x200?text=No+Image')
        time_left = sanitize_html(auction.get('time_left', 'Ending soon'))
        
        # Generate card HTML
        card_html = f"""
        <div class="auction-card" data-link="{link}" role="button" aria-label="View auction: {title}">
            <div class="card-image-container">
                <img src="{image}" alt="{title}" class="card-image" loading="lazy">
                <div class="time-badge">{time_left}</div>
            </div>
            <div class="card-content">
                <div class="card-title">{title}</div>
                <div class="card-price">{price}</div>
                <div class="card-footer">
                    <div class="bid-info">Click to view</div>
                    <button class="view-btn" aria-label="View this auction">View</button>
                </div>
            </div>
        </div>"""
        
        return card_html
    
    def generate_no_results_html(self):
        """Generate HTML for when no results are found"""
        return """
        <div class="no-results">
            <h2>No GameBoy Advance auctions found</h2>
            <p>This could be due to:</p>
            <ul style="text-align: left; display: inline-block; margin: 20px 0;">
                <li>No current GBA auctions ending soon</li>
                <li>eBay temporarily blocking requests</li>
                <li>Network connectivity issues</li>
            </ul>
            <p>Try running the scraper again in a few minutes!</p>
        </div>"""
    
    def generate_page(self, auction_data):
        """Generate complete HTML page"""
        try:
            Logger.info("Generating HTML page...")
            
            if not auction_data:
                auction_cards = self.generate_no_results_html()
                auction_count = 0
            else:
                # Generate cards
                cards = []
                for auction in auction_data:
                    card_html = self.generate_card_html(auction)
                    cards.append(card_html)
                
                auction_cards = '\\n'.join(cards)
                auction_count = len(auction_data)
            
            # Get timestamp
            timestamp = get_timestamp()
            
            # Fill template
            html_content = self.template.format(
                auction_cards=auction_cards,
                timestamp=timestamp,
                auction_count=auction_count
            )
            
            Logger.success(f"Generated HTML with {auction_count} auctions")
            return html_content
            
        except Exception as e:
            Logger.error(f"Error generating HTML: {e}")
            return self._generate_error_page(str(e))
    
    def _generate_error_page(self, error_message):
        """Generate error page when HTML generation fails"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Error - GBA Auction Scraper</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
        .error {{ background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #e74c3c; }}
        .error-details {{ background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Error Generating Results</h1>
        <p>There was an error creating the auction results page.</p>
        <div class="error-details">
            <strong>Error:</strong> {sanitize_html(error_message)}
        </div>
        <p>Please try running the scraper again. If the problem persists, check your internet connection.</p>
    </div>
</body>
</html>"""
    
    def save_to_file(self, html_content, filename):
        """Save HTML content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            Logger.success(f"HTML saved as '{filename}'")
            return True
        except Exception as e:
            Logger.error(f"Error saving HTML file: {e}")
            return False
