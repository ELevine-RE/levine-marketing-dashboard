#!/usr/bin/env python3
"""
Test Unified Dashboard
=====================

Test version that uses mock data to demonstrate the unified dashboard functionality.
"""

import os
import json
from datetime import datetime

def test_unified_dashboard():
    """Test unified dashboard with mock data."""
    
    print("🧪 Testing unified dashboard with mock data...")
    
    # Mock Google Analytics data
    analytics_data = {
        "summary": {
            "total_sessions": 8500,
            "total_users": 7200,
            "total_page_views": 12500,
            "avg_bounce_rate": 45.2,
            "avg_session_duration": 135.5,
            "total_goals": 67,
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-30"
            }
        },
        "traffic_sources": {
            "google / cpc": 2975,
            "google / organic": 3400,
            "(direct) / (none)": 2125
        },
        "top_pages": {
            "/": 3500,
            "/buyers": 2800,
            "/contact": 2200,
            "/sellers": 1800,
            "/about": 1200
        },
        "daily_trends": {
            "2024-01-01": {"sessions": 280, "users": 240, "page_views": 420, "goals": 2},
            "2024-01-02": {"sessions": 295, "users": 250, "page_views": 445, "goals": 3},
            "2024-01-03": {"sessions": 310, "users": 265, "page_views": 465, "goals": 2}
        },
        "collected_at": datetime.now().isoformat()
    }
    
    # Mock Google Ads data
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
    
    # Calculate unified metrics
    unified_metrics = calculate_unified_metrics(ads_data, analytics_data)
    
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
    
    print("✅ Mock data created!")
    print(f"📊 ROAS: ${unified_metrics['roas']:.2f}")
    print(f"🎯 Conversion Rate: {unified_metrics['conversion_rate']:.1f}%")
    print(f"💰 Cost per Session: ${unified_metrics['cost_per_session']:.2f}")
    print(f"📈 Paid Traffic: {unified_metrics['paid_traffic_ratio']:.1f}%")
    
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
    test_unified_dashboard()
