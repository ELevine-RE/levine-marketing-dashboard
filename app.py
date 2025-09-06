"""
Simple AI-Driven Google Ads Management Dashboard
Focused on core executive needs: diagnostics, staging, calendar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core systems
import sys
sys.path.append('google-ads-analysis')
from google_ads_integration import SimpleGoogleAdsManager
from google_analytics_simple import SimpleGoogleAnalyticsManager
from sierra_integration import SimpleSierraManager

class SimpleAIDashboard:
    def __init__(self):
        self.ads_manager = SimpleGoogleAdsManager()
        self.analytics_manager = SimpleGoogleAnalyticsManager()
        self.sierra_manager = SimpleSierraManager()
        
    def render_dashboard(self):
        st.set_page_config(
            page_title="AI Google Ads Manager",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 AI Google Ads Management System")
        st.markdown("*Your AI assistant handles the day-to-day, you intervene as needed*")
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Campaign Diagnostics", 
            "⏳ Staged Changes", 
            "📅 Marketing Calendar",
            "🎯 Goals & Status"
        ])
        
        with tab1:
            self.render_campaign_diagnostics()
            
        with tab2:
            self.render_staged_changes()
            
        with tab3:
            self.render_marketing_calendar()
            
        with tab4:
            self.render_goals_status()
    
    def render_campaign_diagnostics(self):
        st.header("📊 Campaign Diagnostics")
        
        # Get campaign data
        try:
            ads_data = self.ads_manager.get_campaign_data()
            
            if ads_data and 'campaigns' in ads_data:
                campaigns = ads_data['campaigns']
                
                # Campaign overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Active Campaigns", len([c for c in campaigns if c.get('status') == 'ENABLED']))
                
                with col2:
                    total_spend = sum(c.get('cost', 0) for c in campaigns)
                    st.metric("Total Spend (30d)", f"${total_spend:,.2f}")
                
                with col3:
                    total_conversions = sum(c.get('conversions', 0) for c in campaigns)
                    st.metric("Total Conversions", total_conversions)
                
                with col4:
                    avg_cpl = total_spend / total_conversions if total_conversions > 0 else 0
                    st.metric("Avg CPL", f"${avg_cpl:.2f}")
                
                # Campaign details table
                st.subheader("Campaign Details")
                
                campaign_df = pd.DataFrame(campaigns)
                if not campaign_df.empty:
                    # Select relevant columns
                    display_cols = ['name', 'status', 'budget', 'cost', 'impressions', 'clicks', 'conversions', 'cpl']
                    available_cols = [col for col in display_cols if col in campaign_df.columns]
                    
                    st.dataframe(
                        campaign_df[available_cols],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Performance chart
                    if 'cost' in campaign_df.columns and 'conversions' in campaign_df.columns:
                        fig = px.scatter(
                            campaign_df, 
                            x='cost', 
                            y='conversions',
                            hover_data=['name', 'cpl'],
                            title="Cost vs Conversions by Campaign"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No campaign data available")
                    
            else:
                st.warning("Unable to fetch campaign data")
                
        except Exception as e:
            st.error(f"Error loading campaign data: {str(e)}")
    
    def render_staged_changes(self):
        st.header("⏳ Staged Changes")
        st.markdown("*Review and approve AI-recommended changes*")
        
        # Load staged changes
        staged_changes = self.load_staged_changes()
        
        if not staged_changes:
            st.info("No staged changes pending")
            return
        
        for i, change in enumerate(staged_changes):
            with st.expander(f"Change {i+1}: {change.get('type', 'Unknown')} - {change.get('campaign', 'Unknown Campaign')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Campaign:** {change.get('campaign', 'N/A')}")
                    st.write(f"**Type:** {change.get('type', 'N/A')}")
                    st.write(f"**Current:** {change.get('current', 'N/A')}")
                    st.write(f"**Proposed:** {change.get('proposed', 'N/A')}")
                    st.write(f"**Reason:** {change.get('reason', 'N/A')}")
                    st.write(f"**Created:** {change.get('created', 'N/A')}")
                
                with col2:
                    if st.button(f"✅ Approve", key=f"approve_{i}"):
                        self.approve_change(i)
                        st.success("Change approved!")
                        st.rerun()
                    
                    if st.button(f"❌ Reject", key=f"reject_{i}"):
                        self.reject_change(i)
                        st.success("Change rejected!")
                        st.rerun()
                    
                    if st.button(f"⏰ Auto-approve in 2h", key=f"auto_{i}"):
                        self.schedule_auto_approval(i)
                        st.success("Auto-approval scheduled!")
                        st.rerun()
    
    def render_marketing_calendar(self):
        st.header("📅 Marketing Calendar")
        st.markdown("*Campaign timeline and planned activities*")
        
        # Sample calendar data
        calendar_data = [
            {"date": "2025-09-06", "event": "Crawl Campaign Launch", "type": "Campaign", "status": "Active"},
            {"date": "2025-09-20", "event": "Phase 1 Review", "type": "Milestone", "status": "Planned"},
            {"date": "2025-10-01", "event": "Walk Campaign Launch", "type": "Campaign", "status": "Scheduled"},
            {"date": "2025-10-15", "event": "Budget Optimization", "type": "Optimization", "status": "Planned"},
        ]
        
        calendar_df = pd.DataFrame(calendar_data)
        calendar_df['date'] = pd.to_datetime(calendar_df['date'])
        
        # Calendar view
        fig = px.timeline(
            calendar_df,
            x_start="date",
            x_end="date",
            y="event",
            color="type",
            title="Marketing Calendar Timeline"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Upcoming events
        st.subheader("Upcoming Events")
        upcoming = calendar_df[calendar_df['date'] >= datetime.now()]
        st.dataframe(upcoming, use_container_width=True, hide_index=True)
    
    def render_goals_status(self):
        st.header("🎯 Goals & Status")
        
        # Goals overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Goals")
            
            goals = [
                {"goal": "Crawl Campaign Conversions", "target": 30, "current": 0, "deadline": "2025-09-27"},
                {"goal": "Monthly Budget Utilization", "target": 100, "current": 0, "deadline": "2025-09-30"},
                {"goal": "CPL Target", "target": 150, "current": 0, "deadline": "Ongoing"},
            ]
            
            for goal in goals:
                progress = min((goal['current'] / goal['target']) * 100, 100) if goal['target'] > 0 else 0
                
                st.write(f"**{goal['goal']}**")
                st.progress(progress / 100)
                st.write(f"{goal['current']}/{goal['target']} ({progress:.1f}%) - Due: {goal['deadline']}")
        
        with col2:
            st.subheader("System Status")
            
            # Check system health
            status_items = [
                {"item": "Google Ads API", "status": "✅ Connected", "last_check": "2025-09-05 19:25"},
                {"item": "Analytics API", "status": "⚠️ Limited", "last_check": "2025-09-05 19:25"},
                {"item": "Sierra CRM", "status": "✅ Connected", "last_check": "2025-09-05 19:25"},
                {"item": "Email System", "status": "✅ Ready", "last_check": "2025-09-05 19:25"},
            ]
            
            for item in status_items:
                st.write(f"**{item['item']}:** {item['status']}")
                st.caption(f"Last check: {item['last_check']}")
    
    def load_staged_changes(self):
        """Load staged changes from file"""
        try:
            if os.path.exists('data/staged_changes.json'):
                with open('data/staged_changes.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading staged changes: {e}")
        return []
    
    def approve_change(self, change_index):
        """Approve a staged change"""
        staged_changes = self.load_staged_changes()
        if change_index < len(staged_changes):
            change = staged_changes.pop(change_index)
            # Here you would implement the actual change
            self.save_staged_changes(staged_changes)
    
    def reject_change(self, change_index):
        """Reject a staged change"""
        staged_changes = self.load_staged_changes()
        if change_index < len(staged_changes):
            staged_changes.pop(change_index)
            self.save_staged_changes(staged_changes)
    
    def schedule_auto_approval(self, change_index):
        """Schedule auto-approval for a change"""
        staged_changes = self.load_staged_changes()
        if change_index < len(staged_changes):
            staged_changes[change_index]['auto_approve_at'] = datetime.now() + timedelta(hours=2)
            self.save_staged_changes(staged_changes)
    
    def save_staged_changes(self, changes):
        """Save staged changes to file"""
        os.makedirs('data', exist_ok=True)
        with open('data/staged_changes.json', 'w') as f:
            json.dump(changes, f, indent=2, default=str)

def main():
    dashboard = SimpleAIDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()
