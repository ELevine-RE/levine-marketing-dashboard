#!/usr/bin/env python3
"""
Campaign Audit View
==================

Comprehensive campaign audit page for Streamlit that displays all API data
and includes sophisticated guardrails and optimization recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, List, Optional

# Add google-ads-analysis to path for imports
google_ads_path = os.path.join(os.path.dirname(__file__), 'google-ads-analysis')
sys.path.insert(0, google_ads_path)

try:
    from tools.campaign_auditor import CampaignAuditor
    HAS_CAMPAIGN_AUDITOR = True
except ImportError as e:
    CampaignAuditor = None
    HAS_CAMPAIGN_AUDITOR = False
    print(f"Campaign Auditor import error: {e}")

try:
    from guardrails import PerformanceMaxGuardrails
    HAS_GUARDRAILS = True
except ImportError as e:
    PerformanceMaxGuardrails = None
    HAS_GUARDRAILS = False
    print(f"Guardrails import error: {e}")

try:
    from ads.guardrails import PerformanceMaxGuardrails as AdsGuardrails
    HAS_ADS_GUARDRAILS = True
except ImportError as e:
    AdsGuardrails = None
    HAS_ADS_GUARDRAILS = False
    print(f"Ads Guardrails import error: {e}")

class CampaignAuditView:
    """Campaign Audit page for Streamlit."""
    
    def __init__(self):
        self.customer_id = st.session_state.get('customer_id', '5426234549')
        self.campaign_name = "L.R - PMax - General"
        self.audit_results = None
        self.guardrails = None
        
    def render(self):
        """Render the campaign audit page."""
        st.title("🔍 Campaign Audit & Optimization")
        st.markdown("Comprehensive campaign analysis with sophisticated guardrails and recommendations")
        
        # Initialize guardrails
        self.guardrails = None
        if HAS_ADS_GUARDRAILS:
            try:
                self.guardrails = AdsGuardrails()
            except Exception as e:
                st.warning(f"Could not initialize ads guardrails: {e}")
        elif HAS_GUARDRAILS:
            try:
                self.guardrails = PerformanceMaxGuardrails()
            except Exception as e:
                st.warning(f"Could not initialize guardrails: {e}")
        else:
            st.warning("Guardrails not available - please check imports")
        
        # Campaign selection
        col1, col2 = st.columns([2, 1])
        with col1:
            self.campaign_name = st.text_input(
                "Campaign Name", 
                value=self.campaign_name,
                help="Enter the exact campaign name from Google Ads"
            )
        with col2:
            if st.button("🔍 Run Audit", type="primary"):
                self._run_campaign_audit()
        
        # Display audit results
        if self.audit_results:
            self._display_audit_results()
        else:
            st.info("👆 Click 'Run Audit' to analyze your campaign")
    
    def _run_campaign_audit(self):
        """Run the campaign audit."""
        if not HAS_CAMPAIGN_AUDITOR:
            st.error("Campaign Auditor not available. Please check imports.")
            return
        
        with st.spinner("🔍 Running comprehensive campaign audit..."):
            try:
                auditor = CampaignAuditor(self.customer_id)
                self.audit_results = auditor.audit_campaign(self.campaign_name)
                
                if self.audit_results["success"]:
                    st.success("✅ Campaign audit completed successfully!")
                else:
                    st.error(f"❌ Campaign audit failed: {self.audit_results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error running audit: {e}")
                self.audit_results = None
    
    def _display_audit_results(self):
        """Display comprehensive audit results."""
        if not self.audit_results or not self.audit_results["success"]:
            return
        
        campaign_data = self.audit_results["campaign_data"]
        analysis = self.audit_results["analysis"]
        recommendations = self.audit_results["recommendations"]
        summary = self.audit_results["summary"]
        
        # Audit Summary
        st.subheader("📊 Audit Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🔴" if summary["overall_status"] == "Critical" else "🟡" if summary["overall_status"] == "Needs Attention" else "🟢"
            st.metric("Overall Status", f"{status_color} {summary['overall_status']}")
        
        with col2:
            st.metric("Total Recommendations", summary["total_recommendations"])
        
        with col3:
            st.metric("High Priority", summary["high_priority"], delta=f"{summary['high_priority']} critical issues")
        
        with col4:
            st.metric("Medium Priority", summary["medium_priority"], delta=f"{summary['medium_priority']} important fixes")
        
        # Campaign Overview
        st.subheader("📋 Campaign Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Campaign ID", campaign_data["id"])
            st.metric("Status", campaign_data["status"])
        
        with col2:
            st.metric("Type", campaign_data["channel_type"])
            st.metric("Budget", f"${campaign_data['budget_amount']:.2f}")
        
        with col3:
            st.metric("Bidding Strategy", campaign_data["bidding_strategy"])
            if campaign_data.get("target_cpa"):
                st.metric("Target CPA", f"${campaign_data['target_cpa']:.2f}")
        
        with col4:
            st.metric("Budget Delivery", campaign_data.get("budget_delivery", "N/A"))
            if campaign_data.get("target_roas"):
                st.metric("Target ROAS", f"{campaign_data['target_roas']:.2f}")
        
        # Performance Data
        self._display_performance_data(analysis["performance"])
        
        # Asset Analysis
        self._display_asset_analysis(analysis["assets"])
        
        # Targeting Analysis
        self._display_targeting_analysis(analysis["targeting"])
        
        # Budget Analysis
        self._display_budget_analysis(analysis["budget"])
        
        # Guardrails Analysis
        self._display_guardrails_analysis(campaign_data)
        
        # Recommendations
        self._display_recommendations(recommendations)
        
        # Optimization Actions
        self._display_optimization_actions(campaign_data, recommendations)
    
    def _display_performance_data(self, performance_data):
        """Display performance metrics."""
        st.subheader("📈 Performance Analysis")
        
        if performance_data.get("status") == "no_data":
            st.warning("📊 No performance data available (campaign too new)")
            return
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Impressions", f"{performance_data['total_impressions']:,}")
            st.metric("Total Clicks", f"{performance_data['total_clicks']:,}")
        
        with col2:
            st.metric("Total Cost", f"${performance_data['total_cost']:.2f}")
            st.metric("Total Conversions", f"{performance_data['total_conversions']:.0f}")
        
        with col3:
            st.metric("Average CTR", f"{performance_data['avg_ctr']:.2f}%")
            st.metric("Average CPC", f"${performance_data['avg_cpc']:.2f}")
        
        with col4:
            st.metric("Conversion Rate", f"{performance_data['conversion_rate']:.2f}%")
            st.metric("Cost per Conversion", f"${performance_data['cost_per_conversion']:.2f}")
        
        # Performance Charts
        if performance_data['total_impressions'] > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # CTR vs CPC scatter
                fig_ctr = go.Figure()
                fig_ctr.add_trace(go.Scatter(
                    x=[performance_data['avg_cpc']],
                    y=[performance_data['avg_ctr']],
                    mode='markers',
                    marker=dict(size=20, color='blue'),
                    text=[f"CTR: {performance_data['avg_ctr']:.2f}%<br>CPC: ${performance_data['avg_cpc']:.2f}"],
                    hovertemplate='%{text}<extra></extra>'
                ))
                fig_ctr.update_layout(
                    title="CTR vs CPC Performance",
                    xaxis_title="Cost Per Click ($)",
                    yaxis_title="Click-Through Rate (%)",
                    height=400
                )
                st.plotly_chart(fig_ctr, use_container_width=True)
            
            with col2:
                # Performance gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = performance_data['avg_ctr'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "CTR Performance"},
                    delta = {'reference': 2.0},
                    gauge = {
                        'axis': {'range': [None, 10]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 1], 'color': "lightgray"},
                            {'range': [1, 3], 'color': "yellow"},
                            {'range': [3, 10], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 2.0
                        }
                    }
                ))
                fig_gauge.update_layout(height=400)
                st.plotly_chart(fig_gauge, use_container_width=True)
    
    def _display_asset_analysis(self, asset_data):
        """Display asset analysis."""
        st.subheader("🖼️ Asset Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Assets", asset_data["total_assets"])
            
            if asset_data["asset_types"]:
                st.markdown("**Asset Types:**")
                for asset_type, count in asset_data["asset_types"].items():
                    st.write(f"• {asset_type}: {count}")
            else:
                st.warning("No asset types found")
        
        with col2:
            if asset_data["asset_sets"]:
                st.markdown("**Asset Sets:**")
                for asset_set, count in asset_data["asset_sets"].items():
                    st.write(f"• {asset_set}: {count}")
            else:
                st.warning("No asset sets found")
        
        # Asset Requirements Check
        if self.guardrails:
            st.markdown("**Asset Requirements Check:**")
            asset_requirements = self.guardrails.ASSET_REQUIREMENTS
            
            for category, requirements in asset_requirements.items():
                if isinstance(requirements, dict) and 'min' in requirements:
                    current_count = asset_data["asset_types"].get(category, 0)
                    required_count = requirements['min']
                    
                    if current_count >= required_count:
                        st.success(f"✅ {category}: {current_count}/{required_count}")
                    else:
                        st.error(f"❌ {category}: {current_count}/{required_count} (Need {required_count - current_count} more)")
    
    def _display_targeting_analysis(self, targeting_data):
        """Display targeting analysis."""
        st.subheader("🎯 Targeting Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Keywords", targeting_data["total_keywords"])
            
            if targeting_data["match_types"]:
                st.markdown("**Match Types:**")
                for match_type, count in targeting_data["match_types"].items():
                    st.write(f"• {match_type}: {count}")
            else:
                st.info("Performance Max campaigns use automated targeting")
        
        with col2:
            st.metric("High Performing Keywords", targeting_data["keyword_performance"]["high_performing"])
            st.metric("Low Performing Keywords", targeting_data["keyword_performance"]["low_performing"])
        
        # Targeting Recommendations
        if targeting_data["total_keywords"] == 0:
            st.info("💡 **Recommendation:** Consider adding negative keywords to exclude irrelevant traffic")
    
    def _display_budget_analysis(self, budget_data):
        """Display budget analysis."""
        st.subheader("💰 Budget & Bidding Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Budget Amount", f"${budget_data['budget_amount']:.2f}")
            st.metric("Bidding Strategy", budget_data["bidding_strategy"])
        
        with col2:
            if budget_data.get("target_cpa"):
                st.metric("Target CPA", f"${budget_data['target_cpa']:.2f}")
            if budget_data.get("target_roas"):
                st.metric("Target ROAS", f"{budget_data['target_roas']:.2f}")
        
        with col3:
            st.metric("Budget Delivery", budget_data.get("budget_delivery", "N/A"))
            st.metric("Budget Type", budget_data.get("budget_type", "N/A"))
        
        # Budget Recommendations
        budget = budget_data["budget_amount"]
        if budget < 1000:
            st.warning(f"⚠️ **Budget Alert:** ${budget:.2f} may be too low for effective Performance Max optimization")
        elif budget > 5000:
            st.info(f"ℹ️ **Budget Note:** ${budget:.2f} is high for initial testing - consider starting lower")
        else:
            st.success(f"✅ **Budget Status:** ${budget:.2f} is within reasonable range")
    
    def _display_guardrails_analysis(self, campaign_data):
        """Display guardrails analysis."""
        st.subheader("🛡️ Guardrails Analysis")
        
        if not self.guardrails:
            st.warning("Guardrails not available")
            return
        
        # Create campaign state for guardrails
        campaign_state = {
            'daily_budget': campaign_data.get('budget_amount', 0),
            'target_cpa': campaign_data.get('target_cpa', 0),
            'total_conversions': self.audit_results["analysis"]["performance"].get("total_conversions", 0),
            'asset_groups': [{'name': 'Main Group', 'status': 'ENABLED', 'asset_counts': {}}],
            'url_exclusions': [],
            'targeting_type': 'PRESENCE_ONLY',
            'primary_conversions': ['Lead Form Submission'],
            'secondary_conversions': []
        }
        
        # Check hard invariants
        invariant_check = self.guardrails._check_hard_invariants(campaign_state)
        
        if invariant_check['passed']:
            st.success("✅ All hard invariants passed")
        else:
            st.error("❌ Hard invariant violations:")
            for reason in invariant_check['reasons']:
                st.error(f"• {reason}")
        
        # Guardrails Summary
        guardrails_summary = self.guardrails.get_guardrail_summary()
        
        with st.expander("📋 Guardrails Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Budget Limits:**")
                budget_limits = guardrails_summary['budget_limits']
                st.write(f"• Min Daily: ${budget_limits['min_daily']}")
                st.write(f"• Max Daily: ${budget_limits['max_daily']}")
                st.write(f"• Max Adjustment: {budget_limits['max_adjustment_percent']}%")
                st.write(f"• Frequency: {budget_limits['max_frequency_days']} days")
            
            with col2:
                st.markdown("**Target CPA Limits:**")
                tcpa_limits = guardrails_summary['target_cpa_limits']
                st.write(f"• Min Value: ${tcpa_limits['min_value']}")
                st.write(f"• Max Value: ${tcpa_limits['max_value']}")
                st.write(f"• Min Conversions: {tcpa_limits['min_conversions']}")
                st.write(f"• Frequency: {tcpa_limits['max_frequency_days']} days")
    
    def _display_recommendations(self, recommendations):
        """Display optimization recommendations."""
        st.subheader("💡 Optimization Recommendations")
        
        # Group recommendations by priority
        high_priority = [r for r in recommendations if r["priority"] == "High"]
        medium_priority = [r for r in recommendations if r["priority"] == "Medium"]
        low_priority = [r for r in recommendations if r["priority"] == "Low"]
        
        # High Priority
        if high_priority:
            st.markdown("### 🔴 High Priority (Fix Immediately)")
            for i, rec in enumerate(high_priority, 1):
                with st.expander(f"{i}. {rec['recommendation']}"):
                    st.markdown(f"**Issue:** {rec['issue']}")
                    st.markdown(f"**Impact:** {rec['impact']}")
                    st.markdown(f"**Category:** {rec['category']}")
        
        # Medium Priority
        if medium_priority:
            st.markdown("### 🟡 Medium Priority (Important)")
            for i, rec in enumerate(medium_priority, 1):
                with st.expander(f"{i}. {rec['recommendation']}"):
                    st.markdown(f"**Issue:** {rec['issue']}")
                    st.markdown(f"**Impact:** {rec['impact']}")
                    st.markdown(f"**Category:** {rec['category']}")
        
        # Low Priority
        if low_priority:
            st.markdown("### 🟢 Low Priority (Nice to Have)")
            for i, rec in enumerate(low_priority, 1):
                with st.expander(f"{i}. {rec['recommendation']}"):
                    st.markdown(f"**Issue:** {rec['issue']}")
                    st.markdown(f"**Impact:** {rec['impact']}")
                    st.markdown(f"**Category:** {rec['category']}")
    
    def _display_optimization_actions(self, campaign_data, recommendations):
        """Display optimization actions with guardrails."""
        st.subheader("⚡ Optimization Actions")
        
        if not self.guardrails:
            st.warning("Guardrails not available - actions disabled")
            return
        
        # Budget Optimization
        with st.expander("💰 Budget Optimization"):
            current_budget = campaign_data.get('budget_amount', 0)
            
            col1, col2 = st.columns(2)
            with col1:
                new_budget = st.number_input(
                    "New Daily Budget ($)",
                    min_value=30.0,
                    max_value=250.0,
                    value=current_budget,
                    step=10.0
                )
            
            with col2:
                if st.button("🔍 Check Budget Change"):
                    change_request = {
                        'type': 'budget_adjustment',
                        'new_daily_budget': new_budget
                    }
                    
                    campaign_state = {
                        'daily_budget': current_budget,
                        'last_budget_change_date': None
                    }
                    
                    verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
                    
                    if verdict.approved:
                        st.success("✅ Budget change approved!")
                        st.info(f"Execute after: {verdict.execute_after}")
                    else:
                        st.error("❌ Budget change rejected:")
                        for reason in verdict.reasons:
                            st.error(f"• {reason}")
        
        # Target CPA Optimization
        with st.expander("🎯 Target CPA Optimization"):
            current_tcpa = campaign_data.get('target_cpa', 0)
            total_conversions = self.audit_results["analysis"]["performance"].get("total_conversions", 0)
            
            col1, col2 = st.columns(2)
            with col1:
                new_tcpa = st.number_input(
                    "New Target CPA ($)",
                    min_value=80.0,
                    max_value=350.0,
                    value=current_tcpa if current_tcpa > 0 else 100.0,
                    step=5.0
                )
            
            with col2:
                st.metric("Current Conversions", f"{total_conversions:.0f}")
                
                if st.button("🔍 Check tCPA Change"):
                    change_request = {
                        'type': 'target_cpa_adjustment',
                        'new_target_cpa': new_tcpa
                    }
                    
                    campaign_state = {
                        'target_cpa': current_tcpa,
                        'total_conversions': total_conversions,
                        'last_tcpa_change_date': None
                    }
                    
                    verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
                    
                    if verdict.approved:
                        st.success("✅ Target CPA change approved!")
                        st.info(f"Execute after: {verdict.execute_after}")
                    else:
                        st.error("❌ Target CPA change rejected:")
                        for reason in verdict.reasons:
                            st.error(f"• {reason}")
        
        # Asset Management
        with st.expander("🖼️ Asset Management"):
            st.info("💡 Use the Intelligent Campaign Creator to automatically add assets:")
            st.code("python tools/smart_campaign_manager.py --customer 5426234549 create 'L.R - PMax - General' --goal lead_generation")
        
        # Campaign Status
        with st.expander("⏸️ Campaign Status"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⏸️ Pause Campaign", type="secondary"):
                    change_request = {'type': 'campaign_pause', 'action': 'pause'}
                    campaign_state = {'daily_budget': current_budget}
                    
                    verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
                    
                    if verdict.approved:
                        st.success("✅ Campaign pause approved!")
                        if verdict.alerts:
                            for alert in verdict.alerts:
                                st.warning(f"⚠️ {alert}")
                    else:
                        st.error("❌ Campaign pause rejected:")
                        for reason in verdict.reasons:
                            st.error(f"• {reason}")
            
            with col2:
                if st.button("▶️ Enable Campaign", type="primary"):
                    change_request = {'type': 'campaign_enable', 'action': 'enable'}
                    campaign_state = {'daily_budget': current_budget}
                    
                    verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
                    
                    if verdict.approved:
                        st.success("✅ Campaign enable approved!")
                    else:
                        st.error("❌ Campaign enable rejected:")
                        for reason in verdict.reasons:
                            st.error(f"• {reason}")
        
        # Export Audit Results
        with st.expander("📊 Export Results"):
            if st.button("💾 Download Audit Report"):
                audit_json = json.dumps(self.audit_results, indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=audit_json,
                    file_name=f"campaign_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
