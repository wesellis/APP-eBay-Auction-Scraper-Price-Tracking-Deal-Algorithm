# eBay Auction Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

A Python tool for monitoring eBay auctions and tracking prices.

## Overview

This tool scrapes eBay auction listings and helps track prices over time. It includes basic filtering and can generate HTML reports of results.

## Features

- Scrapes eBay auction listings
- Multiple search term support
- Async and synchronous scraping modes
- Price extraction and formatting
- HTML report generation
- Basic duplicate detection
- Configurable search parameters

## Requirements

- Python 3.8 or higher
- Internet connection

## Installation

```bash
git clone https://github.com/wesellis/ebay-auction-scraper.git
cd ebay-auction-scraper
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py
```

This will scrape eBay for the configured search terms and generate an HTML report in the `output/` directory.

### Configuration

Edit `src/config.py` to customize:

- Search terms
- Maximum listings per search
- Performance settings
- Output file location

Example configuration:

```python
SEARCH_TERMS = [
    "gameboy+advance",
    "gba+sp",
    "nintendo+handheld"
]

SCRAPING.max_listings_per_search = 30
SCRAPING.max_total_listings = 100
```

### Operating Modes

The scraper supports different modes:

- **Optimized Mode**: Uses async requests for faster scraping (default)
- **Standard Mode**: Synchronous requests
- **Test Mode**: Runs performance comparisons

## Project Structure

```
ebay-auction-scraper/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── config.py          # Configuration settings
│   ├── core/              # Core scraping logic
│   ├── utils/             # Helper functions
│   └── generators/        # Report generators
├── output/                # Generated reports
└── tests/                 # Test files
```

## Technical Details

### Dependencies

- **aiohttp**: Async HTTP requests
- **BeautifulSoup4**: HTML parsing
- **lxml**: XML/HTML parser
- **requests**: HTTP client
- **psutil**: System monitoring

### Performance Settings

The tool includes configurable performance settings:

- Concurrent request limits
- Connection pooling
- Memory usage caps
- Request timeouts

## Known Limitations

- Requires stable internet connection
- eBay may rate limit requests
- HTML structure changes can break parsing
- No built-in authentication
- Basic error handling

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/name`)
5. Open Pull Request

## Legal Notice

This tool is for educational purposes. Users are responsible for:
- Respecting eBay's Terms of Service
- Following rate limits
- Using data ethically and legally
- Complying with local laws

No warranty is provided. Use at your own risk.

## License

MIT License - see LICENSE file for details.

## Author

Wesley Ellis

---

## Project Status & Roadmap

**Completion: ~60%**

### What Works
- ✅ eBay auction scraping with BeautifulSoup
- ✅ Async and synchronous scraping modes
- ✅ Multiple search term support
- ✅ HTML report generation
- ✅ Price extraction and formatting
- ✅ Basic duplicate detection
- ✅ Configurable performance settings
- ✅ Connection pooling and async optimization

### Known Limitations & Missing Features

**Core Features Missing:**
- ❌ **Price Tracking Over Time**: Project name mentions "Price Tracking" but no database or historical tracking implemented
- ❌ **Deal Algorithm**: Project name mentions "Deal Algorithm" but no price comparison or deal detection logic
- ❌ **Data Persistence**: No database - results only saved to HTML reports
- ❌ **Notifications**: No email/push notifications for deals or price drops
- ❌ **Watchlist Management**: No ability to save and monitor specific items

**Technical Limitations:**
- ⚠️ **eBay API**: Uses web scraping instead of official eBay API (fragile to HTML changes)
- ⚠️ **Authentication**: No eBay account login support
- ⚠️ **Rate Limiting**: Basic delays but no sophisticated anti-blocking measures
- ⚠️ **Error Recovery**: Minimal retry logic and error handling
- ⚠️ **Testing**: No automated tests

**Missing Features:**
- ⚠️ **GUI**: Command-line only, no desktop or web interface
- ⚠️ **Scheduling**: No built-in cron/scheduled scraping
- ⚠️ **Filtering**: Basic filtering only - no advanced price ranges, condition filters
- ⚠️ **Export Formats**: HTML only - no CSV, JSON, or database export
- ⚠️ **Analytics**: No price history graphs or trend analysis

### What Needs Work

1. **Price History Database** - Implement SQLite/PostgreSQL for tracking prices over time
2. **Deal Detection Algorithm** - Add logic to identify good deals based on historical prices
3. **eBay API Integration** - Switch from scraping to official eBay Finding API (more reliable)
4. **Notification System** - Email/SMS alerts for price drops and new listings
5. **Web Dashboard** - Flask/FastAPI interface for viewing results and managing watchlists
6. **Advanced Filtering** - Price ranges, seller ratings, item condition, shipping options
7. **Scheduled Monitoring** - Built-in scheduler for automatic periodic scraping
8. **Better Error Handling** - Retry logic, proxy support, CAPTCHA detection
9. **Testing Suite** - Unit tests and integration tests
10. **Export Options** - CSV, JSON, Excel export formats

### Current Status

This project is a **basic web scraper** that works for quick eBay searches. Despite the project name suggesting "Price Tracking" and "Deal Algorithm" functionality, those features are not implemented. It's useful for one-time auction research but not for ongoing price monitoring or deal hunting.

### Contributing

If you'd like to help implement the missing features, contributions are welcome. Priority areas:
1. Adding SQLite database for price history
2. Implementing deal detection logic
3. Migrating to eBay Finding API
4. Adding tests

---

**Note**: This is a personal project for learning web scraping techniques. It may not work reliably due to changes in eBay's website structure. The project name is aspirational - price tracking and deal algorithm features are not yet implemented.
