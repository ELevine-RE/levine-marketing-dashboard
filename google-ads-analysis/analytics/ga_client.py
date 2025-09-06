#!/usr/bin/env python3
"""
Google Analytics API Client
===========================

Handles Google Analytics data collection and processing.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.auth import default

class GoogleAnalyticsClient:
    """Client for Google Analytics Data API."""
    
    def __init__(self):
        """Initialize the GA client."""
        self.credentials, self.project = default()
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        self.property_id = os.environ.get('GOOGLE_ANALYTICS_PROPERTY_ID')
        
        if not self.property_id:
            raise ValueError("GOOGLE_ANALYTICS_PROPERTY_ID environment variable required")
    
    def get_summary_metrics(self, days: int = 30) -> Dict:
        """Get summary metrics for the specified period."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
            metrics=[
                Metric(name="sessions"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="conversions"),
            ],
        )
        
        response = self.client.run_report(request)
        
        if not response.rows:
            return self._empty_summary()
        
        row = response.rows[0]
        return {
            "total_sessions": int(row.metric_values[0].value),
            "total_users": int(row.metric_values[1].value),
            "total_page_views": int(row.metric_values[2].value),
            "avg_bounce_rate": float(row.metric_values[3].value),
            "avg_session_duration": float(row.metric_values[4].value),
            "total_goals": int(row.metric_values[5].value),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    def get_traffic_sources(self, days: int = 30) -> Dict:
        """Get traffic sources breakdown."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
            dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
            metrics=[Metric(name="sessions")],
        )
        
        response = self.client.run_report(request)
        
        traffic_sources = {}
        for row in response.rows:
            source = row.dimension_values[0].value
            medium = row.dimension_values[1].value
            sessions = int(row.metric_values[0].value)
            
            source_medium = f"{source}/{medium}"
            traffic_sources[source_medium] = sessions
        
        return traffic_sources
    
    def get_top_pages(self, days: int = 30, limit: int = 10) -> Dict:
        """Get top pages by page views."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews")],
            limit=limit
        )
        
        response = self.client.run_report(request)
        
        top_pages = {}
        for row in response.rows:
            page = row.dimension_values[0].value
            views = int(row.metric_values[0].value)
            top_pages[page] = views
        
        return top_pages
    
    def get_daily_trends(self, days: int = 30) -> Dict:
        """Get daily trends for the period."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date.isoformat(), end_date=end_date.isoformat())],
            dimensions=[Dimension(name="date")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
            ],
        )
        
        response = self.client.run_report(request)
        
        daily_trends = {}
        for row in response.rows:
            date = row.dimension_values[0].value
            daily_trends[date] = {
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
                "page_views": int(row.metric_values[2].value),
                "goals": int(row.metric_values[3].value)
            }
        
        return daily_trends
    
    def _empty_summary(self) -> Dict:
        """Return empty summary when no data available."""
        return {
            "total_sessions": 0,
            "total_users": 0,
            "total_page_views": 0,
            "avg_bounce_rate": 0,
            "avg_session_duration": 0,
            "total_goals": 0,
            "date_range": {
                "start": (datetime.now() - timedelta(days=30)).date().isoformat(),
                "end": datetime.now().date().isoformat()
            }
        }
