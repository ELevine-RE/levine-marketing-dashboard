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

# Page configuration
st.set_page_config(
    page_title="Marketing Dashboard - A/B Test",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    def load_google_analytics_data(self) -> Dict:
        """Load Google Analytics data (placeholder for actual API integration)."""
        logger.info("📊 Loading Google Analytics data")
        # This would integrate with Google Analytics API
        # For now, return sample data
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Generate sample GA data
        dates = pd.date_range(start_date, end_date, freq='D')
        
        ga_data = {
            "website_traffic": {
                "sessions": np.random.randint(100, 500, len(dates)),
                "users": np.random.randint(80, 400, len(dates)),
                "pageviews": np.random.randint(200, 1000, len(dates)),
                "bounce_rate": np.random.uniform(0.3, 0.7, len(dates)),
                "avg_session_duration": np.random.uniform(60, 300, len(dates))
            },
            "conversions": {
                "lead_form_submissions": np.random.randint(0, 5, len(dates)),
                "phone_calls": np.random.randint(0, 3, len(dates)),
                "email_signups": np.random.randint(0, 8, len(dates))
            },
            "traffic_sources": {
                "organic": 45,
                "paid": 35,
                "direct": 15,
                "social": 5
            },
            "top_pages": [
                {"page": "/", "views": 1200, "conversions": 15},
                {"page": "/properties", "views": 800, "conversions": 12},
                {"page": "/contact", "views": 400, "conversions": 8},
                {"page": "/about", "views": 300, "conversions": 2}
            ]
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
            start_date = end_date - timedelta(days=30)
            dates = pd.date_range(start_date, end_date, freq='D')
            
            ads_data = {}
            
            for campaign_key, campaign_config in self.campaigns.items():
                # Generate realistic campaign data
                daily_budget = campaign_config["budget_month1"]  # Use month 1 budget for now
                
                campaign_data = {
                    "impressions": np.random.randint(1000, 5000, len(dates)),
                    "clicks": np.random.randint(50, 200, len(dates)),
                    "conversions": np.random.randint(0, 3, len(dates)),
                    "cost": np.random.uniform(daily_budget * 0.8, daily_budget * 1.2, len(dates)),
                    "ctr": np.random.uniform(0.02, 0.08, len(dates)),
                    "cpc": np.random.uniform(2, 8, len(dates)),
                    "cpl": np.random.uniform(50, 300, len(dates))
                }
                
                # Calculate cumulative metrics
                total_impressions = np.cumsum(campaign_data["impressions"])
                total_clicks = np.cumsum(campaign_data["clicks"])
                total_conversions = np.cumsum(campaign_data["conversions"])
                total_cost = np.cumsum(campaign_data["cost"])
                
                # Calculate averages (scalar values)
                def safe_last(data, default=0):
                    if isinstance(data, (list, np.ndarray)):
                        return data[-1] if len(data) > 0 else default
                    return data if data is not None else default
                
                # Convert numpy arrays to scalars for safe comparison
                last_clicks = float(safe_last(total_clicks))
                last_impressions = float(safe_last(total_impressions))
                last_cost = float(safe_last(total_cost))
                last_conversions = float(safe_last(total_conversions))
                
                avg_ctr = last_clicks / last_impressions if last_impressions > 0 else 0
                avg_cpc = last_cost / last_clicks if last_clicks > 0 else 0
                avg_cpl = last_cost / last_conversions if last_conversions > 0 else 0
                
                cumulative_data = {
                    "total_impressions": total_impressions,
                    "total_clicks": total_clicks,
                    "total_conversions": total_conversions,
                    "total_cost": total_cost,
                    "avg_ctr": avg_ctr,
                    "avg_cpc": avg_cpc,
                    "avg_cpl": avg_cpl
                }
                
                ads_data[campaign_key] = {
                    "daily": campaign_data,
                    "cumulative": cumulative_data,
                    "config": campaign_config
                }
            
            return ads_data
            
        except Exception as e:
            st.error(f"Error loading Google Ads data: {e}")
            return {}
    
    def calculate_goal_progress(self, campaign_data: Dict, campaign_config: Dict) -> Dict:
        """Calculate progress towards campaign goals."""
        try:
            # Safely get cumulative data with fallbacks
            cumulative = campaign_data.get("cumulative", {})
            total_conversions = self.safe_get_last(cumulative, "total_conversions", 0)
            total_cost = self.safe_get_last(cumulative, "total_cost", 0)
            
            # Convert to regular Python numbers, handling multi-dimensional arrays
            if hasattr(total_conversions, 'item') and total_conversions.size == 1:
                total_conversions = total_conversions.item()  # For NumPy scalars
            elif hasattr(total_conversions, 'sum'):
                total_conversions = float(total_conversions.sum())  # For multi-element arrays
            else:
                total_conversions = float(total_conversions)  # For regular numbers
                
            if hasattr(total_cost, 'item') and total_cost.size == 1:
                total_cost = total_cost.item()  # For NumPy scalars
            elif hasattr(total_cost, 'sum'):
                total_cost = float(total_cost.sum())  # For multi-element arrays
            else:
                total_cost = float(total_cost)  # For regular numbers
            
            # Calculate average CPL safely
            avg_cpl = total_cost / total_conversions if total_conversions > 0 else 0
            # Convert to regular Python float, handling multi-dimensional arrays
            if hasattr(avg_cpl, 'item') and avg_cpl.size == 1:
                avg_cpl = avg_cpl.item()  # For NumPy scalars
            elif hasattr(avg_cpl, 'sum'):
                avg_cpl = float(avg_cpl.sum())  # For multi-element arrays
            else:
                avg_cpl = float(avg_cpl)  # For regular numbers
            
            goal_conversions = campaign_config.get("goal_conversions", 30)
            goal_cpl = campaign_config.get("goal_cpl", 150)
            
            conversion_progress = min(100, (total_conversions / goal_conversions) * 100)
            cpl_progress = max(0, min(100, (goal_cpl - avg_cpl) / goal_cpl * 100))
            
            # Phase progression logic
            current_phase = campaign_config.get("phase", "phase_1")
            phase_progress = 0
            
            if current_phase == "phase_1":
                if total_conversions >= 30:
                    phase_progress = 100
                else:
                    phase_progress = (total_conversions / 30) * 100
            
            return {
                "conversions": {
                    "current": total_conversions,
                    "goal": goal_conversions,
                    "progress": conversion_progress
                },
                "cpl": {
                    "current": avg_cpl,
                    "goal": goal_cpl,
                    "progress": cpl_progress
                },
                "phase": {
                    "current": current_phase,
                    "progress": phase_progress
                }
            }
            
        except Exception as e:
            st.error(f"Error calculating goal progress: {e}")
            # Return default values
            return {
                "conversions": {"current": 0, "goal": 30, "progress": 0},
                "cpl": {"current": 0, "goal": 150, "progress": 0},
                "phase": {"current": "phase_1", "progress": 0}
            }
    
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
            total_conversions = sum(ga_data["conversions"]["lead_form_submissions"]) + sum(ga_data["conversions"]["phone_calls"])
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
                "Daily Budget": config["budget_month1"]
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
                trend_data.append({
                    "Date": date_val,
                    "Campaign": config["name"],
                    "Impressions": daily_data["impressions"][i],
                    "Clicks": daily_data["clicks"][i],
                    "Conversions": daily_data["conversions"][i],
                    "Cost": daily_data["cost"][i],
                    "CTR": daily_data["ctr"][i] * 100,
                    "CPC": daily_data["cpc"][i],
                    "CPL": daily_data["cpl"][i]
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
            logger.info("✅ Data loaded successfully")
            
            # Render dashboard sections
            logger.info("🎨 Rendering dashboard sections...")
            self.render_header()
            self.render_overview_metrics(ga_data, ads_data)
            self.render_campaign_comparison(ads_data)
            self.render_goal_progress(ads_data)
            self.render_trend_analysis(ads_data)
            self.render_google_analytics_section(ga_data)
            self.render_alerts_and_recommendations(ads_data)
            logger.info("✅ Dashboard rendering completed successfully")
        except Exception as e:
            logger.error(f"❌ Error in dashboard rendering: {e}", exc_info=True)
            st.error(f"Error loading dashboard: {e}")
        
        # Update refresh time
        st.session_state.last_refresh = datetime.now()

def main():
    """Main function to run the dashboard."""
    logger.info("🎯 Starting Marketing Dashboard application")
    try:
        dashboard = MarketingDashboard()
        dashboard.run_dashboard()
        logger.info("✅ Dashboard application completed successfully")
    except Exception as e:
        logger.error(f"❌ Fatal error in main application: {e}", exc_info=True)
        st.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
