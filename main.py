"""
Main script for the eBay GameBoy Advance auction scraper
Modular, robust version with comprehensive error handling
"""

import sys
import os
import webbrowser
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from scraper import EbayScraper
    from html_generator import HTMLGenerator
    from config import OUTPUT_FILENAME
    from utils import Logger, Timer
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all module files are in the same directory:")
    print("- config.py")
    print("- utils.py") 
    print("- scraper.py")
    print("- html_generator.py")
    input("Press Enter to exit...")
    sys.exit(1)

class GBAScraperApp:
    """Main application class"""
    
    def __init__(self):
        self.scraper = EbayScraper()
        self.html_generator = HTMLGenerator()
        self.timer = Timer()
    
    def run(self):
        """Main application entry point"""
        try:
            self.timer.start()
            self._print_banner()
            
            # Scrape auctions
            Logger.info("Starting auction scrape...")
            auctions = self.scraper.scrape_all_terms()
            
            if not auctions:
                Logger.warning("No auctions found - this could be temporary")
                Logger.info("Possible reasons:")
                Logger.info("• No GBA auctions ending soon")
                Logger.info("• eBay anti-bot protection activated") 
                Logger.info("• Network connectivity issues")
                Logger.info("• Search terms need adjustment")
            
            # Generate HTML
            Logger.info("Creating HTML page...")
            html_content = self.html_generator.generate_page(auctions)
            
            # Save to file
            success = self.html_generator.save_to_file(html_content, OUTPUT_FILENAME)
            
            if success:
                self._print_results(auctions)
                self._open_html_file()
            else:
                Logger.error("Failed to save HTML file")
            
        except KeyboardInterrupt:
            Logger.warning("\\nScraping stopped by user")
        except Exception as e:
            Logger.error(f"Unexpected error: {e}")
            Logger.info("This might be due to:")
            Logger.info("• eBay's anti-bot protection")
            Logger.info("• Network connectivity issues") 
            Logger.info("• Changes in eBay's page structure")
        finally:
            self._print_footer()
    
    def _print_banner(self):
        """Print application banner"""
        print("=" * 60)
        print("GAMEBOY ADVANCE AUCTION SCRAPER v2.0")
        print("=" * 60)
        print("Searching eBay for GBA auctions ending soon...")
        print("Creating beautiful HTML results page...")
        print("Modular, robust, and respectful scraping")
        print("-" * 60)
    
    def _print_results(self, auctions):
        """Print final results summary"""
        elapsed = self.timer.elapsed_str()
        
        print("\\n" + "=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"Results: {len(auctions)} GameBoy Advance auctions found")
        print(f"Time taken: {elapsed}")
        print(f"HTML file: {OUTPUT_FILENAME}")
        print(f"Opening '{OUTPUT_FILENAME}' in your browser...")
        
        if auctions:
            print("\\nSample results:")
            for i, auction in enumerate(auctions[:3], 1):
                title = auction['title'][:50] + "..." if len(auction['title']) > 50 else auction['title']
                print(f"  {i}. {title} - {auction['price']}")
            
            if len(auctions) > 3:
                print(f"  ... and {len(auctions) - 3} more!")
        
        print("\\nRun again anytime to get fresh results!")
    
    def _open_html_file(self):
        """Open the HTML file in the default browser"""
        try:
            html_path = os.path.abspath(OUTPUT_FILENAME)
            if os.path.exists(html_path):
                Logger.success(f"Opening {OUTPUT_FILENAME} in browser...")
                webbrowser.open(f"file://{html_path}")
            else:
                Logger.warning(f"HTML file not found: {html_path}")
        except Exception as e:
            Logger.error(f"Could not open HTML file: {e}")
            Logger.info(f"Please manually open: {OUTPUT_FILENAME}")
    
    def _print_footer(self):
        """Print application footer"""
        print("\\n" + "-" * 60)
        print("Thanks for using GBA Auction Scraper!")
        print("Tip: Run regularly to catch new auctions")
        print("Always respect eBay's terms of service")
        print("-" * 60)

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import requests
        import bs4
        return True
    except ImportError as e:
        Logger.error("Missing required packages!")
        Logger.info("Please install: pip install requests beautifulsoup4")
        return False

def main():
    """Main entry point"""
    print("Checking dependencies...")
    
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    try:
        app = GBAScraperApp()
        app.run()
    except Exception as e:
        Logger.error(f"Fatal error: {e}")
        Logger.info("Please check your internet connection and try again")
    finally:
        input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
