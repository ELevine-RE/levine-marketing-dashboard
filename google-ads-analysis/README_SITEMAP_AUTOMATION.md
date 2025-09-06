# 🗺️ Sitemap Automation System

Complete automation system that fetches URLs from your website's sitemap and automatically creates/updates Google Ads page feeds.

## 🚀 Features

### ✅ **Automated Sitemap Processing**
- Fetches sitemap.xml from `https://levine.realestate/sitemap.xml`
- Parses XML sitemaps and sitemap indexes
- Handles multiple sitemap files automatically
- Caches results for 24 hours to reduce API calls

### ✅ **Smart URL Filtering**
- Excludes unwanted URLs (`/sitemap/*`, `/blog/*`, `/privacy/*`, etc.)
- Prioritizes property-related content (`/property/`, `/communities/`, etc.)
- Scores URLs based on relevance and priority
- Limits to configurable maximum URLs (default: 1000)

### ✅ **Google Ads Integration**
- Creates PAGE_FEED asset sets automatically
- Generates page feed assets from sitemap URLs
- Links asset sets to campaigns
- Adds priority labels to assets

### ✅ **Scheduling & Monitoring**
- Runs automatically every 24 hours (configurable)
- Tracks success/failure rates
- Logs all operations to `data/sitemap_automation.log`
- Provides status monitoring and reporting

## 📁 Files Created

```
google-ads-analysis/tools/
├── sitemap_parser.py          # Core sitemap parsing logic
├── page_feed_creator.py       # Google Ads page feed creation
├── sitemap_automation.py      # Complete automation system
├── test_sitemap_automation.py # Comprehensive test suite
└── requirements.txt           # Updated with new dependencies
```

## 🛠️ Installation

1. **Install new dependencies:**
   ```bash
   cd /Users/evan/WebTool/google-ads-analysis
   pip install schedule beautifulsoup4 Pillow lxml
   ```

2. **Verify environment variables:**
   ```bash
   # Check your .env file has all required Google Ads credentials
   cat .env | grep GOOGLE_ADS
   ```

## 🧪 Testing

### **Run Complete Test Suite:**
```bash
cd /Users/evan/WebTool/google-ads-analysis
python tools/test_sitemap_automation.py
```

### **Test Individual Components:**
```bash
# Test sitemap parser only
python tools/sitemap_parser.py

# Test page feed creator only  
python tools/page_feed_creator.py

# Test automation system only
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --test
```

## 🚀 Usage

### **Run Once:**
```bash
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --run
```

### **Schedule Automatic Runs:**
```bash
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --schedule
```

### **Check Status:**
```bash
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --status
```

## ⚙️ Configuration

The system automatically creates `data/sitemap_automation_config.json`:

```json
{
  "campaign_name": "L.R - PMax - General",
  "asset_set_name": "Levine Real Estate Page Feed", 
  "max_urls": 1000,
  "update_frequency_hours": 24,
  "auto_create_page_feeds": true,
  "auto_link_to_campaigns": true,
  "last_run": "2025-09-05T18:00:00",
  "last_run_status": "success",
  "total_runs": 5,
  "successful_runs": 5
}
```

### **Update Configuration:**
```python
from tools.sitemap_automation import SitemapAutomation

automation = SitemapAutomation("YOUR_CUSTOMER_ID")
automation.update_config({
    "max_urls": 500,
    "update_frequency_hours": 12,
    "asset_set_name": "Custom Page Feed Name"
})
```

## 📊 What It Does

### **1. Sitemap Processing:**
- Fetches `https://levine.realestate/sitemap.xml`
- Parses all URLs and metadata
- Filters out unwanted paths
- Scores URLs by relevance

### **2. Page Feed Creation:**
- Creates Google Ads PAGE_FEED asset set
- Generates page feed assets for each URL
- Adds priority labels (high/medium/low)
- Links asset set to your campaign

### **3. Automation:**
- Runs automatically every 24 hours
- Updates page feeds when sitemap changes
- Tracks success/failure rates
- Logs all operations

## 🎯 URL Prioritization

The system automatically prioritizes URLs:

**High Priority (Score 2.0+):**
- `/property/` pages
- Community pages (`/deer-valley`, `/park-city`, `/promontory`)

**Medium Priority (Score 1.0-2.0):**
- `/communities/` pages
- Search result pages

**Low Priority (Score <1.0):**
- Generic pages (`/`, `/home`)
- Other content pages

## 📈 Monitoring

### **Check Logs:**
```bash
tail -f data/sitemap_automation.log
```

### **View Status:**
```bash
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --status
```

### **View Cache:**
```bash
cat data/sitemap_cache.json
```

## 🔧 Troubleshooting

### **Common Issues:**

1. **"No URLs found in sitemap"**
   - Check if `https://levine.realestate/sitemap.xml` is accessible
   - Verify sitemap format is valid XML

2. **"Failed to create asset set"**
   - Check Google Ads API credentials
   - Verify customer ID permissions

3. **"Campaign not found"**
   - Ensure campaign name matches exactly: "L.R - PMax - General"
   - Check campaign exists in the specified customer account

### **Debug Mode:**
```bash
# Run with verbose logging
python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --test --verbose
```

## 🎉 Integration with Existing System

This sitemap automation **complements** your existing asset extraction system:

- **Sitemap Automation**: Handles page feeds (URLs)
- **Asset Extraction**: Handles images, videos, text content

Both systems work together to provide complete automation for your Google Ads campaigns.

## 📋 Next Steps

1. **Test the system:**
   ```bash
   python tools/test_sitemap_automation.py
   ```

2. **Run your first automation:**
   ```bash
   python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --run
   ```

3. **Schedule automatic updates:**
   ```bash
   python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --schedule
   ```

4. **Monitor and adjust:**
   - Check logs regularly
   - Adjust URL filtering if needed
   - Update configuration as required

Your sitemap automation system is now ready to automatically keep your Google Ads page feeds up-to-date! 🚀
