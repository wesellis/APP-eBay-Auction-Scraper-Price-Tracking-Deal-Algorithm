# GameBoy Advance eBay Auction Scraper

A robust, modular Python scraper that finds GameBoy Advance auctions ending soon on eBay and generates a beautiful HTML results page.

## 🚀 Features

- **Modular Design**: Clean separation of concerns across multiple files
- **Robust Error Handling**: Graceful handling of network issues and eBay's anti-bot protection
- **Beautiful UI**: Modern masonry-style HTML layout with hover effects
- **Smart Filtering**: Only shows GameBoy Advance related items
- **Duplicate Removal**: Automatically removes duplicate listings
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Multiple Search Terms**: Uses various GBA-related keywords for comprehensive results

## 📁 Project Structure

```
A:\Project\Ebay Scraper\
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── scraper.py           # eBay scraping logic
├── html_generator.py    # HTML page generation
├── utils.py             # Utility functions and helpers
└── README.md            # This file
```

## 🛠️ Installation

1. **Install Python dependencies:**
   ```bash
   pip install requests beautifulsoup4
   ```

2. **Run the scraper:**
   ```bash
   python main.py
   ```

## 📋 Usage

1. **Run the main script:**
   ```bash
   cd "A:\Project\Ebay Scraper"
   python main.py
   ```

2. **View results:**
   - Open `gba_auctions.html` in your browser
   - Click any auction card to view on eBay
   - Enjoy the beautiful masonry layout!

## ⚙️ Configuration

Edit `config.py` to customize:

- **Search Terms**: Add/modify search keywords
- **Request Settings**: Timeouts, delays, retry limits
- **Output Settings**: Filename, image settings
- **CSS Selectors**: Update if eBay changes their layout

## 🔧 Modules Overview

### `main.py`
- Application entry point
- Coordinates scraping and HTML generation
- Handles user interaction and error reporting

### `config.py`
- All configuration settings
- Search terms and keywords
- Request headers and timeouts
- CSS selectors for different page layouts

### `scraper.py`
- Core eBay scraping functionality
- Handles requests, parsing, and data extraction
- Includes retry logic and error handling
- Removes duplicate listings

### `html_generator.py`
- Creates beautiful HTML results pages
- Modern CSS with animations and responsive design
- Handles image loading and click events

### `utils.py`
- Utility functions and helpers
- Logging with emojis
- Text processing and validation
- Timer and progress tracking

## 🛡️ Error Handling

The scraper includes comprehensive error handling for:

- **Network Issues**: Automatic retries with exponential backoff
- **eBay Anti-Bot Protection**: Graceful handling of rate limits
- **Missing Elements**: Fallback selectors for page structure changes
- **Invalid Data**: Input validation and sanitization

## 🎨 HTML Output Features

- **Masonry Layout**: Pinterest-style responsive grid
- **Hover Effects**: Smooth animations and transitions
- **Mobile Responsive**: Adapts to all screen sizes
- **Accessibility**: Keyboard navigation and ARIA labels
- **Loading States**: Smooth entrance animations
- **Error Handling**: Broken image fallbacks

## 📊 Sample Output

The scraper finds auctions with details like:
- Auction title and description
- Current bid price
- Time remaining
- High-quality images
- Direct links to eBay listings

## 🔄 Running Regularly

For best results:
- Run every few hours to catch new auctions
- Check during peak listing times (evenings, weekends)
- Be respectful of eBay's servers with appropriate delays

## ⚖️ Legal & Ethical Use

- **Respect eBay's Terms of Service**
- **Don't overload their servers** - reasonable delays included
- **For personal use only** - not for commercial scraping
- **Be a good citizen** of the internet

## 🐛 Troubleshooting

**No results found:**
- eBay may be blocking requests temporarily
- Try again in 5-10 minutes
- Check your internet connection

**Script crashes:**
- Ensure all module files are present
- Check Python version (3.6+ required)
- Verify dependencies are installed

**HTML page doesn't load properly:**
- Check if `gba_auctions.html` was created
- Try opening in a different browser
- Look for error messages in the console

## 🔮 Future Enhancements

Potential improvements:
- Email notifications for interesting auctions
- Price tracking and alerts
- Database storage for historical data
- API integration for more reliable data
- Advanced filtering by condition, price, etc.

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Verify your internet connection
4. Try running again in a few minutes

---

**Happy hunting for those rare GameBoy Advance gems! 🎮**
