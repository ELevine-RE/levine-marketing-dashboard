# 🔍 Campaign Audit System

Comprehensive campaign audit system that downloads all campaign data from Google Ads API and provides detailed analysis and optimization recommendations.

## 🚀 **What It Does:**

### **✅ Complete Data Download:**
1. **Campaign Structure** - Type, bidding strategy, budget, targeting
2. **Performance Metrics** - Impressions, clicks, CTR, CPC, conversions, cost per conversion
3. **Asset Analysis** - Images, videos, text assets, asset sets
4. **Targeting Analysis** - Keywords, match types, performance
5. **Budget & Bidding** - Budget amount, delivery method, bidding strategy

### **✅ Intelligent Analysis:**
1. **Structure Analysis** - Campaign configuration and setup
2. **Performance Analysis** - Metrics analysis and benchmarking
3. **Targeting Analysis** - Keyword and audience performance
4. **Asset Analysis** - Creative assets and variety
5. **Budget Analysis** - Budget optimization and bidding strategy

### **✅ Optimization Recommendations:**
1. **High Priority** - Critical issues that need immediate attention
2. **Medium Priority** - Important optimizations for better performance
3. **Low Priority** - Nice-to-have improvements

## 🛠️ **Usage:**

### **1. Basic Campaign Audit:**
```bash
python tools/audit_campaign.py --customer YOUR_CUSTOMER_ID
```

### **2. Audit Specific Campaign:**
```bash
python tools/audit_campaign.py --customer YOUR_CUSTOMER_ID --campaign "L.R - Deer Valley"
```

### **3. Detailed Analysis:**
```bash
python tools/audit_campaign.py --customer YOUR_CUSTOMER_ID --verbose
```

### **4. Save Results to File:**
```bash
python tools/audit_campaign.py --customer YOUR_CUSTOMER_ID --output audit_results.json
```

## 📊 **Example Output:**

```
🔍 Auditing campaign: L.R - PMax - General
============================================================
✅ Campaign audit completed successfully!
   Campaign: L.R - PMax - General
   Audit File: data/campaign_audit_20250905_183000.json

📊 Audit Summary:
   Overall Status: Needs Attention
   Total Recommendations: 8
   High Priority: 2
   Medium Priority: 4
   Low Priority: 2

📋 Campaign Data:
   Campaign ID: 1234567890
   Status: ENABLED
   Type: PERFORMANCE_MAX
   Budget: $2000.00
   Bidding Strategy: MAXIMIZE_CONVERSIONS
   Target CPA: $75.00

📈 Performance Data:
   Total Impressions: 15,432
   Total Clicks: 234
   Total Cost: $1,456.78
   Total Conversions: 3
   Average CTR: 1.52%
   Average CPC: $6.22
   Conversion Rate: 1.28%
   Cost per Conversion: $485.59

🖼️ Asset Data:
   Total Assets: 12
   Asset Types: IMAGE, TEXT, LOGO
   Asset Sets: Levine Real Estate - General Assets

🎯 Targeting Data:
   Total Keywords: 0
   High Performing Keywords: 0
   Low Performing Keywords: 0

💡 Recommendations:
   1. [High] Add more images, videos, and text assets
       Issue: Insufficient assets
       Impact: High

   2. [High] Increase budget to $1,000+ for better performance
       Issue: Budget too low
       Impact: High

   3. [Medium] Improve ad relevance and targeting
       Issue: Low CTR: 1.52%
       Impact: Medium

   4. [Medium] Adjust bidding strategy or improve ad quality
       Issue: High CPC: $6.22
       Impact: Medium
```

## 🔍 **Analysis Categories:**

### **✅ Campaign Structure Analysis:**
- **Campaign Type** - Performance Max, Search, Display, etc.
- **Bidding Strategy** - Target CPA, Target ROAS, Maximize Conversions
- **Budget Configuration** - Amount, delivery method, period
- **Targeting Settings** - CPA, ROAS targets

### **✅ Performance Analysis:**
- **Traffic Metrics** - Impressions, clicks, CTR
- **Cost Metrics** - CPC, total cost, cost per conversion
- **Conversion Metrics** - Conversions, conversion rate, value per conversion
- **Benchmarking** - Industry averages and best practices

### **✅ Targeting Analysis:**
- **Keyword Performance** - High/low performing keywords
- **Match Types** - Broad, phrase, exact match distribution
- **Audience Performance** - Demographic and interest targeting
- **Negative Keywords** - Exclusion opportunities

### **✅ Asset Analysis:**
- **Asset Types** - Images, videos, text, logos
- **Asset Quantity** - Sufficient variety for ad rotation
- **Asset Quality** - Relevance and performance
- **Asset Sets** - Organization and grouping

### **✅ Budget Analysis:**
- **Budget Amount** - Appropriate for campaign goals
- **Budget Delivery** - Standard vs. accelerated
- **Bidding Strategy** - Optimization for goals
- **Target Settings** - CPA/ROAS appropriateness

## 💡 **Recommendation Types:**

### **🔴 High Priority (Critical):**
- **No Performance Data** - Campaign too new to analyze
- **Insufficient Assets** - Less than 5 assets
- **Budget Too Low** - Less than $500/day
- **No Conversion Tracking** - Missing conversion setup

### **🟡 Medium Priority (Important):**
- **Low CTR** - Below 1% click-through rate
- **High CPC** - Above $5 cost per click
- **Low Conversion Rate** - Below 2% conversion rate
- **High Cost per Conversion** - Above $200
- **Missing Asset Types** - No images, videos, or text

### **🟢 Low Priority (Nice to Have):**
- **Non-standard Budget Delivery** - Accelerated delivery
- **Could Use More Assets** - Less than 20 assets
- **Keyword Optimization** - Match type improvements
- **Target Adjustments** - CPA/ROAS fine-tuning

## 📈 **Performance Benchmarks:**

### **Real Estate Industry Averages:**
- **CTR:** 1-3% (Good: 2-5%, Excellent: 5%+)
- **CPC:** $2-8 (Good: $1-5, Excellent: $1-3)
- **Conversion Rate:** 2-5% (Good: 3-7%, Excellent: 7%+)
- **Cost per Conversion:** $50-200 (Good: $25-100, Excellent: $25-50)

### **Performance Max Specific:**
- **Asset Quantity:** 20+ assets for optimal performance
- **Asset Types:** Images, videos, text, logos required
- **Budget:** $1,000+ for effective optimization
- **Learning Period:** 2-4 weeks for algorithm optimization

## 🔧 **Common Issues & Solutions:**

### **Issue: Low CTR (< 1%)**
**Solutions:**
- Improve ad relevance and targeting
- Add more specific keywords
- Improve ad copy and headlines
- Use more relevant images

### **Issue: High CPC (> $5)**
**Solutions:**
- Adjust bidding strategy
- Improve ad quality score
- Add negative keywords
- Use more specific targeting

### **Issue: No Conversions**
**Solutions:**
- Verify conversion tracking
- Improve landing page experience
- Add conversion-optimized assets
- Adjust targeting for qualified traffic

### **Issue: Insufficient Assets**
**Solutions:**
- Add more images (property photos, lifestyle)
- Add videos (property tours, testimonials)
- Add text assets (headlines, descriptions)
- Create asset sets for different campaigns

## 📋 **Audit Checklist:**

### **✅ Campaign Setup:**
- [ ] Campaign type appropriate (Performance Max for real estate)
- [ ] Bidding strategy optimized for goals
- [ ] Budget sufficient for performance ($1,000+)
- [ ] Conversion tracking properly set up

### **✅ Assets:**
- [ ] 20+ assets for optimal performance
- [ ] Images: Property photos, lifestyle, community
- [ ] Videos: Property tours, testimonials, community
- [ ] Text: Headlines, descriptions, calls-to-action
- [ ] Logos: Brand assets

### **✅ Targeting:**
- [ ] Relevant keywords and audiences
- [ ] Negative keywords to exclude irrelevant traffic
- [ ] Geographic targeting appropriate
- [ ] Demographic targeting optimized

### **✅ Performance:**
- [ ] CTR above 1%
- [ ] CPC below $5
- [ ] Conversion rate above 2%
- [ ] Cost per conversion below $200

## 🚀 **Quick Start:**

1. **Install Dependencies:**
   ```bash
   pip install google-ads
   ```

2. **Set Environment Variables:**
   ```bash
   # Your .env file should have Google Ads credentials
   GOOGLE_ADS_CUSTOMER_ID=your_customer_id
   ```

3. **Run Campaign Audit:**
   ```bash
   python tools/audit_campaign.py --customer YOUR_CUSTOMER_ID
   ```

4. **Review Results:**
   - Check audit summary
   - Review recommendations
   - Implement high-priority fixes
   - Monitor performance improvements

## 🎯 **Perfect for Your Use Case:**

This audit system is perfect for your first campaign because it:

1. **✅ Downloads Everything** - Gets all campaign data from Google Ads API
2. **✅ Analyzes Everything** - Comprehensive analysis of all aspects
3. **✅ Recommends Everything** - Prioritized optimization recommendations
4. **✅ Benchmarks Everything** - Compares against industry standards
5. **✅ Saves Everything** - Detailed audit report for reference

**Run this audit to ensure your first campaign is set up correctly!** 🚀

## 📊 **Next Steps After Audit:**

1. **Implement High-Priority Recommendations** - Fix critical issues first
2. **Add Missing Assets** - Ensure sufficient asset variety
3. **Optimize Budget** - Adjust budget for better performance
4. **Improve Targeting** - Add negative keywords and refine audiences
5. **Monitor Performance** - Track improvements over time
6. **Re-audit Regularly** - Run audits monthly for ongoing optimization

Your campaign audit system is ready to ensure your first campaign is optimized for success! 🎉
