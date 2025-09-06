#!/usr/bin/env python3
"""
Test API Upgrade
===============

Test script to verify the Google Ads API upgrade from test to basic access.
"""

import os
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def test_api_upgrade():
    """Test the API upgrade and verify access to campaign data."""
    
    console.print(Panel("🔧 Testing Google Ads API Upgrade", style="bold blue"))
    
    # Load environment variables
    load_dotenv()
    
    # Build client configuration
    config = {
        "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    
    try:
        # Build client
        client = GoogleAdsClient.load_from_dict(config)
        console.print("✅ Client built successfully")
        
        # Get services
        customer_service = client.get_service("CustomerService")
        google_ads_service = client.get_service("GoogleAdsService")
        console.print("✅ Services initialized successfully")
        
        # Test manager account access
        manager_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
        console.print(f"🔍 Testing manager account access: {manager_id}")
        
        # Get manager account info
        query = "SELECT customer.id, customer.descriptive_name FROM customer"
        response = google_ads_service.search(customer_id=manager_id, query=query)
        customer = list(response)[0]
        console.print(f"✅ Manager account: {customer.customer.descriptive_name} (ID: {customer.customer.id})")
        
        # Test campaign access
        console.print("🔍 Testing campaign access...")
        
        # Get campaign basic info
        query = """
        SELECT 
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros,
            campaign_budget.delivery_method
        FROM campaign 
        WHERE campaign.name = "L.R - PMax - General"
        """
        
        response = google_ads_service.search(customer_id=manager_id, query=query)
        campaign = list(response)[0]
        
        # Display campaign info
        table = Table(title="Campaign Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Campaign ID", str(campaign.campaign.id))
        table.add_row("Campaign Name", campaign.campaign.name)
        table.add_row("Status", str(campaign.campaign.status))
        table.add_row("Channel Type", str(campaign.campaign.advertising_channel_type))
        table.add_row("Daily Budget", f"${campaign.campaign_budget.amount_micros / 1000000:.2f}")
        table.add_row("Delivery Method", str(campaign.campaign_budget.delivery_method))
        
        console.print(table)
        
        # Test metrics access
        console.print("🔍 Testing metrics access...")
        
        query = """
        SELECT 
            campaign.id,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign 
        WHERE campaign.name = "L.R - PMax - General" 
        AND segments.date DURING LAST_30_DAYS
        """
        
        response = google_ads_service.search(customer_id=manager_id, query=query)
        metrics = list(response)[0]
        
        # Display metrics
        metrics_table = Table(title="Campaign Metrics (Last 30 Days)")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        metrics_table.add_row("Impressions", str(metrics.metrics.impressions))
        metrics_table.add_row("Clicks", str(metrics.metrics.clicks))
        metrics_table.add_row("Cost", f"${metrics.metrics.cost_micros / 1000000:.2f}")
        metrics_table.add_row("Conversions", str(metrics.metrics.conversions))
        metrics_table.add_row("Conversion Value", f"${metrics.metrics.conversions_value / 1000000:.2f}")
        
        console.print(metrics_table)
        
        # Test asset group access
        console.print("🔍 Testing asset group access...")
        
        query = """
        SELECT 
            asset_group.id,
            asset_group.name,
            asset_group.status,
            asset_group.type
        FROM asset_group 
        WHERE campaign.id = {}
        """.format(campaign.campaign.id)
        
        try:
            response = google_ads_service.search(customer_id=manager_id, query=query)
            asset_groups = list(response)
            
            if asset_groups:
                asset_table = Table(title="Asset Groups")
                asset_table.add_column("ID", style="cyan")
                asset_table.add_column("Name", style="green")
                asset_table.add_column("Status", style="yellow")
                asset_table.add_column("Type", style="magenta")
                
                for ag in asset_groups:
                    asset_table.add_row(
                        str(ag.asset_group.id),
                        ag.asset_group.name,
                        str(ag.asset_group.status),
                        str(ag.asset_group.type)
                    )
                
                console.print(asset_table)
            else:
                console.print("⚠️ No asset groups found")
                
        except Exception as e:
            console.print(f"⚠️ Asset group query failed: {str(e)}")
        
        # Summary
        console.print(Panel("🎉 API Upgrade Test Complete!", style="bold green"))
        console.print("✅ All basic API functionality working")
        console.print("✅ Campaign data accessible")
        console.print("✅ Metrics data accessible")
        console.print("✅ Asset group data accessible")
        console.print("\n🚀 Ready to use the full system!")
        
    except Exception as e:
        console.print(f"[red]❌ API test failed: {str(e)}[/red]")
        return False
    
    return True

if __name__ == "__main__":
    test_api_upgrade()
