#!/usr/bin/env python3
"""
Comprehensive Marketing Dashboard
================================

A Streamlit dashboard that displays:
- Google Analytics metrics
- Google Ads campaign performance
- Goal progression tracking
- A/B test comparison
- Real-time monitoring

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import os
import sys
import logging
from typing import Dict, List, Optional, Any

# Configure logging to write to app.log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Google Ads integration if available, otherwise use mock data
try:
    from google_ads_integration import SimpleGoogleAdsManager
    HAS_GOOGLE_ADS = True
    logger.info("✅ Successfully imported Google Ads integration")
except ImportError as e:
    HAS_GOOGLE_ADS = False
    logger.warning(f"⚠️ Google Ads integration not available, using mock data. Import error: {e}")
    print("⚠️  Google Ads integration not available, using mock data")

# Import Google Analytics integration if available, otherwise use mock data
try:
    from google_analytics_simple import SimpleGoogleAnalyticsManager
    HAS_GOOGLE_ANALYTICS = True
    logger.info("✅ Successfully imported Google Analytics integration")
except ImportError as e:
    HAS_GOOGLE_ANALYTICS = False
    logger.warning(f"⚠️ Google Analytics integration not available, using mock data. Import error: {e}")
    print("⚠️  Google Analytics integration not available, using mock data")

# Import Sierra Interactive integration if available, otherwise use mock data
try:
    from sierra_integration import SimpleSierraManager
    HAS_SIERRA = True
    logger.info("✅ Successfully imported Sierra Interactive integration")
except ImportError as e:
    HAS_SIERRA = False
    logger.warning(f"⚠️ Sierra Interactive integration not available, using mock data. Import error: {e}")
    print("⚠️  Sierra Interactive integration not available, using mock data")

# Import other local modules if available
try:
    from ads.phase_manager import CampaignPhaseManager
    from ads.guardrails import PerformanceMaxGuardrails
    HAS_LOCAL_MODULES = True
    logger.info("✅ Successfully imported local modules")
except ImportError as e:
    HAS_LOCAL_MODULES = False
    logger.warning(f"⚠️ Local modules not available. Import error: {e}")
    print("⚠️  Local modules not available")

# Import Command Center view
try:
    from command_center_view import render_command_center_view
    HAS_COMMAND_CENTER = True
    logger.info("✅ Successfully imported Command Center view")
except ImportError as e:
    HAS_COMMAND_CENTER = False
    logger.warning(f"⚠️ Command Center view not available. Import error: {e}")
    print("⚠️  Command Center view not available")

# Import Strategic Plan view
try:
    from strategic_plan_view import render_strategic_plan_view
    HAS_STRATEGIC_PLAN = True
    logger.info("✅ Successfully imported Strategic Plan view")
except ImportError as e:
    HAS_STRATEGIC_PLAN = False
    logger.warning(f"⚠️ Strategic Plan view not available. Import error: {e}")
    print("⚠️  Strategic Plan view not available")

# Import Marketing Plan & Timeline view
try:
    from marketing_plan_view import render_marketing_plan_view
    HAS_MARKETING_PLAN = True
    logger.info("✅ Successfully imported Marketing Plan & Timeline view")
except ImportError as e:
    HAS_MARKETING_PLAN = False
    logger.warning(f"⚠️ Marketing Plan & Timeline view not available. Import error: {e}")
    print("⚠️  Marketing Plan & Timeline view not available")

# Page configuration
st.set_page_config(
    page_title="Marketing Dashboard - A/B Test",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("📊 Marketing Dashboard")
page = st.sidebar.selectbox(
    "Select Page",
    ["Main Dashboard", "Strategic Plan", "Marketing Plan & Timeline", "AI Command Center", "Diagnostics"]
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .goal-progress {
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        border-radius: 0.5rem;
        padding: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
    .campaign-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .phase-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .phase-1 { background-color: #ffeb3b; color: #000; }
    .phase-2 { background-color: #4caf50; color: white; }
    .phase-3 { background-color: #2196f3; color: white; }
</style>
""", unsafe_allow_html=True)

class MarketingDashboard:
    """Comprehensive marketing dashboard for A/B test monitoring."""
    
    def __init__(self):
        """Initialize the dashboard."""
        logger.info("🚀 Initializing MarketingDashboard")
        
        # Initialize Google Ads integration
        if HAS_GOOGLE_ADS:
            try:
                self.google_ads_manager = SimpleGoogleAdsManager()
                logger.info("✅ Google Ads integration initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Ads integration failed, using mock data: {e}")
                self.google_ads_manager = None
        else:
            self.google_ads_manager = None
            logger.info("⚠️ Google Ads integration not available, using mock data")
        
        # Initialize Google Analytics integration
        if HAS_GOOGLE_ANALYTICS:
            try:
                self.google_analytics_manager = SimpleGoogleAnalyticsManager()
                logger.info("✅ Google Analytics integration initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Analytics integration failed, using mock data: {e}")
                self.google_analytics_manager = None
        else:
            self.google_analytics_manager = None
            logger.info("⚠️ Google Analytics integration not available, using mock data")
        
        # Initialize Sierra Interactive integration
        if HAS_SIERRA:
            try:
                self.sierra_manager = SimpleSierraManager()
                logger.info("✅ Sierra Interactive integration initialized")
            except Exception as e:
                logger.warning(f"⚠️ Sierra Interactive integration failed, using mock data: {e}")
                self.sierra_manager = None
        else:
            self.sierra_manager = None
            logger.info("⚠️ Sierra Interactive integration not available, using mock data")
        
        # Initialize other local modules
        if HAS_LOCAL_MODULES:
            self.phase_manager = CampaignPhaseManager()
            self.guardrails = PerformanceMaxGuardrails()
            logger.info("✅ Initialized with local modules")
        else:
            self.phase_manager = None
            self.guardrails = None
            logger.info("⚠️ Local modules not available")
        
        # Campaign configurations
        self.campaigns = {
            "local_presence": {
                "name": "Local Presence",
                "id": "campaign_1_id",  # Replace with actual ID
                "budget_month1": 31.50,
                "budget_months2_5": 34.50,
                "goal_conversions": 30,
                "goal_cpl": 150,
                "phase": "phase_1"
            },
            "feeder_markets": {
                "name": "Feeder Markets", 
                "id": "campaign_2_id",  # Replace with actual ID
                "budget_month1": 73.50,
                "budget_months2_5": 80.50,
                "goal_conversions": 30,
                "goal_cpl": 200,
                "phase": "phase_1"
            }
        }
        
        # Initialize session state
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
    
    def safe_get_last(self, data, key, default=0):
        """Safely get the last element from a list or return the value if it's scalar."""
        value = data.get(key, default)
        if isinstance(value, list):
            return value[-1] if len(value) > 0 else default
        return value if value is not None else default
    
    def calculate_goal_progress(self, campaign_data: Dict, campaign_config: Dict) -> Dict:
        """Calculate progress towards campaign goals."""
        try:
            # Safely get cumulative data with fallbacks
            cumulative = campaign_data.get("cumulative", {})
            
            # Convert to regular Python numbers, handling multi-dimensional arrays
            def safe_convert(value):
                if hasattr(value, 'item') and value.size == 1:
                    return value.item()  # For NumPy scalars
                elif hasattr(value, 'sum'):
                    return float(value.sum())  # For multi-element arrays
                else:
                    return float(value)  # For regular numbers
            
            total_conversions = safe_convert(cumulative.get("total_conversions", 0))
            total_cost = safe_convert(cumulative.get("total_cost", 0))
            
            # Calculate goal progress (simplified for real data)
            monthly_goal = campaign_config.get("monthly_goal", 50)  # Default goal
            progress_percentage = min((total_conversions / monthly_goal) * 100, 100) if monthly_goal > 0 else 0
            
            cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else 0
            cpl_goal = campaign_config.get("cpl_goal", 100)  # Default CPL goal
            cpl_progress = max(0, min(100, (cpl_goal - cost_per_conversion) / cpl_goal * 100)) if cpl_goal > 0 else 0
            
            return {
                "conversions": {
                    "current": total_conversions,
                    "goal": monthly_goal,
                    "progress": progress_percentage
                },
                "cpl": {
                    "current": cost_per_conversion,
                    "goal": cpl_goal,
                    "progress": cpl_progress
                },
                "phase": {
                    "current": campaign_config.get("phase", "growth"),
                    "progress": progress_percentage  # Use conversion progress as phase progress
                },
                "cost": {
                    "total": total_cost,
                    "per_conversion": cost_per_conversion
                }
            }
        except Exception as e:
            logger.error(f"Error calculating goal progress: {e}")
            return {
                "conversions": {
                    "current": 0,
                    "goal": 50,
                    "progress": 0
                },
                "cpl": {
                    "current": 0,
                    "goal": 100,
                    "progress": 0
                },
                "phase": {
                    "current": "growth",
                    "progress": 0
                },
                "cost": {
                    "total": 0,
                    "per_conversion": 0
                }
            }
    
    def load_google_analytics_data(self) -> Dict:
        """Load Google Analytics data."""
        logger.info("📊 Loading Google Analytics data")
        
        # Try to use real Google Analytics data first
        if self.google_analytics_manager:
            try:
                logger.info("📡 Attempting to fetch real Google Analytics data")
                real_data = self.google_analytics_manager.get_analytics_data(days=30)
                if real_data and "error" not in real_data:
                    logger.info("✅ Successfully loaded real Google Analytics data")
                    return real_data
                else:
                    logger.warning(f"⚠️ Google Analytics API returned error: {real_data.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"❌ Error fetching Google Analytics data: {e}")
        
        # Fallback to mock data if real data fails
        logger.info("⚠️ Using mock Google Analytics data")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Generate sample GA data
        dates = pd.date_range(start_date, end_date, freq='D')
        
        ga_data = {
            "website_traffic": {
                "dates": [d.strftime("%Y-%m-%d") for d in dates],
                "sessions": np.random.randint(100, 500, len(dates)),
                "users": np.random.randint(80, 400, len(dates)),
                "pageviews": np.random.randint(200, 1000, len(dates)),
                "bounce_rate": np.random.uniform(0.3, 0.7, len(dates)),
                "avg_session_duration": np.random.uniform(60, 300, len(dates))
            },
            "conversions": {
                "dates": [d.strftime("%Y-%m-%d") for d in dates],
                "lead_form_submissions": np.random.randint(0, 3, len(dates)),
                "phone_calls": np.random.randint(0, 2, len(dates)),
                "email_signups": np.random.randint(0, 5, len(dates)),
                "conversions": np.random.randint(0, 5, len(dates)),
                "revenue": np.random.uniform(0, 1000, len(dates)),
                "purchase_revenue": np.random.uniform(0, 800, len(dates))
            },
            "traffic_sources": {
                "Organic Search": {"sessions": 450, "users": 380, "percentage": 45},
                "Paid Search": {"sessions": 350, "users": 300, "percentage": 35},
                "Direct": {"sessions": 150, "users": 120, "percentage": 15},
                "Social": {"sessions": 50, "users": 40, "percentage": 5}
            },
            "summary": {
                "total_sessions": sum(np.random.randint(100, 500, len(dates))),
                "total_users": sum(np.random.randint(80, 400, len(dates))),
                "total_pageviews": sum(np.random.randint(200, 1000, len(dates))),
                "avg_bounce_rate": np.random.uniform(0.3, 0.7),
                "avg_session_duration": np.random.uniform(60, 300),
                "total_conversions": sum(np.random.randint(0, 5, len(dates))),
                "total_revenue": sum(np.random.uniform(0, 1000, len(dates)))
            }
        }
        
        return ga_data
    
    def load_google_ads_data(self) -> Dict:
        """Load Google Ads campaign data."""
        logger.info("🎯 Loading Google Ads data")
        
        # Try to use real Google Ads data first
        if self.google_ads_manager:
            try:
                logger.info("📡 Attempting to fetch real Google Ads data")
                real_data = self.google_ads_manager.get_campaign_data(days=30)
                if real_data:
                    logger.info(f"✅ Successfully loaded real data for {len(real_data)} campaigns")
                    return real_data
                else:
                    logger.error("❌ No real data returned from Google Ads API")
                    return {"error": "No campaigns found in Google Ads account"}
            except Exception as e:
                logger.error(f"❌ Failed to load real Google Ads data: {e}")
                return {"error": f"Google Ads API Error: {str(e)}"}
        
        # No Google Ads manager available
        logger.error("❌ Google Ads integration not available")
        return {"error": "Google Ads integration not configured"}
    
    def load_sierra_data(self) -> Dict:
        """Load Sierra Interactive CRM data."""
        logger.info("📋 Loading Sierra Interactive data")
        
        # Try to use real Sierra Interactive data first
        if self.sierra_manager:
            try:
                logger.info("📡 Attempting to fetch real Sierra Interactive data")
                real_data = self.sierra_manager.get_comprehensive_data(days=30)
                if real_data and "error" not in real_data:
                    logger.info("✅ Successfully loaded real Sierra Interactive data")
                    return real_data
                else:
                    logger.warning(f"⚠️ Sierra Interactive API returned error: {real_data.get('error', 'No valid credentials available')}")
            except Exception as e:
                logger.error(f"❌ Error fetching Sierra Interactive data: {e}")
        
        # Fallback to mock data if real data fails
        logger.info("⚠️ Using mock Sierra Interactive data")
        return self.generate_mock_sierra_data()
    
    def generate_mock_sierra_data(self) -> Dict:
        """Generate mock Sierra Interactive data for testing."""
        logger.info("🎭 Generating mock Sierra Interactive data")
        
        # Generate mock data structure
        sierra_data = {
            "leads": {
                "total_records": 45,
                "records_by_status": {
                    "Active": 25,
                    "New": 12,
                    "Qualify": 5,
                    "Closed": 3
                },
                "records_by_source": {
                    "Website": 20,
                    "Google Ads": 15,
                    "Referral": 7,
                    "Direct": 3
                },
                "recent_records": [
                    {"id": 1, "name": "John Smith", "email": "john@example.com", "status": "Active", "source": "Website"},
                    {"id": 2, "name": "Jane Doe", "email": "jane@example.com", "status": "New", "source": "Google Ads"}
                ],
                "summary": {
                    "total_records": 45,
                    "active_records": 25,
                    "new_records": 12,
                    "converted_records": 3
                }
            },
            "users": {
                "total_users": 5,
                "users_by_role": {
                    "Agent": 3,
                    "Manager": 1,
                    "Primary Manager": 1
                },
                "users_by_status": {
                    "Active": 5
                },
                "active_users": [
                    {"id": 13772, "name": "Evan Levine", "email": "Evan@Levine.RealEstate", "role": "Primary Manager", "phone": "(435) 224-5242"}
                ],
                "summary": {
                    "total_users": 5,
                    "active_users": 5,
                    "agents": 3,
                    "managers": 2
                }
            },
            "summary": {
                "total_records": 45,
                "active_records": 25,
                "total_users": 5,
                "active_users": 5,
                "conversion_rate": 6.7
            }
        }
        
        return sierra_data
    
    def get_ads_data(self) -> Dict:
        """Get Google Ads data for external use."""
        return self.load_google_ads_data()
    
    def get_analytics_data(self) -> Dict:
        """Get Google Analytics data for external use."""
        return self.load_google_analytics_data()
    
    def get_sierra_data(self) -> Dict:
        """Get Sierra Interactive CRM data for external use."""
        return self.load_sierra_data()
    
    def render_header(self):
        """Render the dashboard header."""
        logger.info("🎨 Rendering dashboard header")
        st.markdown('<h1 class="main-header">📊 Marketing Dashboard - A/B Test</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Last Updated", st.session_state.last_refresh.strftime("%H:%M:%S"))
        
        with col2:
            st.metric("Test Duration", "Day 1 of 150")
        
        with col3:
            st.metric("Overall Status", "🟢 Active")
    
    def render_overview_metrics(self, ga_data: Dict, ads_data: Dict):
        """Render overview metrics."""
        logger.info("📈 Rendering overview metrics")
        st.subheader("📈 Overview Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sessions = sum(ga_data["website_traffic"]["sessions"])
            st.metric("Website Sessions (30d)", f"{total_sessions:,}")
        
        with col2:
            # Handle different conversion data structures
            if "lead_form_submissions" in ga_data["conversions"]:
                total_conversions = sum(ga_data["conversions"]["lead_form_submissions"]) + sum(ga_data["conversions"]["phone_calls"])
            elif "conversions" in ga_data["conversions"]:
                total_conversions = sum(ga_data["conversions"]["conversions"])
            else:
                total_conversions = ga_data["summary"].get("total_conversions", 0)
            st.metric("Total Conversions (30d)", f"{total_conversions}")
        
        with col3:
            try:
                total_cost = sum([self.safe_get_last(ads_data[c]["cumulative"], "total_cost", 0) for c in ads_data if "cumulative" in ads_data[c] and "total_cost" in ads_data[c]["cumulative"]])
                # Convert to regular Python float, handling multi-dimensional arrays
                if hasattr(total_cost, 'item') and total_cost.size == 1:
                    total_cost = total_cost.item()  # For NumPy scalars
                elif hasattr(total_cost, 'sum'):
                    total_cost = float(total_cost.sum())  # For multi-element arrays
                else:
                    total_cost = float(total_cost)  # For regular numbers
            except (KeyError, IndexError, ValueError, TypeError):
                total_cost = 0
            st.metric("Total Ad Spend (30d)", f"${total_cost:,.2f}")
        
        with col4:
            try:
                avg_cpl = total_cost / total_conversions if total_conversions > 0 else 0
                # Convert to regular Python float, handling multi-dimensional arrays
                if hasattr(avg_cpl, 'item') and avg_cpl.size == 1:
                    avg_cpl = avg_cpl.item()  # For NumPy scalars
                elif hasattr(avg_cpl, 'sum'):
                    avg_cpl = float(avg_cpl.sum())  # For multi-element arrays
                else:
                    avg_cpl = float(avg_cpl)  # For regular numbers
            except (ZeroDivisionError, TypeError, ValueError):
                avg_cpl = 0
            st.metric("Average CPL", f"${avg_cpl:.2f}")
    
    def render_campaign_comparison(self, ads_data: Dict):
        """Render campaign comparison charts."""
        st.subheader("🎯 Campaign Comparison")
        
        # Create comparison dataframe
        comparison_data = []
        for campaign_key, campaign_data in ads_data.items():
            config = campaign_data["config"]
            cumulative = campaign_data["cumulative"]
            
            # Safely get values with fallbacks
            
            total_impressions = self.safe_get_last(cumulative, "total_impressions", 0)
            total_clicks = self.safe_get_last(cumulative, "total_clicks", 0)
            total_conversions = self.safe_get_last(cumulative, "total_conversions", 0)
            total_cost = self.safe_get_last(cumulative, "total_cost", 0)
            avg_ctr = self.safe_get_last(cumulative, "avg_ctr", 0)
            avg_cpc = self.safe_get_last(cumulative, "avg_cpc", 0)
            avg_cpl = self.safe_get_last(cumulative, "avg_cpl", 0)
            
            comparison_data.append({
                "Campaign": config["name"],
                "Total Impressions": total_impressions,
                "Total Clicks": total_clicks,
                "Total Conversions": total_conversions,
                "Total Cost": total_cost,
                "CTR": avg_ctr * 100,
                "CPC": avg_cpc,
                "CPL": avg_cpl,
                "Daily Budget": config.get("budget_month1", 0)
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Ensure numeric columns are properly typed
        numeric_columns = ["Total Impressions", "Total Clicks", "Total Conversions", "Total Cost", "CTR", "CPC", "CPL", "Daily Budget"]
        for col in numeric_columns:
            if col in df_comparison.columns:
                df_comparison[col] = pd.to_numeric(df_comparison[col], errors='coerce').fillna(0)
        
        # Display comparison table
        st.dataframe(df_comparison, width='stretch')
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversions comparison
            if not df_comparison.empty and "Total Conversions" in df_comparison.columns:
                fig_conversions = px.bar(
                    df_comparison, 
                    x="Campaign", 
                    y="Total Conversions",
                    title="Total Conversions by Campaign",
                    color="Campaign"
                )
                st.plotly_chart(fig_conversions, width='stretch')
            else:
                st.warning("No conversion data available")
        
        with col2:
            # CPL comparison
            if not df_comparison.empty and "CPL" in df_comparison.columns:
                fig_cpl = px.bar(
                    df_comparison, 
                    x="Campaign", 
                    y="CPL",
                    title="Cost Per Lead by Campaign",
                    color="Campaign"
                )
                st.plotly_chart(fig_cpl, width='stretch')
            else:
                st.warning("No CPL data available")
    
    def render_goal_progress(self, ads_data: Dict):
        """Render goal progress tracking."""
        st.subheader("🎯 Goal Progress Tracking")
        
        for campaign_key, campaign_data in ads_data.items():
            config = campaign_data["config"]
            progress = self.calculate_goal_progress(campaign_data, config)
            
            st.markdown(f"""
            <div class="campaign-card">
                <h3>{config['name']}</h3>
                <div class="phase-indicator phase-{config['phase'].split('_')[1]}">{config['phase'].upper()}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                conv_progress = progress["conversions"]["progress"]
                st.metric(
                    "Conversions Progress",
                    f"{progress['conversions']['current']}/{progress['conversions']['goal']}",
                    f"{conv_progress:.1f}%"
                )
                st.progress(conv_progress / 100)
            
            with col2:
                cpl_progress = progress["cpl"]["progress"]
                st.metric(
                    "CPL Progress",
                    f"${progress['cpl']['current']:.2f}",
                    f"{cpl_progress:.1f}%"
                )
                st.progress(cpl_progress / 100)
            
            with col3:
                phase_progress = progress["phase"]["progress"]
                st.metric(
                    "Phase Progress",
                    f"{progress['phase']['current']}",
                    f"{phase_progress:.1f}%"
                )
                st.progress(phase_progress / 100)
    
    def render_trend_analysis(self, ads_data: Dict):
        """Render trend analysis charts."""
        st.subheader("📊 Trend Analysis")
        
        # Create time series data
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start_date, end_date, freq='D')
        
        trend_data = []
        for campaign_key, campaign_data in ads_data.items():
            config = campaign_data["config"]
            daily_data = campaign_data["daily"]
            
            for i, date_val in enumerate(dates):
                date_str = date_val.strftime("%Y-%m-%d")
                
                # Get data for this specific date, or use zeros if no data
                if date_str in daily_data:
                    day_data = daily_data[date_str]
                    trend_data.append({
                        "Date": date_val,
                        "Campaign": config["name"],
                        "Impressions": day_data.get("impressions", 0),
                        "Clicks": day_data.get("clicks", 0),
                        "Conversions": day_data.get("conversions", 0),
                        "Cost": day_data.get("cost", 0),
                        "CTR": day_data.get("ctr", 0) * 100,
                        "CPC": day_data.get("cpc", 0),
                        "CPL": day_data.get("cpl", 0)
                    })
                else:
                    # No data for this date, use zeros
                    trend_data.append({
                        "Date": date_val,
                        "Campaign": config["name"],
                        "Impressions": 0,
                        "Clicks": 0,
                        "Conversions": 0,
                        "Cost": 0,
                        "CTR": 0,
                        "CPC": 0,
                        "CPL": 0
                    })
        
        df_trends = pd.DataFrame(trend_data)
        
        # Create trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversions trend
            if not df_trends.empty:
                fig_conv_trend = px.line(
                    df_trends,
                    x="Date",
                    y="Conversions",
                    color="Campaign",
                    title="Daily Conversions Trend"
                )
                st.plotly_chart(fig_conv_trend, width='stretch')
            else:
                st.info("No trend data available")
        
        with col2:
            # Cost trend
            if not df_trends.empty:
                fig_cost_trend = px.line(
                    df_trends,
                    x="Date",
                    y="Cost",
                    color="Campaign",
                    title="Daily Cost Trend"
                )
                st.plotly_chart(fig_cost_trend, width='stretch')
            else:
                st.info("No cost trend data available")
    
    def render_google_analytics_section(self, ga_data: Dict):
        """Render Google Analytics section."""
        st.subheader("🌐 Google Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Traffic sources pie chart
            traffic_sources = ga_data["traffic_sources"]
            fig_traffic = px.pie(
                values=list(traffic_sources.values()),
                names=list(traffic_sources.keys()),
                title="Traffic Sources"
            )
            st.plotly_chart(fig_traffic, width='stretch')
        
        with col2:
            # Top pages
            top_pages = pd.DataFrame(ga_data["top_pages"])
            fig_pages = px.bar(
                top_pages,
                x="page",
                y="views",
                title="Top Pages by Views"
            )
            st.plotly_chart(fig_pages, width='stretch')
    
    def render_sierra_interactive_section(self, sierra_data: Dict):
        """Render Sierra Interactive CRM section."""
        st.subheader("📋 Sierra Interactive CRM")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Leads by status
            leads_by_status = sierra_data["leads"]["records_by_status"]
            fig_leads_status = px.pie(
                values=list(leads_by_status.values()),
                names=list(leads_by_status.keys()),
                title="Leads by Status"
            )
            st.plotly_chart(fig_leads_status, width='stretch')
            
            # Recent leads table
            st.subheader("Recent Leads")
            recent_leads = sierra_data["leads"]["recent_records"]
            if recent_leads:
                leads_df = pd.DataFrame(recent_leads)
                st.dataframe(leads_df, use_container_width=True)
            else:
                st.info("No recent leads data available")
        
        with col2:
            # Leads by source
            leads_by_source = sierra_data["leads"]["records_by_source"]
            fig_leads_source = px.bar(
                x=list(leads_by_source.keys()),
                y=list(leads_by_source.values()),
                title="Leads by Source"
            )
            st.plotly_chart(fig_leads_source, width='stretch')
            
            # Users summary
            st.subheader("Team Summary")
            users_summary = sierra_data["users"]["summary"]
            st.metric("Total Users", users_summary["total_users"])
            st.metric("Active Users", users_summary["active_users"])
            st.metric("Agents", users_summary["agents"])
            st.metric("Managers", users_summary["managers"])
        
        # Overall CRM metrics
        st.subheader("CRM Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", sierra_data["summary"]["total_records"])
        with col2:
            st.metric("Active Leads", sierra_data["summary"]["active_records"])
        with col3:
            st.metric("Conversion Rate", f"{sierra_data['summary']['conversion_rate']:.1f}%")
        with col4:
            st.metric("Team Size", sierra_data["summary"]["total_users"])
    
    def render_alerts_and_recommendations(self, ads_data: Dict):
        """Render alerts and recommendations."""
        st.subheader("🚨 Alerts & Recommendations")
        
        alerts = []
        recommendations = []
        
        for campaign_key, campaign_data in ads_data.items():
            config = campaign_data["config"]
            cumulative = campaign_data["cumulative"]
            
            # Check for alerts
            total_conversions = self.safe_get_last(cumulative, "total_conversions", 0)
            # Convert to regular Python number, handling multi-dimensional arrays
            if hasattr(total_conversions, 'item') and total_conversions.size == 1:
                total_conversions = total_conversions.item()  # For NumPy scalars
            elif hasattr(total_conversions, 'sum'):
                total_conversions = float(total_conversions.sum())  # For multi-element arrays
            else:
                total_conversions = float(total_conversions)  # For regular numbers
            
            avg_cpl = self.safe_get_last(cumulative, "avg_cpl", 0)
            # Convert to regular Python float, handling multi-dimensional arrays
            if hasattr(avg_cpl, 'item') and avg_cpl.size == 1:
                avg_cpl = avg_cpl.item()  # For NumPy scalars
            elif hasattr(avg_cpl, 'sum'):
                avg_cpl = float(avg_cpl.sum())  # For multi-element arrays
            else:
                avg_cpl = float(avg_cpl)  # For regular numbers
            avg_ctr = self.safe_get_last(cumulative, "avg_ctr", 0)
            
            if total_conversions == 0:
                alerts.append(f"⚠️ {config['name']}: No conversions in 30 days")
            
            if avg_cpl > config["goal_cpl"] * 1.5:
                alerts.append(f"⚠️ {config['name']}: CPL ${avg_cpl:.2f} exceeds goal by 50%")
            
            # Generate recommendations
            if total_conversions < 5:
                recommendations.append(f"📈 {config['name']}: Consider increasing budget to accelerate learning")
            
            if avg_ctr < 0.03:
                recommendations.append(f"🎯 {config['name']}: Low CTR - review ad creative and targeting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if alerts:
                st.error("Alerts")
                for alert in alerts:
                    st.write(alert)
            else:
                st.success("✅ No alerts")
        
        with col2:
            if recommendations:
                st.info("Recommendations")
                for rec in recommendations:
                    st.write(rec)
            else:
                st.success("✅ No recommendations")
    
    def run_dashboard(self):
        """Run the complete dashboard."""
        logger.info("🚀 Starting dashboard rendering")
        try:
            # Load data
            logger.info("📊 Loading data sources...")
            ga_data = self.load_google_analytics_data()
            ads_data = self.load_google_ads_data()
            sierra_data = self.load_sierra_data()
            logger.info("✅ Data loaded successfully")
            
            # Render dashboard sections
            logger.info("🎨 Rendering dashboard sections...")
            self.render_header()
            
            # Check if Google Ads data has errors
            if isinstance(ads_data, dict) and "error" in ads_data:
                st.error(f"🚨 **Google Ads Integration Error**: {ads_data['error']}")
                st.warning("⚠️ **Dashboard is running with limited functionality** - Google Ads data is not available")
                st.info("💡 **To fix this**: Check your Google Ads API credentials and ensure they are properly configured")
                return
            
            self.render_overview_metrics(ga_data, ads_data)
            self.render_campaign_comparison(ads_data)
            self.render_goal_progress(ads_data)
            self.render_trend_analysis(ads_data)
            self.render_google_analytics_section(ga_data)
            self.render_sierra_interactive_section(sierra_data)
            self.render_alerts_and_recommendations(ads_data)
            logger.info("✅ Dashboard rendering completed successfully")
        except Exception as e:
            logger.error(f"❌ Error in dashboard rendering: {e}", exc_info=True)
            st.error(f"Error loading dashboard: {e}")
        
        # Update refresh time
        st.session_state.last_refresh = datetime.now()
    
    def run_diagnostics(self):
        """Run the diagnostics page."""
        logger.info("🔍 Starting diagnostics page")
        try:
            st.markdown('<h1 class="main-header">🔍 Data Source Diagnostics</h1>', unsafe_allow_html=True)
            st.markdown("This page shows all data sources, their fields, and sample data for QA purposes.")
            
            # Load all data sources
            logger.info("📊 Loading all data sources for diagnostics...")
            ga_data = self.load_google_analytics_data()
            ads_data = self.load_google_ads_data()
            sierra_data = self.load_sierra_data()
            
            # Google Ads Diagnostics
            self.render_google_ads_diagnostics(ads_data)
            
            # Google Analytics Diagnostics
            self.render_google_analytics_diagnostics(ga_data)
            
            # Sierra Interactive Diagnostics
            self.render_sierra_diagnostics(sierra_data)
            
            logger.info("✅ Diagnostics page completed successfully")
        except Exception as e:
            logger.error(f"❌ Error in diagnostics page: {e}", exc_info=True)
            st.error(f"Error loading diagnostics: {e}")
    
    def render_google_ads_diagnostics(self, ads_data: Dict):
        """Render Google Ads diagnostics."""
        st.subheader("🎯 Google Ads Data Source")
        
        if isinstance(ads_data, dict) and "error" in ads_data:
            st.error(f"❌ **Error**: {ads_data['error']}")
            return
        
        st.success("✅ **Status**: Connected and working")
        
        # Show data structure
        st.markdown("#### 📊 Data Structure")
        st.json(ads_data)
        
        # Show field examples
        st.markdown("#### 🔍 Field Examples")
        for campaign_key, campaign_data in ads_data.items():
            st.markdown(f"**Campaign: {campaign_key}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Config Fields:**")
                config = campaign_data.get("config", {})
                for field, value in config.items():
                    st.write(f"- `{field}`: `{value}`")
            
            with col2:
                st.markdown("**Cumulative Fields:**")
                cumulative = campaign_data.get("cumulative", {})
                for field, value in cumulative.items():
                    if isinstance(value, (list, np.ndarray)):
                        st.write(f"- `{field}`: `{type(value).__name__}` (length: {len(value)})")
                        if len(value) > 0:
                            st.write(f"  - First value: `{value[0]}`")
                            st.write(f"  - Last value: `{value[-1]}`")
                    else:
                        st.write(f"- `{field}`: `{value}`")
            
            st.markdown("---")
    
    def render_google_analytics_diagnostics(self, ga_data: Dict):
        """Render Google Analytics diagnostics."""
        st.subheader("🌐 Google Analytics Data Source")
        
        if isinstance(ga_data, dict) and "error" in ga_data:
            st.warning(f"⚠️ **Using Mock Data**: {ga_data.get('error', 'No real data available')}")
        else:
            st.success("✅ **Status**: Connected and working")
        
        # Show data structure
        st.markdown("#### 📊 Data Structure")
        st.json(ga_data)
        
        # Show field examples
        st.markdown("#### 🔍 Field Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Website Traffic Fields:**")
            traffic = ga_data.get("website_traffic", {})
            for field, value in traffic.items():
                if isinstance(value, (list, np.ndarray)):
                    st.write(f"- `{field}`: `{type(value).__name__}` (length: {len(value)})")
                    if len(value) > 0:
                        st.write(f"  - First value: `{value[0]}`")
                        st.write(f"  - Last value: `{value[-1]}`")
                else:
                    st.write(f"- `{field}`: `{value}`")
            
            st.markdown("**Traffic Sources:**")
            sources = ga_data.get("traffic_sources", {})
            for source, data in sources.items():
                st.write(f"- `{source}`: {data}")
        
        with col2:
            st.markdown("**Conversions Fields:**")
            conversions = ga_data.get("conversions", {})
            for field, value in conversions.items():
                if isinstance(value, (list, np.ndarray)):
                    st.write(f"- `{field}`: `{type(value).__name__}` (length: {len(value)})")
                    if len(value) > 0:
                        st.write(f"  - First value: `{value[0]}`")
                        st.write(f"  - Last value: `{value[-1]}`")
                else:
                    st.write(f"- `{field}`: `{value}`")
            
            st.markdown("**Summary Fields:**")
            summary = ga_data.get("summary", {})
            for field, value in summary.items():
                st.write(f"- `{field}`: `{value}`")
    
    def render_sierra_diagnostics(self, sierra_data: Dict):
        """Render Sierra Interactive diagnostics."""
        st.subheader("📋 Sierra Interactive Data Source")
        
        if isinstance(sierra_data, dict) and "error" in sierra_data:
            st.warning(f"⚠️ **Using Mock Data**: {sierra_data.get('error', 'No real data available')}")
        else:
            st.success("✅ **Status**: Connected and working")
        
        # Show data structure
        st.markdown("#### 📊 Data Structure")
        st.json(sierra_data)
        
        # Show field examples
        st.markdown("#### 🔍 Field Examples")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Leads Data:**")
            leads = sierra_data.get("leads", {})
            for field, value in leads.items():
                if isinstance(value, dict):
                    st.write(f"- `{field}`: `dict` with {len(value)} items")
                    for subfield, subvalue in value.items():
                        if isinstance(subvalue, (list, np.ndarray)):
                            st.write(f"  - `{subfield}`: `{type(subvalue).__name__}` (length: {len(subvalue)})")
                            if len(subvalue) > 0 and len(subvalue) <= 3:
                                st.write(f"    - Values: `{subvalue}`")
                        else:
                            st.write(f"  - `{subfield}`: `{subvalue}`")
                else:
                    st.write(f"- `{field}`: `{value}`")
        
        with col2:
            st.markdown("**Users Data:**")
            users = sierra_data.get("users", {})
            for field, value in users.items():
                if isinstance(value, dict):
                    st.write(f"- `{field}`: `dict` with {len(value)} items")
                    for subfield, subvalue in value.items():
                        if isinstance(subvalue, (list, np.ndarray)):
                            st.write(f"  - `{subfield}`: `{type(subvalue).__name__}` (length: {len(subvalue)})")
                            if len(subvalue) > 0 and len(subvalue) <= 3:
                                st.write(f"    - Values: `{subvalue}`")
                        else:
                            st.write(f"  - `{subfield}`: `{subvalue}`")
                else:
                    st.write(f"- `{field}`: `{value}`")
            
            st.markdown("**Summary Data:**")
            summary = sierra_data.get("summary", {})
            for field, value in summary.items():
                st.write(f"- `{field}`: `{value}`")

def main():
    """Main function to run the dashboard."""
    logger.info("🎯 Starting Marketing Dashboard application")
    try:
        dashboard = MarketingDashboard()
        
        # Route to appropriate page
        if page == "Main Dashboard":
            dashboard.run_dashboard()
        elif page == "Strategic Plan":
            if HAS_STRATEGIC_PLAN:
                render_strategic_plan_view()
            else:
                st.error("Strategic Plan view is not available. Please check the import.")
        elif page == "Marketing Plan & Timeline":
            if HAS_MARKETING_PLAN:
                render_marketing_plan_view()
            else:
                st.error("Marketing Plan & Timeline view is not available. Please check the import.")
        elif page == "AI Command Center":
            if HAS_COMMAND_CENTER:
                # Get data from the dashboard's data sources
                ads_data = dashboard.get_ads_data()
                analytics_data = dashboard.get_analytics_data()
                crm_data = dashboard.get_sierra_data()
                
                # Render the command center view
                render_command_center_view(ads_data, analytics_data, crm_data)
            else:
                st.error("Command Center view is not available. Please check the import.")
        elif page == "Diagnostics":
            dashboard.run_diagnostics()
        
        logger.info("✅ Dashboard application completed successfully")
    except Exception as e:
        logger.error(f"❌ Fatal error in main application: {e}", exc_info=True)
        st.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
