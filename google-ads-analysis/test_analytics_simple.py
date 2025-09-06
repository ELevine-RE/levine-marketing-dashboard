#!/usr/bin/env python3
"""
Test the new simplified Google Analytics integration
"""

import os
from dotenv import load_dotenv
from google_analytics_simple import SimpleGoogleAnalyticsManager

def test_simple_analytics():
    """Test the simplified Google Analytics integration."""
    load_dotenv()
    
    property_id = os.environ.get("GOOGLE_ANALYTICS_PROPERTY_ID")
    credentials_json = os.environ.get("GOOGLE_ANALYTICS_CREDENTIALS_JSON")
    credentials_file = os.environ.get("GOOGLE_ANALYTICS_CREDENTIALS_FILE")
    
    if not property_id:
        print("❌ GOOGLE_ANALYTICS_PROPERTY_ID not set")
        return
    
    if not credentials_json and not credentials_file:
        print("❌ No Google Analytics credentials found")
        return
    
    # If we have a file but no JSON, read the file
    if not credentials_json and credentials_file and os.path.exists(credentials_file):
        import json
        with open(credentials_file, 'r') as f:
            credentials_json = f.read()
        os.environ["GOOGLE_ANALYTICS_CREDENTIALS_JSON"] = credentials_json
    
    try:
        print("🔧 Testing simplified Google Analytics integration...")
        manager = SimpleGoogleAnalyticsManager()
        
        print("📊 Testing traffic data...")
        traffic_data = manager.get_website_traffic_data(days=7)
        
        if "error" in traffic_data:
            print(f"❌ Error: {traffic_data['error']}")
            return
        
        print(f"✅ Successfully fetched {len(traffic_data['dates'])} days of traffic data")
        
        print("📈 Testing traffic sources...")
        sources_data = manager.get_traffic_sources(days=7)
        
        if "error" in sources_data:
            print(f"❌ Error: {sources_data['error']}")
            return
        
        print(f"✅ Successfully fetched {len(sources_data)} traffic sources")
        
        print("🎯 Testing comprehensive data...")
        analytics_data = manager.get_analytics_data(days=7)
        
        if "error" in analytics_data:
            print(f"❌ Error: {analytics_data['error']}")
            return
        
        print("🎉 All tests passed! Google Analytics integration is working!")
        
        # Show sample data
        if traffic_data["dates"]:
            print(f"\n📊 Sample traffic data:")
            for i, date in enumerate(traffic_data["dates"][:3]):
                print(f"   {date}: {traffic_data['sessions'][i]} sessions, {traffic_data['users'][i]} users")
        
        if sources_data:
            print(f"\n📈 Traffic sources:")
            for source, data in list(sources_data.items())[:3]:
                print(f"   {source}: {data['sessions']} sessions ({data['percentage']:.1f}%)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_simple_analytics()
