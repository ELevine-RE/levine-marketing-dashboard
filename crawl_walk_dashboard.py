#!/usr/bin/env python3
"""
Crawl/Walk Strategy Dashboard
============================

Streamlined dashboard focused entirely on the Crawl/Walk campaign strategy.
Visualizes campaign performance, milestones, and automated execution.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add google-ads-analysis to path for imports
google_ads_path = os.path.join(os.path.dirname(__file__), 'google-ads-analysis')
sys.path.insert(0, google_ads_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import Crawl/Walk components
try:
    from tools.crawl_walk_campaign_creator import CrawlWalkCampaignCreator
    from tools.enhanced_quick_analysis import EnhancedQuickAnalysis
    HAS_CRAWL_WALK = True
except ImportError as e:
    logger.error(f"❌ Failed to import Crawl/Walk components: {e}")
    CrawlWalkCampaignCreator = None
    EnhancedQuickAnalysis = None
    HAS_CRAWL_WALK = False

# Import Google Ads integration
try:
    from google_ads_integration import SimpleGoogleAdsManager
    HAS_GOOGLE_ADS = True
except ImportError:
    SimpleGoogleAdsManager = None
    HAS_GOOGLE_ADS = False

class CrawlWalkDashboard:
    """Streamlined dashboard for Crawl/Walk strategy"""
    
    def __init__(self):
        self.crawl_walk_creator = CrawlWalkCampaignCreator() if HAS_CRAWL_WALK else None
        self.analyzer = EnhancedQuickAnalysis() if HAS_CRAWL_WALK else None
        self.ads_manager = SimpleGoogleAdsManager() if HAS_GOOGLE_ADS else None
        
        # Initialize session state
        if "dashboard_data" not in st.session_state:
            st.session_state.dashboard_data = None
        if "last_analysis" not in st.session_state:
            st.session_state.last_analysis = None
        if "milestones" not in st.session_state:
            st.session_state.milestones = []
    
    def render_main_dashboard(self):
        """Render the main Crawl/Walk dashboard"""
        st.set_page_config(
            page_title="Crawl/Walk Strategy Dashboard",
            page_icon="🚀",
            layout="wide"
        )
        
        # Header
        st.title("🚀 Crawl/Walk Campaign Strategy")
        st.markdown("**Sequential campaign launch strategy with milestone-based automation**")
        
        # Status indicators
        self._render_status_indicators()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Strategy Overview", "🎯 Campaign Performance", "🔍 Milestone Detection", "⚙️ Execution Controls"])
        
        with tab1:
            self._render_strategy_overview()
        
        with tab2:
            self._render_campaign_performance()
        
        with tab3:
            self._render_milestone_detection()
        
        with tab4:
            self._render_execution_controls()
    
    def _render_status_indicators(self):
        """Render status indicators"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if HAS_CRAWL_WALK:
                st.success("✅ Crawl/Walk System")
            else:
                st.error("❌ Crawl/Walk System")
        
        with col2:
            if HAS_GOOGLE_ADS:
                st.success("✅ Google Ads API")
            else:
                st.error("❌ Google Ads API")
        
        with col3:
            if self._check_crawl_campaign_exists():
                st.success("✅ Crawl Campaign")
            else:
                st.warning("⚠️ Crawl Campaign")
        
        with col4:
            if self._check_walk_schedule_exists():
                st.success("✅ Walk Schedule")
            else:
                st.warning("⚠️ Walk Schedule")
    
    def _render_strategy_overview(self):
        """Render strategy overview"""
        st.header("📊 Strategy Overview")
        
        # Strategy phases
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🦎 Crawl Phase - Local Presence")
            st.markdown("""
            **Campaign:** L.R - PMax - Local Presence  
            **Budget:** $49/day ($1,500/month)  
            **Target:** Park City, UT  
            **Goal:** 15-30 conversions to exit Phase 1  
            **Status:** Active Learning Phase
            """)
            
            # Crawl phase metrics
            crawl_data = self._get_crawl_campaign_data()
            if crawl_data:
                st.metric("Current Phase", crawl_data.get('phase', 'PHASE_1'))
                st.metric("Conversions", crawl_data.get('conversions', 0))
                st.metric("Cost", f"${crawl_data.get('cost', 0):.2f}")
                st.metric("Days Active", crawl_data.get('days_active', 0))
        
        with col2:
            st.subheader("🏃 Walk Phase - Feeder Markets")
            st.markdown("""
            **Campaign:** L.R - PMax - Feeder Markets  
            **Budget:** $41/day (remaining allocation)  
            **Target:** HNW zip codes (Dallas, LA, NYC)  
            **Goal:** Scale to high-net-worth markets  
            **Status:** Scheduled (Waiting for Crawl milestone)
            """)
            
            # Walk phase status
            walk_status = self._get_walk_schedule_status()
            st.metric("Schedule Status", walk_status.get('status', 'Not Created'))
            st.metric("Document URL", walk_status.get('doc_url', 'N/A'))
            st.metric("Ready to Launch", walk_status.get('ready', False))
        
        # Strategy timeline
        st.subheader("📅 Strategy Timeline")
        self._render_strategy_timeline()
    
    def _render_campaign_performance(self):
        """Render campaign performance"""
        st.header("🎯 Campaign Performance")
        
        # Refresh data button
        if st.button("🔄 Refresh Performance Data"):
            with st.spinner("Analyzing campaign performance..."):
                self._refresh_performance_data()
        
        # Performance metrics
        if st.session_state.dashboard_data:
            data = st.session_state.dashboard_data
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Campaigns", data.get('total_campaigns', 0))
            with col2:
                st.metric("Active Campaigns", data.get('active_campaigns', 0))
            with col3:
                st.metric("Total Cost", f"${data.get('total_cost', 0):.2f}")
            with col4:
                st.metric("Total Conversions", data.get('total_conversions', 0))
            
            # Campaign details
            campaigns = data.get('campaigns', [])
            if campaigns:
                st.subheader("📈 Campaign Details")
                
                for campaign in campaigns:
                    with st.expander(f"📊 {campaign['campaign_info']['name']}"):
                        perf = campaign['performance']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Impressions", f"{perf.get('impressions', 0):,}")
                            st.metric("Clicks", f"{perf.get('clicks', 0):,}")
                        
                        with col2:
                            st.metric("CTR", f"{perf.get('ctr', 0):.2f}%")
                            st.metric("Cost", f"${perf.get('cost_amount', 0):.2f}")
                        
                        with col3:
                            st.metric("Conversions", perf.get('conversions', 0))
                            st.metric("Cost/Conversion", f"${perf.get('cost_per_conversion', 0):.2f}")
                        
                        # Phase indicator
                        phase = campaign['phase']
                        if phase == 'PHASE_1':
                            st.warning(f"🦎 Learning Phase: {phase}")
                        elif phase == 'PHASE_2':
                            st.info(f"🏃 Learning Complete: {phase}")
                        else:
                            st.success(f"🚀 Optimized: {phase}")
        else:
            st.info("No performance data available. Click 'Refresh Performance Data' to load.")
    
    def _render_milestone_detection(self):
        """Render milestone detection"""
        st.header("🔍 Milestone Detection")
        
        # Run analysis button
        if st.button("🔍 Run Milestone Analysis"):
            with st.spinner("Analyzing milestones..."):
                self._run_milestone_analysis()
        
        # Milestone alerts
        if st.session_state.milestones:
            st.subheader("🚨 Active Milestones")
            
            for milestone in st.session_state.milestones:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #ff6b6b; color: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
                        <h3>🚨 MILESTONE REACHED</h3>
                        <p><strong>Campaign:</strong> {milestone['campaign_name']}</p>
                        <p><strong>Phase:</strong> {milestone['phase']}</p>
                        <p><strong>Message:</strong> {milestone['message']}</p>
                        <p><strong>Action Required:</strong> {milestone['action_required']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No milestones detected. Run analysis to check for milestone triggers.")
        
        # Milestone history
        self._render_milestone_history()
    
    def _render_execution_controls(self):
        """Render execution controls"""
        st.header("⚙️ Execution Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Execute Crawl/Walk Strategy")
            st.markdown("Create the complete Crawl/Walk strategy:")
            
            if st.button("🦎 Create Crawl Campaign", help="Create Local Presence campaign"):
                with st.spinner("Creating Crawl campaign..."):
                    result = self._execute_crawl_campaign()
                    if result['success']:
                        st.success("✅ Crawl campaign created successfully!")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to create Crawl campaign: {result['error']}")
            
            if st.button("📝 Create Walk Schedule", help="Create Feeder Markets schedule document"):
                with st.spinner("Creating Walk schedule document..."):
                    result = self._execute_walk_schedule()
                    if result['success']:
                        st.success("✅ Walk schedule document created!")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to create Walk schedule: {result['error']}")
        
        with col2:
            st.subheader("🔍 Analysis & Monitoring")
            st.markdown("Run analysis and monitoring:")
            
            if st.button("📊 Run Daily Analysis", help="Run comprehensive daily analysis"):
                with st.spinner("Running daily analysis..."):
                    result = self._run_daily_analysis()
                    if result['success']:
                        st.success("✅ Daily analysis completed!")
                        st.json(result['summary'])
                    else:
                        st.error(f"❌ Analysis failed: {result['error']}")
            
            if st.button("📧 Test Email Alerts", help="Test milestone email system"):
                with st.spinner("Testing email alerts..."):
                    result = self._test_email_alerts()
                    if result['success']:
                        st.success("✅ Email alerts tested!")
                    else:
                        st.error(f"❌ Email test failed: {result['error']}")
        
        # Automation status
        st.subheader("🤖 Automation Status")
        self._render_automation_status()
    
    def _render_strategy_timeline(self):
        """Render strategy timeline"""
        timeline_data = [
            {
                'Phase': 'Crawl',
                'Start': 'Day 1',
                'End': 'Phase 1 Exit',
                'Duration': '15-30 conversions',
                'Budget': '$49/day',
                'Target': 'Park City, UT',
                'Status': 'Active'
            },
            {
                'Phase': 'Walk',
                'Start': 'Milestone Trigger',
                'End': 'Ongoing',
                'Duration': 'Continuous',
                'Budget': '$41/day',
                'Target': 'HNW Markets',
                'Status': 'Scheduled'
            }
        ]
        
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True)
    
    def _render_milestone_history(self):
        """Render milestone history"""
        st.subheader("📋 Milestone History")
        
        # Load milestone history
        try:
            if os.path.exists('data/daily_analysis_log.json'):
                with open('data/daily_analysis_log.json', 'r') as f:
                    logs = json.load(f)
                
                # Extract milestones from logs
                milestone_history = []
                for log in logs:
                    if log.get('milestones'):
                        for milestone in log['milestones']:
                            milestone_history.append({
                                'Date': log['timestamp'][:10],
                                'Campaign': milestone['campaign_name'],
                                'Phase': milestone['phase'],
                                'Message': milestone['message']
                            })
                
                if milestone_history:
                    df = pd.DataFrame(milestone_history)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No milestone history found.")
            else:
                st.info("No analysis logs found.")
        except Exception as e:
            st.error(f"Error loading milestone history: {e}")
    
    def _render_automation_status(self):
        """Render automation status"""
        automation_data = {
            'Component': ['Campaign Creator', 'Milestone Detection', 'Email Alerts', 'Daily Analysis'],
            'Status': ['✅ Ready', '✅ Ready', '✅ Ready', '✅ Ready'],
            'Last Run': ['Manual', 'Manual', 'Manual', 'Manual'],
            'Next Run': ['On Demand', 'On Demand', 'On Demand', 'On Demand']
        }
        
        df = pd.DataFrame(automation_data)
        st.dataframe(df, use_container_width=True)
        
        st.info("💡 **GitHub Actions Setup:** Automation will be configured to run daily analysis and milestone detection.")
    
    def _check_crawl_campaign_exists(self) -> bool:
        """Check if Crawl campaign exists"""
        try:
            if self.ads_manager:
                campaigns = self.ads_manager.get_campaign_data()
                # Check if Local Presence campaign exists
                return any('Local Presence' in str(campaign) for campaign in campaigns)
        except Exception:
            pass
        return False
    
    def _check_walk_schedule_exists(self) -> bool:
        """Check if Walk schedule document exists"""
        try:
            return os.path.exists('data/walk_schedule_doc.json')
        except Exception:
            return False
    
    def _get_crawl_campaign_data(self) -> Optional[Dict]:
        """Get Crawl campaign data"""
        try:
            if self.analyzer:
                analysis = self.analyzer.analyze_campaigns()
                campaigns = analysis.get('campaigns', [])
                for campaign in campaigns:
                    if 'Local Presence' in campaign['campaign_info']['name']:
                        perf = campaign['performance']
                        return {
                            'phase': campaign['phase'],
                            'conversions': perf.get('conversions', 0),
                            'cost': perf.get('cost_amount', 0),
                            'days_active': 1  # Placeholder
                        }
        except Exception:
            pass
        return None
    
    def _get_walk_schedule_status(self) -> Dict:
        """Get Walk schedule status"""
        try:
            if os.path.exists('data/walk_schedule_doc.json'):
                with open('data/walk_schedule_doc.json', 'r') as f:
                    data = json.load(f)
                return {
                    'status': 'Created',
                    'doc_url': data.get('doc_url', 'N/A'),
                    'ready': True
                }
        except Exception:
            pass
        return {'status': 'Not Created', 'doc_url': 'N/A', 'ready': False}
    
    def _refresh_performance_data(self):
        """Refresh performance data"""
        try:
            if self.analyzer:
                analysis = self.analyzer.analyze_campaigns()
                st.session_state.dashboard_data = analysis
                st.session_state.last_analysis = datetime.now()
                st.success("✅ Performance data refreshed!")
            else:
                st.error("❌ Analyzer not available")
        except Exception as e:
            st.error(f"❌ Error refreshing data: {e}")
    
    def _run_milestone_analysis(self):
        """Run milestone analysis"""
        try:
            if self.analyzer:
                analysis = self.analyzer.analyze_campaigns()
                st.session_state.milestones = analysis.get('milestones', [])
                st.session_state.dashboard_data = analysis
                
                if st.session_state.milestones:
                    st.success(f"✅ Found {len(st.session_state.milestones)} milestone(s)!")
                else:
                    st.info("ℹ️ No milestones detected.")
            else:
                st.error("❌ Analyzer not available")
        except Exception as e:
            st.error(f"❌ Error running analysis: {e}")
    
    def _execute_crawl_campaign(self) -> Dict:
        """Execute Crawl campaign creation"""
        try:
            if self.crawl_walk_creator:
                return self.crawl_walk_creator.create_crawl_campaign()
            else:
                return {"success": False, "error": "Crawl/Walk creator not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_walk_schedule(self) -> Dict:
        """Execute Walk schedule creation"""
        try:
            if self.crawl_walk_creator:
                result = self.crawl_walk_creator.create_walk_schedule_doc()
                # Save document info
                if result['success']:
                    os.makedirs('data', exist_ok=True)
                    with open('data/walk_schedule_doc.json', 'w') as f:
                        json.dump(result, f)
                return result
            else:
                return {"success": False, "error": "Crawl/Walk creator not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_daily_analysis(self) -> Dict:
        """Run daily analysis"""
        try:
            if self.analyzer:
                result = self.analyzer.run_daily_analysis()
                return result
            else:
                return {"success": False, "error": "Analyzer not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_email_alerts(self) -> Dict:
        """Test email alerts"""
        try:
            # Create test milestone
            test_milestone = {
                'type': 'PHASE_EXIT',
                'campaign_name': 'L.R - PMax - Local Presence (TEST)',
                'phase': 'PHASE_2',
                'message': 'Test milestone reached',
                'action_required': 'Test action required',
                'timestamp': datetime.now().isoformat()
            }
            
            test_analysis = {
                'milestones': [test_milestone],
                'summary': {'milestones_detected': 1}
            }
            
            if self.analyzer:
                self.analyzer._send_milestone_email(test_analysis)
                return {"success": True, "message": "Test email sent"}
            else:
                return {"success": False, "error": "Analyzer not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main function"""
    logger.info("🚀 Starting Crawl/Walk Strategy Dashboard")
    
    try:
        dashboard = CrawlWalkDashboard()
        dashboard.render_main_dashboard()
        
        logger.info("✅ Crawl/Walk Strategy Dashboard completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        st.error(f"Dashboard error: {e}")

if __name__ == "__main__":
    main()
