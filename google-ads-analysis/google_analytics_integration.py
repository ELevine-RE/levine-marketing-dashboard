"""
Google Analytics Integration for Dashboard
=========================================

This module provides integration with Google Analytics Data API (GA4)
to fetch real website traffic and conversion data.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter
)
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class SimpleGoogleAnalyticsManager:
    """Simplified Google Analytics Manager for Dashboard Integration"""
    
    def __init__(self, property_id: Optional[str] = None):
        """Initialize the Google Analytics Manager."""
        load_dotenv()
        
        self.property_id = property_id or os.environ.get("GOOGLE_ANALYTICS_PROPERTY_ID")
        if not self.property_id:
            raise ValueError("Google Analytics Property ID is required")
            
        # Set up credentials
        self._setup_credentials()
        
        # Initialize the client with explicit credentials
        if hasattr(self, '_credentials') and self._credentials:
            try:
                # Create client with explicit credentials and disable default auth
                from google.auth.transport.requests import Request
                from google.auth.transport.grpc import AuthMetadataPlugin
                
                # Refresh credentials to ensure they're valid
                self._credentials.refresh(Request())
                
                # Create client with explicit credentials
                self.client = BetaAnalyticsDataClient(credentials=self._credentials)
                logger.info("✅ Google Analytics client initialized with explicit credentials")
            except Exception as e:
                logger.error(f"❌ Failed to initialize client with explicit credentials: {e}")
                # Fallback to default client
                self.client = BetaAnalyticsDataClient()
        else:
            self.client = BetaAnalyticsDataClient()
    
    def _setup_credentials(self):
        """Set up Google Analytics credentials."""
        # Try JSON string first (for Streamlit Cloud)
        credentials_json = os.environ.get("GOOGLE_ANALYTICS_CREDENTIALS_JSON")
        if credentials_json:
            try:
                import json
                import tempfile
                from google.oauth2 import service_account
                
                # Parse JSON and create credentials object
                creds_data = json.loads(credentials_json)
                
                # Create temporary file for credentials
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(creds_data, f)
                    temp_file = f.name
                
                # Set environment variable
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file
                
                # Store credentials for direct use
                self._credentials = service_account.Credentials.from_service_account_file(
                    temp_file,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                
                logger.info("✅ Using JSON credentials from environment")
                return
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse JSON credentials: {e}")
        
        # Try file path (for local development)
        credentials_file = os.environ.get("GOOGLE_ANALYTICS_CREDENTIALS_FILE")
        if credentials_file and os.path.exists(credentials_file):
            try:
                from google.oauth2 import service_account
                
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file
                self._credentials = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                logger.info("✅ Using credentials file")
                return
            except Exception as e:
                logger.warning(f"⚠️ Failed to load credentials file: {e}")
        
        # No credentials found
        logger.warning("⚠️ No Google Analytics credentials found")
        self._credentials = None
        
    def get_website_traffic_data(self, days: int = 30) -> Dict:
        """Fetch website traffic data from Google Analytics."""
        logger.info(f"🌐 Fetching Google Analytics traffic data for last {days} days")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Request for daily traffic metrics
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration")
                ],
                date_ranges=[DateRange(start_date=str(start_date), end_date=str(end_date))],
            )
            
            response = self.client.run_report(request)
            
            # Process the response
            traffic_data = {
                "dates": [],
                "sessions": [],
                "users": [],
                "pageviews": [],
                "bounce_rate": [],
                "avg_session_duration": []
            }
            
            for row in response.rows:
                traffic_data["dates"].append(row.dimension_values[0].value)
                traffic_data["sessions"].append(int(row.metric_values[0].value))
                traffic_data["users"].append(int(row.metric_values[1].value))
                traffic_data["pageviews"].append(int(row.metric_values[2].value))
                traffic_data["bounce_rate"].append(float(row.metric_values[3].value))
                traffic_data["avg_session_duration"].append(float(row.metric_values[4].value))
            
            logger.info(f"✅ Successfully fetched traffic data for {len(traffic_data['dates'])} days")
            return traffic_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching traffic data: {e}")
            return {"error": str(e)}
    
    def get_conversion_data(self, days: int = 30) -> Dict:
        """Fetch conversion data from Google Analytics."""
        logger.info(f"🎯 Fetching Google Analytics conversion data for last {days} days")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Request for conversion events
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="conversions"),
                    Metric(name="totalRevenue"),
                    Metric(name="purchaseRevenue")
                ],
                date_ranges=[DateRange(start_date=str(start_date), end_date=str(end_date))],
            )
            
            response = self.client.run_report(request)
            
            # Process the response
            conversion_data = {
                "dates": [],
                "conversions": [],
                "revenue": [],
                "purchase_revenue": []
            }
            
            for row in response.rows:
                conversion_data["dates"].append(row.dimension_values[0].value)
                conversion_data["conversions"].append(int(row.metric_values[0].value))
                conversion_data["revenue"].append(float(row.metric_values[1].value))
                conversion_data["purchase_revenue"].append(float(row.metric_values[2].value))
            
            logger.info(f"✅ Successfully fetched conversion data for {len(conversion_data['dates'])} days")
            return conversion_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching conversion data: {e}")
            return {"error": str(e)}
    
    def get_traffic_sources(self, days: int = 30) -> Dict:
        """Fetch traffic sources data from Google Analytics."""
        logger.info(f"📊 Fetching Google Analytics traffic sources for last {days} days")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Request for traffic sources
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="sessionDefaultChannelGrouping")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers")
                ],
                date_ranges=[DateRange(start_date=str(start_date), end_date=str(end_date))],
            )
            
            response = self.client.run_report(request)
            
            # Process the response
            sources_data = {}
            total_sessions = 0
            
            for row in response.rows:
                source = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                users = int(row.metric_values[1].value)
                
                sources_data[source] = {
                    "sessions": sessions,
                    "users": users
                }
                total_sessions += sessions
            
            # Calculate percentages
            for source in sources_data:
                sources_data[source]["percentage"] = (
                    sources_data[source]["sessions"] / total_sessions * 100
                    if total_sessions > 0 else 0
                )
            
            logger.info(f"✅ Successfully fetched traffic sources data")
            return sources_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching traffic sources: {e}")
            return {"error": str(e)}
    
    def get_analytics_data(self, days: int = 30) -> Dict:
        """Get comprehensive Google Analytics data."""
        logger.info(f"📈 Fetching comprehensive Google Analytics data for last {days} days")
        
        try:
            # Fetch all data types
            traffic_data = self.get_website_traffic_data(days)
            conversion_data = self.get_conversion_data(days)
            sources_data = self.get_traffic_sources(days)
            
            # Check for errors
            if "error" in traffic_data:
                return {"error": f"Traffic data error: {traffic_data['error']}"}
            if "error" in conversion_data:
                return {"error": f"Conversion data error: {conversion_data['error']}"}
            if "error" in sources_data:
                return {"error": f"Sources data error: {sources_data['error']}"}
            
            # Combine all data
            analytics_data = {
                "website_traffic": traffic_data,
                "conversions": conversion_data,
                "traffic_sources": sources_data,
                "summary": {
                    "total_sessions": sum(traffic_data["sessions"]),
                    "total_users": sum(traffic_data["users"]),
                    "total_pageviews": sum(traffic_data["pageviews"]),
                    "avg_bounce_rate": np.mean(traffic_data["bounce_rate"]),
                    "avg_session_duration": np.mean(traffic_data["avg_session_duration"]),
                    "total_conversions": sum(conversion_data["conversions"]),
                    "total_revenue": sum(conversion_data["revenue"])
                }
            }
            
            logger.info("✅ Successfully fetched comprehensive Google Analytics data")
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching comprehensive analytics data: {e}")
            return {"error": str(e)}
