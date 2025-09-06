#!/usr/bin/env python3
"""
Unit Tests for Conversion Hygiene in Phase Manager
==================================================

Comprehensive test suite for conversion hygiene validation
that ensures only Primary conversions count for phase gates.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.phase_manager import CampaignPhaseManager, CampaignPhase

class TestConversionHygiene(unittest.TestCase):
    """Test cases for conversion hygiene validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.phase_manager = CampaignPhaseManager()
        
        # Sample metrics with valid conversion mapping
        self.valid_metrics = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'primary_conversions_count': 35,
            'secondary_conversions_count': 150,
            'campaign_age_days': 20,
            'cpl_7d': 120.0,
            'cpl_30d': 125.0,
            'days_since_last_change': 10,
            'current_cpl': 110.0,
            'days_under_tcpa': 35,
            'lead_quality_percent': 8.0,
            'current_pacing': 0.9
        }
    
    def test_conversion_hygiene_valid(self):
        """Test valid conversion mapping."""
        result = self.phase_manager._validate_conversion_hygiene(self.valid_metrics)
        self.assertTrue(result['valid'])
    
    def test_conversion_hygiene_invalid_primary(self):
        """Test invalid primary conversion mapping."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = ['Lead Form Submission', 'Page View']  # Page View should be secondary
        
        result = self.phase_manager._validate_conversion_hygiene(invalid_metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Page View", result['reason'])
        self.assertIn("Only Lead Form Submission can be Primary", result['reason'])
    
    def test_conversion_hygiene_missing_lead_form(self):
        """Test missing Lead Form Submission from primary."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = ['Phone Call']  # Missing Lead Form Submission
        
        result = self.phase_manager._validate_conversion_hygiene(invalid_metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid primary conversions: Phone Call", result['reason'])
        self.assertIn("Only Lead Form Submission can be Primary", result['reason'])
    
    def test_conversion_hygiene_empty_primary(self):
        """Test empty primary conversions list."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = []
        
        result = self.phase_manager._validate_conversion_hygiene(invalid_metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Lead Form Submission must be marked as Primary conversion", result['reason'])
    
    def test_phase_1_eligibility_with_primary_conversions_only(self):
        """Test that only primary conversions count for phase 1 eligibility."""
        # Valid metrics with sufficient primary conversions
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions_count'] = 35  # Above 30 requirement
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        self.assertTrue(result.eligible_for_next)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertTrue(result.details['conversion_hygiene_ok'])
        self.assertEqual(result.details['primary_conversions'], 35)
        self.assertEqual(result.details['secondary_conversions'], 150)
    
    def test_phase_1_eligibility_insufficient_primary_conversions(self):
        """Test phase 1 eligibility with insufficient primary conversions."""
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions_count'] = 25  # Below 30 requirement
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Insufficient primary conversions: 25/30", result.details['blocking_factors'][0])
        self.assertIn("primary_conversions", result.details)
        self.assertEqual(result.details['primary_conversions'], 25)
    
    def test_phase_1_eligibility_conversion_hygiene_failure(self):
        """Test phase 1 eligibility with conversion hygiene failure."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = ['Page View']  # Invalid primary
        
        result = self.phase_manager.check_phase_eligibility(invalid_metrics, CampaignPhase.PHASE_1.value)
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Fix conversion mapping", result.recommended_action)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertFalse(result.details['conversion_hygiene_ok'])
        self.assertIn("conversion_hygiene_reason", result.details)
    
    def test_phase_2_eligibility_with_conversion_hygiene(self):
        """Test phase 2 eligibility includes conversion hygiene validation."""
        metrics = self.valid_metrics.copy()
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_2.value)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertTrue(result.details['conversion_hygiene_ok'])
    
    def test_phase_2_eligibility_conversion_hygiene_failure(self):
        """Test phase 2 eligibility with conversion hygiene failure."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = ['Click']  # Invalid primary
        
        result = self.phase_manager.check_phase_eligibility(invalid_metrics, CampaignPhase.PHASE_2.value)
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Fix conversion mapping", result.recommended_action)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertFalse(result.details['conversion_hygiene_ok'])
    
    def test_phase_3_status_with_conversion_hygiene(self):
        """Test phase 3 status includes conversion hygiene validation."""
        metrics = self.valid_metrics.copy()
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_3.value)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertTrue(result.details['conversion_hygiene_ok'])
    
    def test_phase_3_status_conversion_hygiene_failure(self):
        """Test phase 3 status with conversion hygiene failure."""
        invalid_metrics = self.valid_metrics.copy()
        invalid_metrics['primary_conversions'] = ['Time on Site']  # Invalid primary
        
        result = self.phase_manager.check_phase_eligibility(invalid_metrics, CampaignPhase.PHASE_3.value)
        self.assertFalse(result.eligible_for_next)
        self.assertIn("Fix conversion mapping", result.recommended_action)
        self.assertIn("conversion_hygiene_ok", result.details)
        self.assertFalse(result.details['conversion_hygiene_ok'])
    
    def test_secondary_conversions_logged_but_not_used(self):
        """Test that secondary conversions are logged but not used for phase gates."""
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions_count'] = 35  # Sufficient primary
        metrics['secondary_conversions_count'] = 500  # High secondary, shouldn't affect eligibility
        
        result = self.phase_manager.check_phase_eligibility(metrics, CampaignPhase.PHASE_1.value)
        self.assertTrue(result.eligible_for_next)
        self.assertEqual(result.details['primary_conversions'], 35)
        self.assertEqual(result.details['secondary_conversions'], 500)  # Logged but not used
    
    def test_conversion_hygiene_with_phone_call_not_allowed(self):
        """Test that Phone Call is NOT allowed as primary conversion."""
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions'] = ['Lead Form Submission', 'Phone Call']
        
        result = self.phase_manager._validate_conversion_hygiene(metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Phone Call", result['reason'])
        self.assertIn("Only Lead Form Submission can be Primary", result['reason'])
    
    def test_conversion_hygiene_with_only_phone_call(self):
        """Test that Phone Call alone is not sufficient (needs Lead Form Submission)."""
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions'] = ['Phone Call']  # Missing Lead Form Submission
        
        result = self.phase_manager._validate_conversion_hygiene(metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid primary conversions: Phone Call", result['reason'])
        self.assertIn("Only Lead Form Submission can be Primary", result['reason'])
    
    def test_conversion_hygiene_with_extra_allowed_primary(self):
        """Test that extra allowed primary conversions don't cause issues."""
        metrics = self.valid_metrics.copy()
        metrics['primary_conversions'] = ['Lead Form Submission', 'Lead Form Submission']  # Duplicate allowed
        
        result = self.phase_manager._validate_conversion_hygiene(metrics)
        self.assertTrue(result['valid'])
    
    def test_conversion_hygiene_missing_metrics(self):
        """Test conversion hygiene with missing metrics."""
        metrics = {}
        
        result = self.phase_manager._validate_conversion_hygiene(metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Lead Form Submission must be marked as Primary conversion", result['reason'])
    
    def test_conversion_hygiene_none_values(self):
        """Test conversion hygiene with None values."""
        metrics = {
            'primary_conversions': None,
            'secondary_conversions': None
        }
        
        result = self.phase_manager._validate_conversion_hygiene(metrics)
        self.assertFalse(result['valid'])
        self.assertIn("Lead Form Submission must be marked as Primary conversion", result['reason'])

if __name__ == '__main__':
    unittest.main()
