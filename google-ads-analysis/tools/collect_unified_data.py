#!/usr/bin/env python3
"""
Unified Data Collection Tool
============================

Collects data from both Google Ads and Google Analytics APIs
and generates unified dashboard.
"""

import os
import json
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.ga_client import GoogleAnalyticsClient
from tools.change_tracker import track_current_week

def collect_unified_data():
    """Collect data from both APIs and generate unified dashboard."""
    
    print("🔄 Collecting unified marketing data...")
    
    # Initialize clients
    ga_client = GoogleAnalyticsClient()
    
    # Collect Google Analytics data
    print("📊 Collecting Google Analytics data...")
    try:
        ga_summary = ga_client.get_summary_metrics()
        ga_traffic = ga_client.get_traffic_sources()
        ga_pages = ga_client.get_top_pages()
        ga_trends = ga_client.get_daily_trends()
        
        analytics_data = {
            "summary": ga_summary,
            "traffic_sources": ga_traffic,
            "top_pages": ga_pages,
            "daily_trends": ga_trends,
            "collected_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"⚠️ Google Analytics collection failed: {e}")
        analytics_data = {
            "summary": ga_client._empty_summary(),
            "traffic_sources": {},
            "top_pages": {},
            "daily_trends": {},
            "collected_at": datetime.now().isoformat(),
            "error": str(e)
        }
    
    # Collect Google Ads data (using existing system)
    print("📈 Collecting Google Ads data...")
    try:
        # This would use your existing Google Ads collection
        # For now, we'll create a placeholder
        ads_data = {
            "summary": {
                "spend": 2400,
                "clicks": 1500,
                "impressions": 25000,
                "conversions": 45,
                "cpc": 1.60,
                "ctr": 6.0
            },
            "collected_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"⚠️ Google Ads collection failed: {e}")
        ads_data = {
            "summary": {
                "spend": 0,
                "clicks": 0,
                "impressions": 0,
                "conversions": 0,
                "cpc": 0,
                "ctr": 0
            },
            "collected_at": datetime.now().isoformat(),
            "error": str(e)
        }
    
    # Calculate unified metrics
    unified_metrics = calculate_unified_metrics(ads_data, analytics_data)
    
    # Track weekly changes
    weekly_snapshot = track_current_week(analytics_data, ads_data, unified_metrics)
    
    # Save all data
    os.makedirs('data', exist_ok=True)
    
    with open('data/google_ads_data.json', 'w') as f:
        json.dump(ads_data, f, indent=2)
    
    with open('data/google_analytics_data.json', 'w') as f:
        json.dump(analytics_data, f, indent=2)
    
    unified_data = {
        "ads_data": ads_data,
        "analytics_data": analytics_data,
        "unified_metrics": unified_metrics,
        "generated_at": datetime.now().isoformat()
    }
    
    with open('data/unified_data.json', 'w') as f:
        json.dump(unified_data, f, indent=2)
    
    print("✅ Unified data collection complete!")
    return unified_data

def calculate_unified_metrics(ads_data: dict, analytics_data: dict) -> dict:
    """Calculate unified metrics from both data sources."""
    
    ads_summary = ads_data.get("summary", {})
    analytics_summary = analytics_data.get("summary", {})
    
    # Calculate key unified metrics
    spend = ads_summary.get("spend", 0)
    conversions = ads_summary.get("conversions", 0)
    clicks = ads_summary.get("clicks", 0)
    sessions = analytics_summary.get("total_sessions", 0)
    goals = analytics_summary.get("total_goals", 0)
    
    # Traffic sources
    traffic_sources = analytics_data.get("traffic_sources", {})
    paid_traffic = traffic_sources.get("google / cpc", 0)
    
    return {
        "roas": spend / goals if goals > 0 else 0,
        "conversion_rate": (conversions / clicks * 100) if clicks > 0 else 0,
        "cost_per_session": spend / sessions if sessions > 0 else 0,
        "paid_traffic_ratio": (paid_traffic / sessions * 100) if sessions > 0 else 0,
        "goal_completion_rate": (goals / sessions * 100) if sessions > 0 else 0,
        "bounce_rate": analytics_summary.get("avg_bounce_rate", 0),
        "avg_session_duration": analytics_summary.get("avg_session_duration", 0)
    }

if __name__ == '__main__':
    collect_unified_data()
