# 🎯 Campaign-Specific Asset Extraction

**YES!** This system does exactly what you asked for - it extracts assets from specific landing pages and their children for individual campaigns.

## 🚀 **How It Works:**

### **✅ Campaign-Specific Extraction:**
1. **Define Campaign Landing Pages** - Specify exact URLs for each campaign
2. **Extract from Children** - Automatically finds and extracts from child pages
3. **Create Campaign Asset Sets** - Each campaign gets its own asset set
4. **Link to Campaign** - Assets are automatically linked to the specific campaign

### **✅ Example Configuration:**

```json
{
  "campaigns": {
    "L.R - Deer Valley": {
      "landing_pages": [
        "https://levine.realestate/communities/deer-valley/",
        "https://levine.realestate/property/?location=deer-valley"
      ],
      "include_children": true,
      "max_depth": 3,
      "asset_set_name": "Levine Real Estate - Deer Valley Assets"
    },
    "L.R - Park City": {
      "landing_pages": [
        "https://levine.realestate/communities/park-city/",
        "https://levine.realestate/property/?location=park-city"
      ],
      "include_children": true,
      "max_depth": 3,
      "asset_set_name": "Levine Real Estate - Park City Assets"
    }
  }
}
```

## 🛠️ **Usage:**

### **1. List All Campaigns:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID list
```

### **2. Add New Campaign:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID add "L.R - Promontory" \
  --pages "https://levine.realestate/communities/promontory/" \
  --children --depth 3
```

### **3. Extract Assets for Campaign:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID extract "L.R - Deer Valley"
```

### **4. Test Campaign Extraction:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID test "L.R - Park City"
```

### **5. Check Campaign Status:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID status "L.R - Deer Valley"
```

## 🎯 **What Gets Extracted:**

### **From Landing Pages:**
- **Images** - Property photos, community images, logos
- **Videos** - Property tours, community videos
- **Text Content** - Headlines, descriptions, property details

### **From Child Pages:**
- **Property Pages** - Individual property listings
- **Community Pages** - Neighborhood information
- **Search Results** - Filtered property listings
- **Related Content** - Up to specified depth

## 📊 **Example Output:**

```
🚀 Extracting assets for campaign: L.R - Deer Valley
📋 Step 1: Collecting pages for campaign...
✅ Found 15 pages for campaign
🖼️ Step 2: Extracting assets from pages...
✅ Extracted 45 images, 8 videos
📦 Step 3: Creating campaign asset set...
🔗 Step 4: Linking assets to campaign...
✅ Campaign asset extraction completed successfully!
   Pages Processed: 15
   Total Assets: 53
   Images: 45
   Videos: 8
   Asset Set ID: 1234567890
   Campaign Linked: true
```

## 🔧 **Configuration Options:**

### **Per Campaign:**
- **`landing_pages`** - Specific URLs to start from
- **`include_children`** - Whether to extract from child pages
- **`max_depth`** - How deep to go (1 = direct children, 2 = grandchildren, etc.)
- **`asset_set_name`** - Custom name for the asset set
- **`enabled`** - Whether the campaign is active

### **Child Page Detection:**
- Automatically finds internal links
- Filters for relevant pages (property, community, search)
- Respects depth limits
- Avoids infinite loops

## 🎯 **Campaign Examples:**

### **Deer Valley Campaign:**
- **Landing Pages:** Deer Valley community page, Deer Valley property search
- **Children:** Individual Deer Valley properties, Deer Valley amenities
- **Assets:** Deer Valley photos, property videos, community content

### **Park City Campaign:**
- **Landing Pages:** Park City community page, Park City property search  
- **Children:** Individual Park City properties, Park City attractions
- **Assets:** Park City photos, property tours, local content

### **General Campaign:**
- **Landing Pages:** Homepage, general property search, communities overview
- **Children:** All property pages, all community pages
- **Assets:** General real estate content, brand assets

## 🚀 **Integration with Existing Systems:**

### **Works With:**
- **Sitemap Automation** - For page feed creation
- **Asset Extractor** - For image/video extraction
- **Google Ads API** - For asset set creation
- **Campaign Management** - For automatic linking

### **Complete Workflow:**
1. **Sitemap Automation** - Creates page feeds from sitemap
2. **Campaign Asset Extraction** - Creates asset sets from specific pages
3. **Google Ads** - Uses both page feeds and asset sets for campaigns

## 📋 **Quick Start:**

1. **Install Dependencies:**
   ```bash
   pip install beautifulsoup4 Pillow requests
   ```

2. **Set Environment Variables:**
   ```bash
   # Your .env file should have Google Ads credentials
   GOOGLE_ADS_CUSTOMER_ID=your_customer_id
   ```

3. **Run Your First Campaign:**
   ```bash
   python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID extract "L.R - Deer Valley"
   ```

## 🎉 **Benefits:**

### **✅ Campaign-Specific:**
- Each campaign gets its own asset set
- Only relevant content is extracted
- No mixing of different campaign assets

### **✅ Automated:**
- No manual asset collection
- Automatic child page discovery
- Automatic Google Ads integration

### **✅ Scalable:**
- Easy to add new campaigns
- Configurable depth and scope
- Handles large numbers of pages

### **✅ Smart:**
- Filters for relevant content
- Avoids duplicate assets
- Respects website structure

## 🔍 **Monitoring:**

### **Check Logs:**
```bash
tail -f data/campaign_asset_extraction.log
```

### **View Configuration:**
```bash
cat data/campaign_asset_configs.json
```

### **Check Status:**
```bash
python tools/campaign_asset_manager.py --customer YOUR_CUSTOMER_ID status "L.R - Deer Valley"
```

## 🎯 **Perfect for Your Use Case:**

This system does exactly what you asked for:

1. **✅ Campaign-Specific** - Each campaign gets its own assets
2. **✅ Landing Page Focused** - Starts from specific landing pages
3. **✅ Child Page Extraction** - Automatically finds and extracts from children
4. **✅ Google Ads Integration** - Creates asset sets and links to campaigns
5. **✅ Automated** - No manual intervention required

Your Deer Valley campaign will only get Deer Valley assets, your Park City campaign will only get Park City assets, etc. Perfect! 🚀
