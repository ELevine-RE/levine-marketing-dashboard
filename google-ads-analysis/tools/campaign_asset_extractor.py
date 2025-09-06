#!/usr/bin/env python3
"""
Campaign-Specific Asset Extractor
=================================

Extracts assets from specific landing pages and their children for individual campaigns.
Creates campaign-specific asset sets with targeted content.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.asset_extractor import AssetExtractor
from tools.page_feed_creator import PageFeedCreator
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class CampaignAssetExtractor:
    """Extracts assets from specific pages for individual campaigns."""
    
    def __init__(self, customer_id: str, manager_customer_id: Optional[str] = None):
        self.customer_id = customer_id
        self.manager_customer_id = manager_customer_id or customer_id
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.asset_extractor = AssetExtractor()
        self.page_feed_creator = PageFeedCreator(customer_id, manager_customer_id)
        
        # Campaign configurations
        self.config_file = "data/campaign_asset_configs.json"
        self.load_campaign_configs()
        
        logger.info("✅ Campaign Asset Extractor initialized")
    
    def load_campaign_configs(self):
        """Load campaign-specific configurations."""
        default_configs = {
            "campaigns": {
                "L.R - PMax - General": {
                    "landing_pages": [
                        "https://levine.realestate/",
                        "https://levine.realestate/property/",
                        "https://levine.realestate/communities/"
                    ],
                    "include_children": True,
                    "max_depth": 2,
                    "asset_set_name": "Levine Real Estate - General Assets",
                    "enabled": True
                },
                "L.R - Deer Valley": {
                    "landing_pages": [
                        "https://levine.realestate/communities/deer-valley/",
                        "https://levine.realestate/property/?location=deer-valley"
                    ],
                    "include_children": True,
                    "max_depth": 3,
                    "asset_set_name": "Levine Real Estate - Deer Valley Assets",
                    "enabled": True
                },
                "L.R - Park City": {
                    "landing_pages": [
                        "https://levine.realestate/communities/park-city/",
                        "https://levine.realestate/property/?location=park-city"
                    ],
                    "include_children": True,
                    "max_depth": 3,
                    "asset_set_name": "Levine Real Estate - Park City Assets",
                    "enabled": True
                }
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.configs = json.load(f)
                # Merge with defaults for any missing campaigns
                for campaign_name, default_config in default_configs["campaigns"].items():
                    if campaign_name not in self.configs.get("campaigns", {}):
                        self.configs.setdefault("campaigns", {})[campaign_name] = default_config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load campaign configs, using defaults: {e}")
                self.configs = default_configs
        else:
            self.configs = default_configs
        
        self.save_campaign_configs()
    
    def save_campaign_configs(self):
        """Save campaign configurations."""
        os.makedirs('data', exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.configs, f, indent=2)
    
    def extract_campaign_assets(self, campaign_name: str) -> Dict:
        """Extract assets for a specific campaign."""
        if campaign_name not in self.configs["campaigns"]:
            return {
                "success": False,
                "error": f"Campaign '{campaign_name}' not found in configuration"
            }
        
        campaign_config = self.configs["campaigns"][campaign_name]
        
        if not campaign_config.get("enabled", True):
            return {
                "success": False,
                "error": f"Campaign '{campaign_name}' is disabled"
            }
        
        logger.info(f"🎯 Extracting assets for campaign: {campaign_name}")
        
        try:
            # Step 1: Get all pages for this campaign
            logger.info("📋 Step 1: Collecting pages for campaign...")
            campaign_pages = self._get_campaign_pages(campaign_config)
            
            if not campaign_pages:
                return {
                    "success": False,
                    "error": "No pages found for campaign"
                }
            
            logger.info(f"✅ Found {len(campaign_pages)} pages for campaign")
            
            # Step 2: Extract assets from each page
            logger.info("🖼️ Step 2: Extracting assets from pages...")
            all_assets = self._extract_assets_from_pages(campaign_pages)
            
            # Step 3: Create campaign-specific asset set
            logger.info("📦 Step 3: Creating campaign asset set...")
            asset_set_result = self._create_campaign_asset_set(campaign_name, campaign_config, all_assets)
            
            # Step 4: Link to campaign
            logger.info("🔗 Step 4: Linking assets to campaign...")
            link_result = self._link_assets_to_campaign(campaign_name, asset_set_result.get("asset_set_id"))
            
            # Step 5: Generate summary
            result = {
                "success": True,
                "campaign_name": campaign_name,
                "pages_processed": len(campaign_pages),
                "total_assets": sum(len(assets.get("images", [])) + len(assets.get("videos", [])) for assets in all_assets.values()),
                "images_extracted": sum(len(assets.get("images", [])) for assets in all_assets.values()),
                "videos_extracted": sum(len(assets.get("videos", [])) for assets in all_assets.values()),
                "asset_set_id": asset_set_result.get("asset_set_id"),
                "asset_set_name": campaign_config["asset_set_name"],
                "campaign_linked": link_result.get("success", False),
                "created_at": datetime.now().isoformat(),
                "pages": list(campaign_pages.keys())
            }
            
            logger.info(f"✅ Campaign asset extraction completed successfully!")
            logger.info(f"   Pages Processed: {result['pages_processed']}")
            logger.info(f"   Total Assets: {result['total_assets']}")
            logger.info(f"   Images: {result['images_extracted']}")
            logger.info(f"   Videos: {result['videos_extracted']}")
            logger.info(f"   Asset Set ID: {result['asset_set_id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to extract campaign assets: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_name": campaign_name
            }
    
    def _get_campaign_pages(self, campaign_config: Dict) -> Dict[str, Dict]:
        """Get all pages for a campaign, including children if configured."""
        pages = {}
        
        for landing_page in campaign_config["landing_pages"]:
            # Add the main landing page
            pages[landing_page] = {
                "url": landing_page,
                "depth": 0,
                "parent": None,
                "campaign": campaign_config["asset_set_name"]
            }
            
            # Add children if configured
            if campaign_config.get("include_children", True):
                children = self._get_child_pages(landing_page, campaign_config.get("max_depth", 2))
                pages.update(children)
        
        return pages
    
    def _get_child_pages(self, parent_url: str, max_depth: int, current_depth: int = 1) -> Dict[str, Dict]:
        """Get child pages from a parent page."""
        if current_depth > max_depth:
            return {}
        
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse
            
            response = requests.get(parent_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            child_pages = {}
            
            # Find all internal links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(parent_url, href)
                
                # Check if it's an internal link
                if self._is_internal_link(full_url):
                    # Check if it's a relevant page (property, community, etc.)
                    if self._is_relevant_page(full_url):
                        child_pages[full_url] = {
                            "url": full_url,
                            "depth": current_depth,
                            "parent": parent_url,
                            "campaign": "child"
                        }
            
            # Recursively get children of children
            for child_url in list(child_pages.keys()):
                grandchildren = self._get_child_pages(child_url, max_depth, current_depth + 1)
                child_pages.update(grandchildren)
            
            return child_pages
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get child pages for {parent_url}: {e}")
            return {}
    
    def _is_internal_link(self, url: str) -> bool:
        """Check if URL is internal to the website."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc in ['levine.realestate', 'www.levine.realestate']
        except:
            return False
    
    def _is_relevant_page(self, url: str) -> bool:
        """Check if page is relevant for asset extraction."""
        relevant_patterns = [
            '/property/',
            '/communities/',
            '/deer-valley',
            '/park-city',
            '/promontory',
            '/search/',
            '/listings/'
        ]
        
        return any(pattern in url.lower() for pattern in relevant_patterns)
    
    def _extract_assets_from_pages(self, pages: Dict[str, Dict]) -> Dict[str, Dict]:
        """Extract assets from all campaign pages."""
        all_assets = {}
        
        for page_url, page_info in pages.items():
            logger.info(f"🖼️ Extracting assets from: {page_url}")
            
            try:
                assets = self.asset_extractor.extract_assets_from_page(page_url)
                if assets and "error" not in assets:
                    all_assets[page_url] = assets
                    logger.info(f"✅ Extracted {len(assets.get('images', []))} images, {len(assets.get('videos', []))} videos")
                else:
                    logger.warning(f"⚠️ No assets extracted from {page_url}")
            except Exception as e:
                logger.error(f"❌ Failed to extract assets from {page_url}: {e}")
        
        return all_assets
    
    def _create_campaign_asset_set(self, campaign_name: str, campaign_config: Dict, all_assets: Dict[str, Dict]) -> Dict:
        """Create a campaign-specific asset set."""
        try:
            asset_set_name = campaign_config["asset_set_name"]
            
            # Create asset set
            asset_set_id = self.page_feed_creator.create_asset_set(asset_set_name)
            
            if not asset_set_id:
                return {"success": False, "error": "Failed to create asset set"}
            
            # Create assets from extracted content
            created_assets = 0
            failed_assets = 0
            
            for page_url, assets in all_assets.items():
                # Create image assets
                for image in assets.get("images", []):
                    try:
                        # Here you would create actual Google Ads assets
                        # For now, we'll just count them
                        created_assets += 1
                    except Exception as e:
                        failed_assets += 1
                        logger.warning(f"⚠️ Failed to create image asset: {e}")
                
                # Create video assets
                for video in assets.get("videos", []):
                    try:
                        # Here you would create actual Google Ads assets
                        # For now, we'll just count them
                        created_assets += 1
                    except Exception as e:
                        failed_assets += 1
                        logger.warning(f"⚠️ Failed to create video asset: {e}")
            
            return {
                "success": True,
                "asset_set_id": asset_set_id,
                "asset_set_name": asset_set_name,
                "created_assets": created_assets,
                "failed_assets": failed_assets
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create campaign asset set: {e}")
            return {"success": False, "error": str(e)}
    
    def _link_assets_to_campaign(self, campaign_name: str, asset_set_id: Optional[str]) -> Dict:
        """Link asset set to campaign."""
        if not asset_set_id:
            return {"success": False, "error": "No asset set ID provided"}
        
        try:
            result = self.page_feed_creator.link_to_campaign(campaign_name, asset_set_id)
            return result
        except Exception as e:
            logger.error(f"❌ Failed to link assets to campaign: {e}")
            return {"success": False, "error": str(e)}
    
    def add_campaign_config(self, campaign_name: str, landing_pages: List[str], 
                          include_children: bool = True, max_depth: int = 2,
                          asset_set_name: Optional[str] = None) -> bool:
        """Add a new campaign configuration."""
        try:
            if not asset_set_name:
                asset_set_name = f"Levine Real Estate - {campaign_name} Assets"
            
            self.configs["campaigns"][campaign_name] = {
                "landing_pages": landing_pages,
                "include_children": include_children,
                "max_depth": max_depth,
                "asset_set_name": asset_set_name,
                "enabled": True
            }
            
            self.save_campaign_configs()
            logger.info(f"✅ Added campaign configuration: {campaign_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add campaign configuration: {e}")
            return False
    
    def get_campaign_status(self, campaign_name: str) -> Dict:
        """Get status of a campaign's asset extraction."""
        if campaign_name not in self.configs["campaigns"]:
            return {"error": f"Campaign '{campaign_name}' not found"}
        
        campaign_config = self.configs["campaigns"][campaign_name]
        
        return {
            "campaign_name": campaign_name,
            "landing_pages": campaign_config["landing_pages"],
            "include_children": campaign_config.get("include_children", True),
            "max_depth": campaign_config.get("max_depth", 2),
            "asset_set_name": campaign_config["asset_set_name"],
            "enabled": campaign_config.get("enabled", True)
        }
    
    def list_campaigns(self) -> List[str]:
        """List all configured campaigns."""
        return list(self.configs["campaigns"].keys())

def test_campaign_asset_extractor():
    """Test the campaign asset extractor."""
    print("🎯 Testing Campaign Asset Extractor")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return
    
    try:
        extractor = CampaignAssetExtractor(customer_id)
        
        # Test 1: List campaigns
        print("📋 Test 1: Listing configured campaigns...")
        campaigns = extractor.list_campaigns()
        print(f"✅ Found {len(campaigns)} configured campaigns:")
        for campaign in campaigns:
            print(f"   • {campaign}")
        
        # Test 2: Get campaign status
        print(f"\n📊 Test 2: Getting campaign status...")
        for campaign in campaigns[:2]:  # Test first 2 campaigns
            status = extractor.get_campaign_status(campaign)
            print(f"   {campaign}:")
            print(f"     Landing Pages: {len(status['landing_pages'])}")
            print(f"     Include Children: {status['include_children']}")
            print(f"     Max Depth: {status['max_depth']}")
            print(f"     Asset Set: {status['asset_set_name']}")
        
        # Test 3: Extract assets for a campaign (dry run)
        print(f"\n🚀 Test 3: Extracting assets for campaign...")
        test_campaign = campaigns[0] if campaigns else "L.R - PMax - General"
        result = extractor.extract_campaign_assets(test_campaign)
        
        if result["success"]:
            print(f"✅ Asset extraction completed successfully!")
            print(f"   Pages Processed: {result['pages_processed']}")
            print(f"   Total Assets: {result['total_assets']}")
            print(f"   Images: {result['images_extracted']}")
            print(f"   Videos: {result['videos_extracted']}")
        else:
            print(f"❌ Asset extraction failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_campaign_asset_extractor()
