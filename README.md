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

**Note**: This is a personal project for learning web scraping techniques. It may not work reliably due to changes in eBay's website structure.
