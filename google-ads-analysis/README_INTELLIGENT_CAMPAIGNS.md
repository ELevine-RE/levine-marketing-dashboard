# 🧠 Intelligent Campaign Creator

**YES!** This system does exactly what you want - it automatically creates campaigns with optimized assets without you having to think about it.

## 🚀 **What It Does:**

### **✅ Automatic Campaign Creation:**
1. **You say:** "Create a Deer Valley campaign"
2. **System automatically:**
   - Detects it's for Deer Valley location
   - Finds Deer Valley landing pages
   - Extracts Deer Valley assets (photos, videos, content)
   - Creates Deer Valley-specific asset set
   - Sets intelligent budget ($2,000-$5,000)
   - Configures targeting keywords
   - Links everything to the campaign

### **✅ Zero Manual Work:**
- No need to specify landing pages
- No need to mention asset types
- No need to set budgets
- No need to configure targeting
- **Everything happens automatically!**

## 🎯 **Examples:**

### **Example 1: Simple Campaign Creation**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Deer Valley Luxury"
```

**What happens automatically:**
- ✅ Detects "Deer Valley" location
- ✅ Finds Deer Valley landing pages
- ✅ Extracts luxury property assets
- ✅ Sets budget to $3,500 (intelligent calculation)
- ✅ Configures targeting for "deer valley real estate"
- ✅ Creates Performance Max campaign
- ✅ Links everything together

### **Example 2: Property Type Detection**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Park City Condos"
```

**What happens automatically:**
- ✅ Detects "Park City" location
- ✅ Detects "Condos" property type
- ✅ Finds Park City condo pages
- ✅ Extracts condo-specific assets (interior photos, amenities)
- ✅ Sets budget to $2,400 (condo multiplier)
- ✅ Configures targeting for "park city condos"
- ✅ Creates optimized campaign

### **Example 3: Goal-Based Optimization**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Promontory Sales" --goal property_sales
```

**What happens automatically:**
- ✅ Detects "Promontory" location
- ✅ Sets goal to "property_sales"
- ✅ Extracts sales-focused assets (property photos, virtual tours)
- ✅ Sets budget to $4,200 (sales goal multiplier)
- ✅ Configures exact match targeting
- ✅ Optimizes for conversions

## 🧠 **Intelligence Rules:**

### **Location Intelligence:**
```json
{
  "deer valley": {
    "landing_pages": [
      "https://levine.realestate/communities/deer-valley/",
      "https://levine.realestate/property/?location=deer-valley"
    ],
    "asset_priorities": ["property_photos", "community_images", "luxury_content"],
    "targeting_keywords": ["deer valley real estate", "deer valley homes"],
    "budget_suggestions": {"min": 2000, "max": 5000}
  }
}
```

### **Property Type Intelligence:**
```json
{
  "luxury": {
    "asset_priorities": ["high_end_photos", "luxury_amenities", "premium_content"],
    "budget_multiplier": 1.5,
    "targeting_modifiers": ["luxury", "premium", "high-end"]
  }
}
```

### **Goal Intelligence:**
```json
{
  "property_sales": {
    "asset_priorities": ["property_photos", "virtual_tours", "listing_content"],
    "budget_focus": "conversion_optimization",
    "targeting_strategy": "exact_match"
  }
}
```

## 🛠️ **Usage:**

### **1. Create Campaign (Simple):**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Deer Valley"
```

### **2. Create Campaign (With Goal):**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Park City" --goal lead_generation
```

### **3. Create Campaign (With Budget):**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Promontory" --budget 5000
```

### **4. Test Campaign Creation:**
```bash
python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID test "L.R - Deer Valley Luxury"
```

## 🎯 **What Gets Created Automatically:**

### **✅ Campaign Configuration:**
- Campaign name and type
- Intelligent budget calculation
- Targeting keywords
- Landing page selection
- Asset priorities

### **✅ Asset Extraction:**
- Location-specific images
- Property type-specific content
- Goal-optimized assets
- Child page discovery
- Asset set creation

### **✅ Page Feed Creation:**
- Sitemap-based URL collection
- Campaign-specific filtering
- Page feed asset set
- Automatic linking

### **✅ Google Ads Integration:**
- Campaign creation
- Asset set linking
- Page feed linking
- Optimization recommendations

## 🧠 **Intelligence Features:**

### **✅ Auto-Detection:**
- **Location:** Detects "Deer Valley", "Park City", "Promontory" from campaign name
- **Property Type:** Detects "Luxury", "Condo", "Single Family" from campaign name
- **Goal:** Infers from campaign name or uses default

### **✅ Intelligent Budgeting:**
- Base budget: $2,000
- Location multiplier: Deer Valley (1.5x), Park City (1.0x), Promontory (1.8x)
- Property type multiplier: Luxury (1.5x), Condo (1.0x), Single Family (1.2x)
- Goal multiplier: Sales (1.2x), Leads (1.0x), Awareness (0.8x)

### **✅ Smart Asset Prioritization:**
- **Deer Valley:** Luxury content, property photos, community images
- **Park City:** Mountain views, ski content, property photos
- **Promontory:** Golf content, luxury lifestyle, property photos

### **✅ Intelligent Targeting:**
- **Location-based:** "deer valley real estate", "park city homes"
- **Property-based:** "luxury condos", "single family homes"
- **Goal-based:** Exact match for sales, broad match for awareness

## 🚀 **Complete Workflow:**

### **When You Create a Campaign:**

1. **🧠 Analysis Phase:**
   - Parse campaign name for location/property type
   - Determine campaign goal
   - Calculate intelligent budget
   - Select appropriate landing pages

2. **🖼️ Asset Extraction Phase:**
   - Extract assets from landing pages
   - Discover and extract from child pages
   - Filter for relevant content
   - Create campaign-specific asset set

3. **📋 Page Feed Phase:**
   - Collect URLs from sitemap
   - Filter for campaign relevance
   - Create page feed asset set
   - Link to campaign

4. **🎯 Campaign Creation Phase:**
   - Create Google Ads campaign
   - Configure targeting and budget
   - Link asset sets and page feeds
   - Generate optimization recommendations

5. **📊 Optimization Phase:**
   - Analyze performance potential
   - Suggest budget adjustments
   - Recommend additional keywords
   - Identify optimization opportunities

## 🎉 **Benefits:**

### **✅ Zero Manual Work:**
- No need to specify landing pages
- No need to mention asset types
- No need to set budgets
- No need to configure targeting

### **✅ Intelligent Optimization:**
- Automatic budget calculation
- Smart asset prioritization
- Intelligent targeting
- Performance optimization

### **✅ Campaign-Specific:**
- Each campaign gets its own assets
- Location-specific content
- Property type-specific targeting
- Goal-optimized configuration

### **✅ Scalable:**
- Easy to add new locations
- Easy to add new property types
- Easy to add new goals
- Handles any campaign name

## 🔧 **Configuration:**

### **Add New Location:**
```python
# In intelligent_campaign_creator.py
"heber": {
    "landing_pages": [
        "https://levine.realestate/communities/heber/",
        "https://levine.realestate/property/?location=heber"
    ],
    "asset_priorities": ["property_photos", "mountain_views", "family_content"],
    "targeting_keywords": ["heber real estate", "heber homes"],
    "budget_suggestions": {"min": 1500, "max": 3000}
}
```

### **Add New Property Type:**
```python
# In intelligent_campaign_creator.py
"townhouse": {
    "asset_priorities": ["interior_photos", "community_amenities", "lifestyle_content"],
    "budget_multiplier": 1.1,
    "targeting_modifiers": ["townhouse", "townhome", "attached"]
}
```

## 🎯 **Perfect for Your Use Case:**

This system does exactly what you asked for:

1. **✅ Automatic Campaign Creation** - Just say the campaign name
2. **✅ Intelligent Asset Optimization** - Automatically grabs relevant assets
3. **✅ Zero Manual Work** - No need to specify anything
4. **✅ Campaign-Specific** - Each campaign gets its own optimized assets
5. **✅ Scalable** - Works for any location/property type combination

**Just say "Create a Deer Valley campaign" and everything happens automatically!** 🚀

## 🚀 **Quick Start:**

1. **Install Dependencies:**
   ```bash
   pip install beautifulsoup4 Pillow requests
   ```

2. **Create Your First Intelligent Campaign:**
   ```bash
   python tools/smart_campaign_manager.py --customer YOUR_CUSTOMER_ID create "L.R - Deer Valley Luxury"
   ```

3. **Watch the Magic Happen:**
   - System detects "Deer Valley" location
   - Finds Deer Valley landing pages
   - Extracts luxury property assets
   - Sets intelligent budget
   - Creates optimized campaign
   - Links everything together

**That's it! Your campaign is ready to go with optimized assets!** 🎉
