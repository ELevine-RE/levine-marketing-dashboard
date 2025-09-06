"""
Simplified Google Analytics Integration
======================================

This version uses a different authentication approach that works reliably
on Streamlit Cloud without metadata service issues.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class SimpleGoogleAnalyticsManager:
    """Simplified Google Analytics Manager that works on Streamlit Cloud"""
    
    def __init__(self, property_id: Optional[str] = None):
        """Initialize the Google Analytics Manager."""
        load_dotenv()
        
        self.property_id = property_id or os.environ.get("GOOGLE_ANALYTICS_PROPERTY_ID")
        if not self.property_id:
            raise ValueError("Google Analytics Property ID is required")
            
        # Set up credentials using a different approach
        self._setup_credentials()
        
    def _setup_credentials(self):
        """Set up Google Analytics credentials using service account directly."""
        credentials_json = os.environ.get("GOOGLE_ANALYTICS_CREDENTIALS_JSON")
        if not credentials_json:
            logger.warning("⚠️ No Google Analytics credentials found")
            self._credentials = None
            return
            
        try:
            import tempfile
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            # Parse credentials
            creds_data = json.loads(credentials_json)
            
            # Create credentials object directly from JSON data
            # Handle potential base64 encoding issues
            try:
                self._credentials = service_account.Credentials.from_service_account_info(
                    creds_data,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
            except Exception as e:
                if "base64" in str(e).lower():
                    logger.warning("⚠️ Base64 encoding issue detected, trying alternative approach")
                    # Try creating from file instead
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump(creds_data, f)
                        temp_file = f.name
                    
                    self._credentials = service_account.Credentials.from_service_account_file(
                        temp_file,
                        scopes=['https://www.googleapis.com/auth/analytics.readonly']
                    )
                else:
                    raise e
            
            # Refresh credentials to ensure they're valid
            self._credentials.refresh(Request())
            
            logger.info("✅ Google Analytics credentials initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Analytics credentials: {e}")
            self._credentials = None
    
    def _make_analytics_request(self, metrics: List[str], dimensions: List[str] = None, 
                              start_date: str = None, end_date: str = None) -> Dict:
        """Make a request to Google Analytics Data API."""
        if not self._credentials:
            return {"error": "No valid credentials available"}
            
        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import (
                DateRange, Dimension, Metric, RunReportRequest
            )
            
            # Create client with explicit credentials
            client = BetaAnalyticsDataClient(credentials=self._credentials)
            
            # Build the request
            request_data = {
                "property": f"properties/{self.property_id}",
                "metrics": [Metric(name=metric) for metric in metrics],
                "date_ranges": [DateRange(start_date=start_date, end_date=end_date)]
            }
            
            if dimensions:
                request_data["dimensions"] = [Dimension(name=dim) for dim in dimensions]
            
            request = RunReportRequest(**request_data)
            
            # Make the request
            response = client.run_report(request)
            
            # Process response
            data = {
                "rows": [],
                "dimension_headers": [header.name for header in response.dimension_headers],
                "metric_headers": [header.name for header in response.metric_headers]
            }
            
            for row in response.rows:
                row_data = {
                    "dimensions": [dim.value for dim in row.dimension_values],
                    "metrics": [float(metric.value) for metric in row.metric_values]
                }
                data["rows"].append(row_data)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Analytics API request failed: {e}")
            return {"error": str(e)}
    
    def get_website_traffic_data(self, days: int = 30) -> Dict:
        """Fetch website traffic data from Google Analytics."""
        logger.info(f"🌐 Fetching Google Analytics traffic data for last {days} days")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Make request for daily traffic data
            response = self._make_analytics_request(
                metrics=["sessions", "totalUsers", "screenPageViews", "bounceRate", "averageSessionDuration"],
                dimensions=["date"],
                start_date=str(start_date),
                end_date=str(end_date)
            )
            
            if "error" in response:
                return response
            
            # Process the data
            traffic_data = {
                "dates": [],
                "sessions": [],
                "users": [],
                "pageviews": [],
                "bounce_rate": [],
                "avg_session_duration": []
            }
            
            for row in response["rows"]:
                traffic_data["dates"].append(row["dimensions"][0])
                traffic_data["sessions"].append(int(row["metrics"][0]))
                traffic_data["users"].append(int(row["metrics"][1]))
                traffic_data["pageviews"].append(int(row["metrics"][2]))
                traffic_data["bounce_rate"].append(float(row["metrics"][3]))
                traffic_data["avg_session_duration"].append(float(row["metrics"][4]))
            
            logger.info(f"✅ Successfully fetched traffic data for {len(traffic_data['dates'])} days")
            return traffic_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching traffic data: {e}")
            return {"error": str(e)}
    
    def get_traffic_sources(self, days: int = 30) -> Dict:
        """Fetch traffic sources data from Google Analytics."""
        logger.info(f"📊 Fetching Google Analytics traffic sources for last {days} days")
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Make request for traffic sources
            response = self._make_analytics_request(
                metrics=["sessions", "totalUsers"],
                dimensions=["sessionDefaultChannelGrouping"],
                start_date=str(start_date),
                end_date=str(end_date)
            )
            
            if "error" in response:
                return response
            
            # Process the data
            sources_data = {}
            total_sessions = 0
            
            for row in response["rows"]:
                source = row["dimensions"][0]
                sessions = int(row["metrics"][0])
                users = int(row["metrics"][1])
                
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
            # Fetch traffic data
            traffic_data = self.get_website_traffic_data(days)
            if "error" in traffic_data:
                return traffic_data
            
            # Fetch sources data
            sources_data = self.get_traffic_sources(days)
            if "error" in sources_data:
                return sources_data
            
            # Create comprehensive data structure that matches dashboard expectations
            analytics_data = {
                "website_traffic": traffic_data,
                "traffic_sources": sources_data,
                "conversions": {
                    "dates": traffic_data["dates"],
                    "lead_form_submissions": [0] * len(traffic_data["dates"]),  # Placeholder
                    "phone_calls": [0] * len(traffic_data["dates"]),  # Placeholder
                    "email_signups": [0] * len(traffic_data["dates"])  # Placeholder
                },
                "summary": {
                    "total_sessions": sum(traffic_data["sessions"]),
                    "total_users": sum(traffic_data["users"]),
                    "total_pageviews": sum(traffic_data["pageviews"]),
                    "avg_bounce_rate": np.mean(traffic_data["bounce_rate"]),
                    "avg_session_duration": np.mean(traffic_data["avg_session_duration"]),
                    "total_conversions": 0,  # Placeholder
                    "total_revenue": 0  # Placeholder
                }
            }
            
            logger.info("✅ Successfully fetched comprehensive Google Analytics data")
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching comprehensive analytics data: {e}")
            return {"error": str(e)}
