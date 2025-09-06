#!/usr/bin/env python3
"""
Traffic Sources Test
===================

Show what traffic sources data should display.
"""

import json

def test_traffic_sources():
    """Test and display traffic sources data."""
    
    print("📊 Traffic Sources Analysis")
    print("=" * 50)
    
    # Load the data
    with open('data/google_analytics_data.json', 'r') as f:
        data = json.load(f)
    
    traffic_sources = data.get('traffic_sources', {})
    
    if not traffic_sources:
        print("❌ No traffic sources data found")
        return
    
    print("✅ Traffic Sources Found:")
    print()
    
    total_sessions = sum(traffic_sources.values())
    
    for source_medium, sessions in traffic_sources.items():
        percentage = (sessions / total_sessions) * 100
        source, medium = source_medium.split('/', 1) if '/' in source_medium else (source_medium, 'direct')
        
        print(f"🔸 {source} / {medium}")
        print(f"   Sessions: {sessions} ({percentage:.1f}%)")
        print()
    
    print("📈 Key Insights:")
    print(f"• Total Sessions: {total_sessions}")
    print(f"• Direct Traffic: {traffic_sources.get('(direct)/(none)', 0)} sessions")
    print(f"• Organic Search: {traffic_sources.get('google/organic', 0)} sessions")
    print(f"• Paid Traffic: {traffic_sources.get('google/cpc', 0)} sessions")
    print(f"• Referral Traffic: {sum([v for k, v in traffic_sources.items() if 'referral' in k])} sessions")
    
    print()
    print("🎨 Heat Map Features:")
    print("• Color intensity based on session volume")
    print("• Source and medium breakdown")
    print("• Session count display")
    print("• Interactive hover effects")

if __name__ == '__main__':
    test_traffic_sources()
