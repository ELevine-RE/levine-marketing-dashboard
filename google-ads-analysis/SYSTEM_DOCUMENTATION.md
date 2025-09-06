# AI-Powered Google Ads Management System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [Core Modules](#core-modules)
4. [Decision-Making Logic](#decision-making-logic)
5. [Phase Management System](#phase-management-system)
6. [Guardrails System](#guardrails-system)
7. [Email Integration](#email-integration)
8. [API Integration](#api-integration)
9. [Workflow Examples](#workflow-examples)
10. [Configuration & Setup](#configuration--setup)
11. [Troubleshooting](#troubleshooting)

---

## System Overview

The AI-Powered Google Ads Management System is a comprehensive automation platform designed to manage Google Ads Performance Max campaigns with intelligent decision-making, safety guardrails, and automated reporting.

### Key Features
- **Automated Campaign Management**: AI-driven optimization and bulk operations
- **Phase-Based Progression**: Structured campaign lifecycle management
- **Safety Guardrails**: Automated safety checks and risk mitigation
- **Daily Email Summaries**: Automated reporting with intervention options
- **Progress Tracking**: Real-time monitoring with lag alerts
- **Excel Integration**: Configuration management via Excel files

### System Goals
1. **Automate routine campaign management tasks**
2. **Ensure safe, controlled campaign changes**
3. **Provide clear visibility into campaign performance**
4. **Enable data-driven decision making**
5. **Maintain campaign quality and compliance**

---

## Architecture & Components

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│                    Email Summary System                     │
│                    Progress Tracking                        │
│                    Guardrails System                        │
├─────────────────────────────────────────────────────────────┤
│                    Phase Management System                  │
│                    Campaign Analysis Engine                 │
├─────────────────────────────────────────────────────────────┤
│                    Google Ads API Layer                     │
│                    Excel Configuration Parser               │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Guardrails System** (`guardrails.py`)
- **Purpose**: Consolidated safety and compliance enforcement
- **Responsibilities**:
  - Budget and tCPA validation
  - Change cadence enforcement
  - Geo-targeting validation
  - Safety stop-loss monitoring
  - Risk assessment and mitigation

#### 2. **Change Management** (`change_management.py`)
- **Purpose**: Unified change tracking and performance monitoring
- **Responsibilities**:
  - Lever pull tracking and history
  - Performance snapshot management
  - Intervention item tracking
  - Comprehensive reporting
  - One lever per week enforcement

#### 3. **Asset Management** (`asset_manager.py`)
- **Purpose**: Consolidated asset extraction, validation, and upload
- **Responsibilities**:
  - Asset extraction from web pages
  - Google Ads compliance validation
  - Direct asset upload to campaigns
  - Asset manifest management
  - PMax requirements validation

#### 4. **Baseline Validator** (`baseline_validator.py`)
- **Purpose**: Campaign baseline requirements validation
- **Responsibilities**:
  - URL exclusion validation
  - Geo-targeting requirements
  - Asset requirements validation
  - Campaign naming conventions
  - Budget and tCPA settings validation

#### 5. **Google Ads Manager** (`google_ads_manager.py`)
- **Purpose**: Primary interface to Google Ads API
- **Responsibilities**: 
  - API authentication and connection management
  - Campaign data retrieval and modification
  - Bulk operations execution
  - Error handling and retry logic

#### 6. **Phase Manager** (`phase_manager.py`)
- **Purpose**: Campaign lifecycle and progression management
- **Responsibilities**:
  - Phase eligibility assessment
  - Progress tracking and lag detection
  - Timeline management
  - Readiness signal generation

#### 7. **Email Summary Generator** (`email_summary_generator.py`)
- **Purpose**: Automated reporting and communication
- **Responsibilities**:
  - Performance data aggregation
  - AI-driven recommendations
  - Email formatting and delivery
  - Intervention coordination

#### 8. **Excel Configuration Parser** (`excel_config_analyzer.py`)
- **Purpose**: Configuration management via Excel files
- **Responsibilities**:
  - Excel file parsing and validation
  - Configuration data extraction
  - Campaign creation automation

---

## Core Modules

### Google Ads Manager

#### Authentication Flow
```python
# 1. Load configuration from google-ads.yaml
client = GoogleAdsClient.load_from_storage()

# 2. Set manager account access
client.login_customer_id = "5426234549"

# 3. Initialize services
google_ads_service = client.get_service("GoogleAdsService")
```

#### Data Retrieval Logic
```python
# GAQL query for campaign data
query = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.daily_budget,
  campaign.target_cpa,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.cost_micros
FROM campaign
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
"""
```

#### Error Handling Strategy
1. **API Rate Limiting**: Exponential backoff with jitter
2. **Authentication Errors**: Automatic token refresh
3. **Permission Errors**: Manager account fallback
4. **Data Validation**: Schema validation before API calls

### Phase Management System

#### Phase Definitions

**Phase 1: Initial Setup and Testing**
- **Duration**: Expected 21 days, Max 35 days
- **Goals**: Establish baseline performance, validate targeting
- **Success Criteria**: ≥30 conversions, stable CPL, no recent changes

**Phase 2: tCPA Introduction**
- **Duration**: Expected 45 days, Max 70 days
- **Goals**: Optimize for conversions, establish tCPA targets
- **Success Criteria**: 30+ days under tCPA, CPL $80-$150, ≥5% lead quality

**Phase 3: Scaling and Optimization**
- **Duration**: Expected 90 days, Max 365 days
- **Goals**: Scale efficiently, optimize performance
- **Success Criteria**: Ongoing optimization, efficiency improvements

#### Eligibility Assessment Logic

```python
def check_phase_eligibility(self, metrics: Dict, phase: str) -> Dict:
    # Phase-specific requirements
    if phase == 'phase_1':
        return self._check_phase_1_to_2_eligibility(metrics)
    elif phase == 'phase_2':
        return self._check_phase_2_to_3_eligibility(metrics)
    elif phase == 'phase_3':
        return self._check_phase_3_status(metrics)
```

#### Progress Tracking Algorithm

```python
def check_phase_progress(self, start_date, current_date, phase, eligibility):
    days_in_phase = (current_date - start_date).days
    
    # Grace period: 1-3 days tolerance
    grace_period = 3
    
    if days_in_phase <= expected_days:
        return {"lagging": False, "lag_alert": False}
    elif days_in_phase <= expected_days + grace_period:
        return {"lagging": False, "lag_alert": False}  # Grace period
    elif days_in_phase <= max_days:
        return {"lagging": True, "lag_alert": False}
    else:
        return {"lagging": True, "lag_alert": True}  # Critical
```

---

## Decision-Making Logic

### Campaign Analysis Engine

#### Performance Assessment
```python
def analyze_campaign_performance(self, campaign_data):
    # Calculate key metrics
    cpl = campaign_data['cost'] / campaign_data['conversions']
    conversion_rate = campaign_data['conversions'] / campaign_data['clicks']
    roas = campaign_data['revenue'] / campaign_data['cost']
    
    # Determine performance tier
    if roas > 4.0 and cpl < 100:
        return "EXCELLENT"
    elif roas > 2.0 and cpl < 150:
        return "GOOD"
    elif roas > 1.0:
        return "ACCEPTABLE"
    else:
        return "NEEDS_IMPROVEMENT"
```

#### AI-Driven Recommendations

**Budget Optimization Logic**
```python
def recommend_budget_changes(self, campaign_data):
    current_budget = campaign_data['daily_budget']
    current_cpl = campaign_data['cpl']
    target_cpl = campaign_data['target_cpl']
    
    if current_cpl < target_cpl * 0.8:  # 20% below target
        return {
            'action': 'INCREASE_BUDGET',
            'percentage': 20,
            'reason': 'CPL below target - opportunity to scale'
        }
    elif current_cpl > target_cpl * 1.2:  # 20% above target
        return {
            'action': 'DECREASE_BUDGET',
            'percentage': 15,
            'reason': 'CPL above target - reduce spend'
        }
```

**tCPA Adjustment Logic**
```python
def recommend_tcpa_adjustments(self, campaign_data):
    current_tcpa = campaign_data['target_cpa']
    actual_cpa = campaign_data['actual_cpa']
    conversion_volume = campaign_data['conversions']
    
    if conversion_volume < 30:
        return {
            'action': 'MAINTAIN_TCPA',
            'reason': 'Insufficient conversion data'
        }
    
    if actual_cpa < current_tcpa * 0.9:  # 10% below target
        return {
            'action': 'DECREASE_TCPA',
            'percentage': 10,
            'reason': 'Actual CPA below target - optimize efficiency'
        }
    elif actual_cpa > current_tcpa * 1.1:  # 10% above target
        return {
            'action': 'INCREASE_TCPA',
            'percentage': 10,
            'reason': 'Actual CPA above target - increase volume'
        }
```

### Safety Decision Matrix

#### Risk Assessment Framework
```python
def assess_risk_level(self, change_request, campaign_state):
    risk_score = 0
    
    # Budget change risk
    if change_request['type'] == 'budget_adjustment':
        percentage_change = abs(change_request['new_budget'] - campaign_state['current_budget']) / campaign_state['current_budget']
        if percentage_change > 0.3:  # 30% change
            risk_score += 3
        elif percentage_change > 0.2:  # 20% change
            risk_score += 2
        else:
            risk_score += 1
    
    # Campaign performance risk
    if campaign_state['recent_7d_conversions'] == 0:
        risk_score += 5  # High risk - no conversions
    
    if campaign_state['days_since_last_conversion'] > 14:
        risk_score += 4  # High risk - conversion drought
    
    # Return risk level
    if risk_score >= 7:
        return "CRITICAL"
    elif risk_score >= 4:
        return "HIGH"
    elif risk_score >= 2:
        return "MEDIUM"
    else:
        return "LOW"
```

---

## Phase Management System

### Phase Transition Logic

#### Phase 1 → Phase 2 Decision Tree
```
Start Phase 1 Assessment
├── Check Conversions (≥30?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check Campaign Age (≥14 days?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check CPL Stability (±20%?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check Recent Changes (≥7 days?)
│   ├── Yes → Continue
│   └── No → Block progression
└── All Checks Pass → Eligible for Phase 2
```

#### Phase 2 → Phase 3 Decision Tree
```
Start Phase 2 Assessment
├── Check tCPA Duration (≥30 days?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check CPL Range ($80-$150?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check Lead Quality (≥5%?)
│   ├── Yes → Continue
│   └── No → Block progression
├── Check Pacing (≥80%?)
│   ├── Yes → Continue
│   └── No → Block progression
└── All Checks Pass → Eligible for Phase 3
```

### Progress Monitoring Algorithm

#### Lag Detection Logic
```python
def detect_lag_status(self, days_in_phase, expected_days, max_days, is_eligible):
    grace_period = 3
    
    if days_in_phase <= expected_days:
        return "ON_TRACK"
    elif days_in_phase <= expected_days + grace_period:
        return "GRACE_PERIOD"
    elif days_in_phase <= max_days:
        return "LAGGING"
    else:
        return "CRITICAL_LAG"
```

#### Alert Generation Logic
```python
def generate_alert(self, lag_status, campaign_data):
    if lag_status == "CRITICAL_LAG":
        return {
            'priority': 'CRITICAL',
            'action': 'IMMEDIATE_INTERVENTION',
            'message': f"Campaign exceeded maximum phase duration by {days_over} days"
        }
    elif lag_status == "LAGGING":
        return {
            'priority': 'HIGH',
            'action': 'REVIEW_AND_OPTIMIZE',
            'message': f"Campaign lagging {days_behind} days behind schedule"
        }
    elif lag_status == "GRACE_PERIOD":
        return {
            'priority': 'MEDIUM',
            'action': 'MONITOR',
            'message': f"Campaign slightly behind but within grace period"
        }
```

### Conversion Hygiene

The system enforces strict conversion tracking standards to ensure accurate phase progression and performance measurement:

**Primary Conversions**: Lead Form Submission, Phone Call
- Used for phase eligibility gates
- Required for tCPA adjustments
- Primary KPI for campaign success

**Secondary Conversions**: Page View, Click
- Used for optimization signals
- Not counted for phase progression
- Provide additional performance context

**Phase Gates**: All phase advancement decisions use primary conversions only to ensure consistent, high-quality lead measurement and prevent gaming of the system through soft conversion optimization.

---

## Guardrails System

### Safety Check Categories

#### 1. Budget Guardrails
```python
BUDGET_LIMITS = {
    'min_daily': 30.0,           # Minimum daily budget
    'max_daily': 100.0,          # Maximum daily budget
    'max_adjustment_percent': 30, # Maximum single adjustment
    'min_adjustment_percent': 20, # Minimum adjustment threshold
    'max_frequency_days': 7       # Minimum days between changes
}
```

#### 2. Target CPA Guardrails
```python
TARGET_CPA_LIMITS = {
    'min_value': 80.0,           # Minimum tCPA value
    'max_value': 200.0,          # Maximum tCPA value
    'max_adjustment_percent': 15, # Maximum single adjustment
    'min_adjustment_percent': 10, # Minimum adjustment threshold
    'max_frequency_days': 14,     # Minimum days between changes
    'min_conversions': 30        # Minimum conversions required
}
```

#### 3. Asset Group Guardrails
```python
ASSET_REQUIREMENTS = {
    'headlines': {'min': 5, 'aim': (7, 10)},           # Minimum headlines
    'long_headlines': {'min': 1, 'aim': (1, 2)},       # Minimum long headlines
    'descriptions': {'min': 2, 'aim': (3, 4)},         # Minimum descriptions
    'business_name': {'required': True},                # Business name required
    'logos': {                                          # Logo requirements
        '1_1': {'min': 1, 'aim': (1, 2)},              # Square logos
        '4_1': {'min': 1, 'aim': (1, 2)}               # Landscape logos
    },
    'images': {                                         # Image requirements
        '1_91_1': {'min': 3, 'aim': (3, 5)},          # Landscape images
        '1_1': {'min': 3, 'aim': (3, 5)}               # Square images
    },
    'video': {'min': 1, 'auto_gen_allowed': True}       # Video requirements
}
```

#### 4. Geo Targeting Guardrails
```python
GEO_TARGETING_LIMITS = {
    'presence_only_required': True,     # Must use presence-only targeting
    'max_changes_per_period': 1,        # Maximum changes per period
    'period_days': 21,                  # Period length in days
    'excluded_locations': [            # Required exclusions
        'India', 'Pakistan', 'Bangladesh', 'Philippines'
    ]
}
```

#### 5. Final URL Expansion Safety
```python
REQUIRED_URL_EXCLUSIONS = [
    '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
    '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
]
```

#### 6. Change Cadence Guardrails
```python
ONE_LEVER_PER_WEEK_DAYS = 7  # Maximum one major change per week
```

### Baseline Validation API Checks

The system enforces 6 critical baseline requirements that must be validated before any changes:

#### 1. Presence-Only Geo Targeting
```python
def validate_presence_only_targeting(self, campaign_data):
    # Must use presence-only targeting (not location-based)
    # Required exclusions: India, Pakistan, Bangladesh, Philippines
    return campaign_data['geo_targeting_type'] == 'PRESENCE_ONLY'
```

#### 2. Page Feed Linked
```python
def validate_page_feed_link(self, campaign_data):
    # Campaign must have PAGE_FEED asset set linked
    # Validates CampaignAssetSet relationship exists
    return campaign_data['page_feed_linked'] == True
```

#### 3. URL Exclusions Applied
```python
def validate_url_exclusions(self, campaign_data):
    # Required exclusions must be configured:
    # /buyers/*, /sellers/*, /featured-listings/*, /contact/*, 
    # /blog/*, /property-search/*, /idx/*, /privacy/*, /about/*
    return all(exclusion in campaign_data['url_exclusions'] 
              for exclusion in REQUIRED_URL_EXCLUSIONS)
```

#### 4. Asset Minimums Met
```python
def validate_asset_minimums(self, campaign_data):
    # Headlines ≥5, Long headlines ≥1, Descriptions ≥2
    # Business name required, Logos ≥1 each format
    # Images ≥3 each format, Video ≥1
    return (campaign_data['headlines_count'] >= 5 and
            campaign_data['long_headlines_count'] >= 1 and
            campaign_data['descriptions_count'] >= 2 and
            campaign_data['business_name_present'] == True and
            campaign_data['logos_count'] >= 2 and  # Both formats
            campaign_data['images_count'] >= 6 and  # Both formats
            campaign_data['video_count'] >= 1)
```

#### 5. Primary Conversion Mapping Correct
```python
def validate_conversion_mapping(self, campaign_data):
    # Primary conversions: Lead Form Submission, Phone Call
    # Secondary conversions: Page View, Click
    # Phase gates use primary conversions only
    primary_conversions = ['Lead Form Submission', 'Phone Call']
    return all(conv in campaign_data['conversion_actions'] 
              for conv in primary_conversions)
```

#### 6. One-Lever-Per-Week Rule
```python
def validate_change_cadence(self, campaign_data):
    # No more than one major change in the last 7 days
    # Applies to: Budget, tCPA, geo targeting, asset groups
    last_change_date = campaign_data['last_major_change_date']
    days_since_change = (datetime.now() - last_change_date).days
    return days_since_change >= 7
```

### Safety Stop-Loss Logic

#### Conversion Drought Detection
```python
def check_conversion_drought(self, campaign_data):
    days_since_conversion = campaign_data['days_since_last_conversion']
    recent_spend = campaign_data['recent_7d_spend']
    daily_budget = campaign_data['daily_budget']
    
    # Check for no conversions in 14 days
    if days_since_conversion >= 14:
        return {
            'triggered': True,
            'action': 'FREEZE_CHANGES',
            'reason': f'No conversions in {days_since_conversion} days'
        }
    
    # Check for overspend with no conversions
    if recent_spend > daily_budget * 2 and campaign_data['recent_7d_conversions'] == 0:
        return {
            'triggered': True,
            'action': 'PAUSE_CAMPAIGN',
            'reason': f'Spend ${recent_spend:.2f} exceeds 2x budget with 0 conversions'
        }
    
    return {'triggered': False}
```

### Change Validation Workflow

#### 1. Pre-Change Validation
```python
def validate_change_request(self, change_request, campaign_state):
    # Check basic requirements
    if not self._validate_basic_requirements(change_request):
        return {'approved': False, 'reason': 'Basic requirements not met'}
    
    # Check safety conditions
    safety_check = self._check_safety_stop_loss(campaign_state)
    if safety_check:
        return {'approved': False, 'reason': f'Safety stop-loss: {safety_check}'}
    
    # Check specific guardrails
    guardrail_result = self._check_specific_guardrails(change_request, campaign_state)
    return guardrail_result
```

#### 2. Change Execution Workflow
```python
def execute_change(self, change_request, campaign_state):
    # 1. Validate change
    validation = self.validate_change_request(change_request, campaign_state)
    if not validation['approved']:
        return {'success': False, 'reason': validation['reason']}
    
    # 2. Apply guardrails
    modified_request = self._apply_guardrails(change_request, campaign_state)
    
    # 3. Execute change
    try:
        result = self._execute_api_change(modified_request)
        return {'success': True, 'result': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

## Email Integration

### Email Summary Generation Logic

#### 1. Data Aggregation
```python
def aggregate_performance_data(self, campaigns):
    summary = {
        '24h': self._get_performance_summary(campaigns, 1),
        '7d': self._get_performance_summary(campaigns, 7),
        '14d': self._get_performance_summary(campaigns, 14),
        '30d': self._get_performance_summary(campaigns, 30)
    }
    return summary
```

#### 2. AI Recommendation Generation
```python
def generate_ai_recommendations(self, performance_data):
    recommendations = []
    
    # Budget optimization recommendations
    for campaign in performance_data['campaigns']:
        if campaign['roas'] > 4.0 and campaign['pacing'] < 0.8:
            recommendations.append({
                'type': 'BUDGET_INCREASE',
                'campaign': campaign['name'],
                'reason': 'High ROAS with pacing constraint',
                'action': f'Increase budget by 20-30%'
            })
    
    # tCPA optimization recommendations
    for campaign in performance_data['campaigns']:
        if campaign['actual_cpa'] < campaign['target_cpa'] * 0.9:
            recommendations.append({
                'type': 'TCPA_DECREASE',
                'campaign': campaign['name'],
                'reason': 'Actual CPA below target',
                'action': f'Decrease tCPA by 10%'
            })
    
    return recommendations
```

#### 3. Impact Assessment
```python
def assess_impact(self, recommendations, campaign_data):
    impact_score = 0
    impact_details = []
    
    for rec in recommendations:
        if rec['type'] == 'BUDGET_INCREASE':
            # Estimate additional spend and conversions
            estimated_spend = campaign_data['daily_budget'] * 0.25  # 25% increase
            estimated_conversions = estimated_spend / campaign_data['cpl']
            impact_score += 3
            impact_details.append(f"Budget increase: +${estimated_spend:.2f}/day, +{estimated_conversions:.1f} conversions/day")
        
        elif rec['type'] == 'TCPA_DECREASE':
            # Estimate efficiency improvement
            efficiency_gain = (campaign_data['target_cpa'] - campaign_data['actual_cpa']) / campaign_data['target_cpa']
            impact_score += 2
            impact_details.append(f"tCPA optimization: {efficiency_gain:.1%} efficiency gain")
    
    return {
        'score': impact_score,
        'level': 'HIGH' if impact_score >= 5 else 'MEDIUM' if impact_score >= 3 else 'LOW',
        'details': impact_details
    }
```

### Email Content Structure

#### 1. Performance Summary Section
```
📊 Performance Summary (Last 24 Hours)
• Impressions: 1,234
• Clicks: 45
• Conversions: 3
• Spend: $156.78
• CPL: $52.26
• ROAS: 2.8x

📈 Performance Summary (Last 7 Days)
• Impressions: 8,567
• Clicks: 312
• Conversions: 18
• Spend: $1,089.45
• CPL: $60.52
• ROAS: 2.4x
```

#### 2. Planned Changes Section
```
🎯 Planned Changes
• Campaign: L.R - PMax - General
  - Action: Increase budget by 25%
  - Reason: High ROAS (3.2x) with pacing constraint (65%)
  - Expected Impact: +$12.50/day spend, +0.8 conversions/day

• Campaign: L.R - PMax - Scaling
  - Action: Decrease tCPA by 10%
  - Reason: Actual CPA ($95) below target ($120)
  - Expected Impact: Improved efficiency, reduced CPL
```

#### 3. Intervention Section
```
⏰ Intervention Window
You have 2 hours to cancel these changes by replying to this email.
Changes will be executed automatically at 10:00 AM MT.

To cancel: Reply with "CANCEL" in the subject line.
```

---

## API Integration

### Google Ads API Connection

#### Authentication Flow
```python
# 1. Load OAuth credentials
client = GoogleAdsClient.load_from_storage('google-ads.yaml')

# 2. Set manager account access
client.login_customer_id = "5426234549"

# 3. Initialize required services
google_ads_service = client.get_service("GoogleAdsService")
campaign_service = client.get_service("CampaignService")
asset_set_service = client.get_service("AssetSetService")
```

#### Error Handling Strategy
```python
def handle_api_error(self, error):
    if "Authentication of the request failed" in str(error):
        return self._refresh_authentication()
    elif "User doesn't have permission" in str(error):
        return self._switch_to_manager_account()
    elif "Rate limit exceeded" in str(error):
        return self._implement_rate_limiting()
    else:
        return self._log_and_report_error(error)
```

### Data Retrieval Patterns

#### Campaign Performance Query
```python
query = """
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.daily_budget,
  campaign.target_cpa,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.cost_micros,
  metrics.conversions_value
FROM campaign
WHERE 
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date BETWEEN '2024-01-01' AND '2024-01-31'
"""
```

#### Asset Set Query
```python
query = """
SELECT
  asset_set.id,
  asset_set.name,
  asset_set.type,
  asset_set_asset.asset_set,
  asset.page_feed_asset.page_url
FROM asset_set
WHERE asset_set.type = 'PAGE_FEED'
"""
```

---

## Workflow Examples

### Daily Email Summary Workflow

#### 1. Data Collection (8:00 AM MT)
```python
# Collect performance data for all campaigns
performance_data = manager.get_campaign_performance(
    customer_id="8335511794",
    date_range="LAST_30_DAYS"
)

# Aggregate data by time periods
summary_data = {
    '24h': aggregate_by_period(performance_data, 1),
    '7d': aggregate_by_period(performance_data, 7),
    '14d': aggregate_by_period(performance_data, 14),
    '30d': aggregate_by_period(performance_data, 30)
}
```

#### 2. AI Analysis (8:05 AM MT)
```python
# Generate AI recommendations
recommendations = ai_engine.analyze_performance(summary_data)

# Assess impact of recommendations
impact_assessment = ai_engine.assess_impact(recommendations, summary_data)

# Generate planned changes
planned_changes = ai_engine.generate_change_plan(recommendations)
```

#### 3. Email Generation (8:10 AM MT)
```python
# Generate email content
email_content = email_generator.generate_email_content(
    summary_data,
    recommendations,
    impact_assessment,
    planned_changes
)

# Send email
email_generator.send_email(
    subject="Your Google Ads Summary Report",
    recipient="evan@levine.realestate",
    content=email_content
)
```

### Phase Progression Workflow

#### 1. Phase Eligibility Check
```python
# Check if campaign is eligible for next phase
eligibility = phase_manager.check_phase_eligibility(
    metrics=campaign_metrics,
    phase="phase_1"
)

if eligibility['eligible_for_next']:
    # Generate phase transition plan
    transition_plan = phase_manager.generate_transition_plan(eligibility)
    
    # Check guardrails for transition
    guardrail_check = guardrails.enforce_guardrails(
        change_request=transition_plan,
        campaign_state=campaign_metrics
    )
    
    if guardrail_check.verdict == 'APPROVED':
        # Execute phase transition
        execute_phase_transition(transition_plan)
```

#### 2. Progress Monitoring
```python
# Check progress against timeline
progress = phase_manager.check_phase_progress(
    start_date=phase_start_date,
    current_date=datetime.now(),
    phase="phase_1",
    eligibility=eligibility_result
)

if progress['lag_alert']:
    # Generate critical alert
    alert = phase_manager.generate_progress_notification(
        progress, "phase_1", campaign_name
    )
    send_critical_alert(alert)
elif progress['lagging']:
    # Generate lagging alert
    alert = phase_manager.generate_progress_notification(
        progress, "phase_1", campaign_name
    )
    include_in_daily_summary(alert)
```

### Emergency Response Workflow

#### 1. Safety Stop-Loss Detection
```python
# Monitor for safety conditions
safety_check = guardrails.check_safety_stop_loss(campaign_metrics)

if safety_check:
    # Generate emergency action
    emergency_action = guardrails.generate_emergency_action(
        safety_check, campaign_metrics
    )
    
    # Execute emergency action
    execute_emergency_action(emergency_action)
    
    # Send immediate notification
    send_emergency_notification(emergency_action)
```

#### 2. Critical Lag Alert Response
```python
# Detect critical phase lag
progress = phase_manager.check_phase_progress(...)

if progress['lag_alert']:
    # Generate emergency intervention
    intervention = phase_manager.generate_emergency_intervention(
        progress, campaign_metrics
    )
    
    # Check guardrails for emergency action
    guardrail_check = guardrails.enforce_guardrails(
        change_request=intervention,
        campaign_state=campaign_metrics
    )
    
    if guardrail_check.verdict == 'APPROVED':
        execute_emergency_intervention(intervention)
```

---

## Configuration & Setup

### Environment Configuration

#### Required Environment Variables
```bash
# Google Ads API Configuration
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=5426234549
GOOGLE_ADS_CUSTOMER_ID=8335511794

# Email Configuration
EMAIL_SENDER=elevine17@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=evan@levine.realestate
EMAIL_REPLY_TO=developer@levine.realestate
```

#### Google Ads Configuration File (`google-ads.yaml`)
```yaml
developer_token: "your_developer_token"
client_id: "your_client_id"
client_secret: "your_client_secret"
refresh_token: "your_refresh_token"
use_proto_plus: true
login_customer_id: "5426234549"
```

### Phase Configuration

#### Default Phase Settings
```python
PHASE_CONFIGURATION = {
    'phase_1': {
        'expected_days': 21,
        'max_days': 35,
        'requirements': {
            'min_conversions': 30,
            'min_days': 14,
            'cpl_stability_threshold': 20,
            'no_changes_days': 7
        }
    },
    'phase_2': {
        'expected_days': 45,
        'max_days': 70,
        'requirements': {
            'min_tcpa_days': 30,
            'cpl_min': 80.0,
            'cpl_max': 150.0,
            'lead_quality_threshold': 5.0,
            'pacing_threshold': 0.8
        }
    },
    'phase_3': {
        'expected_days': 90,
        'max_days': 365,
        'requirements': {
            'optimization_focus': True
        }
    }
}
```

### Guardrails Configuration

#### Safety Thresholds
```python
SAFETY_CONFIGURATION = {
    'budget_limits': {
        'min_daily': 30.0,
        'max_daily': 100.0,
        'max_adjustment_percent': 30,
        'min_adjustment_percent': 20,
        'max_frequency_days': 7
    },
    'target_cpa_limits': {
        'min_value': 80.0,
        'max_value': 200.0,
        'max_adjustment_percent': 15,
        'min_adjustment_percent': 10,
        'max_frequency_days': 14,
        'min_conversions': 30
    },
    'safety_limits': {
        'spend_multiplier_threshold': 2.0,
        'conversion_dry_spell_days': 14,
        'budget_overspend_days': 7
    }
}
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. API Authentication Errors
**Problem**: "Authentication of the request failed"
**Solution**:
```python
# Refresh OAuth token
def refresh_authentication(self):
    try:
        # Re-authenticate using refresh token
        client = GoogleAdsClient.load_from_storage('google-ads.yaml')
        client.refresh_access_token()
        return True
    except Exception as e:
        # Log error and request manual intervention
        self.log_error(f"Authentication refresh failed: {e}")
        return False
```

#### 2. Permission Errors
**Problem**: "User doesn't have permission to access customer"
**Solution**:
```python
# Switch to manager account access
def switch_to_manager_account(self):
    self.client.login_customer_id = "5426234549"  # Manager account
    return self.validate_access()
```

#### 3. Rate Limiting
**Problem**: "Rate limit exceeded"
**Solution**:
```python
# Implement exponential backoff
def implement_rate_limiting(self):
    import time
    import random
    
    wait_time = min(60 * (2 ** self.retry_count), 300)  # Max 5 minutes
    jitter = random.uniform(0, 0.1 * wait_time)
    time.sleep(wait_time + jitter)
    self.retry_count += 1
```

#### 4. Data Validation Errors
**Problem**: Invalid data format in API responses
**Solution**:
```python
# Implement data validation
def validate_campaign_data(self, data):
    required_fields = ['id', 'name', 'status', 'daily_budget']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate data types
    if not isinstance(data['daily_budget'], (int, float)):
        raise ValueError("daily_budget must be numeric")
    
    return True
```

### Debugging Tools

#### 1. Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_ads_system.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Debug Mode
```python
DEBUG_MODE = True

def debug_log(self, message, data=None):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")
        if data:
            print(f"[DEBUG] Data: {data}")
```

#### 3. Performance Monitoring
```python
import time

def monitor_performance(self, func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        self.log_performance(func.__name__, execution_time)
        
        return result
    return wrapper
```

### System Health Checks

#### 1. API Connectivity Check
```python
def check_api_connectivity(self):
    try:
        # Test API connection
        response = self.google_ads_service.search(
            customer_id=self.customer_id,
            query="SELECT campaign.id FROM campaign LIMIT 1"
        )
        return True
    except Exception as e:
        self.log_error(f"API connectivity check failed: {e}")
        return False
```

#### 2. Data Integrity Check
```python
def check_data_integrity(self):
    # Verify campaign data consistency
    campaigns = self.get_all_campaigns()
    
    for campaign in campaigns:
        if not self.validate_campaign_data(campaign):
            self.log_error(f"Data integrity issue in campaign: {campaign['id']}")
            return False
    
    return True
```

#### 3. Phase Consistency Check
```python
def check_phase_consistency(self):
    # Verify phase progression logic
    campaigns = self.get_all_campaigns()
    
    for campaign in campaigns:
        phase_result = self.check_phase_eligibility(
            campaign['metrics'],
            campaign['phase']
        )
        
        if phase_result['eligible_for_next'] and campaign['phase'] == 'phase_3':
            self.log_error(f"Phase 3 campaign marked as eligible for next phase")
            return False
    
    return True
```

---

## Conclusion

The AI-Powered Google Ads Management System provides comprehensive automation for Performance Max campaign management with intelligent decision-making, safety guardrails, and automated reporting. The system's modular architecture ensures scalability and maintainability while providing robust error handling and monitoring capabilities.

Key strengths of the system include:
- **Intelligent decision-making** based on performance data and AI analysis
- **Comprehensive safety measures** through the guardrails system
- **Structured campaign progression** with phase-based management
- **Automated reporting** with intervention options
- **Robust error handling** and troubleshooting capabilities

The system is designed to be production-ready with proper configuration and monitoring in place.
