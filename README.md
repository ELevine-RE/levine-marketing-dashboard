# 🤖 AI Google Ads Management System

**Your AI assistant handles the day-to-day, you intervene as needed**

## 🎯 Core Vision

This is a **simplified, focused AI-driven Google Ads management system** that allows you to act as an executive while the AI handles the majority of day-to-day operations.

### What You Get Daily
- **📧 Email Summary**: Status, goals, planned changes with 2-hour intervention window
- **📊 Simple Dashboard**: Campaign diagnostics, staged changes, marketing calendar
- **⏳ Staging System**: Review/approve AI-recommended changes (auto-approve if ignored)
- **🤖 AI Chat Agent**: Intervene and modify via Cursor when needed

## 🚀 Quick Start

### 1. Run the Simple Dashboard
```bash
streamlit run simple_dashboard.py
```

### 2. Test Daily Email System
```bash
python daily_email_system.py
```

### 3. Test AI Campaign Builder
```bash
python ai_campaign_builder.py
```

## 📋 Core Components

### 1. **Simple Dashboard** (`simple_dashboard.py`)
- **Campaign Diagnostics**: Real-time performance, spend, conversions
- **Staged Changes**: Review AI recommendations, approve/reject/modify
- **Marketing Calendar**: Campaign timeline and planned activities
- **Goals & Status**: Progress tracking and system health

### 2. **Daily Email System** (`daily_email_system.py`)
- **Executive Summary**: Status, goals, staged changes
- **Automated Delivery**: Daily at 8 AM MT
- **Intervention Window**: 2-hour delay before auto-execution

### 3. **AI Campaign Builder** (`ai_campaign_builder.py`)
- **Intelligent Creation**: Parses campaign names for smart defaults
- **Guardrails Integration**: Validates all changes against safety rules
- **Automated Asset Management**: Extracts and uploads assets
- **Audit Trail**: Logs all campaign creation activities

## 🛡️ Guardrails System

The system enforces critical safety rules:

### Budget Limits
- **Min**: $30/day
- **Max**: $250/day
- **Adjustment**: ±20-30% per change
- **Frequency**: No more than once per week

### Safety Stop-Loss
- **Spend > 2× budget in 7d with 0 conversions** → Pause campaign
- **No conversions in 14 days** → Freeze changes

### Required URL Exclusions
```
/buyers/*, /sellers/*, /featured-listings/*, /contact/*, 
/blog/*, /property-search/*, /idx/*, /privacy/*, /about/*
```

## 📧 Email Configuration

Set up your `.env` file:
```env
# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=5426234549
GOOGLE_ADS_CUSTOMER_ID=8335511794

# Email System
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=evan@levine.realestate
```

## 🎯 Usage Workflow

### Daily Routine
1. **Morning**: Check email summary
2. **Review**: Staged changes in dashboard
3. **Intervene**: Use Cursor chat if needed
4. **Monitor**: Let AI handle optimization

### Weekly Tasks
1. **Review**: Campaign performance trends
2. **Approve**: Batch of staged changes
3. **Plan**: New campaign strategies
4. **Adjust**: Goals and targets

## 🔧 Development

### Project Structure
```
WebTool/
├── simple_dashboard.py          # Main dashboard
├── daily_email_system.py        # Email automation
├── ai_campaign_builder.py       # Campaign creation
├── google-ads-analysis/         # Core AI systems
│   ├── guardrails.py           # Safety rules
│   ├── change_management.py    # Change tracking
│   ├── phase_manager.py        # Campaign phases
│   └── tools/                  # Utilities
├── data/                       # Data storage
│   ├── staged_changes.json     # Pending changes
│   └── campaign_creation_log.json
├── requirements.txt            # Dependencies
└── README.md                  # This file
```

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run simple_dashboard.py

# Test email system
python daily_email_system.py
```

### Production (GitHub Actions)
The system includes automated workflows for:
- Daily email summaries
- Campaign analysis
- Milestone detection
- Change execution

## 📞 Support

For issues or questions:
1. Check the dashboard for system status
2. Review staged changes for pending actions
3. Use Cursor chat for AI interventions
4. Check email summaries for daily updates

---

**Your AI assistant is ready to manage your Google Ads campaigns! 🎯**