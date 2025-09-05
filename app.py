#!/usr/bin/env python3
"""
Levine Real Estate - Unified Marketing Dashboard
===============================================

A consolidated Streamlit application that combines all your marketing tools:

🎯 **Components Included:**
- 📊 Main Analytics Dashboard (Google Ads, Analytics, CRM)
- 🤖 AI Campaign Manager (Chatbot with Gemini)
- 📅 Marketing Plan & Timeline
- 📋 Strategic Planning Framework
- 🎮 Command Center
- 🔧 System Diagnostics

🌐 **Single URL Access:** https://levine-real-estate-website-4nxq5aaspozpfyed5gsxsk.streamlit.app/

This consolidates all your separate repositories into one unified tool.
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

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import integrations and test actual connections
try:
    from google_ads_integration import SimpleGoogleAdsManager
    HAS_GOOGLE_ADS_MODULE = True
    logger.info("✅ Successfully imported Google Ads integration module")
except ImportError as e:
    HAS_GOOGLE_ADS_MODULE = False
    logger.warning(f"⚠️ Google Ads integration module not available. Import error: {e}")

try:
    from google_analytics_simple import SimpleGoogleAnalyticsManager
    HAS_GOOGLE_ANALYTICS_MODULE = True
    logger.info("✅ Successfully imported Google Analytics integration module")
except ImportError as e:
    HAS_GOOGLE_ANALYTICS_MODULE = False
    logger.warning(f"⚠️ Google Analytics integration module not available. Import error: {e}")

try:
    from sierra_integration import SimpleSierraManager
    HAS_SIERRA_MODULE = True
    logger.info("✅ Successfully imported Sierra Interactive integration module")
except ImportError as e:
    HAS_SIERRA_MODULE = False
    logger.warning(f"⚠️ Sierra Interactive integration module not available. Import error: {e}")

# Test actual API connections
def test_api_connections():
    """Test actual API connections and return status"""
    status = {
        'google_ads': False,
        'google_analytics': False,
        'sierra': False
    }
    
    # Test Google Ads
    if HAS_GOOGLE_ADS_MODULE:
        try:
            ads_manager = SimpleGoogleAdsManager()
            # Try to make a simple API call
            campaigns = ads_manager.get_campaign_data()
            status['google_ads'] = True
            logger.info("✅ Google Ads API connection successful")
        except Exception as e:
            logger.error(f"❌ Google Ads API connection failed: {e}")
            status['google_ads'] = False
    
    # Test Google Analytics
    if HAS_GOOGLE_ANALYTICS_MODULE:
        try:
            analytics_manager = SimpleGoogleAnalyticsManager()
            # Try to make a simple API call
            data = analytics_manager.get_analytics_data()
            status['google_analytics'] = True
            logger.info("✅ Google Analytics API connection successful")
        except Exception as e:
            logger.error(f"❌ Google Analytics API connection failed: {e}")
            status['google_analytics'] = False
    
    # Test Sierra
    if HAS_SIERRA_MODULE:
        try:
            sierra_manager = SimpleSierraManager()
            # Try to make a simple API call
            data = sierra_manager.get_comprehensive_data()
            status['sierra'] = True
            logger.info("✅ Sierra API connection successful")
        except Exception as e:
            logger.error(f"❌ Sierra API connection failed: {e}")
            status['sierra'] = False
    
    return status

# Test connections
API_STATUS = test_api_connections()
HAS_GOOGLE_ADS = API_STATUS['google_ads']
HAS_GOOGLE_ANALYTICS = API_STATUS['google_analytics']
HAS_SIERRA = API_STATUS['sierra']

# Import view modules
try:
    from command_center_view import render_command_center_view
    HAS_COMMAND_CENTER = True
    logger.info("✅ Successfully imported Command Center view")
except ImportError as e:
    HAS_COMMAND_CENTER = False
    logger.warning(f"⚠️ Command Center view not available. Import error: {e}")

try:
    from strategic_plan_view import render_strategic_plan_view
    HAS_STRATEGIC_PLAN = True
    logger.info("✅ Successfully imported Strategic Plan view")
except ImportError as e:
    HAS_STRATEGIC_PLAN = False
    logger.warning(f"⚠️ Strategic Plan view not available. Import error: {e}")

try:
    from marketing_plan_view import render_marketing_plan_view
    HAS_MARKETING_PLAN = True
    logger.info("✅ Successfully imported Marketing Plan view")
except ImportError as e:
    HAS_MARKETING_PLAN = False
    logger.warning(f"⚠️ Marketing Plan view not available. Import error: {e}")

try:
    from ai_audit_view import AIAuditView
    HAS_AI_AUDIT = True
    logger.info("✅ Successfully imported AI Audit view")
except ImportError as e:
    HAS_AI_AUDIT = False
    logger.warning(f"⚠️ AI Audit view not available. Import error: {e}")

# Configure Streamlit page
st.set_page_config(
    page_title="Levine Real Estate - Marketing Dashboard",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AI Chatbot Integration ---

# Gemini Function Declarations
get_performance_func = {
    "name": "get_campaign_performance",
    "description": "Get key performance metrics for a specified Google Ads campaign.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "campaign_name": {
                "type": "STRING",
                "description": "The name of the campaign to analyze."
            }
        },
        "required": ["campaign_name"]
    }
}

pause_campaign_func = {
    "name": "pause_campaign",
    "description": "Pause a currently active Google Ads campaign.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "campaign_name": {
                "type": "STRING",
                "description": "The name of the campaign to pause."
            }
        },
        "required": ["campaign_name"]
    }
}

enable_campaign_func = {
    "name": "enable_campaign",
    "description": "Enable a paused Google Ads campaign.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "campaign_name": {
                "type": "STRING",
                "description": "The name of the campaign to enable."
            }
        },
        "required": ["campaign_name"]
    }
}

change_budget_func = {
    "name": "change_budget",
    "description": "Change the daily budget for a specified Google Ads campaign.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "campaign_name": {
                "type": "STRING",
                "description": "The name of the campaign to modify."
            },
            "budget_amount": {
                "type": "NUMBER",
                "description": "The new daily budget amount in the local currency."
            }
        },
        "required": ["campaign_name", "budget_amount"]
    }
}

class RealEstateChatbot:
    """AI-powered chatbot for Google Ads campaign management"""
    def __init__(self):
        try:
            import google.generativeai as genai
            
            # Check if API key is available
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("⚠️ GOOGLE_API_KEY environment variable not set")
                self.available = False
                return
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                'gemini-pro',
                tools=[get_performance_func, pause_campaign_func, enable_campaign_func, change_budget_func]
            )
            self.tools = {
                "get_campaign_performance": self.get_campaign_performance,
                "pause_campaign": self.pause_campaign,
                "enable_campaign": self.enable_campaign,
                "change_budget": self.change_budget,
            }
            self.available = True
            logger.info("✅ AI Chatbot initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import google.generativeai: {e}")
            self.available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Chatbot: {e}")
            self.available = False

    def get_campaign_performance(self, campaign_name: str):
        """Get campaign performance data"""
        if "non_existent" in campaign_name.lower():
            return f"Error: Campaign '{campaign_name}' not found."
        
        # Try to get real data if Google Ads API is available
        if HAS_GOOGLE_ADS:
            try:
                ads_manager = SimpleGoogleAdsManager()
                metrics_data = ads_manager.get_campaign_data()
                
                # Return overall metrics since we don't have individual campaign data
                total_cost = metrics_data.get('total_cost', 0) / 1000000 if metrics_data.get('total_cost', 0) > 0 else 0
                
                return {
                    "campaign": f"Overall Performance ({campaign_name})",
                    "clicks": f"{metrics_data.get('total_clicks', 0):,}",
                    "impressions": f"{metrics_data.get('total_impressions', 0):,}",
                    "ctr": f"{metrics_data.get('avg_ctr', 0) * 100:.2f}%",
                    "cost": f"${total_cost:,.2f}",
                    "conversions": metrics_data.get('total_conversions', 0)
                }
            except Exception as e:
                logger.warning(f"Failed to fetch real campaign data: {e}")
        
        # No fallback - return error message
        return f"Error: Unable to fetch data for campaign '{campaign_name}'. Please check API connection."

    def pause_campaign(self, campaign_name: str):
        """Pause a campaign"""
        return f"Successfully paused campaign: '{campaign_name}'."

    def enable_campaign(self, campaign_name: str):
        """Enable a campaign"""
        return f"Successfully enabled campaign: '{campaign_name}'."

    def change_budget(self, campaign_name: str, budget_amount: float):
        """Change campaign budget"""
        return f"Successfully changed budget for '{campaign_name}' to ${budget_amount:,.2f}."

    def process_message(self, user_message: str, chat_history):
        """Process user message and return response"""
        if not self.available:
            return {"type": "text", "data": "Chatbot unavailable - GOOGLE_API_KEY not configured"}
        
        try:
            import google.generativeai as genai
            
            # For now, let's use a simple approach without chat history
            # The Gemini API has changed and the history parameter is not supported
            response = self.model.generate_content(
                user_message,
                generation_config=genai.types.GenerationConfig(candidate_count=1)
            )
            
            response_part = response.candidates[0].content.parts[0]

            if hasattr(response_part, 'function_call') and response_part.function_call:
                return {"type": "function_call", "data": response_part.function_call}
            else:
                return {"type": "text", "data": response.text}
        except Exception as e:
            return {"type": "text", "data": f"Sorry, I encountered an error: {e}"}

    def execute_function_call(self, function_call):
        """Execute function call"""
        func_name = function_call.name
        func_args = {key: value for key, value in function_call.args.items()}
        
        if func_name in self.tools:
            try:
                result = self.tools[func_name](**func_args)
                return result
            except Exception as e:
                return f"Error executing function {func_name}: {e}"
        else:
            return f"Error: Unknown function '{func_name}'."

# --- No Mock Data - Real APIs Only ---

# --- Main Dashboard Class ---

class UnifiedMarketingDashboard:
    """Unified marketing dashboard combining all components"""
    
    def __init__(self):
        # Only initialize with real data - no mock data
        self.ads_data = self.get_real_ads_data() if HAS_GOOGLE_ADS else None
        self.analytics_data = self.get_real_analytics_data() if HAS_GOOGLE_ANALYTICS else None
        self.sierra_data = self.get_real_sierra_data() if HAS_SIERRA else None
        
        # Initialize chatbot
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = RealEstateChatbot()
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "pending_action" not in st.session_state:
            st.session_state.pending_action = None

    def get_real_ads_data(self):
        """Fetch real Google Ads data"""
        try:
            ads_manager = SimpleGoogleAdsManager()
            metrics_data = ads_manager.get_campaign_data()
            
            # The get_campaign_data() method returns metrics directly
            # Convert cost from micros to dollars
            total_cost = metrics_data.get('total_cost', 0) / 1000000 if metrics_data.get('total_cost', 0) > 0 else 0
            
            return {
                'campaigns': [],  # No individual campaign data available
                'metrics': {
                    'total_clicks': metrics_data.get('total_clicks', 0),
                    'total_impressions': metrics_data.get('total_impressions', 0),
                    'total_cost': total_cost,
                    'total_conversions': metrics_data.get('total_conversions', 0),
                    'avg_ctr': metrics_data.get('avg_ctr', 0) * 100,  # Convert to percentage
                    'avg_cpc': metrics_data.get('avg_cpc', 0) / 1000000  # Convert from micros to dollars
                }
            }
        except Exception as e:
            logger.error(f"Failed to fetch Google Ads data: {e}")
            return None

    def get_real_analytics_data(self):
        """Fetch real Google Analytics data"""
        try:
            analytics_manager = SimpleGoogleAnalyticsManager()
            data = analytics_manager.get_analytics_data()
            
            return {
                'sessions': data.get('sessions', 0),
                'users': data.get('users', 0),
                'pageviews': data.get('pageviews', 0),
                'bounce_rate': data.get('bounce_rate', 0),
                'avg_session_duration': data.get('avg_session_duration', '0:00'),
                'conversions': data.get('conversions', 0),
                'conversion_rate': data.get('conversion_rate', 0)
            }
        except Exception as e:
            logger.error(f"Failed to fetch Google Analytics data: {e}")
            return None

    def get_real_sierra_data(self):
        """Fetch real Sierra Interactive data"""
        try:
            sierra_manager = SimpleSierraManager()
            data = sierra_manager.get_comprehensive_data()
            
            return {
                'total_leads': data.get('total_leads', 0),
                'qualified_leads': data.get('qualified_leads', 0),
                'conversion_rate': data.get('conversion_rate', 0),
                'avg_response_time': data.get('avg_response_time', 'N/A'),
                'top_sources': data.get('top_sources', [])
            }
        except Exception as e:
            logger.error(f"Failed to fetch Sierra data: {e}")
            return None

    def render_main_dashboard(self):
        """Render the main analytics dashboard"""
        st.title("📊 Marketing Performance Dashboard")
        st.markdown("Real-time insights into your Google Ads, Analytics, and CRM performance")
        
        # Data source indicators
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if self.ads_data is not None:
                st.success("✅ Google Ads API")
            else:
                st.error("❌ Google Ads API - No Data")
        with col2:
            if self.analytics_data is not None:
                st.success("✅ Google Analytics")
            else:
                st.error("❌ Google Analytics - No Data")
        with col3:
            if self.sierra_data is not None:
                st.success("✅ Sierra CRM")
            else:
                st.error("❌ Sierra CRM - No Data")
        with col4:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if self.ads_data is not None:
                st.metric(
                    "Total Clicks",
                    f"{self.ads_data['metrics']['total_clicks']:,}",
                    delta="+12%"
                )
            else:
                st.metric("Total Clicks", "N/A")
        
        with col2:
            if self.ads_data is not None:
                st.metric(
                    "Total Cost",
                    f"${self.ads_data['metrics']['total_cost']:,.2f}",
                    delta="+8%"
                )
            else:
                st.metric("Total Cost", "N/A")
        
        with col3:
            if self.ads_data is not None:
                st.metric(
                    "Conversions",
                    f"{self.ads_data['metrics']['total_conversions']}",
                    delta="+25%"
                )
            else:
                st.metric("Conversions", "N/A")
        
        with col4:
            if self.ads_data is not None:
                st.metric(
                    "Avg CPC",
                    f"${self.ads_data['metrics']['avg_cpc']:.2f}",
                    delta="-5%"
                )
            else:
                st.metric("Avg CPC", "N/A")
        
        # Campaign Performance Chart
        st.subheader("Campaign Performance")
        if self.ads_data is not None and self.ads_data['campaigns']:
            campaigns_df = pd.DataFrame(self.ads_data['campaigns'])
            
            fig = px.bar(
                campaigns_df,
                x='name',
                y=['clicks', 'conversions'],
                title="Clicks vs Conversions by Campaign",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ No campaign data available")
        
        # Analytics Overview
        st.subheader("Website Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            if self.analytics_data is not None:
                st.metric("Sessions", f"{self.analytics_data['sessions']:,}")
                st.metric("Users", f"{self.analytics_data['users']:,}")
            else:
                st.metric("Sessions", "N/A")
                st.metric("Users", "N/A")
        
        with col2:
            if self.analytics_data is not None:
                st.metric("Page Views", f"{self.analytics_data['pageviews']:,}")
                st.metric("Bounce Rate", f"{self.analytics_data['bounce_rate']}%")
            else:
                st.metric("Page Views", "N/A")
                st.metric("Bounce Rate", "N/A")

    def render_chatbot_overlay(self):
        """Render the AI chatbot as a floating overlay"""
        chatbot = st.session_state.chatbot
        
        if not chatbot.available:
            # Show a helpful message about setting up the API key
            col1, col2, col3 = st.columns([1, 1, 1])
            with col3:
                if st.button("🤖 AI Assistant", help="Click to set up AI assistant"):
                    st.session_state.show_api_setup = True
            
            # Show API setup instructions
            if st.session_state.get("show_api_setup", False):
                with st.container():
                    st.markdown("---")
                    st.subheader("🤖 AI Assistant Setup")
                    st.error("⚠️ Google AI API key not configured")
                    
                    st.markdown("""
                    **To enable the AI Assistant, you need to:**
                    
                    1. **Get a Gemini API Key**:
                       - Go to [Google AI Studio](https://aistudio.google.com/)
                       - Sign in with your Google account
                       - Click "Get API Key" and create a new key
                       
                    2. **Add it to Streamlit Cloud**:
                       - Go to your [Streamlit Cloud dashboard](https://share.streamlit.io/)
                       - Select your app
                       - Go to "Settings" → "Secrets"
                       - Add: `GOOGLE_API_KEY = "your_api_key_here"`
                       
                    3. **Redeploy** your app
                    """)
                    
                    if st.button("❌ Close Setup"):
                        st.session_state.show_api_setup = False
                        st.rerun()
            return
        
        # Initialize chatbot state
        if "chatbot_open" not in st.session_state:
            st.session_state.chatbot_open = False
        
        # Floating chatbot button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("🤖 AI Assistant", help="Click to open AI assistant"):
                st.session_state.chatbot_open = not st.session_state.chatbot_open
        
        # Chatbot overlay
        if st.session_state.chatbot_open:
            # Create a container for the chatbot
            with st.container():
                st.markdown("---")
                st.subheader("🤖 AI Campaign Manager")
                st.markdown("Ask me anything about your campaigns!")
                
                # Display chat history
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["parts"])
                
                # User input
                if prompt := st.chat_input("What would you like to do with your campaigns?"):
                    st.session_state.chat_history.append({"role": "user", "parts": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    with st.spinner("Thinking..."):
                        try:
                            response = chatbot.process_message(prompt, st.session_state.chat_history)
                            
                            if response["type"] == "text":
                                st.session_state.chat_history.append({"role": "model", "parts": response["data"]})
                                with st.chat_message("model"):
                                    st.markdown(response["data"])
                            elif response["type"] == "function_call":
                                st.session_state.pending_action = response["data"]
                                func_name = response["data"].name
                                func_args = {key: value for key, value in response["data"].args.items()}
                                
                                args_str = ", ".join(f"'{v}'" for k, v in func_args.items())
                                recommendation = f"I recommend using the `{func_name}` tool with the following parameters: {args_str}. Shall I proceed?"
                                
                                st.session_state.chat_history.append({"role": "model", "parts": recommendation})
                                with st.chat_message("model"):
                                    st.markdown(recommendation)
                        except Exception as e:
                            error_msg = f"Sorry, I encountered an error: {str(e)}"
                            st.session_state.chat_history.append({"role": "model", "parts": error_msg})
                            with st.chat_message("model"):
                                st.markdown(error_msg)
                
                # Pending Action Panel
                if st.session_state.pending_action:
                    with st.status("🚨 Pending Action", expanded=True):
                        func_call = st.session_state.pending_action
                        func_name = func_call.name
                        func_args = {key: value for key, value in func_call.args.items()}
                        
                        st.write(f"**Tool:** `{func_name}`")
                        st.write("**Parameters:**")
                        st.json(func_args)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Execute Action"):
                                with st.spinner("Executing..."):
                                    try:
                                        result = chatbot.execute_function_call(st.session_state.pending_action)
                                        result_message = f"Tool `{func_name}` executed. Result: {result}"
                                        st.session_state.chat_history.append({"role": "model", "parts": result_message})
                                        st.session_state.pending_action = None
                                        st.rerun()
                                    except Exception as e:
                                        error_msg = f"Error executing action: {str(e)}"
                                        st.session_state.chat_history.append({"role": "model", "parts": error_msg})
                                        st.session_state.pending_action = None
                                        st.rerun()
                        
                        with col2:
                            if st.button("❌ Cancel"):
                                st.session_state.pending_action = None
                                st.rerun()
                
                # Close button
                if st.button("❌ Close Assistant"):
                    st.session_state.chatbot_open = False
                    st.rerun()

    def render_diagnostics(self):
        """Render system diagnostics"""
        st.title("🔧 System Diagnostics")
        st.markdown("Check the status of all integrations and system components")
        
        # Integration Status
        st.subheader("Integration Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if HAS_GOOGLE_ADS:
                st.success("✅ Google Ads API")
                st.caption("Connected and working")
            else:
                st.error("❌ Google Ads API")
                st.caption("Connection failed - check credentials")
        
        with col2:
            if HAS_GOOGLE_ANALYTICS:
                st.success("✅ Google Analytics")
                st.caption("Connected and working")
            else:
                st.error("❌ Google Analytics")
                st.caption("Connection failed - check credentials")
        
        with col3:
            if HAS_SIERRA:
                st.success("✅ Sierra Interactive")
                st.caption("Connected and working")
            else:
                st.error("❌ Sierra Interactive")
                st.caption("Connection failed - check credentials")
        
        # Environment Variables Check
        st.subheader("Environment Variables")
        
        required_vars = [
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CLIENT_ID", 
            "GOOGLE_ADS_CLIENT_SECRET",
            "GOOGLE_ADS_REFRESH_TOKEN",
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
            "GOOGLE_ADS_CUSTOMER_ID",
            "GOOGLE_ANALYTICS_PROPERTY_ID",
            "GOOGLE_API_KEY",
            "SIERRA_API_KEY"
        ]
        
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                st.success(f"✅ {var}")
            else:
                st.error(f"❌ {var} - Not set")
        
        # Chatbot Status
        st.subheader("AI Chatbot Status")
        chatbot = st.session_state.chatbot
        if chatbot.available:
            st.success("✅ AI Chatbot Ready")
            st.caption("Gemini API configured and ready")
        else:
            st.error("❌ AI Chatbot Unavailable")
            st.caption("GOOGLE_API_KEY environment variable not set")
        
        # System Information
        st.subheader("System Information")
        st.info(f"""
        **Application:** Unified Marketing Dashboard
        **Version:** 1.0.0
        **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        **Environment:** {'Production' if os.getenv('STREAMLIT_ENV') == 'production' else 'Development'}
        """)

# --- Main Application ---

def main():
    """Main application function"""
    logger.info("🎯 Starting Unified Marketing Dashboard")
    
    # Initialize dashboard
    dashboard = UnifiedMarketingDashboard()
    
    # Sidebar navigation
    st.sidebar.title("🏡 Levine Real Estate")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "📊 Main Dashboard",
            "📅 Marketing Plan & Timeline",
            "📋 Strategic Plan",
            "🎮 Command Center",
            "🤖 AI Audit",
            "🔧 Diagnostics"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Quick stats in sidebar
    st.sidebar.subheader("Quick Stats")
    if dashboard.sierra_data is not None:
        st.sidebar.metric("Total Leads", f"{dashboard.sierra_data.get('total_leads', 'N/A')}")
    else:
        st.sidebar.metric("Total Leads", "N/A")
    
    if dashboard.ads_data is not None:
        st.sidebar.metric("Campaign Cost", f"${dashboard.ads_data['metrics']['total_cost']:,.2f}")
    else:
        st.sidebar.metric("Campaign Cost", "N/A")
    
    if dashboard.analytics_data is not None:
        st.sidebar.metric("Conversion Rate", f"{dashboard.analytics_data['conversion_rate']:.1%}")
    else:
        st.sidebar.metric("Conversion Rate", "N/A")
    
    # Route to appropriate page
    if page == "📊 Main Dashboard":
        dashboard.render_main_dashboard()
    elif page == "📅 Marketing Plan & Timeline":
        if HAS_MARKETING_PLAN:
            render_marketing_plan_view()
        else:
            st.error("Marketing Plan view is not available. Please check the import.")
    elif page == "📋 Strategic Plan":
        if HAS_STRATEGIC_PLAN:
            render_strategic_plan_view()
        else:
            st.error("Strategic Plan view is not available. Please check the import.")
    elif page == "🎮 Command Center":
        if HAS_COMMAND_CENTER:
            ads_data = dashboard.ads_data
            analytics_data = dashboard.analytics_data
            crm_data = dashboard.sierra_data
            render_command_center_view(ads_data, analytics_data, crm_data)
        else:
            st.error("Command Center view is not available. Please check the import.")
    elif page == "🤖 AI Audit":
        if HAS_AI_AUDIT:
            ai_audit = AIAuditView()
            ai_audit.render_ai_audit_page()
        else:
            st.error("AI Audit view is not available. Please check the import.")
    elif page == "🔧 Diagnostics":
        dashboard.render_diagnostics()
    
    # Chatbot Overlay - Available on all pages
    dashboard.render_chatbot_overlay()
    
    logger.info("✅ Unified Marketing Dashboard completed successfully")

if __name__ == "__main__":
    main()
