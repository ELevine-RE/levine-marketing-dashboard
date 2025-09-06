"""
Simple Google Ads Integration for Dashboard
==========================================

This module provides a simplified interface for integrating Google Ads data
into the Streamlit dashboard without complex dependencies.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class SimpleGoogleAdsManager:
    """Simplified Google Ads Manager for Dashboard Integration"""
    
    def __init__(self, customer_id: Optional[str] = None):
        """Initialize the Google Ads Manager."""
        load_dotenv()
        
        self.customer_id = customer_id or os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
        if not self.customer_id:
            raise ValueError("Customer ID is required")
            
        self.client = self._build_client()
        self._initialize_services()
        
    def _build_client(self) -> GoogleAdsClient:
        """Build the Google Ads client using environment variables."""
        config = {
            "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
        
        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}
        
        return GoogleAdsClient.load_from_dict(config)
    
    def _initialize_services(self):
        """Initialize Google Ads services."""
        self.google_ads_service = self.client.get_service("GoogleAdsService")
    
    def get_campaign_data(self, days: int = 30) -> Dict:
        """Get campaign data for the dashboard."""
        logger.info(f"🎯 Fetching Google Ads data for last {days} days")
        
        try:
            # Query for campaign performance data
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.average_cpc,
                    segments.date
                FROM campaign
                WHERE segments.date BETWEEN '{self._get_start_date(days)}' AND '{self._get_end_date()}'
                AND campaign.status = 'ENABLED'
            """
            
            response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=query
            )
            
            # Process the data
            campaigns_data = {}
            daily_data = {}
            
            for row in response:
                campaign_id = str(row.campaign.id)
                campaign_name = row.campaign.name
                date_str = row.segments.date
                
                # Initialize campaign data if not exists
                if campaign_id not in campaigns_data:
                    campaigns_data[campaign_id] = {
                        "config": {
                            "name": campaign_name,
                            "id": campaign_id,
                            "status": row.campaign.status.name,
                            "channel_type": row.campaign.advertising_channel_type.name,
                            "goal_conversions": 30,  # Default goal
                            "goal_cpl": 150,  # Default goal
                            "phase": "phase_1"  # Default phase
                        },
                        "daily": {},
                        "cumulative": {}
                    }
                
                # Store daily data
                daily_data_key = f"{campaign_id}_{date_str}"
                daily_data[daily_data_key] = {
                    "date": date_str,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost": row.metrics.cost_micros / 1_000_000 if row.metrics.cost_micros else 0,
                    "conversions": row.metrics.conversions,
                    "ctr": row.metrics.clicks / row.metrics.impressions if row.metrics.impressions > 0 else 0,
                    "cpc": row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                    "cpl": (row.metrics.cost_micros / 1_000_000) / row.metrics.conversions if row.metrics.conversions > 0 else 0
                }
                
                campaigns_data[campaign_id]["daily"][date_str] = daily_data[daily_data_key]
            
            # Calculate cumulative metrics
            for campaign_id, campaign_data in campaigns_data.items():
                cumulative = self._calculate_cumulative_metrics(campaign_data["daily"])
                campaigns_data[campaign_id]["cumulative"] = cumulative
            
            logger.info(f"✅ Successfully fetched data for {len(campaigns_data)} campaigns")
            return campaigns_data
            
        except GoogleAdsException as e:
            logger.error(f"❌ Google Ads API error: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return {}
    
    def _get_start_date(self, days: int) -> str:
        """Get start date string for the query."""
        start_date = date.today() - timedelta(days=days)
        return start_date.strftime("%Y-%m-%d")
    
    def _get_end_date(self) -> str:
        """Get end date string for the query."""
        end_date = date.today()
        return end_date.strftime("%Y-%m-%d")
    
    def _calculate_cumulative_metrics(self, daily_data: Dict) -> Dict:
        """Calculate cumulative metrics from daily data."""
        if not daily_data:
            return {
                "total_impressions": 0,
                "total_clicks": 0,
                "total_cost": 0,
                "total_conversions": 0,
                "avg_ctr": 0,
                "avg_cpc": 0,
                "avg_cpl": 0
            }
        
        # Convert to lists for calculation
        impressions = [data["impressions"] for data in daily_data.values()]
        clicks = [data["clicks"] for data in daily_data.values()]
        costs = [data["cost"] for data in daily_data.values()]
        conversions = [data["conversions"] for data in daily_data.values()]
        
        total_impressions = sum(impressions)
        total_clicks = sum(clicks)
        total_cost = sum(costs)
        total_conversions = sum(conversions)
        
        avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        avg_cpc = total_cost / total_clicks if total_clicks > 0 else 0
        avg_cpl = total_cost / total_conversions if total_conversions > 0 else 0
        
        return {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_cost": total_cost,
            "total_conversions": total_conversions,
            "avg_ctr": avg_ctr,
            "avg_cpc": avg_cpc,
            "avg_cpl": avg_cpl
        }
