#!/usr/bin/env python3
"""
Simplified Marketing Dashboard
==============================

A reliable Streamlit dashboard that displays:
- Google Analytics metrics (mock data)
- Google Ads campaign performance (mock data)
- Goal progression tracking
- A/B test comparison
- Real-time monitoring

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta, date
import os
import sys
from typing import Dict, List, Optional, Any

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

class SimpleMarketingDashboard:
    """Simplified marketing dashboard for A/B test monitoring."""
    
    def __init__(self):
        """Initialize the dashboard."""
        # Campaign configurations
        self.campaigns = {
            "local_presence": {
                "name": "Local Presence",
                "budget_month1": 31.50,
                "budget_months2_5": 34.50,
                "goal_conversions": 30,
                "goal_cpl": 150,
                "phase": "phase_1"
            },
            "feeder_markets": {
                "name": "Feeder Markets", 
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
    
    def generate_mock_data(self) -> Dict:
        """Generate realistic mock data for the dashboard."""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # Generate campaign data
        campaign_data = {}
        
        for campaign_key, config in self.campaigns.items():
            # Generate daily data
            daily_impressions = np.random.randint(1000, 5000, len(dates))
            daily_clicks = np.random.randint(50, 200, len(dates))
            daily_conversions = np.random.randint(0, 3, len(dates))
            daily_cost = np.random.uniform(config["budget_month1"] * 0.8, config["budget_month1"] * 1.2, len(dates))
            
            # Calculate totals
            total_impressions = np.sum(daily_impressions)
            total_clicks = np.sum(daily_clicks)
            total_conversions = np.sum(daily_conversions)
            total_cost = np.sum(daily_cost)
            
            # Calculate averages
            avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            avg_cpc = total_cost / total_clicks if total_clicks > 0 else 0
            avg_cpl = total_cost / total_conversions if total_conversions > 0 else 0
            
            campaign_data[campaign_key] = {
                "config": config,
                "daily": {
                    "impressions": daily_impressions,
                    "clicks": daily_clicks,
                    "conversions": daily_conversions,
                    "cost": daily_cost,
                    "dates": dates
                },
                "totals": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "conversions": total_conversions,
                    "cost": total_cost,
                    "ctr": avg_ctr,
                    "cpc": avg_cpc,
                    "cpl": avg_cpl
                }
            }
        
        # Generate Google Analytics data
        ga_data = {
            "sessions": np.random.randint(100, 500, len(dates)),
            "users": np.random.randint(80, 400, len(dates)),
            "pageviews": np.random.randint(200, 1000, len(dates)),
            "conversions": np.random.randint(0, 5, len(dates)),
            "traffic_sources": {
                "organic": 45,
                "paid": 35,
                "direct": 15,
                "social": 5
            }
        }
        
        return {
            "campaigns": campaign_data,
            "ga": ga_data,
            "dates": dates
        }
    
    def render_header(self):
        """Render the dashboard header."""
        st.markdown('<h1 class="main-header">📊 Marketing Dashboard - A/B Test</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Last Updated", st.session_state.last_refresh.strftime("%H:%M:%S"))
        
        with col2:
            st.metric("Test Duration", "Day 1 of 150")
        
        with col3:
            st.metric("Overall Status", "🟢 Active")
    
    def render_overview_metrics(self, data: Dict):
        """Render overview metrics."""
        st.subheader("📈 Overview Metrics")
        
        campaigns = data["campaigns"]
        ga = data["ga"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sessions = np.sum(ga["sessions"])
            st.metric("Website Sessions (30d)", f"{total_sessions:,}")
        
        with col2:
            total_conversions = sum([campaigns[c]["totals"]["conversions"] for c in campaigns])
            st.metric("Total Conversions (30d)", f"{total_conversions}")
        
        with col3:
            total_cost = sum([campaigns[c]["totals"]["cost"] for c in campaigns])
            st.metric("Total Ad Spend (30d)", f"${total_cost:,.2f}")
        
        with col4:
            avg_cpl = total_cost / total_conversions if total_conversions > 0 else 0
            st.metric("Average CPL", f"${avg_cpl:.2f}")
    
    def render_campaign_comparison(self, data: Dict):
        """Render campaign comparison charts."""
        st.subheader("🎯 Campaign Comparison")
        
        campaigns = data["campaigns"]
        
        # Create comparison dataframe
        comparison_data = []
        for campaign_key, campaign_data in campaigns.items():
            config = campaign_data["config"]
            totals = campaign_data["totals"]
            
            comparison_data.append({
                "Campaign": config["name"],
                "Total Impressions": totals["impressions"],
                "Total Clicks": totals["clicks"],
                "Total Conversions": totals["conversions"],
                "Total Cost": totals["cost"],
                "CTR": totals["ctr"] * 100,
                "CPC": totals["cpc"],
                "CPL": totals["cpl"],
                "Daily Budget": config["budget_month1"]
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Display comparison table
        st.dataframe(df_comparison, width='stretch')
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_comparison.empty:
                fig_conversions = px.bar(
                    df_comparison, 
                    x="Campaign", 
                    y="Total Conversions",
                    title="Total Conversions by Campaign",
                    color="Campaign"
                )
                st.plotly_chart(fig_conversions, width='stretch')
        
        with col2:
            if not df_comparison.empty:
                fig_cpl = px.bar(
                    df_comparison, 
                    x="Campaign", 
                    y="CPL",
                    title="Cost Per Lead by Campaign",
                    color="Campaign"
                )
                st.plotly_chart(fig_cpl, width='stretch')
    
    def render_goal_progress(self, data: Dict):
        """Render goal progress tracking."""
        st.subheader("🎯 Goal Progress Tracking")
        
        campaigns = data["campaigns"]
        
        for campaign_key, campaign_data in campaigns.items():
            config = campaign_data["config"]
            totals = campaign_data["totals"]
            
            st.markdown(f"""
            <div class="campaign-card">
                <h3>{config['name']}</h3>
                <div class="phase-indicator phase-{config['phase'].split('_')[1]}">{config['phase'].upper()}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                conv_progress = min(100, (totals["conversions"] / config["goal_conversions"]) * 100)
                st.metric(
                    "Conversions Progress",
                    f"{totals['conversions']}/{config['goal_conversions']}",
                    f"{conv_progress:.1f}%"
                )
                st.progress(conv_progress / 100)
            
            with col2:
                cpl_progress = max(0, min(100, (config["goal_cpl"] - totals["cpl"]) / config["goal_cpl"] * 100))
                st.metric(
                    "CPL Progress",
                    f"${totals['cpl']:.2f}",
                    f"{cpl_progress:.1f}%"
                )
                st.progress(cpl_progress / 100)
            
            with col3:
                phase_progress = min(100, (totals["conversions"] / 30) * 100)
                st.metric(
                    "Phase Progress",
                    f"{config['phase']}",
                    f"{phase_progress:.1f}%"
                )
                st.progress(phase_progress / 100)
    
    def render_trend_analysis(self, data: Dict):
        """Render trend analysis charts."""
        st.subheader("📊 Trend Analysis")
        
        campaigns = data["campaigns"]
        dates = data["dates"]
        
        # Create trend data
        trend_data = []
        for campaign_key, campaign_data in campaigns.items():
            config = campaign_data["config"]
            daily = campaign_data["daily"]
            
            for i, date_val in enumerate(dates):
                trend_data.append({
                    "Date": date_val,
                    "Campaign": config["name"],
                    "Conversions": daily["conversions"][i],
                    "Cost": daily["cost"][i]
                })
        
        df_trends = pd.DataFrame(trend_data)
        
        # Create trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_trends.empty:
                fig_conv_trend = px.line(
                    df_trends,
                    x="Date",
                    y="Conversions",
                    color="Campaign",
                    title="Daily Conversions Trend"
                )
                st.plotly_chart(fig_conv_trend, width='stretch')
        
        with col2:
            if not df_trends.empty:
                fig_cost_trend = px.line(
                    df_trends,
                    x="Date",
                    y="Cost",
                    color="Campaign",
                    title="Daily Cost Trend"
                )
                st.plotly_chart(fig_cost_trend, width='stretch')
    
    def render_google_analytics_section(self, data: Dict):
        """Render Google Analytics section."""
        st.subheader("🌐 Google Analytics")
        
        ga = data["ga"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Traffic sources pie chart
            traffic_sources = ga["traffic_sources"]
            fig_traffic = px.pie(
                values=list(traffic_sources.values()),
                names=list(traffic_sources.keys()),
                title="Traffic Sources"
            )
            st.plotly_chart(fig_traffic, width='stretch')
        
        with col2:
            # Sessions trend
            dates = data["dates"]
            sessions_df = pd.DataFrame({
                "Date": dates,
                "Sessions": ga["sessions"]
            })
            
            fig_sessions = px.line(
                sessions_df,
                x="Date",
                y="Sessions",
                title="Daily Sessions Trend"
            )
            st.plotly_chart(fig_sessions, width='stretch')
    
    def render_alerts_and_recommendations(self, data: Dict):
        """Render alerts and recommendations."""
        st.subheader("🚨 Alerts & Recommendations")
        
        campaigns = data["campaigns"]
        alerts = []
        recommendations = []
        
        for campaign_key, campaign_data in campaigns.items():
            config = campaign_data["config"]
            totals = campaign_data["totals"]
            
            # Check for alerts
            if totals["conversions"] == 0:
                alerts.append(f"⚠️ {config['name']}: No conversions in 30 days")
            
            if totals["cpl"] > config["goal_cpl"] * 1.5:
                alerts.append(f"⚠️ {config['name']}: CPL ${totals['cpl']:.2f} exceeds goal by 50%")
            
            # Generate recommendations
            if totals["conversions"] < 5:
                recommendations.append(f"📈 {config['name']}: Consider increasing budget to accelerate learning")
            
            if totals["ctr"] < 0.03:
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
        # Generate mock data
        data = self.generate_mock_data()
        
        # Render dashboard sections
        self.render_header()
        self.render_overview_metrics(data)
        self.render_campaign_comparison(data)
        self.render_goal_progress(data)
        self.render_trend_analysis(data)
        self.render_google_analytics_section(data)
        self.render_alerts_and_recommendations(data)
        
        # Update refresh time
        st.session_state.last_refresh = datetime.now()

def main():
    """Main function to run the dashboard."""
    dashboard = SimpleMarketingDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
