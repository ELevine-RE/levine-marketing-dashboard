#!/usr/bin/env python3
"""
Test Impact Analysis
===================

Demonstrate the impact analysis functionality.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.impact_analyzer import ImpactAnalyzer
from tools.change_tracker import ChangeTracker

def test_impact_analysis():
    """Test and display impact analysis functionality."""
    
    print("📊 Impact Analysis Test")
    print("=" * 50)
    
    # First, let's add some sample performance data that shows impact
    print("📝 Adding sample performance data...")
    add_sample_performance_data()
    
    # Now analyze impacts
    analyzer = ImpactAnalyzer()
    analyses = analyzer.analyze_all_levers()
    
    print(f"\n✅ Analyzed {len(analyses)} lever impacts:")
    
    for analysis in analyses:
        lever = analysis['lever']
        impact = analysis['impact']
        significance = analysis['significance']
        recommendation = analysis['recommendation']
        
        print(f"\n🔧 {lever['lever_type'].replace('_', ' ').title()}:")
        print(f"   Change: {lever['old_value']} → {lever['new_value']}")
        print(f"   Date: {lever['date']}")
        print(f"   Significance: {significance}")
        print(f"   Recommendation: {recommendation}")
        
        if impact:
            print("   📈 Impact on Metrics:")
            for metric, data in impact.items():
                if metric in ['sessions', 'users', 'bounce_rate', 'session_duration', 'roas', 'conversion_rate']:
                    direction = "🟢" if data['direction'] == 'positive' else "🔴" if data['direction'] == 'negative' else "🟡"
                    print(f"     • {metric}: {data['change_pct']:+.1f}% {direction}")
    
    print("\n🎯 Key Benefits:")
    print("• Quantifies impact of each lever pull")
    print("• Shows correlation between changes and performance")
    print("• Provides actionable recommendations")
    print("• Reduces noise by focusing on significant changes")
    print("• Helps identify which levers work best")

def add_sample_performance_data():
    """Add sample performance data that shows impact of lever pulls."""
    
    # Create sample performance data that shows impact
    sample_data = [
        # Before budget increase (Sept 1)
        {
            "week_start": "2025-08-25",
            "week_end": "2025-08-31",
            "timestamp": "2025-08-28T12:00:00",
            "metrics": {
                "sessions": 35,
                "users": 18,
                "bounce_rate": 55.0,
                "session_duration": 7.5,
                "roas": 0,
                "conversion_rate": 2.5
            }
        },
        # After budget increase (Sept 1)
        {
            "week_start": "2025-09-01",
            "week_end": "2025-09-07",
            "timestamp": "2025-09-04T12:00:00",
            "metrics": {
                "sessions": 47,  # +34% increase
                "users": 25,    # +39% increase
                "bounce_rate": 53.2,  # -3% improvement
                "session_duration": 8.0,  # +7% improvement
                "roas": 0,
                "conversion_rate": 3.0  # +20% improvement
            }
        }
    ]
    
    # Save to change history
    os.makedirs('data', exist_ok=True)
    with open('data/change_history.json', 'w') as f:
        json.dump(sample_data, f, indent=2)

if __name__ == '__main__':
    test_impact_analysis()
