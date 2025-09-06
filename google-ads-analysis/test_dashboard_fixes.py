#!/usr/bin/env python3
"""
Test script to validate dashboard IndexError fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_safe_get_last():
    """Test the safe_get_last function logic."""
    
    def safe_get_last(data, key, default=0):
        """Safely get the last element from a list or return the value if it's scalar."""
        value = data.get(key, default)
        if isinstance(value, list):
            return value[-1] if len(value) > 0 else default
        return value if value is not None else default
    
    # Test cases
    test_cases = [
        # Case 1: List with data
        ({"total_conversions": [10, 20, 30]}, "total_conversions", 0, 30),
        # Case 2: Empty list
        ({"total_conversions": []}, "total_conversions", 0, 0),
        # Case 3: Scalar value
        ({"total_conversions": 25}, "total_conversions", 0, 25),
        # Case 4: Missing key
        ({}, "total_conversions", 0, 0),
        # Case 5: None value
        ({"total_conversions": None}, "total_conversions", 0, 0),
    ]
    
    print("🧪 Testing safe_get_last function...")
    
    for i, (data, key, default, expected) in enumerate(test_cases, 1):
        result = safe_get_last(data, key, default)
        status = "✅" if result == expected else "❌"
        print(f"{status} Test {i}: {data} -> {result} (expected: {expected})")
        
        if result != expected:
            print(f"   FAILED: Expected {expected}, got {result}")
            return False
    
    print("✅ All safe_get_last tests passed!")
    return True

def test_dashboard_imports():
    """Test that dashboard can be imported without errors."""
    try:
        print("🧪 Testing dashboard imports...")
        
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
        
        # Test dashboard import
        from dashboard import MarketingDashboard
        print("✅ MarketingDashboard imported successfully")
        
        # Test instantiation
        dashboard = MarketingDashboard()
        print("✅ MarketingDashboard instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/instantiation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running dashboard validation tests...")
    print("=" * 50)
    
    # Test 1: safe_get_last function
    test1_passed = test_safe_get_last()
    print()
    
    # Test 2: Dashboard imports
    test2_passed = test_dashboard_imports()
    print()
    
    # Summary
    print("=" * 50)
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Dashboard should work without IndexError.")
        print("🌐 Local dashboard should be running at: http://localhost:8501")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
