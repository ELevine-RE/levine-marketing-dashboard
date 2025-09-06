#!/usr/bin/env python3
"""
Test Change Tracking
===================

Demonstrate the rolling 4-week change tracking functionality.
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.change_tracker import ChangeTracker

def test_change_tracking():
    """Test and display change tracking functionality."""
    
    print("📈 Change Tracking Test")
    print("=" * 50)
    
    tracker = ChangeTracker()
    
    # Load current data
    try:
        with open('data/unified_data.json', 'r') as f:
            unified_data = json.load(f)
    except FileNotFoundError:
        print("❌ No unified data found. Run collect_unified_data.py first.")
        return
    
    analytics_data = unified_data.get("analytics_data", {})
    ads_data = unified_data.get("ads_data", {})
    unified_metrics = unified_data.get("unified_metrics", {})
    
    # Add current week snapshot
    snapshot = tracker.add_weekly_snapshot(analytics_data, ads_data, unified_metrics)
    
    print("✅ Current Week Snapshot Added:")
    print(f"   Week: {snapshot['week_start']} to {snapshot['week_end']}")
    print(f"   Sessions: {snapshot['metrics']['sessions']}")
    print(f"   Users: {snapshot['metrics']['users']}")
    print(f"   Bounce Rate: {snapshot['metrics']['bounce_rate']:.1f}%")
    print(f"   Session Duration: {snapshot['metrics']['session_duration']:.1f} min")
    
    if snapshot['changes']:
        print("\n⚠️ Changes Detected:")
        for change in snapshot['changes']:
            print(f"   • {change}")
    else:
        print("\n✅ No significant changes detected")
    
    # Show rolling 4 weeks
    weeks = tracker.get_rolling_4_weeks()
    print(f"\n📊 Rolling 4-Week History ({len(weeks)} weeks):")
    
    for i, week in enumerate(weeks):
        is_current = i == len(weeks) - 1
        status = "(Current)" if is_current else ""
        print(f"   Week {i+1}: {week['week_start']} {status}")
        print(f"     Sessions: {week['metrics']['sessions']}")
        print(f"     Users: {week['metrics']['users']}")
        if week['changes']:
            print(f"     Changes: {len(week['changes'])} detected")
        print()
    
    print("🎯 Key Benefits:")
    print("• Track performance week-over-week")
    print("• Identify when metrics break")
    print("• See traffic source changes")
    print("• Monitor engagement trends")
    print("• Detect anomalies automatically")

if __name__ == '__main__':
    test_change_tracking()
