"""
Optimized main application with performance monitoring and error recovery
"""

import asyncio
import os
import sys
import webbrowser
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Check for optimized modules first, fall back to original
try:
    from config_optimized import DEBUG_MODE, OUTPUT_FILENAME
    from scraper_optimized import scrape_auctions_sync
    from utils_optimized import HighPerformanceTimer, Logger
    print("✅ Using optimized modules")
except ImportError:
    try:
        from scraper import EbayScraper

        from config import DEBUG_MODE, OUTPUT_FILENAME
        from utils import Logger
        from utils import Timer as HighPerformanceTimer
        print("⚠️ Falling back to original modules")
        
        # Create wrapper for compatibility
        def scrape_auctions_sync():
            scraper = EbayScraper()
            return scraper.scrape_all_terms()
    except ImportError as e:
        print(f"❌ Critical import error: {e}")
        print("\nRequired files:")
        print("- scraper.py (or scraper_optimized.py)")
        print("- utils.py (or utils_optimized.py)")
        print("- config.py (or config_optimized.py)")
        print("- html_generator.py")
        input("Press Enter to exit...")
        sys.exit(1)

try:
    from html_generator import HTMLGenerator
except ImportError:
    print("❌ html_generator.py not found")
    sys.exit(1)

class OptimizedGBAScraperApp:
    """Optimized main application with performance monitoring"""
    
    def __init__(self):
        self.html_generator = HTMLGenerator()
        self.timer = HighPerformanceTimer()
        self.performance_stats = {}
    
    def check_dependencies(self) -> bool:
        """Check required dependencies with detailed feedback"""
        missing_deps = []
        
        try:
            import requests
        except ImportError:
            missing_deps.append("requests")
        
        try:
            import bs4
        except ImportError:
            missing_deps.append("beautifulsoup4")
        
        # Check for async dependencies
        try:
            import aiohttp
            self.has_async = True
            Logger.success("🚀 Async support available (aiohttp found)")
        except ImportError:
            self.has_async = False
            Logger.warning("⚠️ Async support unavailable (install aiohttp for better performance)")
        
        if missing_deps:
            Logger.error("❌ Missing required packages:")
            for dep in missing_deps:
                Logger.error(f"  • {dep}")
            Logger.info("\\nInstall with: pip install " + " ".join(missing_deps))
            return False
        
        Logger.success("✅ All dependencies satisfied")
        return True
    
    def print_banner(self):
        """Enhanced banner with performance info"""
        print("=" * 65)
        print("🎮 GAMEBOY ADVANCE AUCTION SCRAPER v3.0 - OPTIMIZED")
        print("=" * 65)
        print("🚀 High-performance async scraping with intelligent deduplication")
        print("🎯 Smart GBA filtering with confidence scoring")
        print("💾 Memory-optimized processing with caching")
        print("🌐 Beautiful responsive HTML results")
        
        if hasattr(self, 'has_async') and self.has_async:
            print("⚡ Async mode: ENABLED (faster performance)")
        else:
            print("🐌 Sync mode: ENABLED (standard performance)")
        
        print("-" * 65)
    
    def print_performance_summary(self):
        """Print detailed performance metrics"""
        if not self.performance_stats:
            return
        
        print("\\n" + "📊 PERFORMANCE METRICS")
        print("-" * 40)
        
        for metric, value in self.performance_stats.items():
            if isinstance(value, float):
                print(f"{metric}: {value:.2f}")
            else:
                print(f"{metric}: {value}")
    
    def handle_scraping_error(self, error: Exception) -> bool:
        """Intelligent error handling with recovery suggestions"""
        error_str = str(error).lower()
        
        if "429" in error_str or "rate limit" in error_str:
            Logger.warning("🛑 eBay rate limiting detected")
            Logger.info("💡 Suggestions:")
            Logger.info("  • Wait 5-10 minutes before retrying")
            Logger.info("  • eBay may be experiencing high traffic")
            Logger.info("  • Try again during off-peak hours")
            return True
        
        elif "timeout" in error_str or "connection" in error_str:
            Logger.warning("🌐 Network connectivity issue")
            Logger.info("💡 Suggestions:")
            Logger.info("  • Check your internet connection")
            Logger.info("  • Try again in a few moments")
            Logger.info("  • Consider using a VPN if blocked")
            return True
        
        elif "403" in error_str or "blocked" in error_str:
            Logger.warning("🚫 Access blocked by eBay")
            Logger.info("💡 This is likely temporary - try again later")
            return True
        
        else:
            Logger.error(f"💥 Unexpected error: {error}")
            Logger.info("💡 This might be due to:")
            Logger.info("  • Changes in eBay's page structure")
            Logger.info("  • Temporary service disruption")
            Logger.info("  • Local system issues")
            return False
    
    def create_fallback_page(self) -> str:
        """Create fallback page when scraping fails"""
        from final_solution import GBAAuctionFinder
        
        Logger.info("🔄 Creating fallback page with direct search links")
        finder = GBAAuctionFinder()
        return finder.generate_interactive_html()
    
    def run(self):
        """Optimized main execution flow"""
        try:
            self.timer.start()
            self.print_banner()
            
            # Dependency check
            if not self.check_dependencies():
                return False
            
            # Start scraping
            Logger.info("🔍 Starting auction search...")
            self.timer.split("scraping_start")
            
            try:
                # Use optimized scraper
                auctions = scrape_auctions_sync()
                scraping_time = self.timer.split("scraping_end")
                
                self.performance_stats.update({
                    'scraping_time_seconds': scraping_time,
                    'auctions_found': len(auctions) if auctions else 0
                })
                
            except Exception as e:
                # Intelligent error handling
                should_create_fallback = self.handle_scraping_error(e)
                
                if should_create_fallback:
                    html_content = self.create_fallback_page()
                    success = self.html_generator.save_to_file(html_content, OUTPUT_FILENAME)
                    
                    if success:
                        self.open_html_file()
                        Logger.success("✅ Fallback page created successfully")
                        return True
                
                return False
            
            # Generate HTML
            Logger.info("🎨 Creating beautiful HTML page...")
            html_start = self.timer.split("html_start")
            
            html_content = self.html_generator.generate_page(auctions)
            success = self.html_generator.save_to_file(html_content, OUTPUT_FILENAME)
            
            html_time = self.timer.split("html_end") - html_start
            self.performance_stats['html_generation_time'] = html_time
            
            if success:
                self.print_results(auctions)
                self.open_html_file()
                return True
            else:
                Logger.error("❌ Failed to save HTML file")
                return False
                
        except KeyboardInterrupt:
            Logger.warning("\\n⏹️ Stopped by user")
            return False
        except Exception as e:
            Logger.error(f"💥 Fatal error: {e}")
            return False
        finally:
            self.print_performance_summary()
            self.print_footer()
    
    def print_results(self, auctions):
        """Enhanced results summary with insights"""
        total_time = self.timer.elapsed_str()
        
        print("\\n" + "🎉 SCRAPING COMPLETE!")
        print("=" * 50)
        print(f"📦 Results: {len(auctions)} GameBoy Advance auctions found")
        print(f"⏱️ Total time: {total_time}")
        print(f"📄 HTML file: {OUTPUT_FILENAME}")
        
        if auctions:
            # Show top results by confidence if available
            sorted_auctions = sorted(auctions, key=lambda x: x.get('confidence', 0), reverse=True)
            
            print("\\n🏆 Top results:")
            for i, auction in enumerate(sorted_auctions[:3], 1):
                title = auction['title'][:55] + "..." if len(auction['title']) > 55 else auction['title']
                confidence = auction.get('confidence', 0)
                confidence_str = f" ({confidence:.1f}★)" if confidence > 0 else ""
                print(f"  {i}. {title} - {auction['price']}{confidence_str}")
            
            if len(auctions) > 3:
                print(f"  ... and {len(auctions) - 3} more!")
            
            # Price analysis
            prices = []
            for auction in auctions:
                price_text = auction['price'].replace('$', '').replace(',', '')
                try:
                    if 'to' not in price_text and price_text.replace('.', '').isdigit():
                        prices.append(float(price_text))
                except:
                    pass
            
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                print(f"\\n💰 Price range: ${min_price:.2f} - ${max_price:.2f} (avg: ${avg_price:.2f})")
        
        print("\\n🔄 Run again anytime for fresh results!")
    
    def open_html_file(self):
        """Open HTML file with error handling"""
        try:
            html_path = os.path.abspath(OUTPUT_FILENAME)
            if os.path.exists(html_path):
                Logger.success(f"🌐 Opening {OUTPUT_FILENAME} in browser...")
                webbrowser.open(f"file://{html_path}")
            else:
                Logger.warning(f"⚠️ HTML file not found: {html_path}")
        except Exception as e:
            Logger.error(f"❌ Could not open HTML file: {e}")
            Logger.info(f"📁 Please manually open: {OUTPUT_FILENAME}")
    
    def print_footer(self):
        """Enhanced footer with tips"""
        print("\\n" + "-" * 65)
        print("✨ Thanks for using the Optimized GBA Auction Scraper!")
        print("💡 Pro tips:")
        print("  • Run during peak hours (evenings/weekends) for more auctions")
        print("  • Check the 'Auctions Ending Soon' regularly for time-sensitive deals")
        print("  • Look for AGS-101 models (backlit screens) - they're worth more!")
        print("  • Always verify condition and authenticity before bidding")
        print("🤝 Always respect eBay's terms of service")
        print("-" * 65)

def main():
    """Enhanced main entry point"""
    print("🔧 Initializing Optimized GBA Auction Scraper...")
    
    try:
        app = OptimizedGBAScraperApp()
        success = app.run()
        
        if not success:
            print("\\n⚠️ Scraping encountered issues, but fallback options may be available.")
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        print("🆘 Please check your setup and try again")
    finally:
        input("\\n⏸️ Press Enter to exit...")

if __name__ == "__main__":
    main()
