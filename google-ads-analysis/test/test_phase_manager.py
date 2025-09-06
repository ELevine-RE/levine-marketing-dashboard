#!/usr/bin/env python3
"""
Unit Tests for Google Ads Phase Manager
======================================

Comprehensive test suite for the CampaignPhaseManager class.
Tests phase eligibility and progress tracking.
"""

import os
import sys
import unittest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.phase_manager import CampaignPhaseManager, PhaseEligibilityResult, PhaseProgressResult, CampaignPhase

class TestCampaignPhaseManager(unittest.TestCase):
    """Test cases for CampaignPhaseManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.phase_manager = CampaignPhaseManager()
        
        # Sample metrics for testing
        self.sample_phase_1_metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'primary_conversions_count': 35,
            'secondary_conversions_count': 150,
            'total_conversions': 35,  # Keep for backward compatibility
            'campaign_age_days': 20,
            'cpl_7d': 95.0,
            'cpl_30d': 100.0,
            'days_since_last_change': 10
        }
        
        self.sample_phase_2_metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'primary_conversions_count': 50,
            'secondary_conversions_count': 200,
            'days_under_tcpa': 35,
            'current_cpl': 120.0,
            'lead_quality_percent': 6.0,
            'current_pacing': 0.85
        }
    
    def test_phase_1_eligibility_with_sufficient_conversions(self):
        """Test Phase 1 eligibility with ≥30 conversions in ≥14 days."""
        metrics = self.sample_phase_1_metrics.copy()
        metrics['primary_conversions_count'] = 35
        metrics['total_conversions'] = 35  # Keep for backward compatibility
        metrics['campaign_age_days'] = 20
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        
        self.assertTrue(result.eligible_for_next)
        self.assertIn("Safe to introduce tCPA at $100-$150", result.recommended_action)
        self.assertEqual(len(result.details['blocking_factors']), 0)
    
    def test_phase_1_eligibility_insufficient_conversions(self):
        """Test Phase 1 eligibility with <30 conversions."""
        metrics = self.sample_phase_1_metrics.copy()
        metrics['primary_conversions_count'] = 25  # Below minimum of 30
        metrics['total_conversions'] = 25  # Keep for backward compatibility
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Insufficient primary conversions: 25/30", result.details['blocking_factors'][0])
        self.assertIn("Continue Phase 1 optimization", result.recommended_action)
    
    def test_phase_1_eligibility_campaign_too_new(self):
        """Test Phase 1 eligibility with campaign too new."""
        metrics = self.sample_phase_1_metrics.copy()
        metrics['campaign_age_days'] = 10  # Below minimum of 14
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Campaign too new: 10/14 days", result.details['blocking_factors'][0])
    
    def test_phase_1_eligibility_cpl_unstable(self):
        """Test Phase 1 eligibility with unstable CPL."""
        metrics = self.sample_phase_1_metrics.copy()
        metrics['cpl_7d'] = 80.0
        metrics['cpl_30d'] = 120.0  # 33.3% difference, above 20% threshold
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("CPL unstable: 33.3% variation", result.details['blocking_factors'][0])
    
    def test_phase_1_eligibility_recent_changes(self):
        """Test Phase 1 eligibility with recent changes."""
        metrics = self.sample_phase_1_metrics.copy()
        metrics['days_since_last_change'] = 5  # Below minimum of 7
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Recent changes detected: 5 days ago", result.details['blocking_factors'][0])
    
    def test_phase_2_eligibility_sufficient_tcpa_time(self):
        """Test Phase 2 eligibility with ≥30 days under tCPA."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['days_under_tcpa'] = 35  # Above minimum of 30
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertTrue(result.eligible_for_next)
        self.assertIn("Safe to scale budget by +20-30%", result.recommended_action)
        self.assertEqual(len(result.details['blocking_factors']), 0)
    
    def test_phase_2_eligibility_insufficient_tcpa_time(self):
        """Test Phase 2 eligibility with <30 days under tCPA."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['days_under_tcpa'] = 25  # Below minimum of 30
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Insufficient tCPA time: 25/30 days", result.details['blocking_factors'][0])
    
    def test_phase_2_eligibility_cpl_too_low(self):
        """Test Phase 2 eligibility with CPL too low."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['current_cpl'] = 70.0  # Below minimum of 80
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("CPL too low: $70.00 (min $80.00)", result.details['blocking_factors'][0])
    
    def test_phase_2_eligibility_cpl_too_high(self):
        """Test Phase 2 eligibility with CPL too high."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['current_cpl'] = 160.0  # Above maximum of 150
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("CPL too high: $160.00 (max $150.00)", result.details['blocking_factors'][0])
    
    def test_phase_2_eligibility_low_lead_quality(self):
        """Test Phase 2 eligibility with low lead quality."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['lead_quality_percent'] = 3.0  # Below minimum of 5.0
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Low lead quality: 3.0% (min 5.0% of leads tagged as 'serious')", result.details['blocking_factors'][0])
    
    def test_phase_2_eligibility_pacing_constrained(self):
        """Test Phase 2 eligibility with constrained pacing."""
        metrics = self.sample_phase_2_metrics.copy()
        metrics['current_pacing'] = 0.7  # Below minimum of 0.8
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Pacing constrained: 70.0% (min 80.0%)", result.details['blocking_factors'][0])
    
    def test_phase_3_status_optimization_focus(self):
        """Test Phase 3 status focuses on optimization."""
        metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'current_cpl': 140.0,
            'current_pacing': 0.9,
            'lead_quality_percent': 6.0
        }
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_3.value)
        
        self.assertFalse(result.eligible_for_next)  # Phase 3 is final
        self.assertIn("Phase 3 optimization", result.recommended_action)
    
    def test_phase_3_status_high_cpl_opportunity(self):
        """Test Phase 3 status identifies high CPL opportunity."""
        metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'current_cpl': 160.0,  # Above 150 threshold
            'current_pacing': 0.9,
            'lead_quality_percent': 6.0
        }
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_3.value)
        
        self.assertIn("High CPL - consider tCPA adjustment", result.details['optimization_opportunities'][0])
    
    def test_phase_3_status_pacing_constrained_opportunity(self):
        """Test Phase 3 status identifies pacing constraint opportunity."""
        metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'current_cpl': 120.0,
            'current_pacing': 0.7,  # Below 0.8 threshold
            'lead_quality_percent': 6.0
        }
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_3.value)
        
        self.assertIn("Pacing constrained - consider budget increase", result.details['optimization_opportunities'][0])
    
    def test_phase_progress_within_expected_days(self):
        """Test phase progress within expected days."""
        start_date = date.today() - timedelta(days=15)
        today = date.today()
        eligibility = {'eligible_for_next': False}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertFalse(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 15)
        self.assertIn("Phase progressing normally", result.message)
    
    def test_phase_progress_within_grace_period(self):
        """Test phase progress within grace period."""
        start_date = date.today() - timedelta(days=24)  # 3 days past expected (21)
        today = date.today()
        eligibility = {'eligible_for_next': False}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertFalse(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 24)
        self.assertIn("within grace period", result.message)
    
    def test_phase_progress_lagging_but_within_max(self):
        """Test phase progress lagging but within max days."""
        start_date = date.today() - timedelta(days=30)  # 9 days past expected (21)
        today = date.today()
        eligibility = {'eligible_for_next': False}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 30)
        self.assertIn("Phase lagging", result.message)
    
    def test_phase_progress_critical_lag(self):
        """Test phase progress exceeding max days."""
        start_date = date.today() - timedelta(days=40)  # 5 days past max (35)
        today = date.today()
        eligibility = {
            'eligible_for_next': False,
            'details': {
                'blocking_factors': ['Insufficient conversions', 'CPL unstable']
            }
        }
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertTrue(result.lag_alert)
        self.assertEqual(result.days_in_phase, 40)
        self.assertIn("🚨 CRITICAL ALERT", result.message)
        self.assertIn("Blocking factors: Insufficient conversions, CPL unstable", result.message)
    
    def test_phase_progress_eligible_but_lagging(self):
        """Test phase progress when eligible but lagging."""
        start_date = date.today() - timedelta(days=30)
        today = date.today()
        eligibility = {'eligible_for_next': True}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertIn("Phase lagging but eligible for next phase", result.message)
    
    def test_phase_progress_eligible_and_critical_lag(self):
        """Test phase progress when eligible but critical lag."""
        start_date = date.today() - timedelta(days=40)
        today = date.today()
        eligibility = {'eligible_for_next': True}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertTrue(result.lag_alert)
        self.assertIn("⚠️ CRITICAL: Phase exceeded maximum duration", result.message)
        self.assertIn("Proceed immediately", result.message)
    
    def test_phase_progress_custom_timeline(self):
        """Test phase progress with custom timeline."""
        start_date = date.today() - timedelta(days=25)
        today = date.today()
        eligibility = {'eligible_for_next': False}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_1.value, eligibility,
            expected_days=20, max_days=30
        )
        
        self.assertTrue(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 25)
        self.assertIn("5 days past expected completion", result.message)
    
    def test_phase_progress_phase_2_timeline(self):
        """Test phase progress with Phase 2 timeline."""
        start_date = date.today() - timedelta(days=50)
        today = date.today()
        eligibility = {'eligible_for_next': False}
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_2.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 50)
        self.assertIn("5 days past expected completion", result.message)
    
    def test_phase_progress_phase_2_critical_lag(self):
        """Test phase progress with Phase 2 critical lag."""
        start_date = date.today() - timedelta(days=75)
        today = date.today()
        eligibility = {
            'eligible_for_next': False,
            'details': {
                'blocking_factors': ['Low lead quality', 'Pacing constrained']
            }
        }
        
        result = self.phase_manager.check_phase_progress(
            start_date, today, CampaignPhase.PHASE_2.value, eligibility
        )
        
        self.assertTrue(result.lagging)
        self.assertTrue(result.lag_alert)
        self.assertEqual(result.days_in_phase, 75)
        self.assertIn("🚨 CRITICAL ALERT", result.message)
        self.assertIn("Blocking factors: Low lead quality, Pacing constrained", result.message)
    
    def test_cpl_stability_calculation(self):
        """Test CPL stability calculation."""
        metrics = {
            'cpl_7d': 90.0,
            'cpl_30d': 100.0
        }
        
        stability = self.phase_manager._calculate_cpl_stability(metrics)
        
        self.assertEqual(stability, 10.0)  # 10% difference
    
    def test_cpl_stability_zero_30d_cpl(self):
        """Test CPL stability with zero 30-day CPL."""
        metrics = {
            'cpl_7d': 90.0,
            'cpl_30d': 0.0
        }
        
        stability = self.phase_manager._calculate_cpl_stability(metrics)
        
        self.assertEqual(stability, 0.0)
    
    def test_cpl_stability_missing_data(self):
        """Test CPL stability with missing data."""
        metrics = {}
        
        stability = self.phase_manager._calculate_cpl_stability(metrics)
        
        self.assertEqual(stability, 0.0)
    
    def test_get_phase_defaults(self):
        """Test getting phase defaults."""
        phase_1_defaults = self.phase_manager._get_phase_defaults('phase_1')
        self.assertEqual(phase_1_defaults['expected_days'], 21)
        self.assertEqual(phase_1_defaults['max_days'], 35)
        
        phase_2_defaults = self.phase_manager._get_phase_defaults('phase_2')
        self.assertEqual(phase_2_defaults['expected_days'], 45)
        self.assertEqual(phase_2_defaults['max_days'], 70)
        
        phase_3_defaults = self.phase_manager._get_phase_defaults('phase_3')
        self.assertEqual(phase_3_defaults['expected_days'], 90)
        self.assertEqual(phase_3_defaults['max_days'], 365)
        
        unknown_defaults = self.phase_manager._get_phase_defaults('unknown_phase')
        self.assertEqual(unknown_defaults['expected_days'], 30)
        self.assertEqual(unknown_defaults['max_days'], 60)
    
    def test_unknown_phase_handling(self):
        """Test handling of unknown phase."""
        # Include valid conversion hygiene data so it passes that check
        metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site']  # All others are Secondary
        }
        
        result = self.phase_manager.check_phase_eligibility(metrics, 'unknown_phase')
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Unknown phase: unknown_phase", result.recommended_action)
        self.assertIn("error", result.details)
    
    def test_error_handling_in_eligibility_check(self):
        """Test error handling in eligibility check."""
        # Pass invalid metrics to trigger error
        result = self.phase_manager.check_phase_eligibility(None, CampaignPhase.PHASE_1.value)
        
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Error checking eligibility", result.recommended_action)
        self.assertIn("error", result.details)
    
    def test_error_handling_in_progress_check(self):
        """Test error handling in progress check."""
        # Pass invalid dates to trigger error
        result = self.phase_manager.check_phase_progress(
            "invalid_date", "invalid_date", CampaignPhase.PHASE_1.value, {}
        )
        
        self.assertFalse(result.lagging)
        self.assertFalse(result.lag_alert)
        self.assertEqual(result.days_in_phase, 0)
        self.assertIn("Error checking phase progress", result.message)
    
    def test_phase_summary_returns_all_settings(self):
        """Test that get_phase_summary returns all settings."""
        summary = self.phase_manager.get_phase_summary()
        
        self.assertIn('phase_1_requirements', summary)
        self.assertIn('phase_2_requirements', summary)
        self.assertIn('phase_timelines', summary)
        self.assertIn('grace_period_days', summary)
    
    def test_result_to_dict_conversion(self):
        """Test that PhaseEligibilityResult converts to dictionary correctly."""
        result = PhaseEligibilityResult(
            eligible_for_next=True,
            recommended_action="Test action",
            details={'test': 'value'}
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict['eligible_for_next'], True)
        self.assertEqual(result_dict['recommended_action'], "Test action")
        self.assertEqual(result_dict['details'], {'test': 'value'})
    
    def test_progress_result_to_dict_conversion(self):
        """Test that PhaseProgressResult converts to dictionary correctly."""
        result = PhaseProgressResult(
            lagging=True,
            lag_alert=False,
            days_in_phase=25,
            message="Test message"
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict['lagging'], True)
        self.assertEqual(result_dict['lag_alert'], False)
        self.assertEqual(result_dict['days_in_phase'], 25)
        self.assertEqual(result_dict['message'], "Test message")

if __name__ == '__main__':
    unittest.main()
