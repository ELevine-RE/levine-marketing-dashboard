#!/usr/bin/env python3
"""
Campaign Asset Manager
======================

Command-line interface for managing campaign-specific asset extraction.
"""

import os
import sys
import argparse
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.campaign_asset_extractor import CampaignAssetExtractor
from dotenv import load_dotenv

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Campaign Asset Manager")
    parser.add_argument("--customer", required=True, help="Google Ads Customer ID")
    parser.add_argument("--manager", help="Google Ads Manager Customer ID")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List campaigns command
    list_parser = subparsers.add_parser("list", help="List all configured campaigns")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get status of a campaign")
    status_parser.add_argument("campaign", help="Campaign name")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract assets for a campaign")
    extract_parser.add_argument("campaign", help="Campaign name")
    
    # Add campaign command
    add_parser = subparsers.add_parser("add", help="Add a new campaign configuration")
    add_parser.add_argument("campaign", help="Campaign name")
    add_parser.add_argument("--pages", nargs="+", required=True, help="Landing page URLs")
    add_parser.add_argument("--children", action="store_true", default=True, help="Include child pages")
    add_parser.add_argument("--depth", type=int, default=2, help="Maximum depth for child pages")
    add_parser.add_argument("--asset-set", help="Custom asset set name")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test asset extraction for a campaign")
    test_parser.add_argument("campaign", help="Campaign name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load environment variables
    load_dotenv()
    
    try:
        extractor = CampaignAssetExtractor(args.customer, args.manager)
        
        if args.command == "list":
            campaigns = extractor.list_campaigns()
            print("📋 Configured Campaigns:")
            print("=" * 40)
            for campaign in campaigns:
                status = extractor.get_campaign_status(campaign)
                print(f"• {campaign}")
                print(f"  Landing Pages: {len(status['landing_pages'])}")
                print(f"  Include Children: {status['include_children']}")
                print(f"  Max Depth: {status['max_depth']}")
                print(f"  Asset Set: {status['asset_set_name']}")
                print(f"  Enabled: {status['enabled']}")
                print()
        
        elif args.command == "status":
            status = extractor.get_campaign_status(args.campaign)
            if "error" in status:
                print(f"❌ {status['error']}")
            else:
                print(f"📊 Campaign Status: {args.campaign}")
                print("=" * 40)
                print(f"Landing Pages: {len(status['landing_pages'])}")
                for page in status['landing_pages']:
                    print(f"  • {page}")
                print(f"Include Children: {status['include_children']}")
                print(f"Max Depth: {status['max_depth']}")
                print(f"Asset Set: {status['asset_set_name']}")
                print(f"Enabled: {status['enabled']}")
        
        elif args.command == "extract":
            print(f"🚀 Extracting assets for campaign: {args.campaign}")
            result = extractor.extract_campaign_assets(args.campaign)
            
            if result["success"]:
                print(f"✅ Asset extraction completed successfully!")
                print(f"   Pages Processed: {result['pages_processed']}")
                print(f"   Total Assets: {result['total_assets']}")
                print(f"   Images: {result['images_extracted']}")
                print(f"   Videos: {result['videos_extracted']}")
                print(f"   Asset Set ID: {result['asset_set_id']}")
                print(f"   Campaign Linked: {result['campaign_linked']}")
            else:
                print(f"❌ Asset extraction failed: {result.get('error', 'Unknown error')}")
        
        elif args.command == "add":
            success = extractor.add_campaign_config(
                campaign_name=args.campaign,
                landing_pages=args.pages,
                include_children=args.children,
                max_depth=args.depth,
                asset_set_name=args.asset_set
            )
            
            if success:
                print(f"✅ Added campaign configuration: {args.campaign}")
                print(f"   Landing Pages: {len(args.pages)}")
                print(f"   Include Children: {args.children}")
                print(f"   Max Depth: {args.depth}")
                print(f"   Asset Set: {args.asset_set or f'Levine Real Estate - {args.campaign} Assets'}")
            else:
                print(f"❌ Failed to add campaign configuration")
        
        elif args.command == "test":
            print(f"🧪 Testing asset extraction for campaign: {args.campaign}")
            result = extractor.extract_campaign_assets(args.campaign)
            
            if result["success"]:
                print(f"✅ Test completed successfully!")
                print(f"   Pages Processed: {result['pages_processed']}")
                print(f"   Total Assets: {result['total_assets']}")
                print(f"   Images: {result['images_extracted']}")
                print(f"   Videos: {result['videos_extracted']}")
                print(f"   Pages:")
                for page in result.get("pages", [])[:5]:  # Show first 5 pages
                    print(f"     • {page}")
                if len(result.get("pages", [])) > 5:
                    print(f"     ... and {len(result['pages']) - 5} more")
            else:
                print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
