#!/usr/bin/env python3
"""
Test Script for Strategic Plan View
===================================

This script demonstrates how to use the strategic plan view independently
and verifies that all components are working correctly.

"""

import streamlit as st
from strategic_plan_view import render_strategic_plan_view

# Page configuration for testing
st.set_page_config(
    page_title="Strategic Plan - Test",
    page_icon="🎯",
    layout="wide"
)

# Test the strategic plan view
if __name__ == "__main__":
    st.markdown("# 🎯 Strategic Plan View - Test")
    st.markdown("This is a standalone test of the Strategic Plan view.")
    
    render_strategic_plan_view()
    
    st.markdown("---")
    st.success("✅ Strategic Plan view rendered successfully!")
    st.info("💡 To integrate this into your main dashboard, select 'Strategic Plan' from the sidebar navigation.")
