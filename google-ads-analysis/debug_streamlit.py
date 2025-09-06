#!/usr/bin/env python3
"""
Debug script to test Streamlit Cloud environment variables
"""

import streamlit as st
import os

st.title("🔍 Streamlit Cloud Debug")

st.header("Environment Variables Check")

# Check each required environment variable
env_vars = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID", 
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    "GOOGLE_ADS_CUSTOMER_ID"
]

st.subheader("Google Ads Environment Variables:")
for var in env_vars:
    value = os.environ.get(var)
    if value:
        # Show first 10 chars + "..." for security
        display_value = value[:10] + "..." if len(value) > 10 else value
        st.success(f"✅ {var}: {display_value}")
    else:
        st.error(f"❌ {var}: NOT SET")

st.subheader("All Environment Variables:")
all_env = dict(os.environ)
google_ads_vars = {k: v for k, v in all_env.items() if 'GOOGLE_ADS' in k}
st.json(google_ads_vars)

st.subheader("Test Google Ads Connection:")
try:
    from google_ads_integration import SimpleGoogleAdsManager
    manager = SimpleGoogleAdsManager()
    st.success("✅ Google Ads integration initialized successfully!")
    
    # Try to fetch data
    data = manager.get_campaign_data()
    if data and "error" not in data:
        st.success(f"✅ Successfully fetched data for {len(data)} campaigns")
    else:
        st.error(f"❌ Error fetching data: {data.get('error', 'Unknown error')}")
        
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
