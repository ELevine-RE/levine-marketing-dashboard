#!/usr/bin/env python3
"""
Unit Tests for Google Ads Guardrails
===================================

Comprehensive test suite for the PerformanceMaxGuardrails class.
Tests all guardrail rules and edge cases.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.guardrails import PerformanceMaxGuardrails, GuardrailVerdict, ChangeType

class TestPerformanceMaxGuardrails(unittest.TestCase):
    """Test cases for PerformanceMaxGuardrails class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.guardrails = PerformanceMaxGuardrails()
        
        # Sample campaign state for testing
        self.sample_campaign_state = {
            'daily_budget': 50.0,
            'target_cpa': 120.0,
            'total_conversions': 35,
            'recent_7d_spend': 350.0,
            'recent_7d_conversions': 5,
            'days_since_last_conversion': 3,
            'last_budget_change_date': (datetime.now() - timedelta(days=10)).isoformat(),
            'last_tcpa_change_date': (datetime.now() - timedelta(days=20)).isoformat(),
            'last_major_change_date': (datetime.now() - timedelta(days=8)).isoformat(),
            # Hard invariants
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click'],  # All others are Secondary
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
            ],
            'targeting_type': 'PRESENCE_ONLY',
            'presence_only_exclusions': ['India', 'Pakistan', 'Bangladesh', 'Philippines'],
            'asset_groups': [
                {
                    'name': 'Main Group',
                    'status': 'ENABLED',
                    'active': True,
                    'asset_counts': {
                        'headlines': 6,
                        'long_headlines': 1,
                        'descriptions': 3,
                        'business_name': 1,
                        'logos_1_1': 1,
                        'logos_4_1': 1,
                        'images_1_91_1': 4,
                        'images_1_1': 3,
                        'videos': 1
                    },
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 4, '1_1': 3},
                    'videos': {'vertical': 1}
                }
            ]
        }
    
    def test_budget_change_outside_30_percent_rejected(self):
        """Test that budget changes outside ±30% are rejected."""
        # Test budget increase > 30%
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 80.0  # 60% increase from 50
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Budget adjustment 60.0% exceeds maximum 30%", verdict.reasons[0])
        self.assertIsNotNone(verdict.modified_change)
        self.assertEqual(verdict.modified_change['new_daily_budget'], 65.0)  # Max allowed increase
    
    def test_budget_below_minimum_rejected(self):
        """Test that budget below minimum is rejected."""
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 20.0  # Below minimum of 30
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Budget $20.00 below minimum $30.00", verdict.reasons[0])
    
    def test_budget_above_maximum_rejected(self):
        """Test that budget above maximum is rejected."""
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 150.0  # Above maximum of 100
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Budget $150.00 above maximum $100.00", verdict.reasons[0])
    
    def test_budget_change_too_frequent_rejected(self):
        """Test that budget changes too frequently are rejected."""
        # Set last budget change to 3 days ago (less than 7 required)
        self.sample_campaign_state['last_budget_change_date'] = (datetime.now() - timedelta(days=3)).isoformat()
        
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0  # Valid amount
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Budget changed 3 days ago (minimum 7 days)", verdict.reasons[0])
    
    def test_valid_budget_change_approved(self):
        """Test that valid budget changes are approved."""
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0  # 20% increase, within limits
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertTrue(verdict.approved)
        self.assertIn("Budget adjustment meets all guardrail requirements", verdict.reasons[0])
        self.assertIsNotNone(verdict.execute_after)
    
    def test_tcpa_set_with_less_than_30_conversions_rejected(self):
        """Test that tCPA changes with <30 conversions are rejected."""
        # Set conversions to 25 (below minimum of 30)
        self.sample_campaign_state['total_conversions'] = 25
        
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 100.0
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Only 25 conversions (minimum 30)", verdict.reasons[0])
    
    def test_tcpa_below_minimum_rejected(self):
        """Test that tCPA below minimum is rejected."""
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 60.0  # Below minimum of 80
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Target CPA $60.00 below minimum $80.00", verdict.reasons[0])
    
    def test_tcpa_above_maximum_rejected(self):
        """Test that tCPA above maximum is rejected."""
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 250.0  # Above maximum of 200
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Target CPA $250.00 above maximum $200.00", verdict.reasons[0])
    
    def test_tcpa_adjustment_too_large_rejected(self):
        """Test that tCPA adjustments >15% are rejected."""
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 150.0  # 25% increase from 120
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("tCPA adjustment 25.0% exceeds maximum 15%", verdict.reasons[0])
        self.assertIsNotNone(verdict.modified_change)
        self.assertEqual(verdict.modified_change['new_target_cpa'], 138.0)  # Max allowed increase
    
    def test_tcpa_change_too_frequent_rejected(self):
        """Test that tCPA changes too frequently are rejected."""
        # Set last tCPA change to 10 days ago (less than 14 required)
        self.sample_campaign_state['last_tcpa_change_date'] = (datetime.now() - timedelta(days=10)).isoformat()
        
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 110.0  # Valid amount
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("tCPA changed 10 days ago (minimum 14 days)", verdict.reasons[0])
    
    def test_valid_tcpa_change_approved(self):
        """Test that valid tCPA changes are approved."""
        change_request = {
            'type': ChangeType.TARGET_CPA_ADJUSTMENT.value,
            'new_target_cpa': 110.0  # 8.3% decrease, within limits
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertTrue(verdict.approved)
        self.assertIn("Target CPA adjustment meets all guardrail requirements", verdict.reasons[0])
        self.assertIsNotNone(verdict.execute_after)
    
    def test_pause_all_asset_groups_rejected(self):
        """Test that pausing all asset groups is rejected."""
        change_request = {
            'type': ChangeType.ASSET_GROUP_MODIFICATION.value,
            'action': 'pause_all'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Cannot pause all asset groups", verdict.reasons[0])
    
    def test_asset_group_missing_required_assets_rejected(self):
        """Test that asset groups missing required assets are rejected."""
        # Create asset group missing required assets
        self.sample_campaign_state['asset_groups'] = [
            {
                'name': 'Incomplete Group',
                'status': 'ENABLED',
                'asset_counts': {
                    'headlines': 2,  # Need 5
                    'long_headlines': 0,  # Need 1
                    'descriptions': 1,  # Need 2
                    'business_name': 0,  # Need 1
                    'logos_1_1': 0,  # Need 1
                    'logos_4_1': 0,  # Need 1
                    'images_1_91_1': 1,  # Need 3
                    'images_1_1': 1,  # Need 3
                    'videos': 0  # Need 1
                }
            }
        ]
        
        change_request = {
            'type': ChangeType.ASSET_GROUP_MODIFICATION.value,
            'action': 'modify_assets'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Asset group 'Incomplete Group' missing:", verdict.reasons[0])
    
    def test_valid_asset_group_change_approved(self):
        """Test that valid asset group changes are approved."""
        change_request = {
            'type': ChangeType.ASSET_GROUP_MODIFICATION.value,
            'action': 'add_assets'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertTrue(verdict.approved)
        self.assertIn("Asset group modification meets all guardrail requirements", verdict.reasons[0])
    
    def test_geo_targeting_non_presence_rejected(self):
        """Test that non-presence geo targeting is rejected."""
        change_request = {
            'type': ChangeType.GEO_TARGETING_MODIFICATION.value,
            'action': 'add_location',
            'location_type': 'interest'  # Not presence
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Location type 'interest' not allowed (presence-only required)", verdict.reasons[0])
    
    def test_geo_targeting_too_frequent_rejected(self):
        """Test that geo targeting changes too frequently are rejected."""
        # Set last geo change to 10 days ago (less than 21 required)
        self.sample_campaign_state['last_geo_change_date'] = (datetime.now() - timedelta(days=10)).isoformat()
        
        change_request = {
            'type': ChangeType.GEO_TARGETING_MODIFICATION.value,
            'action': 'add_location',
            'location_type': 'presence'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Geo targeting changed 10 days ago (minimum 21 days)", verdict.reasons[0])
    
    def test_valid_geo_targeting_change_approved(self):
        """Test that valid geo targeting changes are approved."""
        change_request = {
            'type': ChangeType.GEO_TARGETING_MODIFICATION.value,
            'action': 'add_location',
            'location_type': 'presence'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertTrue(verdict.approved)
        self.assertIn("Geo targeting modification meets all guardrail requirements", verdict.reasons[0])
    
    def test_one_lever_per_week_enforced(self):
        """Test that one lever per week rule is enforced."""
        # Set last major change to 5 days ago (less than 7 required)
        self.sample_campaign_state['last_major_change_date'] = (datetime.now() - timedelta(days=5)).isoformat()
        
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("One lever per week rule: major change 5 days ago (minimum 7 days)", verdict.reasons[0])
    
    def test_safety_stop_loss_overspend_detected(self):
        """Test that safety stop-loss detects overspend with no conversions."""
        # Set overspend condition
        self.sample_campaign_state['recent_7d_spend'] = 120.0  # 2.4x budget
        self.sample_campaign_state['recent_7d_conversions'] = 0
        
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertIn("STOP-LOSS: Spend $120.00 exceeds 2.0x budget", verdict.alerts[0])
    
    def test_safety_stop_loss_conversion_drought_detected(self):
        """Test that safety stop-loss detects conversion drought."""
        # Set conversion drought condition
        self.sample_campaign_state['days_since_last_conversion'] = 15  # >14 days
        
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertIn("STOP-LOSS: No conversions in 15 days - freeze all changes", verdict.alerts[0])
        self.assertFalse(verdict.approved)
    
    def test_change_window_applied_to_approved_changes(self):
        """Test that 2-hour change window is applied to approved changes."""
        change_request = {
            'type': ChangeType.BUDGET_ADJUSTMENT.value,
            'new_daily_budget': 60.0
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertTrue(verdict.approved)
        self.assertIsNotNone(verdict.execute_after)
        
        # Verify execute_after is 2 hours from now
        execute_time = datetime.fromisoformat(verdict.execute_after.replace('Z', '+00:00'))
        expected_time = datetime.now() + timedelta(hours=2)
        
        # Allow 1 minute tolerance for test execution time
        time_diff = abs((execute_time - expected_time).total_seconds())
        self.assertLess(time_diff, 60)
    
    def test_unknown_change_type_rejected(self):
        """Test that unknown change types are rejected."""
        change_request = {
            'type': 'unknown_change_type',
            'some_data': 'value'
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, self.sample_campaign_state)
        
        self.assertFalse(verdict.approved)
        self.assertIn("Unknown change type: unknown_change_type", verdict.reasons[0])
    
    def test_guardrail_summary_returns_all_settings(self):
        """Test that get_guardrail_summary returns all settings."""
        summary = self.guardrails.get_guardrail_summary()
        
        self.assertIn('budget_limits', summary)
        self.assertIn('target_cpa_limits', summary)
        self.assertIn('asset_requirements', summary)
        self.assertIn('geo_targeting_limits', summary)
        self.assertIn('safety_limits', summary)
        self.assertIn('change_window_hours', summary)
        self.assertIn('one_lever_per_week_days', summary)
        self.assertIn('required_url_exclusions', summary)
    
    def test_verdict_to_dict_conversion(self):
        """Test that GuardrailVerdict converts to dictionary correctly."""
        verdict = GuardrailVerdict(
            approved=True,
            modified_change={'test': 'value'},
            reasons=['Reason 1', 'Reason 2'],
            execute_after='2024-01-01T10:00:00',
            alerts=['Alert 1']
        )
        
        verdict_dict = verdict.to_dict()
        
        self.assertEqual(verdict_dict['approved'], True)
        self.assertEqual(verdict_dict['modified_change'], {'test': 'value'})
        self.assertEqual(verdict_dict['reasons'], ['Reason 1', 'Reason 2'])
        self.assertEqual(verdict_dict['execute_after'], '2024-01-01T10:00:00')
        self.assertEqual(verdict_dict['alerts'], ['Alert 1'])

if __name__ == '__main__':
    unittest.main()
