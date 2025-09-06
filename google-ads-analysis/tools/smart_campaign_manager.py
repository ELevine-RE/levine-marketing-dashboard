#!/usr/bin/env python3
"""
Smart Campaign Manager
======================

Simple command-line interface for creating intelligent campaigns with automatic asset optimization.
"""

import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.intelligent_campaign_creator import IntelligentCampaignCreator
from dotenv import load_dotenv

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Smart Campaign Manager")
    parser.add_argument("--customer", required=True, help="Google Ads Customer ID")
    parser.add_argument("--manager", help="Google Ads Manager Customer ID")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create campaign command
    create_parser = subparsers.add_parser("create", help="Create an intelligent campaign")
    create_parser.add_argument("campaign", help="Campaign name")
    create_parser.add_argument("--goal", choices=["lead_generation", "brand_awareness", "property_sales"], 
                             default="lead_generation", help="Campaign goal")
    create_parser.add_argument("--location", help="Target location (e.g., 'deer valley', 'park city')")
    create_parser.add_argument("--property-type", help="Property type (e.g., 'luxury', 'condo', 'single family')")
    create_parser.add_argument("--budget", type=float, help="Campaign budget")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test campaign creation")
    test_parser.add_argument("campaign", help="Campaign name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load environment variables
    load_dotenv()
    
    try:
        creator = IntelligentCampaignCreator(args.customer, args.manager)
        
        if args.command == "create":
            print(f"🧠 Creating intelligent campaign: {args.campaign}")
            print("=" * 60)
            
            result = creator.create_intelligent_campaign(
                campaign_name=args.campaign,
                campaign_goal=args.goal,
                target_location=args.location,
                property_type=args.property_type,
                budget=args.budget
            )
            
            if result["success"]:
                print(f"✅ Campaign created successfully!")
                print(f"   Campaign ID: {result['campaign_id']}")
                print(f"   Campaign Name: {result['campaign_name']}")
                print(f"   Target Location: {result['campaign_config']['target_location']}")
                print(f"   Property Type: {result['campaign_config']['property_type']}")
                print(f"   Budget: ${result['campaign_config']['budget']}")
                print(f"   Campaign Type: {result['campaign_config']['campaign_type']}")
                print(f"   Landing Pages: {len(result['campaign_config']['landing_pages'])}")
                print(f"   Pages Processed: {result['pages_processed']}")
                print(f"   Assets Extracted: {result['assets_extracted']}")
                print(f"   Images: {result['images_extracted']}")
                print(f"   Videos: {result['videos_extracted']}")
                print(f"   Campaign Linked: {result['campaign_linked']}")
                
                print(f"\n📊 Optimization Recommendations:")
                for rec in result['optimization_recommendations']:
                    print(f"   • {rec}")
                
                print(f"\n🎯 Campaign Configuration:")
                print(f"   Asset Priorities: {', '.join(result['campaign_config']['asset_priorities'])}")
                print(f"   Targeting Keywords: {', '.join(result['campaign_config']['targeting_keywords'])}")
                
            else:
                print(f"❌ Campaign creation failed: {result.get('error', 'Unknown error')}")
        
        elif args.command == "test":
            print(f"🧪 Testing campaign creation: {args.campaign}")
            print("=" * 60)
            
            result = creator.create_intelligent_campaign(
                campaign_name=args.campaign,
                campaign_goal="lead_generation"
            )
            
            if result["success"]:
                print(f"✅ Test completed successfully!")
                print(f"   Auto-detected Location: {result['campaign_config']['target_location']}")
                print(f"   Auto-detected Property Type: {result['campaign_config']['property_type']}")
                print(f"   Intelligent Budget: ${result['campaign_config']['budget']}")
                print(f"   Landing Pages: {len(result['campaign_config']['landing_pages'])}")
                print(f"   Assets Extracted: {result['assets_extracted']}")
                print(f"   Pages Processed: {result['pages_processed']}")
            else:
                print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
