# 🚀 Crawl/Walk Strategy Dashboard

A streamlined dashboard focused entirely on the Crawl/Walk campaign strategy with automated milestone detection and GitHub Actions integration.

## 🎯 **What This Dashboard Does**

### **📊 Strategy Visualization**
- **Crawl Phase:** Local Presence campaign ($49/day, Park City, UT)
- **Walk Phase:** Feeder Markets campaign ($41/day, HNW markets)
- **Milestone Detection:** Automatic Phase 1 exit detection
- **Performance Tracking:** Real-time campaign metrics

### **🤖 Automation Features**
- **Daily Analysis:** Automated milestone detection
- **Email Alerts:** Milestone notifications
- **GitHub Actions:** Cloud-based execution
- **Campaign Creation:** Automated campaign setup

## 🚀 **Quick Start**

### **1. Run Dashboard Locally**
```bash
streamlit run crawl_walk_dashboard.py
```

### **2. Execute Strategy**
```bash
cd google-ads-analysis/tools
python execute_crawl_walk.py execute
```

### **3. Run Analysis**
```bash
python execute_crawl_walk.py analyze
```

## 🔧 **GitHub Actions Setup**

### **1. Configure Secrets**
Follow the guide in `GITHUB_SECRETS_SETUP.md` to set up:
- Google Ads API credentials
- Google Drive API credentials  
- Email notification settings

### **2. Automation Schedule**
- **Daily at 9 AM UTC:** Automatic milestone analysis
- **Manual trigger:** Execute strategy or run tests
- **Email alerts:** Milestone notifications

## 📋 **Dashboard Features**

### **📊 Strategy Overview Tab**
- Crawl/Walk phase visualization
- Campaign status and metrics
- Strategy timeline
- Performance indicators

### **🎯 Campaign Performance Tab**
- Real-time campaign data
- Conversion tracking
- Cost analysis
- Phase progression

### **🔍 Milestone Detection Tab**
- Active milestone alerts
- Milestone history
- Analysis results
- Action requirements

### **⚙️ Execution Controls Tab**
- Campaign creation tools
- Analysis runners
- Email testing
- Automation status

## 🛠️ **Components**

### **Core Files**
- `crawl_walk_dashboard.py` - Main dashboard
- `google-ads-analysis/tools/crawl_walk_campaign_creator.py` - Campaign creation
- `google-ads-analysis/tools/enhanced_quick_analysis.py` - Milestone detection
- `google-ads-analysis/tools/execute_crawl_walk.py` - CLI interface

### **Automation**
- `.github/workflows/crawl-walk-automation.yml` - GitHub Actions workflow
- `GITHUB_SECRETS_SETUP.md` - Secrets configuration guide
- `deploy_crawl_walk.py` - Deployment script

## 🎯 **Strategy Details**

### **🦎 Crawl Phase (Immediate)**
- **Campaign:** L.R - PMax - Local Presence
- **Budget:** $49/day ($1,500/month)
- **Target:** Park City, UT
- **Goal:** 15-30 conversions to exit Phase 1

### **🏃 Walk Phase (Triggered)**
- **Campaign:** L.R - PMax - Feeder Markets
- **Budget:** $41/day (remaining allocation)
- **Target:** HNW zip codes (Dallas, LA, NYC)
- **Trigger:** When Crawl exits Phase 1

## 🚨 **Milestone Alerts**

When the Local Presence campaign reaches Phase 2 or 3:
```
🚨 MILESTONE REACHED: Campaign 'Local Presence' is now optimized. 
Please review the 'Scheduled Campaign Launch' Google Doc to launch 
the 'Feeder Markets' campaign.
```

## 📧 **Email Notifications**

- **Milestone Alerts:** Immediate notifications for phase exits
- **Daily Summaries:** Comprehensive performance reports
- **Action Required:** Clear next steps and requirements

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

# Google Drive API
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token

# Email Notifications
EMAIL_SENDER=evan@levine.realestate
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=evan@levine.realestate
```

## 🚀 **Deployment**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run crawl_walk_dashboard.py

# Test deployment
python deploy_crawl_walk.py
```

### **GitHub Actions**
1. Set up secrets (see `GITHUB_SECRETS_SETUP.md`)
2. Push to repository
3. Monitor Actions tab for automation
4. Check email for milestone alerts

## 📊 **Monitoring**

### **Daily Automation**
- **9 AM UTC:** Automatic milestone analysis
- **Email alerts:** Milestone notifications
- **Logs:** Complete audit trail
- **Artifacts:** Performance data storage

### **Manual Controls**
- **Execute strategy:** Create campaigns and schedules
- **Run analysis:** Check milestones and performance
- **Test system:** Verify all components

## 🎉 **Perfect for Your Strategy**

This dashboard is designed specifically for your Crawl/Walk strategy:
- ✅ **Sequential Launch:** Crawl first, then Walk
- ✅ **Milestone Detection:** Automatic Phase 1 exit detection
- ✅ **Budget Optimization:** $49/$41 split for $1,500/month
- ✅ **Market Targeting:** Local → HNW progression
- ✅ **Automation:** GitHub Actions for cloud execution
- ✅ **Monitoring:** Real-time performance tracking

**Your streamlined Crawl/Walk dashboard is ready!** 🚀