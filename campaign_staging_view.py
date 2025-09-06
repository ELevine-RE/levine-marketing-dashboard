#!/usr/bin/env python3
"""
Campaign Staging View
====================

Staging area for campaign changes where you can review and approve them
before they go live. Integrates with guardrails for safety validation.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
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

try:
    from ads.guardrails import PerformanceMaxGuardrails as AdsGuardrails
    HAS_ADS_GUARDRAILS = True
except ImportError as e:
    AdsGuardrails = None
    HAS_ADS_GUARDRAILS = False

class CampaignStagingView:
    """Campaign staging area for reviewing and approving changes."""
    
    def __init__(self):
        self.customer_id = st.session_state.get('customer_id', '5426234549')
        self.staging_file = 'data/campaign_staging.json'
        self.guardrails = None
        
        # Initialize guardrails
        if HAS_ADS_GUARDRAILS:
            try:
                self.guardrails = AdsGuardrails()
            except Exception as e:
                st.warning(f"Could not initialize guardrails: {e}")
        
        # Load existing staging data
        self.staging_data = self._load_staging_data()
    
    def render(self):
        """Render the campaign staging page."""
        st.title("🎭 Campaign Staging Area")
        st.markdown("Review and approve campaign changes before they go live")
        
        # Tabs for different staging areas
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Pending Changes", "💰 Budget Changes", "🎯 Targeting Changes", "🖼️ Asset Changes"])
        
        with tab1:
            self._render_pending_changes()
        
        with tab2:
            self._render_budget_changes()
        
        with tab3:
            self._render_targeting_changes()
        
        with tab4:
            self._render_asset_changes()
    
    def _load_staging_data(self) -> Dict:
        """Load staging data from file."""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'pending_changes': [],
                    'approved_changes': [],
                    'rejected_changes': [],
                    'budget_changes': [],
                    'targeting_changes': [],
                    'asset_changes': []
                }
        except Exception as e:
            st.error(f"Error loading staging data: {e}")
            return {'pending_changes': [], 'approved_changes': [], 'rejected_changes': []}
    
    def _save_staging_data(self):
        """Save staging data to file."""
        try:
            with open(self.staging_file, 'w') as f:
                json.dump(self.staging_data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving staging data: {e}")
    
    def _render_pending_changes(self):
        """Render pending changes tab."""
        st.subheader("📋 Pending Changes")
        
        if not self.staging_data.get('pending_changes'):
            st.info("No pending changes. Create changes in the other tabs.")
            return
        
        for i, change in enumerate(self.staging_data['pending_changes']):
            with st.expander(f"Change {i+1}: {change.get('type', 'Unknown')} - {change.get('campaign_name', 'Unknown Campaign')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Change Details:**")
                    st.json(change.get('change_details', {}))
                
                with col2:
                    st.markdown("**Guardrails Validation:**")
                    if change.get('guardrails_approved'):
                        st.success("✅ Approved by Guardrails")
                    else:
                        st.error("❌ Rejected by Guardrails")
                        for reason in change.get('guardrails_reasons', []):
                            st.error(f"• {reason}")
                
                with col3:
                    st.markdown("**Actions:**")
                    if st.button(f"✅ Approve", key=f"approve_{i}"):
                        self._approve_change(i)
                    if st.button(f"❌ Reject", key=f"reject_{i}"):
                        self._reject_change(i)
                    if st.button(f"📝 Modify", key=f"modify_{i}"):
                        self._modify_change(i)
    
    def _render_budget_changes(self):
        """Render budget changes tab."""
        st.subheader("💰 Budget Changes")
        
        # Current campaign budget
        st.markdown("### Current Campaign Budget")
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.selectbox(
                "Select Campaign",
                ["L.R - PMax - General", "Local Presence", "Feeder Markets"],
                key="budget_campaign_select"
            )
        
        with col2:
            current_budget = st.number_input(
                "Current Daily Budget ($)",
                min_value=30.0,
                max_value=250.0,
                value=105.0,
                step=5.0,
                key="current_budget_input"
            )
        
        # New budget proposal
        st.markdown("### Propose New Budget")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_budget = st.number_input(
                "New Daily Budget ($)",
                min_value=30.0,
                max_value=250.0,
                value=115.0,
                step=5.0,
                key="new_budget_input"
            )
        
        with col2:
            budget_reason = st.selectbox(
                "Reason for Change",
                ["Scale successful campaign", "Optimize performance", "A/B test adjustment", "Seasonal adjustment"],
                key="budget_reason_select"
            )
        
        with col3:
            effective_date = st.date_input(
                "Effective Date",
                value=datetime.now().date() + timedelta(days=1),
                key="budget_effective_date"
            )
        
        # Guardrails validation
        if st.button("🔍 Validate with Guardrails", key="validate_budget"):
            self._validate_budget_change(campaign_name, current_budget, new_budget, budget_reason, effective_date)
        
        # Display existing budget changes
        if self.staging_data.get('budget_changes'):
            st.markdown("### Existing Budget Changes")
            for i, change in enumerate(self.staging_data['budget_changes']):
                with st.expander(f"Budget Change {i+1}: {change.get('campaign_name')} - ${change.get('new_budget')}/day"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.json(change)
                    with col2:
                        if st.button(f"Remove", key=f"remove_budget_{i}"):
                            self._remove_budget_change(i)
    
    def _render_targeting_changes(self):
        """Render targeting changes tab."""
        st.subheader("🎯 Targeting Changes")
        
        st.markdown("### Propose Targeting Changes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.selectbox(
                "Select Campaign",
                ["L.R - PMax - General", "Local Presence", "Feeder Markets"],
                key="targeting_campaign_select"
            )
            
            change_type = st.selectbox(
                "Change Type",
                ["Add Location", "Remove Location", "Adjust Demographics", "Add Negative Keywords"],
                key="targeting_change_type"
            )
        
        with col2:
            if change_type == "Add Location":
                location = st.text_input("Location", placeholder="Park City, UT", key="targeting_location")
                location_type = st.selectbox("Location Type", ["Presence", "Interest"], key="targeting_location_type")
            elif change_type == "Remove Location":
                location = st.text_input("Location to Remove", placeholder="Salt Lake City, UT", key="targeting_remove_location")
            elif change_type == "Adjust Demographics":
                age_range = st.slider("Age Range", 18, 65, (25, 55), key="targeting_age")
                income_range = st.selectbox("Income Range", ["$50k+", "$75k+", "$100k+", "$150k+"], key="targeting_income")
            elif change_type == "Add Negative Keywords":
                negative_keywords = st.text_area("Negative Keywords (one per line)", key="targeting_negative_keywords")
        
        if st.button("🔍 Validate Targeting Change", key="validate_targeting"):
            self._validate_targeting_change(campaign_name, change_type)
    
    def _render_asset_changes(self):
        """Render asset changes tab."""
        st.subheader("🖼️ Asset Changes")
        
        st.markdown("### Propose Asset Changes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.selectbox(
                "Select Campaign",
                ["L.R - PMax - General", "Local Presence", "Feeder Markets"],
                key="asset_campaign_select"
            )
            
            asset_type = st.selectbox(
                "Asset Type",
                ["Images", "Videos", "Text Assets", "Logos"],
                key="asset_type_select"
            )
        
        with col2:
            action = st.selectbox(
                "Action",
                ["Add Assets", "Remove Assets", "Update Assets"],
                key="asset_action_select"
            )
            
            if action == "Add Assets":
                asset_count = st.number_input("Number of Assets to Add", min_value=1, max_value=20, value=5, key="asset_count")
                asset_source = st.selectbox("Asset Source", ["Website Scraping", "Upload", "AI Generated"], key="asset_source")
            elif action == "Remove Assets":
                asset_count = st.number_input("Number of Assets to Remove", min_value=1, max_value=10, value=1, key="asset_remove_count")
            elif action == "Update Assets":
                asset_count = st.number_input("Number of Assets to Update", min_value=1, max_value=10, value=1, key="asset_update_count")
        
        if st.button("🔍 Validate Asset Change", key="validate_asset"):
            self._validate_asset_change(campaign_name, asset_type, action)
    
    def _validate_budget_change(self, campaign_name: str, current_budget: float, new_budget: float, reason: str, effective_date):
        """Validate budget change with guardrails."""
        if not self.guardrails:
            st.error("Guardrails not available")
            return
        
        change_request = {
            'type': 'budget_adjustment',
            'new_daily_budget': new_budget,
            'campaign_name': campaign_name,
            'reason': reason,
            'effective_date': effective_date.isoformat()
        }
        
        campaign_state = {
            'daily_budget': current_budget,
            'last_budget_change_date': None
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
        
        if verdict.approved:
            st.success("✅ Budget change approved by guardrails!")
            st.info(f"Execute after: {verdict.execute_after}")
            
            # Add to staging
            change_details = {
                'type': 'budget_adjustment',
                'campaign_name': campaign_name,
                'current_budget': current_budget,
                'new_budget': new_budget,
                'reason': reason,
                'effective_date': effective_date.isoformat(),
                'guardrails_approved': True,
                'guardrails_reasons': verdict.reasons,
                'execute_after': verdict.execute_after,
                'created_at': datetime.now().isoformat()
            }
            
            self.staging_data['pending_changes'].append(change_details)
            self.staging_data['budget_changes'].append(change_details)
            self._save_staging_data()
            
            st.success("Budget change added to staging area!")
        else:
            st.error("❌ Budget change rejected by guardrails:")
            for reason in verdict.reasons:
                st.error(f"• {reason}")
    
    def _validate_targeting_change(self, campaign_name: str, change_type: str):
        """Validate targeting change with guardrails."""
        if not self.guardrails:
            st.error("Guardrails not available")
            return
        
        change_request = {
            'type': 'geo_targeting_modification',
            'action': change_type.lower().replace(' ', '_'),
            'campaign_name': campaign_name
        }
        
        campaign_state = {
            'last_geo_change_date': None
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
        
        if verdict.approved:
            st.success("✅ Targeting change approved by guardrails!")
            st.info(f"Execute after: {verdict.execute_after}")
            
            # Add to staging
            change_details = {
                'type': 'targeting_modification',
                'campaign_name': campaign_name,
                'change_type': change_type,
                'guardrails_approved': True,
                'guardrails_reasons': verdict.reasons,
                'execute_after': verdict.execute_after,
                'created_at': datetime.now().isoformat()
            }
            
            self.staging_data['pending_changes'].append(change_details)
            self.staging_data['targeting_changes'].append(change_details)
            self._save_staging_data()
            
            st.success("Targeting change added to staging area!")
        else:
            st.error("❌ Targeting change rejected by guardrails:")
            for reason in verdict.reasons:
                st.error(f"• {reason}")
    
    def _validate_asset_change(self, campaign_name: str, asset_type: str, action: str):
        """Validate asset change with guardrails."""
        if not self.guardrails:
            st.error("Guardrails not available")
            return
        
        change_request = {
            'type': 'asset_group_modification',
            'action': action.lower().replace(' ', '_'),
            'campaign_name': campaign_name,
            'asset_type': asset_type
        }
        
        campaign_state = {
            'asset_groups': [{'name': 'Main Group', 'status': 'ENABLED', 'asset_counts': {}}]
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
        
        if verdict.approved:
            st.success("✅ Asset change approved by guardrails!")
            st.info(f"Execute after: {verdict.execute_after}")
            
            # Add to staging
            change_details = {
                'type': 'asset_modification',
                'campaign_name': campaign_name,
                'asset_type': asset_type,
                'action': action,
                'guardrails_approved': True,
                'guardrails_reasons': verdict.reasons,
                'execute_after': verdict.execute_after,
                'created_at': datetime.now().isoformat()
            }
            
            self.staging_data['pending_changes'].append(change_details)
            self.staging_data['asset_changes'].append(change_details)
            self._save_staging_data()
            
            st.success("Asset change added to staging area!")
        else:
            st.error("❌ Asset change rejected by guardrails:")
            for reason in verdict.reasons:
                st.error(f"• {reason}")
    
    def _approve_change(self, index: int):
        """Approve a pending change."""
        change = self.staging_data['pending_changes'].pop(index)
        change['approved_at'] = datetime.now().isoformat()
        change['status'] = 'approved'
        self.staging_data['approved_changes'].append(change)
        self._save_staging_data()
        st.success("Change approved and moved to approved changes!")
        st.rerun()
    
    def _reject_change(self, index: int):
        """Reject a pending change."""
        change = self.staging_data['pending_changes'].pop(index)
        change['rejected_at'] = datetime.now().isoformat()
        change['status'] = 'rejected'
        self.staging_data['rejected_changes'].append(change)
        self._save_staging_data()
        st.success("Change rejected and moved to rejected changes!")
        st.rerun()
    
    def _modify_change(self, index: int):
        """Modify a pending change."""
        st.info("Modify functionality coming soon!")
    
    def _remove_budget_change(self, index: int):
        """Remove a budget change."""
        self.staging_data['budget_changes'].pop(index)
        self._save_staging_data()
        st.success("Budget change removed!")
        st.rerun()
