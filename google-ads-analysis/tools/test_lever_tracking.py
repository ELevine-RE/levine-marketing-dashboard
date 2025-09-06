#!/usr/bin/env python3
"""
Test Lever Tracking
==================

Demonstrate the lever tracking functionality.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.lever_tracker import LeverTracker

def test_lever_tracking():
    """Test and display lever tracking functionality."""
    
    print("🔧 Lever Tracking Test")
    print("=" * 50)
    
    tracker = LeverTracker()
    
    # Add sample levers for demonstration
    print("📝 Adding sample lever pulls...")
    tracker.add_sample_levers()
    
    # Show recent levers
    recent_levers = tracker.get_recent_levers(28)
    print(f"\n✅ Found {len(recent_levers)} levers pulled in last 4 weeks:")
    
    for lever in recent_levers:
        print(f"   • {lever['lever_type'].replace('_', ' ').title()}: {lever['old_value']} → {lever['new_value']}")
        print(f"     Date: {lever['date']} | Reason: {lever['reason']}")
        print()
    
    # Show levers by type
    budget_levers = tracker.get_levers_by_type('budget')
    tcpa_levers = tracker.get_levers_by_type('tCPA')
    
    print("📊 Lever Summary:")
    print(f"   Budget changes: {len(budget_levers)}")
    print(f"   tCPA changes: {len(tcpa_levers)}")
    print(f"   Total changes: {len(recent_levers)}")
    
    print("\n🎯 Key Benefits:")
    print("• Track every lever pulled")
    print("• See what changed and when")
    print("• Understand why changes were made")
    print("• Correlate changes with performance")
    print("• Maintain change history")

if __name__ == '__main__':
    test_lever_tracking()
