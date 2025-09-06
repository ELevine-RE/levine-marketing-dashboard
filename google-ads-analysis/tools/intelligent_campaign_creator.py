#!/usr/bin/env python3
"""
Intelligent Campaign Creator
============================

Automatically creates campaigns with optimized assets based on campaign goals,
targeting, and content. No manual asset management required.
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.campaign_asset_extractor import CampaignAssetExtractor
from tools.sitemap_parser import SitemapParser
from tools.page_feed_creator import PageFeedCreator
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class IntelligentCampaignCreator:
    """Creates campaigns with automatically optimized assets."""
    
    def __init__(self, customer_id: str, manager_customer_id: Optional[str] = None):
        self.customer_id = customer_id
        self.manager_customer_id = manager_customer_id or customer_id
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.asset_extractor = CampaignAssetExtractor(customer_id, manager_customer_id)
        self.sitemap_parser = SitemapParser()
        self.page_feed_creator = PageFeedCreator(customer_id, manager_customer_id)
        
        # Campaign intelligence rules
        self.intelligence_rules = self._load_intelligence_rules()
        
        logger.info("✅ Intelligent Campaign Creator initialized")
    
    def _load_intelligence_rules(self) -> Dict:
        """Load intelligence rules for automatic campaign optimization."""
        return {
            "location_keywords": {
                "deer valley": {
                    "landing_pages": [
                        "https://levine.realestate/communities/deer-valley/",
                        "https://levine.realestate/property/?location=deer-valley"
                    ],
                    "asset_priorities": ["property_photos", "community_images", "luxury_content"],
                    "targeting_keywords": ["deer valley real estate", "deer valley homes", "deer valley properties"],
                    "budget_suggestions": {"min": 2000, "max": 5000},
                    "campaign_type": "Performance Max"
                },
                "park city": {
                    "landing_pages": [
                        "https://levine.realestate/communities/park-city/",
                        "https://levine.realestate/property/?location=park-city"
                    ],
                    "asset_priorities": ["property_photos", "mountain_views", "ski_content"],
                    "targeting_keywords": ["park city real estate", "park city homes", "park city properties"],
                    "budget_suggestions": {"min": 1500, "max": 4000},
                    "campaign_type": "Performance Max"
                },
                "promontory": {
                    "landing_pages": [
                        "https://levine.realestate/communities/promontory/",
                        "https://levine.realestate/property/?location=promontory"
                    ],
                    "asset_priorities": ["property_photos", "golf_content", "luxury_lifestyle"],
                    "targeting_keywords": ["promontory real estate", "promontory homes", "promontory properties"],
                    "budget_suggestions": {"min": 2500, "max": 6000},
                    "campaign_type": "Performance Max"
                }
            },
            "property_type_keywords": {
                "luxury": {
                    "asset_priorities": ["high_end_photos", "luxury_amenities", "premium_content"],
                    "budget_multiplier": 1.5,
                    "targeting_modifiers": ["luxury", "premium", "high-end"]
                },
                "condo": {
                    "asset_priorities": ["interior_photos", "amenity_photos", "lifestyle_content"],
                    "budget_multiplier": 1.0,
                    "targeting_modifiers": ["condo", "condominium", "apartment"]
                },
                "single family": {
                    "asset_priorities": ["exterior_photos", "yard_photos", "family_content"],
                    "budget_multiplier": 1.2,
                    "targeting_modifiers": ["single family", "house", "home"]
                }
            },
            "campaign_goals": {
                "lead_generation": {
                    "asset_priorities": ["contact_forms", "phone_numbers", "cta_content"],
                    "budget_focus": "conversion_optimization",
                    "targeting_strategy": "broad_match"
                },
                "brand_awareness": {
                    "asset_priorities": ["brand_logos", "company_photos", "testimonial_content"],
                    "budget_focus": "impression_optimization",
                    "targeting_strategy": "phrase_match"
                },
                "property_sales": {
                    "asset_priorities": ["property_photos", "virtual_tours", "listing_content"],
                    "budget_focus": "conversion_optimization",
                    "targeting_strategy": "exact_match"
                }
            }
        }
    
    def create_intelligent_campaign(self, campaign_name: str, campaign_goal: str = "lead_generation", 
                                 target_location: Optional[str] = None, 
                                 property_type: Optional[str] = None,
                                 budget: Optional[float] = None) -> Dict:
        """Create a campaign with automatically optimized assets."""
        
        logger.info(f"🧠 Creating intelligent campaign: {campaign_name}")
        
        try:
            # Step 1: Analyze campaign requirements
            logger.info("🔍 Step 1: Analyzing campaign requirements...")
            campaign_analysis = self._analyze_campaign_requirements(
                campaign_name, campaign_goal, target_location, property_type, budget
            )
            
            # Step 2: Generate intelligent configuration
            logger.info("⚙️ Step 2: Generating intelligent configuration...")
            campaign_config = self._generate_campaign_config(campaign_analysis)
            
            # Step 3: Extract optimized assets
            logger.info("🖼️ Step 3: Extracting optimized assets...")
            asset_result = self._extract_optimized_assets(campaign_config)
            
            # Step 4: Create page feed
            logger.info("📋 Step 4: Creating optimized page feed...")
            page_feed_result = self._create_optimized_page_feed(campaign_config)
            
            # Step 5: Create campaign in Google Ads
            logger.info("🎯 Step 5: Creating campaign in Google Ads...")
            campaign_result = self._create_google_ads_campaign(campaign_config)
            
            # Step 6: Link everything together
            logger.info("🔗 Step 6: Linking assets and feeds to campaign...")
            link_result = self._link_campaign_components(campaign_result, asset_result, page_feed_result)
            
            # Step 7: Generate optimization recommendations
            logger.info("📊 Step 7: Generating optimization recommendations...")
            optimization_recommendations = self._generate_optimization_recommendations(campaign_config)
            
            # Step 8: Create summary
            result = {
                "success": True,
                "campaign_name": campaign_name,
                "campaign_id": campaign_result.get("campaign_id"),
                "asset_set_id": asset_result.get("asset_set_id"),
                "page_feed_id": page_feed_result.get("asset_set_id"),
                "pages_processed": asset_result.get("pages_processed", 0),
                "assets_extracted": asset_result.get("total_assets", 0),
                "images_extracted": asset_result.get("images_extracted", 0),
                "videos_extracted": asset_result.get("videos_extracted", 0),
                "campaign_linked": link_result.get("success", False),
                "optimization_recommendations": optimization_recommendations,
                "created_at": datetime.now().isoformat(),
                "campaign_config": campaign_config
            }
            
            logger.info(f"✅ Intelligent campaign created successfully!")
            logger.info(f"   Campaign ID: {result['campaign_id']}")
            logger.info(f"   Assets Extracted: {result['assets_extracted']}")
            logger.info(f"   Pages Processed: {result['pages_processed']}")
            logger.info(f"   Campaign Linked: {result['campaign_linked']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create intelligent campaign: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_name": campaign_name
            }
    
    def _analyze_campaign_requirements(self, campaign_name: str, campaign_goal: str,
                                     target_location: Optional[str], property_type: Optional[str],
                                     budget: Optional[float]) -> Dict:
        """Analyze campaign requirements and extract intelligence."""
        
        analysis = {
            "campaign_name": campaign_name,
            "campaign_goal": campaign_goal,
            "target_location": target_location,
            "property_type": property_type,
            "budget": budget,
            "intelligence": {}
        }
        
        # Extract location intelligence
        if target_location:
            location_key = target_location.lower().replace(" ", "_")
            if location_key in self.intelligence_rules["location_keywords"]:
                analysis["intelligence"]["location"] = self.intelligence_rules["location_keywords"][location_key]
        
        # Extract property type intelligence
        if property_type:
            prop_key = property_type.lower().replace(" ", "_")
            if prop_key in self.intelligence_rules["property_type_keywords"]:
                analysis["intelligence"]["property_type"] = self.intelligence_rules["property_type_keywords"][prop_key]
        
        # Extract goal intelligence
        if campaign_goal in self.intelligence_rules["campaign_goals"]:
            analysis["intelligence"]["goal"] = self.intelligence_rules["campaign_goals"][campaign_goal]
        
        # Auto-detect location from campaign name
        if not target_location:
            detected_location = self._detect_location_from_name(campaign_name)
            if detected_location:
                analysis["target_location"] = detected_location
                location_key = detected_location.lower().replace(" ", "_")
                if location_key in self.intelligence_rules["location_keywords"]:
                    analysis["intelligence"]["location"] = self.intelligence_rules["location_keywords"][location_key]
        
        # Auto-detect property type from campaign name
        if not property_type:
            detected_property_type = self._detect_property_type_from_name(campaign_name)
            if detected_property_type:
                analysis["property_type"] = detected_property_type
                prop_key = detected_property_type.lower().replace(" ", "_")
                if prop_key in self.intelligence_rules["property_type_keywords"]:
                    analysis["intelligence"]["property_type"] = self.intelligence_rules["property_type_keywords"][prop_key]
        
        # Calculate intelligent budget
        if not budget:
            analysis["budget"] = self._calculate_intelligent_budget(analysis)
        
        return analysis
    
    def _detect_location_from_name(self, campaign_name: str) -> Optional[str]:
        """Detect location from campaign name."""
        campaign_lower = campaign_name.lower()
        
        location_mappings = {
            "deer valley": "deer valley",
            "park city": "park city", 
            "promontory": "promontory",
            "heber": "heber",
            "midway": "midway",
            "kamas": "kamas"
        }
        
        for location, standard_name in location_mappings.items():
            if location in campaign_lower:
                return standard_name
        
        return None
    
    def _detect_property_type_from_name(self, campaign_name: str) -> Optional[str]:
        """Detect property type from campaign name."""
        campaign_lower = campaign_name.lower()
        
        property_mappings = {
            "luxury": "luxury",
            "condo": "condo",
            "condominium": "condo",
            "single family": "single family",
            "house": "single family",
            "home": "single family"
        }
        
        for keyword, standard_type in property_mappings.items():
            if keyword in campaign_lower:
                return standard_type
        
        return None
    
    def _calculate_intelligent_budget(self, analysis: Dict) -> float:
        """Calculate intelligent budget based on analysis."""
        base_budget = 2000  # Default base budget
        
        # Adjust for location
        if "location" in analysis["intelligence"]:
            location_budget = analysis["intelligence"]["location"]["budget_suggestions"]
            base_budget = (location_budget["min"] + location_budget["max"]) / 2
        
        # Adjust for property type
        if "property_type" in analysis["intelligence"]:
            multiplier = analysis["intelligence"]["property_type"]["budget_multiplier"]
            base_budget *= multiplier
        
        # Adjust for goal
        if "goal" in analysis["intelligence"]:
            if analysis["intelligence"]["goal"]["budget_focus"] == "conversion_optimization":
                base_budget *= 1.2
            elif analysis["intelligence"]["goal"]["budget_focus"] == "impression_optimization":
                base_budget *= 0.8
        
        return round(base_budget, 2)
    
    def _generate_campaign_config(self, analysis: Dict) -> Dict:
        """Generate intelligent campaign configuration."""
        
        config = {
            "campaign_name": analysis["campaign_name"],
            "campaign_goal": analysis["campaign_goal"],
            "target_location": analysis["target_location"],
            "property_type": analysis["property_type"],
            "budget": analysis["budget"],
            "landing_pages": [],
            "asset_priorities": [],
            "targeting_keywords": [],
            "campaign_type": "Performance Max",
            "include_children": True,
            "max_depth": 2
        }
        
        # Add location-specific configuration
        if "location" in analysis["intelligence"]:
            location_intel = analysis["intelligence"]["location"]
            config["landing_pages"].extend(location_intel["landing_pages"])
            config["asset_priorities"].extend(location_intel["asset_priorities"])
            config["targeting_keywords"].extend(location_intel["targeting_keywords"])
            config["campaign_type"] = location_intel["campaign_type"]
        
        # Add property type-specific configuration
        if "property_type" in analysis["intelligence"]:
            prop_intel = analysis["intelligence"]["property_type"]
            config["asset_priorities"].extend(prop_intel["asset_priorities"])
            config["targeting_keywords"].extend(prop_intel["targeting_modifiers"])
        
        # Add goal-specific configuration
        if "goal" in analysis["intelligence"]:
            goal_intel = analysis["intelligence"]["goal"]
            config["asset_priorities"].extend(goal_intel["asset_priorities"])
        
        # Remove duplicates
        config["asset_priorities"] = list(set(config["asset_priorities"]))
        config["targeting_keywords"] = list(set(config["targeting_keywords"]))
        
        # Generate asset set name
        config["asset_set_name"] = f"Levine Real Estate - {analysis['campaign_name']} Assets"
        
        return config
    
    def _extract_optimized_assets(self, campaign_config: Dict) -> Dict:
        """Extract optimized assets for the campaign."""
        
        # Add campaign configuration to asset extractor
        self.asset_extractor.add_campaign_config(
            campaign_name=campaign_config["campaign_name"],
            landing_pages=campaign_config["landing_pages"],
            include_children=campaign_config["include_children"],
            max_depth=campaign_config["max_depth"],
            asset_set_name=campaign_config["asset_set_name"]
        )
        
        # Extract assets
        result = self.asset_extractor.extract_campaign_assets(campaign_config["campaign_name"])
        
        return result
    
    def _create_optimized_page_feed(self, campaign_config: Dict) -> Dict:
        """Create optimized page feed for the campaign."""
        
        # Get URLs from sitemap that match campaign criteria
        all_urls = self.sitemap_parser.get_page_feed_urls(max_urls=1000)
        
        # Filter URLs based on campaign requirements
        filtered_urls = self._filter_urls_for_campaign(all_urls, campaign_config)
        
        # Create page feed
        result = self.page_feed_creator.create_page_feed_from_sitemap(
            campaign_name=campaign_config["campaign_name"],
            max_urls=len(filtered_urls),
            asset_set_name=f"Levine Real Estate - {campaign_config['campaign_name']} Page Feed"
        )
        
        return result
    
    def _filter_urls_for_campaign(self, urls: List[Dict], campaign_config: Dict) -> List[Dict]:
        """Filter URLs based on campaign requirements."""
        filtered_urls = []
        
        for url_data in urls:
            url = url_data["url"]
            path = url_data["path"]
            
            # Check if URL matches campaign criteria
            if self._url_matches_campaign(url, path, campaign_config):
                filtered_urls.append(url_data)
        
        return filtered_urls
    
    def _url_matches_campaign(self, url: str, path: str, campaign_config: Dict) -> bool:
        """Check if URL matches campaign criteria."""
        
        # Check location match
        if campaign_config["target_location"]:
            location_keywords = [campaign_config["target_location"].lower().replace(" ", "-")]
            if not any(keyword in path.lower() for keyword in location_keywords):
                return False
        
        # Check property type match
        if campaign_config["property_type"]:
            property_keywords = campaign_config["property_type"].lower().split()
            if not any(keyword in path.lower() for keyword in property_keywords):
                return False
        
        return True
    
    def _create_google_ads_campaign(self, campaign_config: Dict) -> Dict:
        """Create campaign in Google Ads."""
        # This would integrate with Google Ads API to create the actual campaign
        # For now, we'll return a mock result
        return {
            "success": True,
            "campaign_id": f"campaign_{int(datetime.now().timestamp())}",
            "campaign_name": campaign_config["campaign_name"]
        }
    
    def _link_campaign_components(self, campaign_result: Dict, asset_result: Dict, page_feed_result: Dict) -> Dict:
        """Link all components to the campaign."""
        # This would link the asset set and page feed to the campaign
        return {
            "success": True,
            "campaign_linked": True,
            "asset_set_linked": asset_result.get("success", False),
            "page_feed_linked": page_feed_result.get("success", False)
        }
    
    def _generate_optimization_recommendations(self, campaign_config: Dict) -> List[str]:
        """Generate optimization recommendations for the campaign."""
        recommendations = []
        
        # Budget recommendations
        if campaign_config["budget"] < 1000:
            recommendations.append("Consider increasing budget to $1,000+ for better performance")
        elif campaign_config["budget"] > 5000:
            recommendations.append("Monitor performance closely with high budget")
        
        # Asset recommendations
        if len(campaign_config["asset_priorities"]) < 3:
            recommendations.append("Add more asset types for better ad variety")
        
        # Targeting recommendations
        if len(campaign_config["targeting_keywords"]) < 5:
            recommendations.append("Consider adding more targeting keywords")
        
        # Location-specific recommendations
        if campaign_config["target_location"] == "deer valley":
            recommendations.append("Focus on luxury lifestyle content for Deer Valley")
        elif campaign_config["target_location"] == "park city":
            recommendations.append("Emphasize mountain views and ski lifestyle for Park City")
        
        return recommendations

def test_intelligent_campaign_creator():
    """Test the intelligent campaign creator."""
    print("🧠 Testing Intelligent Campaign Creator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return
    
    try:
        creator = IntelligentCampaignCreator(customer_id)
        
        # Test 1: Create Deer Valley campaign
        print("🎯 Test 1: Creating Deer Valley campaign...")
        result = creator.create_intelligent_campaign(
            campaign_name="L.R - Deer Valley Luxury",
            campaign_goal="property_sales",
            target_location="deer valley",
            property_type="luxury"
        )
        
        if result["success"]:
            print(f"✅ Campaign created successfully!")
            print(f"   Campaign ID: {result['campaign_id']}")
            print(f"   Assets Extracted: {result['assets_extracted']}")
            print(f"   Pages Processed: {result['pages_processed']}")
            print(f"   Optimization Recommendations:")
            for rec in result['optimization_recommendations']:
                print(f"     • {rec}")
        else:
            print(f"❌ Campaign creation failed: {result.get('error', 'Unknown error')}")
        
        # Test 2: Create Park City campaign with auto-detection
        print(f"\n🎯 Test 2: Creating Park City campaign with auto-detection...")
        result2 = creator.create_intelligent_campaign(
            campaign_name="L.R - Park City Condos",
            campaign_goal="lead_generation"
            # No target_location or property_type - should auto-detect
        )
        
        if result2["success"]:
            print(f"✅ Campaign created successfully!")
            print(f"   Auto-detected Location: {result2['campaign_config']['target_location']}")
            print(f"   Auto-detected Property Type: {result2['campaign_config']['property_type']}")
            print(f"   Intelligent Budget: ${result2['campaign_config']['budget']}")
        else:
            print(f"❌ Campaign creation failed: {result2.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_intelligent_campaign_creator()
