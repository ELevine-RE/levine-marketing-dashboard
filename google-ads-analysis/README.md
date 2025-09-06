# AI-Powered Google Ads Management System

🚀 **Your personal AI assistant for Google Ads campaign management**

This system allows you to "chat with an expert (AI)" to manage your Google Ads campaigns, automate changes en masse, and troubleshoot issues efficiently.

## ✨ Features

- 🤖 **AI-Powered Analysis**: Get intelligent insights and recommendations
- 📊 **Performance Monitoring**: Real-time campaign performance tracking
- 🔧 **Bulk Operations**: Automate changes across multiple campaigns
- 🚨 **Issue Detection**: Automatic troubleshooting and health checks
- 📈 **Data Export**: Export data for further analysis
- 🎯 **Smart Recommendations**: AI-driven optimization suggestions

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Test connection
python test_connection.py
```

### 2. Quick Analysis
```bash
# Get immediate insights
python examples/quick_analysis.py
```

### 3. Bulk Operations
```bash
# Perform bulk operations
python examples/bulk_operations.py
```

### 4. QA Ramp Check
```bash
# Run comprehensive system check
bash tools/qa_ramp.sh --customer 8335511794 --campaign "L.R - PMax - General"
```

## 📋 Prerequisites

- ✅ Google Ads Account
- ✅ Google Cloud Project with Google Ads API enabled
- ✅ OAuth 2.0 credentials
- ✅ Developer Token
- ✅ Customer IDs (Manager + Regular accounts)

## 🔧 Configuration

Your `.env` file should contain:
```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=manager_account_id
GOOGLE_ADS_CUSTOMER_ID=target_account_id
```

## 🛠️ Consolidated Architecture

The system has been consolidated into **4 core modules** for improved maintainability and performance:

### Core Modules

#### 1. **Guardrails System** (`guardrails.py`)
- **Purpose**: Enforces all safety rules and business logic
- **Features**: Budget limits, tCPA validation, change cadence, geo-targeting
- **Usage**: Automatic validation of all campaign changes

#### 2. **Change Management** (`change_management.py`)
- **Purpose**: Tracks all campaign changes and performance
- **Features**: Lever tracking, performance monitoring, intervention management
- **Usage**: Comprehensive change history and reporting

#### 3. **Asset Management** (`asset_manager.py`)
- **Purpose**: Handles asset extraction, validation, and upload
- **Features**: Asset extraction, Google Ads compliance, direct upload
- **Usage**: Automated asset management for campaigns

#### 4. **Baseline Validator** (`baseline_validator.py`)
- **Purpose**: Validates campaign baseline requirements
- **Features**: URL exclusions, geo-targeting, asset requirements
- **Usage**: Ensures campaigns meet all baseline requirements

### QA Ramp Script
The `tools/qa_ramp.sh` script provides a comprehensive end-to-end system check:

```bash
# Run with default settings
bash tools/qa_ramp.sh

# Run with custom customer and campaign
bash tools/qa_ramp.sh --customer 8335511794 --campaign "L.R - PMax - General"

# Show help
bash tools/qa_ramp.sh --help
```

**What it does:**
1. ✅ Runs all unit tests (80 tests)
2. ✅ Validates baseline configuration (dry-run)
3. ✅ Performs quick analysis with phase status
4. ✅ Reports system health status

**Output format:**
```
Baseline OK | Guardrails active | Phase status: PHASE_1: Progressing normally
```

**Exit codes:**
- `0`: All systems healthy
- `1`: Issues detected (baseline failures, critical lag, etc.)

## 🛡️ Guardrails System

The system enforces critical safety invariants to prevent campaign damage:

### **Conversion Mapping**
- **Primary conversions = Lead Form Submission and Phone Call**; both represent high-value customer engagement
- Only Primary conversions count for phase progression gates
- Secondary conversions (Page View, Click, Time on Site, etc.) are logged but not used for phase eligibility

### **Asset Format Requirements**
- **Logos**: 1:1 & 4:1 formats required
- **Images**: 1.91:1 ≥3 and 1:1 ≥3 required  
- **Video**: ≥1 vertical video (or auto-generation enabled)

### **Final URL Exclusions**
The following URL exclusions must always be included:
```
/buyers/*, /sellers/*, /featured-listings/*, /contact/*, /blog/*, /property-search/*, /idx/*, /privacy/*, /about/*
```

### **Presence-Only Targeting**
- Presence-only targeting/exclusion is a hard fail invariant
- Any change from PRESENCE_ONLY targeting type will be rejected
- Required exclusions: India, Pakistan, Bangladesh, Philippines

### **Change Safety Rules**
- **Budget**: ±20-30% per adjustment, no more than once per week, min $30/day, max $250/day
- **tCPA**: Only after ≥30 conversions; adjust ±10-15% at a time, no more than once every 2 weeks, min $80, max $350
- **Asset Groups**: Never pause all groups; ensure each group meets minimum PMax asset requirements
- **Geo Targeting**: Enforce presence-only; at most one geo preset change every 21 days
- **One Lever Per Week**: No multiple major changes in 7 days
- **Change Window**: Announce planned change with a 2-hour delay before execution
- **Safety Stop-Loss**: If spend > 2× budget in last 7d with 0 conversions, pause campaign and alert

## 🎯 **Phase Management System**

The system manages campaign progression through three phases with automatic eligibility checking:

### **Phase Progression**
- **Phase 1 → Phase 2**: ≥30 primary conversions, ≥14 days, stable CPL, no recent changes
- **Phase 2 → Phase 3**: ≥30 days under tCPA, CPL $80-$150, lead quality ≥5% of leads tagged as 'serious' (CRM/manual tagging), pacing OK

### **Progress Tracking**
- **Timeline Monitoring**: Tracks days in current phase with grace periods
- **Lag Detection**: Identifies campaigns behind schedule with actionable alerts
- **Conversion Hygiene**: Only Primary conversions (lead form submissions and phone calls) count for phase gates

### **Phase Status**
- **Progressing Normally**: Campaign on track for phase advancement
- **Lagging**: Behind expected timeline but within grace period
- **Critical Lag**: Exceeded maximum timeline, requires immediate attention

## 🌐 **Unified Dashboard**

### **Web Dashboard Features**
- **Real-time Data**: Combines Google Ads and Google Analytics data
- **Unified Metrics**: CpHQL (Cost per High-Quality Lead), Average LQS, conversion rates, cost per session, paid traffic ratio
- **Visual Charts**: Traffic sources, performance trends, top pages
- **Auto-refresh**: Updates every 5 minutes
- **Mobile-friendly**: Responsive design for all devices

## 🤖 **Automated Asset Management**

### **Asset Extraction System**
- **Automatic Extraction**: Pulls images, videos, and text from your website pages
- **Google Ads Compliance**: Validates assets meet Google Ads requirements
- **Direct Upload**: Automatically uploads assets to campaigns
- **Continuous Refresh**: Updates assets when website content changes

### **How It Works**
1. **Feed Saved Search Results**: Provide URLs from your saved searches
2. **Automatic Extraction**: System extracts all images, videos, and text content
3. **Compliance Checking**: Validates dimensions, formats, and quality
4. **Direct Upload**: Uploads compliant assets to Google Ads campaigns
5. **Asset Tracking**: Maintains manifest of all extracted assets

### **Asset Types Extracted**
- **Images**: Property photos, hero images, general images
- **Logos**: Brand logos and variations
- **Videos**: Property videos and promotional content
- **Text Content**: Headlines and descriptions from page content

### **Usage**
```bash
# Extract assets from saved search results
python tools/test_asset_automation.py

# Upload assets to Google Ads (when API access is approved)
python tools/asset_uploader.py --customer 8335511794 --campaign "L.R - PMax - General"
```

### **Key Metrics Displayed**
- **CpHQL**: Cost per High-Quality Lead (primary metric)
- **Average LQS**: Lead Quality Score from Sierra Interactive
- **High-Quality Lead Ratio**: Percentage of leads with LQS ≥5
- **Conversion Rate**: Ads to conversions percentage
- **Cost per Session**: Paid traffic cost analysis
- **Paid Traffic Ratio**: Percentage of traffic from ads
- **Traffic Sources**: Breakdown of organic vs paid traffic
- **Top Pages**: Most visited pages on your website

### **Access Your Dashboard**
```bash
# Generate dashboard locally
python tools/test_unified_dashboard.py
python tools/generate_unified_dashboard.py

# View dashboard
open dashboard/index.html
```

### **Production Dashboard**
- **URL**: `https://yourusername.github.io/google-ads-setup`
- **Updates**: Daily at 8 AM MT via GitHub Actions
- **Data**: Real Google Ads and Analytics data
- **Security**: Credentials stored in GitHub Secrets

## 🎯 Usage Examples

### Daily Check-in
```python
from google_ads_manager import GoogleAdsManager

manager = GoogleAdsManager()
manager.analyze_performance()
manager.troubleshoot_issues()
```


### Email Summaries
```python
from email_summary_generator import EmailSummaryGenerator

# Generate and send email summary
generator = EmailSummaryGenerator(email_config)
generator.send_email(
    subject="Your Google Ads Summary Report",
    recipient="your-email@example.com"
)
```

### System Health Check
```bash
# Run comprehensive system check
bash tools/qa_ramp.sh --customer 8335511794 --campaign "L.R - PMax - General"

# Output: "Baseline OK | Guardrails active | Phase status: ..."
```

### Pause Underperforming Campaigns
```python
# Automatically pause campaigns spending >$50 with <1 conversion
manager = GoogleAdsManager()
campaigns = manager.get_campaigns()

underperforming = campaigns[
    (campaigns['cost'] > 50) & 
    (campaigns['conversions'] < 1)
]

updates = [{
    "campaign_id": str(campaign_id),
    "field": "status",
    "value": "PAUSED"
} for campaign_id in underperforming['campaign_id']]

manager.bulk_update_campaigns(updates)
```

### Adjust Budgets by Performance
```python
# Increase budgets for high performers, decrease for low performers
manager = GoogleAdsManager()
manager.adjust_budgets_by_performance()
```

## 🤖 AI Features

### Performance Analysis
- **CTR Analysis**: Identify low-click campaigns
- **CPC Optimization**: Find overpriced keywords
- **Conversion Tracking**: Monitor conversion rates
- **LQS Integration**: Lead Quality Score from Sierra Interactive
- **CpHQL Calculation**: Cost per High-Quality Lead tracking

### Smart Recommendations
- 🔴 **High Priority**: Issues requiring immediate attention
- 🟡 **Medium Priority**: Optimization opportunities
- 🟢 **Low Priority**: Minor improvements

### Automated Actions
- Pause underperforming campaigns
- Adjust budgets based on performance
- Optimize bid strategies
- Monitor account health

## 📊 Data Export

Export campaign data for external analysis:
```python
import pandas as pd

manager = GoogleAdsManager()
campaigns_df = manager.get_campaigns()

# Export to Excel
campaigns_df.to_excel('campaign_data.xlsx', index=False)

# Export to CSV
campaigns_df.to_csv('campaign_data.csv', index=False)
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check OAuth credentials
   - Verify developer token
   - Ensure API is enabled

2. **Permission Issues**
   - Verify account access
   - Check manager account setup
   - Confirm customer IDs

3. **Data Access Issues**
   - Check campaign status
   - Verify date ranges
   - Ensure sufficient permissions

### Health Check
```python
manager = GoogleAdsManager()
issues = manager.troubleshoot_issues()
```

## 🛠️ Development

### Project Structure
```
google-ads-setup/
├── guardrails.py           # Consolidated guardrails system
├── change_management.py     # Unified change tracking & reporting
├── asset_manager.py        # Asset extraction & management
├── baseline_validator.py   # Campaign baseline validation
├── google_ads_manager.py   # Main manager class
├── phase_manager.py        # Phase progression logic
├── examples/               # Example scripts
│   ├── quick_analysis.py   # Daily check-in
│   └── bulk_operations.py  # Bulk operations
├── tools/                  # Utility scripts
│   ├── qa_ramp.sh         # System health check
│   └── asset_extractor.py # Asset extraction tools
├── test_connection.py      # Connection test
├── oauth_helper.py         # OAuth setup
├── requirements.txt        # Dependencies
└── .env                    # Configuration
```

### Adding New Features
1. Extend `GoogleAdsManager` class
2. Add new methods for specific operations
3. Create example scripts
4. Update documentation

## 📈 Best Practices

### Daily Operations
1. **Morning Check**: Run quick analysis
2. **Performance Review**: Monitor key metrics
3. **Issue Resolution**: Address AI recommendations
4. **Optimization**: Implement suggested changes

### Weekly Tasks
1. **Deep Analysis**: Comprehensive performance review
2. **Budget Adjustments**: Optimize spend allocation
3. **Campaign Cleanup**: Pause underperformers
4. **Strategy Review**: Plan improvements

### Monthly Reviews
1. **ROI Analysis**: Calculate return on investment
2. **Trend Analysis**: Identify performance patterns
3. **Competitive Analysis**: Benchmark against industry
4. **Strategy Planning**: Plan next month's approach

## 🔐 Security

- Store credentials in `.env` file (never commit)
- Use virtual environments
- Regular credential rotation
- Monitor API usage

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review error messages
3. Verify configuration
4. Test with simple operations first

## 🚀 Future Enhancements

- [ ] Real-time alerts and notifications
- [ ] Advanced machine learning predictions
- [ ] Integration with other marketing tools
- [ ] Custom reporting dashboards
- [ ] Automated bid management
- [ ] Competitor analysis

---

**Happy optimizing! 🎯**
