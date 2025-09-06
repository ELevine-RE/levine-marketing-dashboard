#!/usr/bin/env python3
"""
Asset Manager
============

Consolidated asset management system that handles extraction, validation,
and uploading of assets for Google Ads campaigns.
"""

import os
import json
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from PIL import Image
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class AssetManager:
    """Consolidated asset management for Google Ads campaigns."""
    
    def __init__(self, customer_id: str = None, base_url: str = "https://levine.realestate"):
        self.base_url = base_url
        self.customer_id = customer_id
        self.assets_dir = "data/extracted_assets"
        self.asset_manifest_file = "data/asset_manifest.json"
        self.load_manifest()
        
        # Google Ads asset requirements
        self.asset_requirements = {
            "images": {
                "formats": ["1.91:1", "1:1", "4:3"],
                "min_size": (600, 600),
                "max_size": (1200, 1200),
                "file_types": [".jpg", ".jpeg", ".png"]
            },
            "logos": {
                "formats": ["1:1", "4:1"],
                "min_size": (128, 128),
                "max_size": (512, 512),
                "file_types": [".png", ".jpg"]
            },
            "videos": {
                "formats": ["16:9", "9:16", "1:1"],
                "min_duration": 6,
                "max_duration": 60,
                "file_types": [".mp4", ".mov"]
            }
        }
        
        # PMax specific requirements
        self.pmax_requirements = {
            'headlines': {'min': 5, 'aim': (7, 10)},
            'long_headlines': {'min': 1, 'aim': (1, 2)},
            'descriptions': {'min': 2, 'aim': (3, 4)},
            'business_name': {'required': True},
            'logos': {
                '1_1': {'min': 1, 'aim': (1, 2)},
                '4_1': {'min': 1, 'aim': (1, 2)}
            },
            'images': {
                '1_91_1': {'min': 3, 'aim': (3, 5)},
                '1_1': {'min': 3, 'aim': (3, 5)}
            },
            'video': {'min': 1, 'auto_gen_allowed': True}
        }
        
        # Initialize Google Ads client if customer_id provided
        if self.customer_id:
            self.client = GoogleAdsClient.load_from_storage()
            self.asset_service = self.client.get_service("AssetService")
            self.campaign_asset_service = self.client.get_service("CampaignAssetService")
    
    def load_manifest(self):
        """Load existing asset manifest."""
        if os.path.exists(self.asset_manifest_file):
            with open(self.asset_manifest_file, 'r') as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {
                "assets": [],
                "last_extraction": None,
                "total_assets": 0
            }
    
    def save_manifest(self):
        """Save asset manifest."""
        os.makedirs('data', exist_ok=True)
        with open(self.asset_manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def extract_assets_from_page(self, page_url: str) -> Dict:
        """Extract all assets from a specific page."""
        try:
            response = requests.get(page_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            assets = {
                "page_url": page_url,
                "images": [],
                "logos": [],
                "videos": [],
                "text_content": [],
                "extracted_at": datetime.now().isoformat()
            }
            
            # Extract images
            images = soup.find_all('img')
            for img in images:
                img_url = img.get('src')
                if img_url:
                    full_url = urljoin(page_url, img_url)
                    if self._is_valid_image_url(full_url):
                        image_asset = self._process_image(full_url, img)
                        if image_asset:
                            assets["images"].append(image_asset)
            
            # Extract videos
            videos = soup.find_all(['video', 'iframe'])
            for video in videos:
                video_url = video.get('src') or video.get('data-src')
                if video_url:
                    full_url = urljoin(page_url, video_url)
                    if self._is_valid_video_url(full_url):
                        video_asset = self._process_video(full_url, video)
                        if video_asset:
                            assets["videos"].append(video_asset)
            
            # Extract text content for headlines/descriptions
            text_content = self._extract_text_content(soup)
            assets["text_content"] = text_content
            
            return assets
            
        except Exception as e:
            print(f"Error extracting assets from {page_url}: {str(e)}")
            return {"page_url": page_url, "error": str(e)}
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image."""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        return any(url.lower().endswith(ext) for ext in valid_extensions)
    
    def _is_valid_video_url(self, url: str) -> bool:
        """Check if URL is a valid video."""
        valid_extensions = ['.mp4', '.mov', '.avi', '.webm']
        return any(url.lower().endswith(ext) for ext in valid_extensions)
    
    def _process_image(self, image_url: str, img_element) -> Optional[Dict]:
        """Process and validate an image asset."""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Get image dimensions
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            
            # Calculate aspect ratio
            aspect_ratio = width / height
            
            # Determine asset type based on dimensions and context
            asset_type = self._classify_image_asset(img_element, width, height, aspect_ratio)
            
            # Generate unique filename
            filename = self._generate_filename(image_url, "image")
            
            # Save image
            filepath = os.path.join(self.assets_dir, filename)
            os.makedirs(self.assets_dir, exist_ok=True)
            img.save(filepath)
            
            return {
                "url": image_url,
                "filename": filename,
                "filepath": filepath,
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio,
                "asset_type": asset_type,
                "alt_text": img_element.get('alt', ''),
                "file_size": len(response.content),
                "meets_requirements": self._check_image_requirements(width, height, asset_type)
            }
            
        except Exception as e:
            print(f"Error processing image {image_url}: {str(e)}")
            return None
    
    def _process_video(self, video_url: str, video_element) -> Optional[Dict]:
        """Process and validate a video asset."""
        try:
            # For now, just extract metadata (full video processing would require more complex logic)
            return {
                "url": video_url,
                "asset_type": "video",
                "title": video_element.get('title', ''),
                "meets_requirements": True  # Would need actual video analysis
            }
            
        except Exception as e:
            print(f"Error processing video {video_url}: {str(e)}")
            return None
    
    def _classify_image_asset(self, img_element, width: int, height: int, aspect_ratio: float) -> str:
        """Classify image as logo, hero image, or general image."""
        # Check for logo indicators
        alt_text = img_element.get('alt', '').lower()
        class_names = img_element.get('class', [])
        
        if any(word in alt_text for word in ['logo', 'brand']) or \
           any('logo' in cls.lower() for cls in class_names) or \
           (width < 200 and height < 200):
            return "logo"
        elif width > 800 and height > 600:
            return "hero_image"
        else:
            return "general_image"
    
    def _check_image_requirements(self, width: int, height: int, asset_type: str) -> bool:
        """Check if image meets Google Ads requirements."""
        requirements = self.asset_requirements["images"] if asset_type != "logo" else self.asset_requirements["logos"]
        
        min_width, min_height = requirements["min_size"]
        max_width, max_height = requirements["max_size"]
        
        return min_width <= width <= max_width and min_height <= height <= max_height
    
    def _extract_text_content(self, soup) -> List[Dict]:
        """Extract text content for headlines and descriptions."""
        text_content = []
        
        # Extract headings
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            text = heading.get_text().strip()
            if len(text) > 10 and len(text) < 90:  # Good headline length
                text_content.append({
                    "type": "headline",
                    "text": text,
                    "tag": heading.name,
                    "length": len(text)
                })
        
        # Extract paragraphs for descriptions
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 30 and len(text) < 150:  # Good description length
                text_content.append({
                    "type": "description",
                    "text": text,
                    "length": len(text)
                })
        
        return text_content
    
    def _generate_filename(self, url: str, asset_type: str) -> str:
        """Generate unique filename for asset."""
        # Create hash from URL
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Get file extension
        parsed_url = urlparse(url)
        extension = os.path.splitext(parsed_url.path)[1]
        if not extension:
            extension = '.jpg'  # Default
        
        return f"{asset_type}_{url_hash}{extension}"
    
    def extract_from_saved_searches(self, search_results: List[str]) -> Dict:
        """Extract assets from a list of saved search result URLs."""
        all_assets = {
            "extraction_date": datetime.now().isoformat(),
            "pages_processed": 0,
            "total_assets": 0,
            "assets_by_type": {
                "images": [],
                "logos": [],
                "videos": [],
                "text_content": []
            },
            "recommendations": []
        }
        
        for page_url in search_results:
            print(f"Processing: {page_url}")
            page_assets = self.extract_assets_from_page(page_url)
            
            if "error" not in page_assets:
                all_assets["pages_processed"] += 1
                
                # Aggregate assets
                for asset_type in ["images", "logos", "videos", "text_content"]:
                    if asset_type in page_assets:
                        all_assets["assets_by_type"][asset_type].extend(page_assets[asset_type])
                        all_assets["total_assets"] += len(page_assets[asset_type])
        
        # Generate recommendations
        all_assets["recommendations"] = self._generate_asset_recommendations(all_assets["assets_by_type"])
        
        # Update manifest
        self._update_manifest(all_assets)
        
        return all_assets
    
    def _generate_asset_recommendations(self, assets_by_type: Dict) -> List[str]:
        """Generate recommendations for asset optimization."""
        recommendations = []
        
        # Check image requirements
        images = assets_by_type.get("images", [])
        logos = assets_by_type.get("logos", [])
        videos = assets_by_type.get("videos", [])
        
        if len(images) < 5:
            recommendations.append("Need more images for Google Ads (minimum 5 recommended)")
        
        if len(logos) < 2:
            recommendations.append("Need more logos for different formats (1:1 and 4:1)")
        
        if len(videos) == 0:
            recommendations.append("Consider adding video content for better ad performance")
        
        # Check for specific formats
        aspect_ratios = [img["aspect_ratio"] for img in images]
        if not any(0.9 < ratio < 1.1 for ratio in aspect_ratios):
            recommendations.append("Need square format images (1:1 aspect ratio)")
        
        if not any(1.8 < ratio < 2.0 for ratio in aspect_ratios):
            recommendations.append("Need landscape format images (1.91:1 aspect ratio)")
        
        return recommendations
    
    def _update_manifest(self, extraction_results: Dict):
        """Update asset manifest with new extraction results."""
        self.manifest["last_extraction"] = extraction_results["extraction_date"]
        self.manifest["total_assets"] = extraction_results["total_assets"]
        
        # Add new assets to manifest
        for asset_type, assets in extraction_results["assets_by_type"].items():
            for asset in assets:
                if "filename" in asset:  # Only track saved assets
                    self.manifest["assets"].append({
                        "filename": asset["filename"],
                        "asset_type": asset_type,
                        "extracted_at": extraction_results["extraction_date"],
                        "meets_requirements": asset.get("meets_requirements", False)
                    })
        
        self.save_manifest()
    
    def validate_asset_group_requirements(self, asset_group: Dict) -> Dict:
        """Validate if asset group meets PMax requirements."""
        missing = []
        asset_counts = asset_group.get('asset_counts', {})
        
        # Check headlines
        headlines = asset_counts.get('headlines', 0)
        if headlines < self.pmax_requirements['headlines']['min']:
            missing.append(f"headlines ({headlines}/{self.pmax_requirements['headlines']['min']})")
        
        # Check long headlines
        long_headlines = asset_counts.get('long_headlines', 0)
        if long_headlines < self.pmax_requirements['long_headlines']['min']:
            missing.append(f"long headlines ({long_headlines}/{self.pmax_requirements['long_headlines']['min']})")
        
        # Check descriptions
        descriptions = asset_counts.get('descriptions', 0)
        if descriptions < self.pmax_requirements['descriptions']['min']:
            missing.append(f"descriptions ({descriptions}/{self.pmax_requirements['descriptions']['min']})")
        
        # Check business name
        if self.pmax_requirements['business_name']['required']:
            business_name = asset_counts.get('business_name', 0)
            if business_name < 1:
                missing.append("business name")
        
        # Check logos
        logos_1_1 = asset_counts.get('logos_1_1', 0)
        logos_4_1 = asset_counts.get('logos_4_1', 0)
        if logos_1_1 < self.pmax_requirements['logos']['1_1']['min']:
            missing.append(f"1:1 logos ({logos_1_1}/{self.pmax_requirements['logos']['1_1']['min']})")
        if logos_4_1 < self.pmax_requirements['logos']['4_1']['min']:
            missing.append(f"4:1 logos ({logos_4_1}/{self.pmax_requirements['logos']['4_1']['min']})")
        
        # Check images
        images_1_91_1 = asset_counts.get('images_1_91_1', 0)
        images_1_1 = asset_counts.get('images_1_1', 0)
        if images_1_91_1 < self.pmax_requirements['images']['1_91_1']['min']:
            missing.append(f"1.91:1 images ({images_1_91_1}/{self.pmax_requirements['images']['1_91_1']['min']})")
        if images_1_1 < self.pmax_requirements['images']['1_1']['min']:
            missing.append(f"1:1 images ({images_1_1}/{self.pmax_requirements['images']['1_1']['min']})")
        
        # Check video
        videos = asset_counts.get('videos', 0)
        auto_gen_videos = asset_counts.get('auto_gen_videos', 0)
        if videos < self.pmax_requirements['video']['min'] and auto_gen_videos == 0:
            missing.append(f"videos ({videos}/{self.pmax_requirements['video']['min']})")
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'requirements': self.pmax_requirements
        }
    
    def upload_image_asset(self, filepath: str, asset_name: str) -> Optional[str]:
        """Upload an image asset to Google Ads."""
        if not self.customer_id:
            raise ValueError("Customer ID required for upload")
            
        try:
            # Read image file
            with open(filepath, 'rb') as image_file:
                image_data = image_file.read()
            
            # Create image asset
            image_asset = self.client.get_type("ImageAsset")
            image_asset.data = image_data
            image_asset.name = asset_name
            
            # Create asset operation
            asset_operation = self.client.get_type("AssetOperation")
            asset_operation.create = image_asset
            
            # Upload asset
            response = self.asset_service.mutate_assets(
                customer_id=self.customer_id,
                operations=[asset_operation]
            )
            
            if response.results:
                return response.results[0].resource_name
            
        except GoogleAdsException as ex:
            print(f"Google Ads error uploading {filepath}: {ex}")
        except Exception as e:
            print(f"Error uploading {filepath}: {str(e)}")
        
        return None
    
    def upload_text_asset(self, text: str, asset_type: str) -> Optional[str]:
        """Upload a text asset (headline/description) to Google Ads."""
        if not self.customer_id:
            raise ValueError("Customer ID required for upload")
            
        try:
            if asset_type == "headline":
                text_asset = self.client.get_type("TextAsset")
                text_asset.text = text
            elif asset_type == "description":
                text_asset = self.client.get_type("TextAsset")
                text_asset.text = text
            else:
                return None
            
            # Create asset operation
            asset_operation = self.client.get_type("AssetOperation")
            asset_operation.create = text_asset
            
            # Upload asset
            response = self.asset_service.mutate_assets(
                customer_id=self.customer_id,
                operations=[asset_operation]
            )
            
            if response.results:
                return response.results[0].resource_name
            
        except GoogleAdsException as ex:
            print(f"Google Ads error uploading text asset: {ex}")
        except Exception as e:
            print(f"Error uploading text asset: {str(e)}")
        
        return None
    
    def link_asset_to_campaign(self, campaign_id: str, asset_resource_name: str, asset_type: str):
        """Link an asset to a campaign."""
        if not self.customer_id:
            raise ValueError("Customer ID required for linking")
            
        try:
            # Create campaign asset
            campaign_asset = self.client.get_type("CampaignAsset")
            campaign_asset.campaign = self.client.get_service("CampaignService").campaign_path(
                self.customer_id, campaign_id
            )
            campaign_asset.asset = asset_resource_name
            
            # Set asset type
            if asset_type == "image":
                campaign_asset.field_type = self.client.enums.AssetFieldTypeEnum.IMAGE
            elif asset_type == "logo":
                campaign_asset.field_type = self.client.enums.AssetFieldTypeEnum.LOGO
            elif asset_type == "headline":
                campaign_asset.field_type = self.client.enums.AssetFieldTypeEnum.HEADLINE
            elif asset_type == "description":
                campaign_asset.field_type = self.client.enums.AssetFieldTypeEnum.DESCRIPTION
            
            # Create operation
            operation = self.client.get_type("CampaignAssetOperation")
            operation.create = campaign_asset
            
            # Link asset
            response = self.campaign_asset_service.mutate_campaign_assets(
                customer_id=self.customer_id,
                operations=[operation]
            )
            
            return response.results[0].resource_name if response.results else None
            
        except GoogleAdsException as ex:
            print(f"Google Ads error linking asset: {ex}")
        except Exception as e:
            print(f"Error linking asset: {str(e)}")
        
        return None
    
    def upload_asset_batch(self, assets: Dict, campaign_id: str) -> Dict:
        """Upload a batch of assets and link them to a campaign."""
        if not self.customer_id:
            raise ValueError("Customer ID required for batch upload")
            
        results = {
            "uploaded": [],
            "failed": [],
            "linked": [],
            "total_assets": 0
        }
        
        # Upload images
        for image in assets.get("images", []):
            results["total_assets"] += 1
            asset_name = f"Extracted_Image_{image['filename']}"
            
            resource_name = self.upload_image_asset(image["filepath"], asset_name)
            if resource_name:
                results["uploaded"].append({
                    "type": "image",
                    "filename": image["filename"],
                    "resource_name": resource_name
                })
                
                # Link to campaign
                link_result = self.link_asset_to_campaign(campaign_id, resource_name, "image")
                if link_result:
                    results["linked"].append(resource_name)
            else:
                results["failed"].append({
                    "type": "image",
                    "filename": image["filename"],
                    "error": "Upload failed"
                })
        
        # Upload logos
        for logo in assets.get("logos", []):
            results["total_assets"] += 1
            asset_name = f"Extracted_Logo_{logo['filename']}"
            
            resource_name = self.upload_image_asset(logo["filepath"], asset_name)
            if resource_name:
                results["uploaded"].append({
                    "type": "logo",
                    "filename": logo["filename"],
                    "resource_name": resource_name
                })
                
                # Link to campaign
                link_result = self.link_asset_to_campaign(campaign_id, resource_name, "logo")
                if link_result:
                    results["linked"].append(resource_name)
            else:
                results["failed"].append({
                    "type": "logo",
                    "filename": logo["filename"],
                    "error": "Upload failed"
                })
        
        # Upload text assets
        for headline in assets.get("headlines", []):
            results["total_assets"] += 1
            asset_name = f"Extracted_Headline_{headline['text'][:20]}"
            
            resource_name = self.upload_text_asset(headline["text"], "headline")
            if resource_name:
                results["uploaded"].append({
                    "type": "headline",
                    "text": headline["text"],
                    "resource_name": resource_name
                })
                
                # Link to campaign
                link_result = self.link_asset_to_campaign(campaign_id, resource_name, "headline")
                if link_result:
                    results["linked"].append(resource_name)
            else:
                results["failed"].append({
                    "type": "headline",
                    "text": headline["text"],
                    "error": "Upload failed"
                })
        
        for description in assets.get("descriptions", []):
            results["total_assets"] += 1
            asset_name = f"Extracted_Description_{description['text'][:20]}"
            
            resource_name = self.upload_text_asset(description["text"], "description")
            if resource_name:
                results["uploaded"].append({
                    "type": "description",
                    "text": description["text"],
                    "resource_name": resource_name
                })
                
                # Link to campaign
                link_result = self.link_asset_to_campaign(campaign_id, resource_name, "description")
                if link_result:
                    results["linked"].append(resource_name)
            else:
                results["failed"].append({
                    "type": "description",
                    "text": description["text"],
                    "error": "Upload failed"
                })
        
        return results
    
    def generate_google_ads_asset_list(self) -> Dict:
        """Generate formatted asset list for Google Ads upload."""
        assets_for_upload = {
            "images": [],
            "logos": [],
            "videos": [],
            "headlines": [],
            "descriptions": []
        }
        
        for asset in self.manifest["assets"]:
            if asset["meets_requirements"]:
                filepath = os.path.join(self.assets_dir, asset["filename"])
                if os.path.exists(filepath):
                    assets_for_upload[asset["asset_type"]].append({
                        "filepath": filepath,
                        "filename": asset["filename"],
                        "asset_type": asset["asset_type"]
                    })
        
        return assets_for_upload

def extract_assets_from_saved_searches(search_results: List[str]) -> Dict:
    """Extract assets from saved search results."""
    manager = AssetManager()
    return manager.extract_from_saved_searches(search_results)

def get_google_ads_asset_list() -> Dict:
    """Get formatted asset list for Google Ads."""
    manager = AssetManager()
    return manager.generate_google_ads_asset_list()

def upload_extracted_assets_to_campaign(customer_id: str, campaign_id: str) -> Dict:
    """Upload extracted assets to a specific campaign."""
    # Get extracted assets
    assets = get_google_ads_asset_list()
    
    # Upload to Google Ads
    manager = AssetManager(customer_id)
    results = manager.upload_asset_batch(assets, campaign_id)
    
    return results
