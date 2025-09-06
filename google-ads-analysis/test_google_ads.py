#!/usr/bin/env python3
"""Test Google Ads Integration"""

from google_ads_integration import SimpleGoogleAdsManager
import logging

logging.basicConfig(level=logging.INFO)

try:
    manager = SimpleGoogleAdsManager()
    print('✅ Simple Google Ads Manager initialized successfully')
    
    # Test getting campaign data
    data = manager.get_campaign_data(days=7)  # Get last 7 days
    print(f'✅ Found {len(data)} campaigns')
    
    if data:
        for campaign_id, campaign_data in data.items():
            name = campaign_data['config']['name']
            conversions = campaign_data['cumulative']['total_conversions']
            cost = campaign_data['cumulative']['total_cost']
            print(f'  - {name}: {conversions} conversions, ${cost:.2f} cost')
    else:
        print('No campaign data found')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
