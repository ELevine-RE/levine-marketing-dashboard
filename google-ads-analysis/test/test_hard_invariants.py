#!/usr/bin/env python3
"""
Unit Tests for Hard Invariant Validation
========================================

Comprehensive test suite for the hard invariant validation system
that enforces critical campaign configuration requirements.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.guardrails import PerformanceMaxGuardrails
from ads.ensure_baseline_config import BaselineConfigValidator

class TestHardInvariants(unittest.TestCase):
    """Test cases for hard invariant validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.guardrails = PerformanceMaxGuardrails()
        self.baseline_validator = BaselineConfigValidator()
    
    def test_conversion_mapping_valid(self):
        """Test valid conversion mapping."""
        campaign_state = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click', 'Time on Site'],  # All others are Secondary
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
            ],
            'targeting_type': 'PRESENCE_ONLY'
        }
        
        result = self.guardrails._check_hard_invariants(campaign_state)
        self.assertTrue(result['passed'])
    
    def test_conversion_mapping_invalid_primary(self):
        """Test invalid primary conversion mapping."""
        campaign_state = {
            'primary_conversions': ['Lead Form Submission', 'Page View'],  # Page View should be secondary
            'secondary_conversions': ['Click', 'Time on Site']
        }
        
        result = self.guardrails._check_hard_invariants(campaign_state)
        self.assertFalse(result['passed'])
        self.assertIn("Page View", result['reasons'][0])
        self.assertIn("Only Lead Form Submission can be Primary", result['reasons'][0])
    
    def test_conversion_mapping_missing_lead_form(self):
        """Test missing Lead Form Submission from primary."""
        campaign_state = {
            'primary_conversions': ['Phone Call'],  # Missing Lead Form Submission
            'secondary_conversions': ['Page View', 'Click']
        }
        
        result = self.guardrails._check_hard_invariants(campaign_state)
        self.assertFalse(result['passed'])
        self.assertIn("Invalid primary conversions: Phone Call", result['reasons'][0])
        self.assertIn("Only Lead Form Submission can be Primary", result['reasons'][0])
    
    def test_url_exclusions_valid(self):
        """Test valid URL exclusions."""
        campaign_state = {
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
            ]
        }
        
        result = self.guardrails._validate_url_exclusions(campaign_state)
        self.assertTrue(result['valid'])
    
    def test_url_exclusions_missing(self):
        """Test missing URL exclusions."""
        campaign_state = {
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/contact/*', '/blog/*'
                # Missing several required exclusions
            ]
        }
        
        result = self.guardrails._validate_url_exclusions(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Missing required URL exclusions", result['reason'])
    
    def test_url_exclusions_extra(self):
        """Test extra URL exclusions."""
        campaign_state = {
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*',
                '/extra-page/*'  # Extra exclusion
            ]
        }
        
        result = self.guardrails._validate_url_exclusions(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Extra URL exclusions found", result['reason'])
        self.assertIn("/extra-page/*", result['reason'])
    
    def test_asset_formats_valid(self):
        """Test valid asset formats."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 1}
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertTrue(result['valid'])
    
    def test_asset_formats_missing_logos(self):
        """Test missing logo formats."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1},  # Missing 4_1 logo
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 1}
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Missing 4:1 logo", result['reason'])
    
    def test_asset_formats_missing_images(self):
        """Test missing image formats."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 2},  # Missing 1_1 images and insufficient 1_91_1
                    'videos': {'vertical': 1}
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Missing 1.91:1 images (need ≥3)", result['reason'])
        self.assertIn("Missing 1:1 images (need ≥3)", result['reason'])
    
    def test_asset_formats_missing_video(self):
        """Test missing video with auto-generation disabled."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 0},
                    'auto_generate_video': False
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Missing vertical video", result['reason'])
    
    def test_asset_formats_auto_generation_enabled(self):
        """Test missing video with auto-generation enabled."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 0},
                    'auto_generate_video': True
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertTrue(result['valid'])
    
    def test_asset_formats_inactive_group(self):
        """Test that inactive asset groups are ignored."""
        campaign_state = {
            'asset_groups': [
                {
                    'active': False,  # Inactive group
                    'logos': {'1_1': 0, '4_1': 0},
                    'images': {'1_91_1': 0, '1_1': 0},
                    'videos': {'vertical': 0}
                }
            ]
        }
        
        result = self.guardrails._validate_asset_formats(campaign_state)
        self.assertTrue(result['valid'])
    
    def test_presence_only_targeting_valid(self):
        """Test valid presence-only targeting."""
        campaign_state = {
            'geo_targeting_type': 'PRESENCE_ONLY',
            'presence_only_exclusions': ['India', 'Pakistan', 'Bangladesh', 'Philippines']
        }
        
        result = self.guardrails._validate_presence_only_targeting(campaign_state)
        self.assertTrue(result['valid'])
    
    def test_presence_only_targeting_wrong_type(self):
        """Test wrong targeting type."""
        campaign_state = {
            'geo_targeting_type': 'LOCATION_BASED',  # Wrong type
            'presence_only_exclusions': ['India', 'Pakistan', 'Bangladesh', 'Philippines']
        }
        
        result = self.guardrails._validate_presence_only_targeting(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Presence-only targeting required", result['reason'])
        self.assertIn("LOCATION_BASED", result['reason'])
    
    def test_presence_only_targeting_missing_exclusions(self):
        """Test missing presence-only exclusions."""
        campaign_state = {
            'geo_targeting_type': 'PRESENCE_ONLY',
            'presence_only_exclusions': ['India', 'Pakistan']  # Missing some exclusions
        }
        
        result = self.guardrails._validate_presence_only_targeting(campaign_state)
        self.assertFalse(result['valid'])
        self.assertIn("Missing presence-only exclusions", result['reason'])
    
    def test_hard_invariants_all_valid(self):
        """Test all hard invariants passing."""
        campaign_state = {
            'primary_conversions': ['Lead Form Submission'],  # Only Lead Form Submission can be Primary
            'secondary_conversions': ['Phone Call', 'Page View', 'Click'],  # All others are Secondary
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
            ],
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 1}
                }
            ],
            'targeting_type': 'PRESENCE_ONLY',
            'presence_only_exclusions': ['India', 'Pakistan', 'Bangladesh', 'Philippines']
        }
        
        result = self.guardrails._check_hard_invariants(campaign_state)
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['reasons']), 0)
    
    def test_hard_invariants_multiple_failures(self):
        """Test multiple hard invariant failures."""
        campaign_state = {
            'primary_conversions': ['Page View'],  # Invalid primary
            'secondary_conversions': ['Click'],
            'url_exclusions': ['/buyers/*'],  # Missing exclusions
            'asset_groups': [
                {
                    'name': 'Test Group',
                    'status': 'ENABLED',
                    'active': True,
                    'logos': {'1_1': 0},  # Missing logos
                    'images': {'1_91_1': 1},  # Missing images
                    'videos': {'vertical': 0}
                }
            ],
            'targeting_type': 'LOCATION_BASED',  # Wrong type
            'presence_only_exclusions': []
        }
        
        result = self.guardrails._check_hard_invariants(campaign_state)
        self.assertFalse(result['passed'])
        self.assertGreater(len(result['reasons']), 0)
        
        # Check that all failure reasons are included
        reasons_text = ' '.join(result['reasons'])
        self.assertIn("Invalid primary conversions", reasons_text)
        self.assertIn("Missing required URL exclusions", reasons_text)
        self.assertIn("Asset group 'Test Group' missing:", reasons_text)
        self.assertIn("Targeting type must be PRESENCE_ONLY", reasons_text)
    
    def test_baseline_validator_hard_invariants(self):
        """Test baseline validator hard invariant validation."""
        campaign_info = {
            'primary_conversions': ['Lead Form Submission', 'Phone Call'],
            'secondary_conversions': ['Page View', 'Click'],
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', '/contact/*',
                '/blog/*', '/property-search/*', '/idx/*', '/privacy/*', '/about/*'
            ],
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 1, '4_1': 1},
                    'images': {'1_91_1': 3, '1_1': 3},
                    'videos': {'vertical': 1}
                }
            ],
            'geo_targeting_type': 'PRESENCE_ONLY',
            'presence_only_exclusions': ['India', 'Pakistan', 'Bangladesh', 'Philippines']
        }
        
        result = self.baseline_validator.validate_hard_invariants(campaign_info)
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['issues']), 0)
    
    def test_baseline_validator_conversion_mapping(self):
        """Test baseline validator conversion mapping validation."""
        campaign_info = {
            'primary_conversions': ['Page View'],  # Invalid
            'secondary_conversions': ['Click']
        }
        
        result = self.baseline_validator._validate_conversion_mapping_hard(campaign_info)
        self.assertFalse(result['valid'])
        self.assertIn("Page View", result['issue'])
    
    def test_baseline_validator_url_exclusions(self):
        """Test baseline validator URL exclusions validation."""
        campaign_info = {
            'url_exclusions': ['/buyers/*', '/sellers/*']  # Missing many required
        }
        
        result = self.baseline_validator._validate_url_exclusions_hard(campaign_info)
        self.assertFalse(result['valid'])
        self.assertIn("Missing required URL exclusions", result['issue'])
    
    def test_baseline_validator_asset_formats(self):
        """Test baseline validator asset formats validation."""
        campaign_info = {
            'asset_groups': [
                {
                    'active': True,
                    'logos': {'1_1': 0, '4_1': 0},  # Missing logos
                    'images': {'1_91_1': 1, '1_1': 1},  # Insufficient images
                    'videos': {'vertical': 0}
                }
            ]
        }
        
        result = self.baseline_validator._validate_asset_formats_hard(campaign_info)
        self.assertFalse(result['valid'])
        self.assertIn("Asset format requirements not met", result['issue'])
    
    def test_baseline_validator_presence_only(self):
        """Test baseline validator presence-only validation."""
        campaign_info = {
            'geo_targeting_type': 'LOCATION_BASED',  # Wrong type
            'presence_only_exclusions': []
        }
        
        result = self.baseline_validator._validate_presence_only_hard(campaign_info)
        self.assertFalse(result['valid'])
        self.assertIn("Presence-only targeting required", result['issue'])
    
    def test_guardrail_integration_with_hard_invariants(self):
        """Test that guardrails reject changes when hard invariants fail."""
        change_request = {
            'type': 'budget_adjustment',
            'new_daily_budget': 50.0
        }
        
        campaign_state = {
            'daily_budget': 40.0,
            'last_budget_change': '2024-01-01T00:00:00',
            'primary_conversions': ['Page View'],  # Invalid - should cause rejection
            'secondary_conversions': ['Click'],
            'url_exclusions': ['/buyers/*'],
            'asset_groups': [],
            'geo_targeting_type': 'LOCATION_BASED',
            'presence_only_exclusions': []
        }
        
        verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
        self.assertFalse(verdict.approved)
        self.assertGreater(len(verdict.reasons), 0)
        
        # Check that hard invariant failure reasons are included
        reasons_text = ' '.join(verdict.reasons)
        self.assertIn("Invalid primary conversions", reasons_text)

if __name__ == '__main__':
    unittest.main()
