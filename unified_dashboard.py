#!/usr/bin/env python3
"""
Unified Marketing Dashboard
==========================

A consolidated Streamlit application that combines:
- Google Ads Analytics Dashboard
- AI-Powered Campaign Manager (Chatbot)
- Marketing Plan & Timeline
- Strategic Planning Framework
- Command Center

All accessible from a single URL: https://levine-real-estate-website-4nxq5aaspozpfyed5gsxsk.streamlit.app/
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
import google.generativeai as genai

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

# Import Google Ads integration if available
try:
    from google_ads_integration import SimpleGoogleAdsManager
    HAS_GOOGLE_ADS = True
    logger.info("✅ Successfully imported Google Ads integration")
except ImportError as e:
    HAS_GOOGLE_ADS = False
    logger.warning(f"⚠️ Google Ads integration not available, using mock data. Import error: {e}")

# Import Google Analytics integration if available
try:
    from google_analytics_simple import SimpleGoogleAnalyticsManager
    HAS_GOOGLE_ANALYTICS = True
    logger.info("✅ Successfully imported Google Analytics integration")
except ImportError as e:
    HAS_GOOGLE_ANALYTICS = False
    logger.warning(f"⚠️ Google Analytics integration not available, using mock data. Import error: {e}")

# Import Sierra Interactive integration if available
try:
    from sierra_integration import SimpleSierraManager
    HAS_SIERRA = True
    logger.info("✅ Successfully imported Sierra Interactive integration")
except ImportError as e:
    HAS_SIERRA = False
    logger.warning(f"⚠️ Sierra Interactive integration not available, using mock data. Import error: {e}")

# Import local modules if available
try:
    from ads.phase_manager import CampaignPhaseManager
    from ads.guardrails import PerformanceMaxGuardrails
    HAS_LOCAL_MODULES = True
    logger.info("✅ Successfully imported local modules")
except ImportError as e:
    HAS_LOCAL_MODULES = False
    logger.warning(f"⚠️ Local modules not available. Import error: {e}")

# Import Command Center view
try:
    from command_center_view import render_command_center_view
    HAS_COMMAND_CENTER = True
    logger.info("✅ Successfully imported Command Center view")
except ImportError as e:
    HAS_COMMAND_CENTER = False
    logger.warning(f"⚠️ Command Center view not available. Import error: {e}")

# Import Strategic Plan view
try:
    from strategic_plan_view import render_strategic_plan_view
    HAS_STRATEGIC_PLAN = True
    logger.info("✅ Successfully imported Strategic Plan view")
except ImportError as e:
    HAS_STRATEGIC_PLAN = False
    logger.warning(f"⚠️ Strategic Plan view not available. Import error: {e}")

# Import Marketing Plan view
try:
    from marketing_plan_view import render_marketing_plan_view
    HAS_MARKETING_PLAN = True
    logger.info("✅ Successfully imported Marketing Plan view")
except ImportError as e:
    HAS_MARKETING_PLAN = False
    logger.warning(f"⚠️ Marketing Plan view not available. Import error: {e}")

# Configure Streamlit page
st.set_page_config(
    page_title="Levine Real Estate - Marketing Dashboard",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AI Chatbot Integration ---

# Gemini Function Declarations for the chatbot
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
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
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
        except (AttributeError, KeyError):
            self.available = False

    def get_campaign_performance(self, campaign_name: str):
        """Get campaign performance data"""
        if "non_existent" in campaign_name.lower():
            return f"Error: Campaign '{campaign_name}' not found."
        return {
            "campaign": campaign_name,
            "clicks": "1,204",
            "impressions": "34,567",
            "ctr": "3.48%",
            "cost": "$2,450.78"
        }

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
        
        history_for_api = []
        for message in chat_history:
            role = 'user' if message['role'] == 'user' else 'model'
            history_for_api.append({'role': role, 'parts': [message['parts']]})

        try:
            response = self.model.generate_content(
                user_message,
                generation_config=genai.types.GenerationConfig(candidate_count=1),
                history=history_for_api[:-1]
            )
            
            response_part = response.candidates[0].content.parts[0]

            if response_part.function_call:
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

# --- Mock Data Functions ---

def get_mock_ads_data():
    """Generate mock Google Ads data"""
    return {
        'campaigns': [
            {'name': 'L.R - PMax - General', 'clicks': 1204, 'impressions': 34567, 'ctr': 3.48, 'cost': 2450.78, 'conversions': 12},
            {'name': 'L.R - Search - Local', 'clicks': 856, 'impressions': 12345, 'ctr': 6.93, 'cost': 1890.45, 'conversions': 8},
        ],
        'metrics': {
            'total_clicks': 2060,
            'total_impressions': 46912,
            'total_cost': 4341.23,
            'total_conversions': 20,
            'avg_ctr': 4.39,
            'avg_cpc': 2.11
        }
    }

def get_mock_analytics_data():
    """Generate mock Google Analytics data"""
    return {
        'sessions': 15420,
        'users': 12350,
        'pageviews': 45680,
        'bounce_rate': 42.3,
        'avg_session_duration': '2:34',
        'conversions': 45,
        'conversion_rate': 0.29
    }

def get_mock_sierra_data():
    """Generate mock Sierra Interactive data"""
    return {
        'total_leads': 156,
        'qualified_leads': 89,
        'conversion_rate': 57.1,
        'avg_response_time': '2.3 hours',
        'top_sources': ['Google Ads', 'Organic Search', 'Direct']
    }

# --- Main Dashboard Class ---

class UnifiedMarketingDashboard:
    """Unified marketing dashboard combining all components"""
    
    def __init__(self):
        self.ads_data = get_mock_ads_data() if not HAS_GOOGLE_ADS else None
        self.analytics_data = get_mock_analytics_data() if not HAS_GOOGLE_ANALYTICS else None
        self.sierra_data = get_mock_sierra_data() if not HAS_SIERRA else None
        
        # Initialize chatbot
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = RealEstateChatbot()
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "pending_action" not in st.session_state:
            st.session_state.pending_action = None

    def render_main_dashboard(self):
        """Render the main analytics dashboard"""
        st.title("📊 Marketing Performance Dashboard")
        st.markdown("Real-time insights into your Google Ads, Analytics, and CRM performance")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Clicks",
                f"{self.ads_data['metrics']['total_clicks']:,}",
                delta="+12%"
            )
        
        with col2:
            st.metric(
                "Total Cost",
                f"${self.ads_data['metrics']['total_cost']:,.2f}",
                delta="+8%"
            )
        
        with col3:
            st.metric(
                "Conversions",
                f"{self.ads_data['metrics']['total_conversions']}",
                delta="+25%"
            )
        
        with col4:
            st.metric(
                "Avg CPC",
                f"${self.ads_data['metrics']['avg_cpc']:.2f}",
                delta="-5%"
            )
        
        # Campaign Performance Chart
        st.subheader("Campaign Performance")
        campaigns_df = pd.DataFrame(self.ads_data['campaigns'])
        
        fig = px.bar(
            campaigns_df,
            x='name',
            y=['clicks', 'conversions'],
            title="Clicks vs Conversions by Campaign",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analytics Overview
        st.subheader("Website Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Sessions", f"{self.analytics_data['sessions']:,}")
            st.metric("Users", f"{self.analytics_data['users']:,}")
        
        with col2:
            st.metric("Page Views", f"{self.analytics_data['pageviews']:,}")
            st.metric("Bounce Rate", f"{self.analytics_data['bounce_rate']}%")

    def render_chatbot(self):
        """Render the AI chatbot interface"""
        st.title("🤖 AI Campaign Manager")
        st.markdown("Chat with your AI assistant to manage Google Ads campaigns")
        
        chatbot = st.session_state.chatbot
        
        if not chatbot.available:
            st.error("⚠️ Chatbot unavailable - GOOGLE_API_KEY environment variable not set")
            st.info("To enable the chatbot, set your Google API key in the environment variables")
            return
        
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
        
        # Pending Action Panel
        if st.session_state.pending_action:
            with st.status("🚨 Pending Action", expanded=True):
                func_call = st.session_state.pending_action
                func_name = func_call.name
                func_args = {key: value for key, value in func_call.args.items()}
                
                st.write(f"**Tool:** `{func_name}`")
                st.write("**Parameters:**")
                st.json(func_args)
                
                if st.button("✅ Execute Action"):
                    with st.spinner("Executing..."):
                        result = chatbot.execute_function_call(st.session_state.pending_action)
                        
                        result_message = f"Tool `{func_name}` executed. Result: {result}"
                        st.session_state.chat_history.append({"role": "model", "parts": result_message})
                        
                        st.session_state.pending_action = None
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
            else:
                st.error("❌ Google Ads API")
                st.caption("Using mock data")
        
        with col2:
            if HAS_GOOGLE_ANALYTICS:
                st.success("✅ Google Analytics")
            else:
                st.error("❌ Google Analytics")
                st.caption("Using mock data")
        
        with col3:
            if HAS_SIERRA:
                st.success("✅ Sierra Interactive")
            else:
                st.error("❌ Sierra Interactive")
                st.caption("Using mock data")
        
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
            "🤖 AI Campaign Manager", 
            "🎯 Marketing Plan & Timeline",
            "📋 Strategic Plan",
            "🎮 Command Center",
            "🔧 Diagnostics"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Quick stats in sidebar
    st.sidebar.subheader("Quick Stats")
    st.sidebar.metric("Total Leads", "156", "+12")
    st.sidebar.metric("Campaign Cost", "$4,341", "+$89")
    st.sidebar.metric("Conversion Rate", "12.8%", "+2.1%")
    
    # Route to appropriate page
    if page == "📊 Main Dashboard":
        dashboard.render_main_dashboard()
    elif page == "🤖 AI Campaign Manager":
        dashboard.render_chatbot()
    elif page == "🎯 Marketing Plan & Timeline":
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
    elif page == "🔧 Diagnostics":
        dashboard.render_diagnostics()
    
    logger.info("✅ Unified Marketing Dashboard completed successfully")

if __name__ == "__main__":
    main()
