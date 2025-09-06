# 🚀 Crawl/Walk Campaign Strategy

A refined A/B test strategy that creates campaigns sequentially based on performance milestones, optimizing budget allocation and learning phases.

## 📋 **Strategy Overview**

### **🎯 "Crawl" Phase - Local Presence Campaign**
- **Campaign Name:** `L.R - PMax - Local Presence`
- **Budget:** $49/day ($1,500/month)
- **Targeting:** Park City, UT (local market)
- **Goal:** Establish local presence and gather initial conversion data
- **Phase Exit:** 15-30 conversions to exit Phase 1

### **🏃 "Walk" Phase - Feeder Markets Campaign**
- **Campaign Name:** `L.R - PMax - Feeder Markets`
- **Budget:** $41/day (remaining budget allocation)
- **Targeting:** HNW zip codes in Dallas, LA, NYC, etc.
- **Goal:** Scale to high-net-worth markets
- **Trigger:** Launch when Local Presence exits Phase 1

## 🛠️ **Implementation Components**

### **1. Campaign Creator (`crawl_walk_campaign_creator.py`)**
Creates the "Crawl" campaign immediately and schedules the "Walk" campaign.

**Features:**
- ✅ Google Ads API integration
- ✅ Performance Max campaign creation
- ✅ Location targeting (Park City, UT)
- ✅ Budget and bidding strategy setup
- ✅ Asset groups and page feed creation
- ✅ Google Drive document scheduling
- ✅ Conversion action configuration

### **2. Enhanced Analysis (`enhanced_quick_analysis.py`)**
Monitors campaign performance and detects Phase 1 exit milestones.

**Features:**
- ✅ Daily campaign analysis
- ✅ Phase detection (Phase 1, 2, 3)
- ✅ Milestone alert system
- ✅ Email notifications
- ✅ Performance tracking
- ✅ Automated reporting

### **3. Command Interface (`execute_crawl_walk.py`)**
Simple CLI to execute the complete strategy.

**Commands:**
- `python execute_crawl_walk.py execute` - Run full strategy
- `python execute_crawl_walk.py analyze` - Run daily analysis

## 🚀 **Quick Start**

### **Step 1: Execute Crawl/Walk Strategy**
```bash
cd google-ads-analysis/tools
python execute_crawl_walk.py execute
```

This will:
1. ✅ Create "L.R - PMax - Local Presence" campaign
2. ✅ Set up $49/day budget with Park City targeting
3. ✅ Create Google Doc for "Feeder Markets" scheduling
4. ✅ Test milestone detection system

### **Step 2: Monitor Daily Performance**
```bash
python execute_crawl_walk.py analyze
```

This will:
1. ✅ Analyze all campaign performance
2. ✅ Detect Phase 1 exit milestones
3. ✅ Send email alerts if milestones reached
4. ✅ Generate daily summary reports

## 📊 **Campaign Configuration**

### **Local Presence Campaign (Crawl)**
```yaml
Campaign Name: "L.R - PMax - Local Presence"
Status: ENABLED
Daily Budget: $49
Bidding Strategy: Maximize Conversions
Location Targeting: Park City, UT
URL Expansion: ON (with page feed)
Conversion Goals: Lead Form Submission, Phone Call
```

### **Feeder Markets Campaign (Walk)**
```yaml
Campaign Name: "L.R - PMax - Feeder Markets"
Status: ENABLED (when triggered)
Daily Budget: $41
Bidding Strategy: Maximize Conversions
Location Targeting: HNW zip codes (Dallas, LA, NYC)
URL Expansion: Same as Local Presence
Conversion Goals: Same as Local Presence
```

## 🔍 **Milestone Detection**

### **Phase Definitions**
- **Phase 1 (Learning):** 0-14 conversions
- **Phase 2 (Learning Complete):** 15-29 conversions
- **Phase 3 (Optimized):** 30+ conversions

### **Milestone Triggers**
When "Local Presence" campaign reaches Phase 2 or 3:
- 🚨 **Email Alert:** "MILESTONE REACHED: Campaign 'Local Presence' is now optimized"
- 📝 **Action Required:** Review scheduled document to launch "Feeder Markets"
- 📊 **Performance Data:** Complete campaign analysis included

## 📧 **Email Notifications**

### **Milestone Alert Email**
```
Subject: 🚨 MILESTONE REACHED: Campaign Phase Exit Detected

** MILESTONE REACHED: Campaign 'Local Presence' is now optimized. 
Please review the 'Scheduled Campaign Launch' Google Doc to launch 
the 'Feeder Markets' campaign. **

Campaign Analysis Summary:
- Total Campaigns: 1
- Active Campaigns: 1
- Total Cost: $XXX.XX
- Total Conversions: XX
- Milestones Detected: 1

Action Required:
- Review the 'Scheduled Campaign Launch - Feeder Markets' Google Doc
- Verify campaign settings and budget allocation ($41/day)
- Set up HNW zip code targeting
- Launch the 'L.R - PMax - Feeder Markets' campaign
```

### **Daily Summary Email**
- 📊 Campaign performance metrics
- 🎯 Phase status for each campaign
- 💰 Cost and conversion tracking
- 🚨 Milestone alerts (if any)

## 🗂️ **File Structure**

```
google-ads-analysis/tools/
├── crawl_walk_campaign_creator.py    # Campaign creation logic
├── enhanced_quick_analysis.py        # Milestone detection
├── execute_crawl_walk.py            # CLI interface
└── README_CRAWL_WALK_STRATEGY.md    # This documentation

data/
├── daily_analysis_log.json          # Analysis history
└── campaign_staging.json            # Staging area data
```

## 🔧 **Environment Setup**

### **Required Environment Variables**
```bash
# Google Ads API
GOOGLE_ADS_CUSTOMER_ID=5426234549
GOOGLE_ADS_LOGIN_CUSTOMER_ID=5426234549
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token

# Google Drive API (for document creation)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token

# Email Notifications
EMAIL_SENDER=evan@levine.realestate
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=evan@levine.realestate
```

### **Google Ads API Setup**
1. **Create Google Ads API Account**
2. **Generate Developer Token**
3. **Create OAuth2 Credentials**
4. **Configure Customer IDs**
5. **Test API Connection**

### **Google Drive API Setup**
1. **Enable Google Drive API**
2. **Create OAuth2 Credentials**
3. **Generate Refresh Token**
4. **Test Document Creation**

## 📈 **Performance Monitoring**

### **Key Metrics to Track**
- **Impressions:** Campaign visibility
- **Clicks:** User engagement
- **CTR:** Click-through rate
- **Cost:** Daily spend
- **Conversions:** Lead generation
- **Cost per Conversion:** Efficiency
- **Phase Status:** Learning progress

### **Success Criteria**
- **Phase 1 Exit:** 15-30 conversions
- **Budget Efficiency:** Maintain $1,500/month total
- **Conversion Quality:** High-value leads
- **Geographic Performance:** Local vs. feeder market comparison

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Campaign Creation Fails**
- ✅ Check Google Ads API credentials
- ✅ Verify customer ID permissions
- ✅ Ensure sufficient account balance
- ✅ Check campaign name uniqueness

#### **Milestone Detection Not Working**
- ✅ Verify campaign naming convention
- ✅ Check conversion tracking setup
- ✅ Ensure email configuration
- ✅ Review analysis logs

#### **Email Notifications Not Sent**
- ✅ Check email credentials
- ✅ Verify SMTP settings
- ✅ Test email configuration
- ✅ Check spam folder

### **Debug Commands**
```bash
# Test Google Ads API connection
python -c "from google.ads.googleads.client import GoogleAdsClient; print('✅ API OK')"

# Test email configuration
python -c "import smtplib; print('✅ Email OK')"

# Run analysis with debug output
python execute_crawl_walk.py analyze
```

## 📋 **Workflow Summary**

### **Initial Setup**
1. ✅ Configure environment variables
2. ✅ Test API connections
3. ✅ Execute crawl/walk strategy
4. ✅ Verify campaign creation

### **Daily Operations**
1. ✅ Run daily analysis
2. ✅ Monitor campaign performance
3. ✅ Check for milestone alerts
4. ✅ Review email notifications

### **Milestone Response**
1. ✅ Receive milestone alert email
2. ✅ Review scheduled campaign document
3. ✅ Launch "Feeder Markets" campaign
4. ✅ Monitor both campaigns

## 🎯 **Expected Outcomes**

### **Month 1: Crawl Phase**
- **Local Presence:** $49/day budget
- **Target:** Park City, UT market
- **Goal:** 15-30 conversions
- **Timeline:** Until Phase 1 exit

### **Month 2+: Walk Phase**
- **Local Presence:** Continue optimization
- **Feeder Markets:** $41/day budget
- **Target:** HNW metropolitan areas
- **Goal:** Scale lead generation
- **Timeline:** Ongoing optimization

## 🚀 **Next Steps**

1. **Execute Strategy:** Run the crawl/walk implementation
2. **Monitor Performance:** Daily analysis and milestone detection
3. **Respond to Milestones:** Launch feeder markets when ready
4. **Optimize Continuously:** Adjust based on performance data

**Your Crawl/Walk strategy is ready for implementation!** 🎉
