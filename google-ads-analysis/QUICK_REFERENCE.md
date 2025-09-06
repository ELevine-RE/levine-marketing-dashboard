# AI-Powered Google Ads Management System - Quick Reference

## 🚀 System Overview

**Purpose**: Automated Google Ads Performance Max campaign management with AI-driven optimization, safety guardrails, and daily reporting.

**Key Components**:
- **Consolidated Guardrails System** - Budget, tCPA, change cadence, geo-targeting
- **Unified Change Management** - Lever tracking, performance monitoring, interventions
- **Asset Management** - Extraction, validation, and upload
- **Baseline Validator** - URL exclusions, geo-targeting, asset requirements
- **Phase Management System** - Campaign lifecycle and progression
- **Email Summary Generator** - Automated reporting and communication

---

## 📋 Quick Commands

### Setup & Testing
```bash
# Test API connection
python test_connection.py

# Test consolidated guardrails system
python guardrails.py

# Test unified change management
python change_management.py

# Test asset management
python asset_manager.py

# Test baseline validator
python baseline_validator.py

# Test phase manager
python phase_manager.py

# Test email system
python daily_email_config.py --test

# Run consolidated audit
python test_consolidated_audit.py
```

### Daily Operations
```bash
# Run daily email summary
python daily_email_config.py

# Check campaign status
python examples/quick_analysis.py

# Bulk operations
python examples/bulk_operations.py
```

---

## ⚙️ Configuration

### Environment Variables
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=5426234549
GOOGLE_ADS_CUSTOMER_ID=8335511794
EMAIL_SENDER=elevine17@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=evan@levine.realestate
```

### Google Ads Config (`google-ads.yaml`)
```yaml
developer_token: "your_token"
client_id: "your_client_id"
client_secret: "your_secret"
refresh_token: "your_refresh_token"
use_proto_plus: true
login_customer_id: "5426234549"
```

---

## 🎯 Phase Management

### Phase Requirements

**Phase 1 → Phase 2**
- ≥30 primary conversions in ≥14 days
- CPL stable within ±20%
- No major changes in last 7 days
- **Timeline**: Expected 21 days, Max 35 days

**Phase 2 → Phase 3**
- ≥30 days under tCPA
- CPL within $80-$150
- Lead quality ≥5% "serious" buyers
- Pacing not constrained
- **Timeline**: Expected 45 days, Max 70 days

### Notifications
- **Phase-Advance**: Only when all gates pass
- **Lagging**: Suppressed for 1–3d beyond expected
- **Critical Lag**: Alert if > max days

### Progress Tracking
```python
# Check phase eligibility
result = phase_manager.check_phase_eligibility(metrics, phase)

# Check progress
progress = phase_manager.check_phase_progress(
    start_date, current_date, phase, eligibility
)
```

### Conversion Hygiene
- **Primary Conversions**: Only Lead Form Submission and Phone Call count for phase gates
- **Secondary Conversions**: Page View, Click, Time on Site, etc. are logged but not used for phase progression
- **Validation**: Phase eligibility checks conversion mapping before evaluating other criteria

---

## 🛡️ Guardrails System

### Budget Limits
- **Min**: $30/day
- **Max**: $100/day
- **Adjustment**: ±20-30% per change
- **Frequency**: No more than once per week

### Target CPA Limits
- **Min**: $80
- **Max**: $200
- **Adjustment**: ±10-15% per change
- **Frequency**: No more than once every 2 weeks
- **Requirement**: ≥30 conversions

### Safety Stop-Loss
- **Spend > 2× budget in 7d with 0 conversions** → Pause campaign
- **No conversions in 14 days** → Freeze changes

### Asset Requirements
- **Headlines**: ≥5 (aim 7–10)
- **Long Headlines**: ≥1
- **Descriptions**: ≥2 (aim 3–4)
- **Business Name**: Required
- **Logos**: 1:1 & 4:1 ≥1 each
- **Images**: 1.91:1 ≥3, 1:1 ≥3
- **Videos**: ≥1 (or auto-gen)

### Geo Targeting (Hard Requirements)
- **Presence-only**: target + exclude
- **Change Frequency**: One geo preset change per 14–21 days
- **Restriction**: Never worldwide

### Final URL Expansion Safety
- **Requirement**: Must use page feed
- **URL Exclusions**: Enforce list `/buyers/*`, `/sellers/*`, `/featured-listings/*`, `/contact/*`, `/blog/*`, `/property-search/*`, `/idx/*`, `/privacy/*`, `/about/*`
- **Validator**: Blocks changes if missing

### Change Cadence
- **"One lever per week"**: Maximum one major change per 7-day period
- **Applies to**: Budget, tCPA, geo targeting, asset group modifications

### Hard Invariants (NEW)
- **Conversion Mapping**: Only Lead Form Submission and Phone Call can be Primary
- **URL Exclusions**: Exact list required: `/buyers/*`, `/sellers/*`, `/featured-listings/*`, `/contact/*`, `/blog/*`, `/property-search/*`, `/idx/*`, `/privacy/*`, `/about/*`
- **Asset Formats**: Each active group must have ≥1 1:1 logo, ≥1 4:1 logo, ≥3 1.91:1 images, ≥3 1:1 images, ≥1 vertical video (or auto-generation enabled)
- **Presence-Only Targeting**: Hard fail if targeting type changes from PRESENCE_ONLY

---

## 📧 Email System

### Daily Summary (8 AM MT)
- **Recipient**: evan@levine.realestate
- **Content**: 24h, 7d, 14d, 30d performance
- **AI Recommendations**: Budget, tCPA, targeting
- **Planned Changes**: With 2-hour intervention window
- **Impact Assessment**: Medium/long-term plan impact

### Alert Types
- **Critical Alerts**: Immediate notification for max days exceeded
- **Lagging Alerts**: Daily summary inclusion for behind schedule
- **Ready Alerts**: Next phase available notifications

---

## 🔧 API Integration

### Key Services
```python
google_ads_service = client.get_service("GoogleAdsService")
campaign_service = client.get_service("CampaignService")
asset_set_service = client.get_service("AssetSetService")
```

### Common Queries
```python
# Campaign performance
query = """
SELECT campaign.id, campaign.name, campaign.status,
       metrics.impressions, metrics.clicks, metrics.conversions
FROM campaign
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
"""

# Asset sets
query = """
SELECT asset_set.id, asset_set.name, asset_set.type
FROM asset_set
WHERE asset_set.type = 'PAGE_FEED'
"""
```

---

## 📊 Decision-Making Logic

### Performance Assessment
- **Excellent**: ROAS > 4.0, CPL < 100
- **Good**: ROAS > 2.0, CPL < 150
- **Acceptable**: ROAS > 1.0
- **Needs Improvement**: ROAS ≤ 1.0

### Budget Optimization
- **Increase**: CPL < target × 0.8 (20% below)
- **Decrease**: CPL > target × 1.2 (20% above)
- **Maintain**: CPL within ±20% of target

### tCPA Optimization
- **Decrease**: Actual CPA < target × 0.9 (10% below)
- **Increase**: Actual CPA > target × 1.1 (10% above)
- **Requirement**: ≥30 conversions for adjustments

---

## 🚨 Emergency Procedures

### Critical Lag Alert
1. **Detect**: Days in phase > max days
2. **Assess**: Check eligibility and blocking factors
3. **Action**: Generate emergency intervention
4. **Execute**: Apply guardrail-approved changes
5. **Notify**: Send immediate alert

### Safety Stop-Loss
1. **Detect**: No conversions in 14 days OR spend > 2× budget
2. **Action**: Pause campaign or freeze changes
3. **Notify**: Send emergency notification
4. **Review**: Schedule performance review

---

## 📁 File Structure

```
google-ads-setup/
├── guardrails.py                 # Consolidated guardrails system
├── change_management.py          # Unified change tracking & reporting
├── asset_manager.py              # Asset extraction & management
├── baseline_validator.py         # Campaign baseline validation
├── google_ads_manager.py         # Core API interface
├── phase_manager.py              # Phase progression system
├── email_summary_generator.py    # Email reporting
├── daily_email_config.py         # Daily email automation
├── excel_config_analyzer.py      # Excel configuration parser
├── pmax_campaign_creator.py      # Campaign creation
├── test_consolidated_audit.py    # Consolidated system audit
├── requirements.txt              # Dependencies
├── google-ads.yaml              # API configuration
├── .env                         # Environment variables
├── examples/                    # Example scripts
│   ├── quick_analysis.py
│   ├── bulk_operations.py
│   ├── guardrails_example.py
│   └── phase_manager_integration.py
├── tools/                       # Utility scripts
│   ├── qa_ramp.sh              # System health check
│   └── asset_extractor.py      # Asset extraction tools
└── docs/                        # Documentation
    ├── SYSTEM_DOCUMENTATION.md
    ├── QUICK_REFERENCE.md
    └── CONSOLIDATED_AUDIT_REPORT.md
```

---

## 🔍 Troubleshooting

### Common Issues

**API Authentication Error**
```python
# Refresh token
client.refresh_access_token()
```

**Permission Error**
```python
# Switch to manager account
client.login_customer_id = "5426234549"
```

**Rate Limiting**
```python
# Implement backoff
time.sleep(min(60 * (2 ** retry_count), 300))
```

### Debug Mode
```python
DEBUG_MODE = True
# Enables detailed logging and error reporting
```

---

## 📞 Support

### Key Functions
- **Guardrails**: `guardrails.validate_budget_adjustment()`, `guardrails.validate_tcpa_adjustment()`
- **Change Management**: `change_management.check_one_lever_per_week()`, `change_management.add_lever_pull()`
- **Asset Management**: `asset_manager.extract_assets_from_page()`, `asset_manager.upload_asset_batch()`
- **Baseline Validator**: `baseline_validator.validate_campaign_structure()`, `baseline_validator.validate_url_exclusions()`
- **Phase Management**: `phase_manager.check_phase_eligibility()`
- **Email**: `email_generator.send_email()`
- **Progress**: `phase_manager.check_phase_progress()`

### Log Files
- **System Log**: `google_ads_system.log`
- **Error Log**: `error.log`
- **Performance Log**: `performance.log`

---

## 🎯 Quick Start Checklist

- [ ] Set up environment variables
- [ ] Configure `google-ads.yaml`
- [ ] Test API connection
- [ ] Verify email configuration
- [ ] Test guardrails system
- [ ] Test phase manager
- [ ] Set up daily cron job
- [ ] Monitor first email summary
- [ ] Review and adjust configurations

---

## 📈 Performance Metrics

### Key KPIs
- **ROAS**: Return on Ad Spend
- **CPL**: Cost per Lead
- **Conversion Rate**: Conversions / Clicks
- **Pacing**: Actual spend / Budget
- **Lead Quality**: % of "serious" buyers

### Alert Thresholds
- **Critical**: ROAS < 1.0, CPL > 200
- **Warning**: ROAS < 2.0, CPL > 150
- **Good**: ROAS > 2.0, CPL < 150
- **Excellent**: ROAS > 4.0, CPL < 100
