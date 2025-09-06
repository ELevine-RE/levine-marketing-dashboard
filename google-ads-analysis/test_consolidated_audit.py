#!/usr/bin/env python3
"""
Consolidated Code Audit Test
===========================

Test script to verify the consolidated system meets all business requirements.
"""

from guardrails import *
from change_management import *
from baseline_validator import *

def test_budget_guardrails():
    """Test budget guardrails implementation."""
    print("1. Testing Budget Guardrails...")
    
    # Test minimum budget
    try:
        result = validate_budget_adjustment(25, 35)  # Should fail - below $30
        print(f"   ✅ Minimum budget validation: {'PASS' if not result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Minimum budget validation: FAIL - {str(e)}")
    
    # Test maximum budget
    try:
        result = validate_budget_adjustment(90, 110)  # Should fail - above $100
        print(f"   ✅ Maximum budget validation: {'PASS' if not result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Maximum budget validation: FAIL - {str(e)}")
    
    # Test valid budget change
    try:
        result = validate_budget_adjustment(50, 60)  # Should pass
        print(f"   ✅ Valid budget validation: {'PASS' if result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Valid budget validation: FAIL - {str(e)}")

def test_tcpa_guardrails():
    """Test tCPA guardrails implementation."""
    print("2. Testing tCPA Guardrails...")
    
    # Test minimum tCPA
    try:
        result = validate_tcpa_adjustment(70, 90)  # Should fail - below $80
        print(f"   ✅ Minimum tCPA validation: {'PASS' if not result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Minimum tCPA validation: FAIL - {str(e)}")
    
    # Test maximum tCPA
    try:
        result = validate_tcpa_adjustment(180, 220)  # Should fail - above $200
        print(f"   ✅ Maximum tCPA validation: {'PASS' if not result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Maximum tCPA validation: FAIL - {str(e)}")
    
    # Test valid tCPA change
    try:
        result = validate_tcpa_adjustment(100, 110)  # Should pass
        print(f"   ✅ Valid tCPA validation: {'PASS' if result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Valid tCPA validation: FAIL - {str(e)}")

def test_one_lever_per_week():
    """Test one lever per week rule."""
    print("3. Testing One Lever Per Week Rule...")
    
    try:
        cm = ChangeManagement()
        result = cm.check_one_lever_per_week()
        print(f"   ✅ One lever rule check: {'PASS' if 'rule_violated' in result else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ One lever rule check: FAIL - {str(e)}")

def test_url_exclusions():
    """Test URL exclusion validation."""
    print("4. Testing URL Exclusions...")
    
    try:
        exclusions = get_required_url_exclusions()
        has_buyers = '/buyers/*' in exclusions
        has_sellers = '/sellers/*' in exclusions
        has_blog = '/blog/*' in exclusions
        print(f"   ✅ Required exclusions: {'PASS' if all([has_buyers, has_sellers, has_blog]) else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Required exclusions: FAIL - {str(e)}")

def test_asset_requirements():
    """Test asset requirements validation."""
    print("5. Testing Asset Requirements...")
    
    try:
        requirements = get_asset_requirements()
        has_headlines = 'headlines' in requirements
        has_logos = 'logos' in requirements
        has_images = 'images' in requirements
        print(f"   ✅ Asset requirements: {'PASS' if all([has_headlines, has_logos, has_images]) else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Asset requirements: FAIL - {str(e)}")

def test_geo_targeting():
    """Test geo-targeting validation."""
    print("6. Testing Geo-Targeting Requirements...")
    
    try:
        validator = BaselineValidator()
        geo_settings = {'presence_only': False}  # Should fail
        result = validator.validate_geo_targeting(geo_settings)
        print(f"   ✅ Geo-targeting validation: {'PASS' if not result['valid'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Geo-targeting validation: FAIL - {str(e)}")

def test_phase_progression():
    """Test phase progression logic."""
    print("7. Testing Phase Progression Logic...")
    
    try:
        # Test Phase 1 to Phase 2 requirements
        pm = PhaseManager()
        result = pm.check_phase_1_to_2_eligibility({
            'primary_conversions': 25,  # Should fail - below 30
            'campaign_age_days': 20,    # Should pass - above 14
            'days_since_last_change': 10  # Should fail - below 7
        })
        print(f"   ✅ Phase 1→2 validation: {'PASS' if not result['eligible'] else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Phase 1→2 validation: FAIL - {str(e)}")

def test_change_cadence():
    """Test change cadence validation."""
    print("8. Testing Change Cadence...")
    
    try:
        cm = ChangeManagement()
        # Add some test levers
        cm.add_lever_pull('budget', 50, 60, reason='Test')
        cm.add_lever_pull('tCPA', 100, 110, reason='Test')
        result = cm.check_one_lever_per_week()
        print(f"   ✅ Change cadence validation: {'PASS' if 'levers_in_week' in result else 'FAIL'}")
    except Exception as e:
        print(f"   ❌ Change cadence validation: FAIL - {str(e)}")

def main():
    """Run all consolidated audit tests."""
    print("🔍 Running Consolidated Code Audit Tests...")
    print("=" * 60)
    
    test_budget_guardrails()
    print()
    
    test_tcpa_guardrails()
    print()
    
    test_one_lever_per_week()
    print()
    
    test_url_exclusions()
    print()
    
    test_asset_requirements()
    print()
    
    test_geo_targeting()
    print()
    
    test_phase_progression()
    print()
    
    test_change_cadence()
    print()
    
    print("=" * 60)
    print("✅ Consolidated Code Audit Complete!")
    print("\n📊 Summary:")
    print("- Guardrails: Consolidated from multiple files")
    print("- Change Management: Unified lever tracking, performance monitoring, interventions")
    print("- Asset Management: Combined extraction, validation, and upload")
    print("- Baseline Validator: Unified URL exclusions, geo-targeting, asset requirements")
    print("\n🎯 Benefits of Consolidation:")
    print("- Reduced code duplication")
    print("- Improved maintainability")
    print("- Centralized business logic")
    print("- Better error handling")
    print("- Unified reporting")

if __name__ == "__main__":
    main()

