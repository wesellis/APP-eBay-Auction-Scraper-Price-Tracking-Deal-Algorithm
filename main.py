#!/usr/bin/env python3
"""
eBay GameBoy Advance Auction Scraper
Main entry point for the application

Usage:
    python main.py [--mode MODE] [--debug] [--help]

Modes:
    optimized   - High-performance async scraping (default)
    standard    - Standard synchronous scraping
    fallback    - Direct eBay search links when blocked
    test        - Performance comparison test
"""

import argparse
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="eBay GameBoy Advance Auction Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Run optimized version
    python main.py --mode standard    # Run standard version  
    python main.py --mode fallback    # Generate fallback page
    python main.py --mode test        # Performance test
    python main.py --debug            # Enable debug output
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["optimized", "standard", "fallback", "test"],
        default="optimized",
        help="Scraping mode (default: optimized)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    parser.add_argument(
        "--output",
        default="output/gba_auctions.html",
        help="Output file path (default: output/gba_auctions.html)",
    )

    args = parser.parse_args()

    # Set debug mode
    if args.debug:
        import os

        os.environ["DEBUG"] = "true"

    # Import and run appropriate mode
    try:
        if args.mode == "optimized":
            from core.app_optimized import OptimizedGBAScraperApp

            app = OptimizedGBAScraperApp(output_file=args.output)
            return app.run()

        elif args.mode == "standard":
            from core.app_standard import StandardGBAScraperApp

            app = StandardGBAScraperApp(output_file=args.output)
            return app.run()

        elif args.mode == "fallback":
            from core.app_fallback import FallbackGBAScraperApp

            app = FallbackGBAScraperApp(output_file=args.output)
            return app.run()

        elif args.mode == "test":
            from tests.performance_test import run_performance_test

            return run_performance_test()

    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("📁 Please ensure all files are in the correct src/ directory structure")
        return False

    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
