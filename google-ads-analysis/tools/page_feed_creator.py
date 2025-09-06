#!/usr/bin/env python3
"""
Page Feed Creator
=================

Creates Google Ads page feeds from sitemap URLs.
Integrates with the sitemap parser to automatically generate page feeds.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sitemap_parser import SitemapParser
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class PageFeedCreator:
    """Creates Google Ads page feeds from sitemap URLs."""
    
    def __init__(self, customer_id: str, manager_customer_id: Optional[str] = None):
        self.customer_id = customer_id
        self.manager_customer_id = manager_customer_id or customer_id
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Google Ads client
        try:
            config = {
                "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
                "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
                "use_proto_plus": True,
            }
            
            self.client = GoogleAdsClient.load_from_dict(config)
            self.asset_service = self.client.get_service("AssetService")
            self.asset_set_service = self.client.get_service("AssetSetService")
            self.campaign_asset_set_service = self.client.get_service("CampaignAssetSetService")
            
            logger.info("✅ Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Ads client: {e}")
            raise
    
    def create_page_feed_from_sitemap(self, 
                                    campaign_name: str = "L.R - PMax - General",
                                    max_urls: int = 1000,
                                    asset_set_name: str = "Levine Real Estate Page Feed") -> Dict:
        """Create a page feed from sitemap URLs and link it to a campaign."""
        
        logger.info(f"🚀 Creating page feed from sitemap for campaign: {campaign_name}")
        
        try:
            # Step 1: Get URLs from sitemap
            logger.info("📋 Step 1: Fetching URLs from sitemap...")
            sitemap_parser = SitemapParser()
            urls = sitemap_parser.get_page_feed_urls(max_urls=max_urls)
            
            if not urls:
                return {
                    "success": False,
                    "error": "No URLs found in sitemap",
                    "urls_processed": 0
                }
            
            logger.info(f"✅ Found {len(urls)} URLs from sitemap")
            
            # Step 2: Create asset set
            logger.info("📦 Step 2: Creating asset set...")
            asset_set_id = self.create_asset_set(asset_set_name)
            
            if not asset_set_id:
                return {
                    "success": False,
                    "error": "Failed to create asset set",
                    "urls_processed": 0
                }
            
            # Step 3: Create page feed assets
            logger.info("🔗 Step 3: Creating page feed assets...")
            asset_results = self.create_page_feed_assets(urls, asset_set_id)
            
            # Step 4: Link to campaign
            logger.info("🎯 Step 4: Linking to campaign...")
            campaign_link_result = self.link_to_campaign(campaign_name, asset_set_id)
            
            # Step 5: Generate summary
            result = {
                "success": True,
                "asset_set_id": asset_set_id,
                "asset_set_name": asset_set_name,
                "urls_processed": len(urls),
                "assets_created": asset_results.get("created", 0),
                "assets_failed": asset_results.get("failed", 0),
                "campaign_linked": campaign_link_result.get("success", False),
                "campaign_name": campaign_name,
                "created_at": datetime.now().isoformat(),
                "urls": [url_data["url"] for url_data in urls[:10]]  # First 10 URLs for reference
            }
            
            logger.info(f"✅ Page feed creation completed successfully!")
            logger.info(f"   Asset Set ID: {asset_set_id}")
            logger.info(f"   URLs Processed: {len(urls)}")
            logger.info(f"   Assets Created: {asset_results.get('created', 0)}")
            logger.info(f"   Campaign Linked: {campaign_link_result.get('success', False)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create page feed: {e}")
            return {
                "success": False,
                "error": str(e),
                "urls_processed": 0
            }
    
    def create_asset_set(self, asset_set_name: str) -> Optional[str]:
        """Create a PAGE_FEED asset set."""
        try:
            # Create asset set
            asset_set = self.client.get_type("AssetSet")
            asset_set.name = asset_set_name
            asset_set.type_ = self.client.enums.AssetSetTypeEnum.PAGE_FEED
            
            # Create operation
            asset_set_operation = self.client.get_type("AssetSetOperation")
            asset_set_operation.create = asset_set
            
            # Execute operation
            response = self.asset_set_service.mutate_asset_sets(
                customer_id=self.customer_id,
                operations=[asset_set_operation]
            )
            
            if response.results:
                asset_set_id = response.results[0].resource_name.split('/')[-1]
                logger.info(f"✅ Created asset set: {asset_set_name} (ID: {asset_set_id})")
                return asset_set_id
            
        except GoogleAdsException as e:
            logger.error(f"❌ Google Ads error creating asset set: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error creating asset set: {e}")
        
        return None
    
    def create_page_feed_assets(self, urls: List[Dict], asset_set_id: str) -> Dict:
        """Create page feed assets from URLs."""
        created_count = 0
        failed_count = 0
        
        # Process URLs in batches
        batch_size = 100
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
            
            try:
                # Create assets for this batch
                batch_result = self._create_assets_batch(batch_urls, asset_set_id)
                created_count += batch_result["created"]
                failed_count += batch_result["failed"]
                
            except Exception as e:
                logger.error(f"❌ Failed to process batch {i//batch_size + 1}: {e}")
                failed_count += len(batch_urls)
        
        return {
            "created": created_count,
            "failed": failed_count
        }
    
    def _create_assets_batch(self, urls: List[Dict], asset_set_id: str) -> Dict:
        """Create a batch of page feed assets."""
        created_count = 0
        failed_count = 0
        
        try:
            # Create asset operations
            asset_operations = []
            asset_set_asset_operations = []
            
            for url_data in urls:
                url = url_data["url"]
                
                try:
                    # Create page feed asset
                    page_feed_asset = self.client.get_type("PageFeedAsset")
                    page_feed_asset.page_url = url
                    
                    # Add labels based on priority score
                    if url_data.get("priority_score", 0) > 2.0:
                        page_feed_asset.labels.append("high_priority")
                    elif url_data.get("priority_score", 0) > 1.0:
                        page_feed_asset.labels.append("medium_priority")
                    else:
                        page_feed_asset.labels.append("low_priority")
                    
                    # Create asset
                    asset = self.client.get_type("Asset")
                    asset.page_feed_asset = page_feed_asset
                    asset.name = f"Page Feed: {url}"
                    
                    # Create asset operation
                    asset_operation = self.client.get_type("AssetOperation")
                    asset_operation.create = asset
                    asset_operations.append(asset_operation)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create asset for {url}: {e}")
                    failed_count += 1
            
            # Execute asset operations
            if asset_operations:
                asset_response = self.asset_service.mutate_assets(
                    customer_id=self.customer_id,
                    operations=asset_operations
                )
                
                # Create asset set asset operations
                for i, result in enumerate(asset_response.results):
                    try:
                        asset_set_asset = self.client.get_type("AssetSetAsset")
                        asset_set_asset.asset_set = f"customers/{self.customer_id}/assetSets/{asset_set_id}"
                        asset_set_asset.asset = result.resource_name
                        
                        asset_set_asset_operation = self.client.get_type("AssetSetAssetOperation")
                        asset_set_asset_operation.create = asset_set_asset
                        asset_set_asset_operations.append(asset_set_asset_operation)
                        
                        created_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to link asset to asset set: {e}")
                        failed_count += 1
                
                # Execute asset set asset operations
                if asset_set_asset_operations:
                    self.client.get_service("AssetSetAssetService").mutate_asset_set_assets(
                        customer_id=self.customer_id,
                        operations=asset_set_asset_operations
                    )
        
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            failed_count += len(urls)
        
        return {
            "created": created_count,
            "failed": failed_count
        }
    
    def link_to_campaign(self, campaign_name: str, asset_set_id: str) -> Dict:
        """Link the asset set to a campaign."""
        try:
            # Find campaign
            campaign_resource_name = self._find_campaign(campaign_name)
            if not campaign_resource_name:
                return {
                    "success": False,
                    "error": f"Campaign '{campaign_name}' not found"
                }
            
            # Create campaign asset set
            campaign_asset_set = self.client.get_type("CampaignAssetSet")
            campaign_asset_set.campaign = campaign_resource_name
            campaign_asset_set.asset_set = f"customers/{self.customer_id}/assetSets/{asset_set_id}"
            
            # Create operation
            campaign_asset_set_operation = self.client.get_type("CampaignAssetSetOperation")
            campaign_asset_set_operation.create = campaign_asset_set
            
            # Execute operation
            response = self.campaign_asset_set_service.mutate_campaign_asset_sets(
                customer_id=self.customer_id,
                operations=[campaign_asset_set_operation]
            )
            
            if response.results:
                logger.info(f"✅ Linked asset set to campaign: {campaign_name}")
                return {"success": True}
            else:
                return {"success": False, "error": "No results from campaign linking"}
        
        except GoogleAdsException as e:
            logger.error(f"❌ Google Ads error linking to campaign: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Unexpected error linking to campaign: {e}")
            return {"success": False, "error": str(e)}
    
    def _find_campaign(self, campaign_name: str) -> Optional[str]:
        """Find campaign by name."""
        try:
            query = f"""
                SELECT campaign.resource_name
                FROM campaign
                WHERE campaign.name = '{campaign_name}'
            """
            
            response = self.client.get_service("GoogleAdsService").search(
                customer_id=self.customer_id,
                query=query
            )
            
            for row in response:
                return row.campaign.resource_name
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find campaign '{campaign_name}': {e}")
            return None
    
    def get_existing_page_feeds(self) -> List[Dict]:
        """Get existing page feed asset sets."""
        try:
            query = """
                SELECT 
                    asset_set.resource_name,
                    asset_set.id,
                    asset_set.name,
                    asset_set.type
                FROM asset_set
                WHERE asset_set.type = 'PAGE_FEED'
            """
            
            response = self.client.get_service("GoogleAdsService").search(
                customer_id=self.customer_id,
                query=query
            )
            
            page_feeds = []
            for row in response:
                page_feeds.append({
                    "resource_name": row.asset_set.resource_name,
                    "id": row.asset_set.id,
                    "name": row.asset_set.name,
                    "type": row.asset_set.type.name
                })
            
            return page_feeds
            
        except Exception as e:
            logger.error(f"❌ Failed to get existing page feeds: {e}")
            return []
    
    def get_page_feed_urls(self, asset_set_id: str, limit: int = 100) -> List[str]:
        """Get URLs from an existing page feed asset set."""
        try:
            query = f"""
                SELECT
                    asset_set_asset.asset_set,
                    asset_set_asset.asset,
                    asset.page_feed_asset.page_url,
                    asset.page_feed_asset.labels
                FROM asset_set_asset
                WHERE asset_set_asset.asset_set = 'customers/{self.customer_id}/assetSets/{asset_set_id}'
                LIMIT {limit}
            """
            
            response = self.client.get_service("GoogleAdsService").search(
                customer_id=self.customer_id,
                query=query
            )
            
            urls = []
            for row in response:
                if row.asset.page_feed_asset.page_url:
                    urls.append(row.asset.page_feed_asset.page_url)
            
            return urls
            
        except Exception as e:
            logger.error(f"❌ Failed to get page feed URLs: {e}")
            return []

def test_page_feed_creator():
    """Test the page feed creator functionality."""
    print("🎯 Testing Page Feed Creator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return
    
    try:
        creator = PageFeedCreator(customer_id)
        
        # Test 1: Get existing page feeds
        print("📋 Test 1: Getting existing page feeds...")
        existing_feeds = creator.get_existing_page_feeds()
        print(f"✅ Found {len(existing_feeds)} existing page feeds")
        for feed in existing_feeds:
            print(f"   • {feed['name']} (ID: {feed['id']})")
        
        # Test 2: Create page feed from sitemap (dry run with small number)
        print(f"\n🚀 Test 2: Creating page feed from sitemap...")
        result = creator.create_page_feed_from_sitemap(
            campaign_name="L.R - PMax - General",
            max_urls=10,  # Small number for testing
            asset_set_name="Test Page Feed from Sitemap"
        )
        
        if result["success"]:
            print(f"✅ Page feed created successfully!")
            print(f"   Asset Set ID: {result['asset_set_id']}")
            print(f"   URLs Processed: {result['urls_processed']}")
            print(f"   Assets Created: {result['assets_created']}")
            print(f"   Campaign Linked: {result['campaign_linked']}")
        else:
            print(f"❌ Page feed creation failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_page_feed_creator()
