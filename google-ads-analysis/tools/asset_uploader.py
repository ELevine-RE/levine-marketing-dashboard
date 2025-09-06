#!/usr/bin/env python3
"""
Asset Uploader
=============

Automatically uploads extracted assets to Google Ads campaigns.
"""

import os
import json
from typing import Dict, List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class AssetUploader:
    """Uploads assets to Google Ads campaigns."""
    
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.client = GoogleAdsClient.load_from_storage()
        self.asset_service = self.client.get_service("AssetService")
        self.campaign_asset_service = self.client.get_service("CampaignAssetService")
    
    def upload_image_asset(self, filepath: str, asset_name: str) -> Optional[str]:
        """Upload an image asset to Google Ads."""
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

def upload_extracted_assets_to_campaign(customer_id: str, campaign_id: str) -> Dict:
    """Upload extracted assets to a specific campaign."""
    from tools.asset_extractor import get_google_ads_asset_list
    
    # Get extracted assets
    assets = get_google_ads_asset_list()
    
    # Upload to Google Ads
    uploader = AssetUploader(customer_id)
    results = uploader.upload_asset_batch(assets, campaign_id)
    
    return results
