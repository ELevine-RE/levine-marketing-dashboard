#!/usr/bin/env python3
"""
Simple Page Feed Checker
========================

Uses our existing Google Ads Manager to verify the Performance Max campaign's page feed configuration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_ads_manager import GoogleAdsManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_page_feed():
    """Check the Performance Max campaign's page feed configuration."""
    console.print(Panel("🔍 Checking Page Feed Configuration", style="bold blue"))
    
    try:
        # Use our existing manager
        manager = GoogleAdsManager()
        
        # Get campaign information
        console.print("\n[bold cyan]1. Campaign Information[/bold cyan]")
        
        # Query for the specific campaign
        query = """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.final_url_expansion_opt_out
            FROM campaign
            WHERE campaign.name = 'L.R - PMax - General'
        """
        
        try:
            # Try to find the campaign in the manager account first
            manager_customer_id = "5426234549"
            
            response = manager.google_ads_service.search(
                customer_id=manager_customer_id,
                query=query
            )
            
            campaign = None
            for row in response:
                campaign = row.campaign
                break
            
            if not campaign:
                console.print("❌ Campaign 'L.R - PMax - General' not found in manager account")
                console.print("This might be because:")
                console.print("1. The campaign was created in a different account")
                console.print("2. The campaign name is different")
                console.print("3. The campaign hasn't been created yet")
                return
            
            # Display campaign info
            campaign_table = Table(title="Campaign Details")
            campaign_table.add_column("Property", style="cyan")
            campaign_table.add_column("Value", style="green")
            
            campaign_table.add_row("Campaign ID", str(campaign.id))
            campaign_table.add_row("Name", campaign.name)
            campaign_table.add_row("Status", campaign.status.name)
            campaign_table.add_row("Channel Type", campaign.advertising_channel_type.name)
            campaign_table.add_row("Final URL Expansion Opt-Out", str(campaign.final_url_expansion_opt_out))
            
            console.print(campaign_table)
            
            # Check Final URL Expansion
            final_url_expansion_opt_out = campaign.final_url_expansion_opt_out
            console.print(f"\n[bold]Final URL Expansion Status:[/bold] {'❌ OFF' if final_url_expansion_opt_out else '✅ ON'}")
            
            # 2. Find PAGE_FEED Asset Sets
            console.print("\n[bold cyan]2. PAGE_FEED Asset Sets[/bold cyan]")
            
            asset_query = """
                SELECT
                    asset_set.resource_name,
                    asset_set.id,
                    asset_set.name,
                    asset_set.type
                FROM asset_set
                WHERE asset_set.type = 'PAGE_FEED'
            """
            
            asset_response = manager.google_ads_service.search(
                customer_id=manager_customer_id,
                query=asset_query
            )
            
            page_feed_sets = []
            for row in asset_response:
                page_feed_sets.append(row.asset_set)
            
            if not page_feed_sets:
                console.print("❌ No PAGE_FEED asset sets found")
            else:
                console.print(f"✅ Found {len(page_feed_sets)} PAGE_FEED asset set(s):")
                for asset_set in page_feed_sets:
                    console.print(f"  • {asset_set.name} (ID: {asset_set.id})")
            
            # 3. Check CampaignAssetSet links
            console.print("\n[bold cyan]3. Campaign Asset Set Links[/bold cyan]")
            
            link_query = f"""
                SELECT
                    campaign_asset_set.campaign,
                    campaign_asset_set.asset_set,
                    asset_set.name,
                    asset_set.type
                FROM campaign_asset_set
                WHERE campaign_asset_set.campaign = 'customers/{manager_customer_id}/campaigns/{campaign.id}'
            """
            
            link_response = manager.google_ads_service.search(
                customer_id=manager_customer_id,
                query=link_query
            )
            
            linked_page_feeds = []
            for row in link_response:
                if row.asset_set.type.name == "PAGE_FEED":
                    linked_page_feeds.append(row.asset_set)
                    console.print(f"✅ Linked PAGE_FEED: {row.asset_set.name} (ID: {row.asset_set.id})")
            
            if not linked_page_feeds:
                console.print("❌ No PAGE_FEED AssetSet linked to campaign")
            
            # 4. List URLs in linked PAGE_FEED sets
            if linked_page_feeds:
                console.print("\n[bold cyan]4. Page Feed URLs[/bold cyan]")
                
                for asset_set in linked_page_feeds:
                    console.print(f"\n[bold]Asset Set: {asset_set.name}[/bold]")
                    
                    url_query = f"""
                        SELECT
                            asset_set_asset.asset_set,
                            asset_set_asset.asset,
                            asset.page_feed_asset.page_url,
                            asset.page_feed_asset.labels
                        FROM asset_set_asset
                        WHERE asset_set_asset.asset_set = 'customers/{manager_customer_id}/assetSets/{asset_set.id}'
                        LIMIT 25
                    """
                    
                    url_response = manager.google_ads_service.search(
                        customer_id=manager_customer_id,
                        query=url_query
                    )
                    
                    url_count = 0
                    for row in url_response:
                        url = row.asset.page_feed_asset.page_url
                        labels = list(row.asset.page_feed_asset.labels) if row.asset.page_feed_asset.labels else []
                        if url:
                            console.print(f"  • {url}")
                            if labels:
                                console.print(f"    Labels: {labels}")
                            url_count += 1
                    
                    if url_count == 0:
                        console.print("  (No page URLs found in this asset set)")
                    else:
                        console.print(f"  Total URLs found: {url_count}")
            
            # 5. Check negative locations
            console.print("\n[bold cyan]5. Negative Locations[/bold cyan]")
            
            location_query = f"""
                SELECT
                    campaign_criterion.campaign,
                    campaign_criterion.type,
                    campaign_criterion.negative,
                    campaign_criterion.location.geo_target_constant
                FROM campaign_criterion
                WHERE campaign_criterion.campaign = 'customers/{manager_customer_id}/campaigns/{campaign.id}'
                AND campaign_criterion.type = 'LOCATION'
                AND campaign_criterion.negative = true
            """
            
            location_response = manager.google_ads_service.search(
                customer_id=manager_customer_id,
                query=location_query
            )
            
            negative_locations = []
            for row in location_response:
                negative_locations.append(row.campaign_criterion.location.geo_target_constant)
            
            console.print(f"Found {len(negative_locations)} negative location(s)")
            for location in negative_locations:
                console.print(f"  • {location}")
            
            # Summary
            console.print("\n[bold cyan]=== Summary ===[/bold cyan]")
            console.print(f"Final URL Expansion: {'✅ ON' if not final_url_expansion_opt_out else '❌ OFF'}")
            console.print(f"PAGE_FEED Asset Sets: {'✅ Found' if page_feed_sets else '❌ None'}")
            console.print(f"PAGE_FEED Linked to Campaign: {'✅ Yes' if linked_page_feeds else '❌ No'}")
            console.print(f"Page URLs Available: {'✅ Yes' if linked_page_feeds else '❌ No'}")
            console.print(f"Negative Locations: {len(negative_locations)}")
            
        except Exception as e:
            console.print(f"[red]Error accessing campaign data: {e}[/red]")
            console.print("\n[bold yellow]Note:[/bold yellow] The campaign might not exist yet or there might be permission issues.")
            console.print("Try running the campaign creation script first: python pmax_campaign_creator.py")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    check_page_feed()
