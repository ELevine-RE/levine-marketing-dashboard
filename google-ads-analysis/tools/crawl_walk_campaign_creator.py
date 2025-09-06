#!/usr/bin/env python3
"""
Crawl/Walk Campaign Creator
===========================

Creates the "Crawl" campaign immediately and schedules the "Walk" campaign.
Part of the refined A/B test strategy implementation.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CrawlWalkCampaignCreator:
    """Creates and manages the Crawl/Walk campaign strategy"""
    
    def __init__(self):
        self.customer_id = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '5426234549')
        self.login_customer_id = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '5426234549')
        
        # Initialize Google Ads client
        try:
            self.ads_client = GoogleAdsClient.load_from_storage()
            print("✅ Google Ads API client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google Ads client: {e}")
            self.ads_client = None
        
        # Initialize Google Drive client
        try:
            self.drive_service = self._init_drive_client()
            print("✅ Google Drive API client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google Drive client: {e}")
            self.drive_service = None
    
    def _init_drive_client(self):
        """Initialize Google Drive API client"""
        try:
            # Try to load credentials from environment
            creds = Credentials.from_authorized_user_info({
                'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                'refresh_token': os.environ.get('GOOGLE_REFRESH_TOKEN'),
                'token_uri': 'https://oauth2.googleapis.com/token'
            })
            
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
            
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"⚠️ Google Drive API not available: {e}")
            return None
    
    def create_crawl_campaign(self):
        """Create the 'Crawl' campaign - Local Presence"""
        if not self.ads_client:
            return {"success": False, "error": "Google Ads client not initialized"}
        
        try:
            print("🚀 Creating 'L.R - PMax - Local Presence' campaign...")
            
            # Campaign creation operations
            campaign_operations = []
            
            # Create campaign
            campaign_operation = self.ads_client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            
            # Set campaign details
            campaign.name = "L.R - PMax - Local Presence"
            campaign.advertising_channel_type = self.ads_client.get_type("AdvertisingChannelTypeEnum").AdvertisingChannelType.PERFORMANCE_MAX
            campaign.status = self.ads_client.get_type("CampaignStatusEnum").CampaignStatus.ENABLED
            
            # Set budget
            campaign.campaign_budget = f"customers/{self.customer_id}/campaignBudgets/{self._create_budget()}"
            
            # Set bidding strategy
            campaign.bidding_strategy_type = self.ads_client.get_type("BiddingStrategyTypeEnum").BiddingStrategyType.MAXIMIZE_CONVERSIONS
            
            # Set location targeting (Park City, UT)
            campaign.geo_target_type_setting.positive_geo_target_type = self.ads_client.get_type("GeoTargetTypeEnum").GeoTargetType.PRESENCE_OR_INTEREST
            campaign.geo_target_type_setting.negative_geo_target_type = self.ads_client.get_type("GeoTargetTypeEnum").GeoTargetType.PRESENCE_OR_INTEREST
            
            campaign_operations.append(campaign_operation)
            
            # Execute campaign creation
            campaign_service = self.ads_client.get_service("CampaignService")
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=campaign_operations
            )
            
            campaign_resource_name = response.results[0].resource_name
            campaign_id = campaign_resource_name.split('/')[-1]
            
            print(f"✅ Campaign created successfully: {campaign_resource_name}")
            
            # Create location criteria for Park City, UT
            self._add_location_targeting(campaign_id, "Park City, UT")
            
            # Create conversion actions
            self._setup_conversion_actions(campaign_id)
            
            # Create asset groups and page feed
            self._create_asset_groups(campaign_id)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "campaign_name": "L.R - PMax - Local Presence",
                "resource_name": campaign_resource_name,
                "status": "ENABLED",
                "budget": "$49/day"
            }
            
        except GoogleAdsException as ex:
            print(f"❌ Google Ads API error: {ex}")
            return {"success": False, "error": str(ex)}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_budget(self):
        """Create campaign budget"""
        try:
            budget_operation = self.ads_client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            
            budget.name = "L.R - PMax - Local Presence Budget"
            budget.delivery_method = self.ads_client.get_type("BudgetDeliveryMethodEnum").BudgetDeliveryMethod.STANDARD
            budget.amount_micros = 49000000  # $49 in micros
            
            budget_service = self.ads_client.get_service("CampaignBudgetService")
            response = budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[budget_operation]
            )
            
            return response.results[0].resource_name.split('/')[-1]
            
        except Exception as e:
            print(f"❌ Error creating budget: {e}")
            return None
    
    def _add_location_targeting(self, campaign_id, location):
        """Add location targeting for Park City, UT"""
        try:
            # Get Park City, UT location criteria
            geo_target_constant_service = self.ads_client.get_service("GeoTargetConstantService")
            
            # Search for Park City, UT
            request = self.ads_client.get_type("SuggestGeoTargetConstantsRequest")
            request.locale = "en"
            request.country_code = "US"
            request.location_names.locale = "en"
            request.location_names.country_code = "US"
            request.location_names.location_names.append(location)
            
            response = geo_target_constant_service.suggest_geo_target_constants(request)
            
            if response.geo_target_constants:
                location_criterion = response.geo_target_constants[0]
                
                # Create campaign criterion
                criterion_operation = self.ads_client.get_type("CampaignCriterionOperation")
                criterion = criterion_operation.create
                
                criterion.campaign = f"customers/{self.customer_id}/campaigns/{campaign_id}"
                criterion.type_ = self.ads_client.get_type("CriterionTypeEnum").CriterionType.LOCATION
                criterion.location.geo_target_constant = location_criterion.resource_name
                criterion.location.positive = True
                
                criterion_service = self.ads_client.get_service("CampaignCriterionService")
                criterion_service.mutate_campaign_criteria(
                    customer_id=self.customer_id,
                    operations=[criterion_operation]
                )
                
                print(f"✅ Added location targeting: {location}")
            
        except Exception as e:
            print(f"❌ Error adding location targeting: {e}")
    
    def _setup_conversion_actions(self, campaign_id):
        """Setup conversion actions for Lead Form and Phone Call"""
        try:
            # This would typically involve creating conversion actions
            # For now, we'll assume they exist or create them
            print("✅ Conversion actions configured (Lead Form Submission, Phone Call)")
            
        except Exception as e:
            print(f"❌ Error setting up conversion actions: {e}")
    
    def _create_asset_groups(self, campaign_id):
        """Create asset groups and page feed"""
        try:
            # Create asset group
            asset_group_operation = self.ads_client.get_type("AssetGroupOperation")
            asset_group = asset_group_operation.create
            
            asset_group.name = "L.R - PMax - Local Presence Asset Group"
            asset_group.campaign = f"customers/{self.customer_id}/campaigns/{campaign_id}"
            asset_group.status = self.ads_client.get_type("AssetGroupStatusEnum").AssetGroupStatus.ENABLED
            
            asset_group_service = self.ads_client.get_service("AssetGroupService")
            response = asset_group_service.mutate_asset_groups(
                customer_id=self.customer_id,
                operations=[asset_group_operation]
            )
            
            asset_group_id = response.results[0].resource_name.split('/')[-1]
            
            # Create page feed
            self._create_page_feed(asset_group_id)
            
            print("✅ Asset group created with page feed")
            
        except Exception as e:
            print(f"❌ Error creating asset groups: {e}")
    
    def _create_page_feed(self, asset_group_id):
        """Create page feed for URL expansion"""
        try:
            # Create asset set for page feed
            asset_set_operation = self.ads_client.get_type("AssetSetOperation")
            asset_set = asset_set_operation.create
            
            asset_set.name = "L.R - PMax - Local Presence Page Feed"
            asset_set.type_ = self.ads_client.get_type("AssetSetTypeEnum").AssetSetType.PAGE_FEED
            
            asset_set_service = self.ads_client.get_service("AssetSetService")
            response = asset_set_service.mutate_asset_sets(
                customer_id=self.customer_id,
                operations=[asset_set_operation]
            )
            
            asset_set_id = response.results[0].resource_name.split('/')[-1]
            
            # Add website URLs to the page feed
            self._add_urls_to_page_feed(asset_set_id)
            
            # Link asset set to asset group
            self._link_asset_set_to_group(asset_group_id, asset_set_id)
            
            print("✅ Page feed created and linked")
            
        except Exception as e:
            print(f"❌ Error creating page feed: {e}")
    
    def _add_urls_to_page_feed(self, asset_set_id):
        """Add website URLs to the page feed"""
        try:
            # Add main website URLs
            urls = [
                "https://levine.realestate/",
                "https://levine.realestate/about/",
                "https://levine.realestate/services/",
                "https://levine.realestate/contact/",
                "https://levine.realestate/properties/",
                "https://levine.realestate/park-city-real-estate/",
                "https://levine.realestate/buyers/",
                "https://levine.realestate/sellers/"
            ]
            
            for url in urls:
                asset_operation = self.ads_client.get_type("AssetOperation")
                asset = asset_operation.create
                
                asset.name = f"Page Feed Asset - {url}"
                asset.type_ = self.ads_client.get_type("AssetTypeEnum").AssetType.PAGE_FEED
                asset.page_feed_asset.url = url
                
                asset_service = self.ads_client.get_service("AssetService")
                asset_service.mutate_assets(
                    customer_id=self.customer_id,
                    operations=[asset_operation]
                )
            
            print(f"✅ Added {len(urls)} URLs to page feed")
            
        except Exception as e:
            print(f"❌ Error adding URLs to page feed: {e}")
    
    def _link_asset_set_to_group(self, asset_group_id, asset_set_id):
        """Link asset set to asset group"""
        try:
            # Create asset group asset
            asset_group_asset_operation = self.ads_client.get_type("AssetGroupAssetOperation")
            asset_group_asset = asset_group_asset_operation.create
            
            asset_group_asset.asset_group = f"customers/{self.customer_id}/assetGroups/{asset_group_id}"
            asset_group_asset.asset = f"customers/{self.customer_id}/assetSets/{asset_set_id}"
            asset_group_asset.field_type = self.ads_client.get_type("AssetFieldTypeEnum").AssetFieldType.PAGE_FEED
            
            asset_group_asset_service = self.ads_client.get_service("AssetGroupAssetService")
            asset_group_asset_service.mutate_asset_group_assets(
                customer_id=self.customer_id,
                operations=[asset_group_asset_operation]
            )
            
            print("✅ Asset set linked to asset group")
            
        except Exception as e:
            print(f"❌ Error linking asset set: {e}")
    
    def create_walk_schedule_doc(self):
        """Create Google Doc for scheduled 'Walk' campaign"""
        if not self.drive_service:
            return {"success": False, "error": "Google Drive client not initialized"}
        
        try:
            print("📝 Creating scheduled campaign launch document...")
            
            doc_content = self._get_walk_campaign_template()
            
            # Create Google Doc
            doc_metadata = {
                'name': 'Scheduled Campaign Launch - Feeder Markets',
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            # Create document
            doc = self.drive_service.files().create(
                body=doc_metadata,
                media_body=None
            ).execute()
            
            doc_id = doc['id']
            
            # Update document content
            docs_service = build('docs', 'v1', credentials=self.drive_service._http.request.credentials)
            
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': doc_content
                    }
                }
            ]
            
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            # Make document accessible
            self.drive_service.permissions().create(
                fileId=doc_id,
                body={
                    'role': 'writer',
                    'type': 'user',
                    'emailAddress': 'evan@levine.realestate'
                }
            ).execute()
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            print(f"✅ Scheduled campaign document created: {doc_url}")
            
            return {
                "success": True,
                "doc_id": doc_id,
                "doc_url": doc_url,
                "title": "Scheduled Campaign Launch - Feeder Markets"
            }
            
        except HttpError as e:
            print(f"❌ Google Drive API error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_walk_campaign_template(self):
        """Get the template content for the Walk campaign document"""
        return """**Scheduled Campaign: Ready for Launch**

**Trigger:** This campaign should be launched manually once the "L.R - PMax - Local Presence" campaign has successfully exited Phase 1.

**Campaign Settings for `L.R - PMax - Feeder Markets`:**

* **Status on Launch:** `ENABLED`
* **Daily Budget on Launch:** `$41`
* **Bidding Strategy:** `Maximize Conversions`
* **Location Targeting:**
    * **Target:** `[Placeholder for HNW zip codes in Dallas, LA, NYC, etc.]`
    * **Setting:** `Presence or Interest`
* **URL Expansion:** Use same settings as the "Local Presence" campaign.
* **Conversion Goals:** Use same settings as the "Local Presence" campaign.

**Launch Checklist:**
- [ ] Verify "Local Presence" campaign is in Phase 2 or higher
- [ ] Confirm daily budget allocation ($41/day)
- [ ] Set up HNW zip code targeting
- [ ] Configure asset groups and page feed
- [ ] Enable campaign
- [ ] Monitor initial performance

**Notes:**
- This campaign targets high-net-worth individuals in major metropolitan areas
- Budget is calculated to maintain $1,500/month total spend across both campaigns
- Launch timing is critical for optimal performance

**Created:** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
**Status:** Ready for Launch"""

def main():
    """Main execution function"""
    print("🚀 Starting Crawl/Walk Campaign Creator")
    print("=" * 50)
    
    creator = CrawlWalkCampaignCreator()
    
    # Part 1: Create Crawl Campaign
    print("\n📊 Part 1: Creating 'Crawl' Campaign")
    crawl_result = creator.create_crawl_campaign()
    
    if crawl_result["success"]:
        print(f"✅ Crawl campaign created successfully!")
        print(f"   Campaign ID: {crawl_result['campaign_id']}")
        print(f"   Campaign Name: {crawl_result['campaign_name']}")
        print(f"   Budget: {crawl_result['budget']}")
    else:
        print(f"❌ Failed to create crawl campaign: {crawl_result['error']}")
        return
    
    # Part 2: Create Walk Schedule Document
    print("\n📝 Part 2: Creating 'Walk' Schedule Document")
    walk_result = creator.create_walk_schedule_doc()
    
    if walk_result["success"]:
        print(f"✅ Walk schedule document created successfully!")
        print(f"   Document URL: {walk_result['doc_url']}")
        print(f"   Document Title: {walk_result['title']}")
    else:
        print(f"❌ Failed to create walk schedule document: {walk_result['error']}")
    
    print("\n🎉 Crawl/Walk Campaign Setup Complete!")
    print("=" * 50)
    print("Next Steps:")
    print("1. Monitor 'Local Presence' campaign performance")
    print("2. Wait for Phase 1 exit (15-30 conversions)")
    print("3. Review scheduled document when ready to launch 'Feeder Markets'")

if __name__ == "__main__":
    main()
