# 📊 Marketing Dashboard - A/B Test

A comprehensive Streamlit dashboard for monitoring Google Analytics, Google Ads campaign performance, and goal progression for your 5-month A/B test.

## 🎯 Features

### **Campaign Monitoring**
- **Real-time Google Ads metrics** for both campaigns
- **Goal progression tracking** with visual progress bars
- **Phase management** with automatic progression detection
- **A/B test comparison** with side-by-side metrics

### **Google Analytics Integration**
- **Website traffic analysis** (sessions, users, pageviews)
- **Conversion tracking** (lead forms, phone calls, email signups)
- **Traffic source breakdown** (organic, paid, direct, social)
- **Top pages performance** with conversion data

### **Goal Tracking**
- **Conversion goals** (30 conversions per campaign)
- **CPL targets** (Local Presence: $150, Feeder Markets: $200)
- **Phase progression** (Phase 1 → Phase 2 → Phase 3)
- **Budget monitoring** with overspend alerts

### **Alerts & Recommendations**
- **Automatic alert generation** for performance issues
- **Smart recommendations** based on campaign performance
- **Phase transition readiness** indicators
- **Budget optimization** suggestions

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
# Install dashboard dependencies
pip install -r dashboard_requirements.txt
```

### **2. Configure Environment**
```bash
# Set up your Google Ads credentials
export GOOGLE_ADS_DEVELOPER_TOKEN="your_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
export GOOGLE_ADS_LOGIN_CUSTOMER_ID="5426234549"
```

### **3. Update Campaign IDs**
Edit `dashboard_config.yaml` and replace:
- `campaign_1_id` with your Local Presence campaign ID
- `campaign_2_id` with your Feeder Markets campaign ID
- `GA_PROPERTY_ID` with your Google Analytics property ID

### **4. Run Dashboard**
```bash
# Option 1: Use the startup script
./run_dashboard.sh

# Option 2: Run directly
streamlit run dashboard.py
```

### **5. Access Dashboard**
Open your browser and go to: **http://localhost:8501**

## 📋 Dashboard Sections

### **1. Overview Metrics**
- Total website sessions (30 days)
- Total conversions (30 days)
- Total ad spend (30 days)
- Average cost per lead

### **2. Campaign Comparison**
- Side-by-side performance metrics
- Conversion comparison charts
- CPL comparison charts
- Interactive data tables

### **3. Goal Progress Tracking**
- **Local Presence Campaign:**
  - Budget: $31.50/day (Month 1), $34.50/day (Months 2-5)
  - Goal: 30 conversions, $150 CPL
  - Phase: Phase 1 (Maximize Conversions)

- **Feeder Markets Campaign:**
  - Budget: $73.50/day (Month 1), $80.50/day (Months 2-5)
  - Goal: 30 conversions, $200 CPL
  - Phase: Phase 1 (Maximize Conversions)

### **4. Trend Analysis**
- Daily conversion trends
- Daily cost trends
- Performance over time
- Campaign comparison trends

### **5. Google Analytics**
- Traffic source breakdown
- Top pages performance
- User behavior metrics
- Conversion funnel analysis

### **6. Alerts & Recommendations**
- Performance alerts
- Optimization recommendations
- Phase transition readiness
- Budget optimization suggestions

## 🔧 Configuration

### **Campaign Settings**
Edit `dashboard_config.yaml` to customize:
- Campaign IDs and names
- Budget allocations
- Goal targets
- Phase progression rules
- Alert thresholds

### **Display Settings**
- Chart colors and themes
- Table configurations
- Refresh intervals
- Alert sensitivity

## 📊 Key Metrics Explained

### **Conversion Rate**
- **Formula:** (Conversions / Clicks) × 100
- **Target:** Optimize for quality leads

### **Cost Per Lead (CPL)**
- **Formula:** Total Cost / Total Conversions
- **Local Presence Target:** $150
- **Feeder Markets Target:** $200

### **Click-Through Rate (CTR)**
- **Formula:** (Clicks / Impressions) × 100
- **Alert Threshold:** < 3%

### **Phase Progression**
- **Phase 1:** Maximize Conversions (gathering data)
- **Phase 2:** Target CPA (optimizing efficiency)
- **Phase 3:** Scaling (maximizing volume)

## 🚨 Alert System

### **Conversion Alerts**
- No conversions in 7+ days
- Conversion rate below 1%
- Lead quality score below 5.0

### **Cost Alerts**
- CPL exceeds goal by 50%
- Daily spend exceeds budget by 20%
- Cost trend increasing rapidly

### **Performance Alerts**
- CTR below 3%
- Bounce rate above 70%
- Session duration below 60 seconds

## 📈 Success Metrics

### **Phase 1 Success Criteria**
- ✅ 30+ conversions per campaign
- ✅ Stable CPL within target range
- ✅ Consistent conversion rates
- ✅ High lead quality scores

### **A/B Test Success Metrics**
- **Primary:** Conversion rate comparison
- **Secondary:** CPL efficiency
- **Tertiary:** Lead quality scores
- **Quaternary:** Overall ROAS

## 🔄 Data Refresh

### **Automatic Refresh**
- **Google Ads:** Every 5 minutes
- **Google Analytics:** Every 15 minutes
- **Alerts:** Real-time monitoring
- **Charts:** Auto-updating

### **Manual Refresh**
- Click the refresh button in the sidebar
- Use the "R" key for quick refresh
- Dashboard auto-refreshes on page reload

## 🛠️ Troubleshooting

### **Common Issues**

**1. Dashboard won't start**
```bash
# Check dependencies
pip install -r dashboard_requirements.txt

# Check environment variables
echo $GOOGLE_ADS_DEVELOPER_TOKEN
```

**2. No data showing**
- Verify campaign IDs in `dashboard_config.yaml`
- Check Google Ads API credentials
- Ensure campaigns are active

**3. Charts not loading**
- Check internet connection
- Verify Plotly installation
- Clear browser cache

### **Error Messages**

**"Google Ads API Error"**
- Verify API credentials
- Check campaign IDs
- Ensure campaigns are accessible

**"No data available"**
- Campaigns may be paused
- Date range may be too narrow
- API quota may be exceeded

## 📞 Support

### **Getting Help**
1. Check the troubleshooting section
2. Review error logs in the terminal
3. Verify configuration settings
4. Contact support with error details

### **Feature Requests**
- Submit via GitHub issues
- Include use case description
- Provide example data if relevant

## 🔮 Future Enhancements

### **Planned Features**
- **Real-time Google Analytics API** integration
- **Advanced A/B test statistical analysis**
- **Predictive performance modeling**
- **Automated optimization recommendations**
- **Email alert notifications**
- **Mobile-responsive design**

### **Integration Roadmap**
- **CRM integration** (Sierra Interactive)
- **Email marketing** (Mailchimp, ConvertKit)
- **Social media** (Facebook, Instagram)
- **Call tracking** (CallRail, Twilio)

---

## 📄 License

This dashboard is part of the Google Ads AI Manager project.

---

*Last Updated: September 4, 2025*
