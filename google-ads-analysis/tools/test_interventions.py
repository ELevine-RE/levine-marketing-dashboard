#!/usr/bin/env python3
"""
Test Interventions
=================

Demonstrate the intervention tracking functionality.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.intervention_tracker import InterventionTracker

def test_interventions():
    """Test and display intervention tracking functionality."""
    
    print("⚠️ Intervention Tracking Test")
    print("=" * 50)
    
    tracker = InterventionTracker()
    
    # Add sample interventions for demonstration
    print("📝 Adding sample intervention items...")
    tracker.add_sample_interventions()
    
    # Show pending interventions
    pending_items = tracker.get_pending_interventions()
    print(f"\n✅ Found {len(pending_items)} pending interventions:")
    
    for item in pending_items:
        priority_icon = "🚨" if item['priority'] == 'high' else "⚠️" if item['priority'] == 'medium' else "ℹ️"
        print(f"\n{priority_icon} {item['category']} ({item['priority'].upper()})")
        print(f"   Action: {item['action']}")
        print(f"   Due: {item['due_date'] or 'Flexible'}")
        if item['notes']:
            print(f"   Note: {item['notes']}")
    
    # Show by priority
    high_priority = tracker.get_interventions_by_priority('high')
    medium_priority = tracker.get_interventions_by_priority('medium')
    low_priority = tracker.get_interventions_by_priority('low')
    
    print(f"\n📊 Intervention Summary:")
    print(f"   High Priority: {len(high_priority)} items")
    print(f"   Medium Priority: {len(medium_priority)} items")
    print(f"   Low Priority: {len(low_priority)} items")
    print(f"   Total Pending: {len(pending_items)} items")
    
    print("\n🎯 Key Benefits:")
    print("• Quickly identify what needs manual attention")
    print("• Prioritize tasks by urgency")
    print("• Track non-automated actions")
    print("• Ensure nothing falls through the cracks")
    print("• Focus on high-impact manual tasks")

if __name__ == '__main__':
    test_interventions()
