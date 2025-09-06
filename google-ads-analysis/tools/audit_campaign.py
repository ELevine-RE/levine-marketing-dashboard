#!/usr/bin/env python3
"""
Campaign Audit Tool
===================

Simple command-line interface for auditing Google Ads campaigns.
"""

import os
import sys
import argparse
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.campaign_auditor import CampaignAuditor
from dotenv import load_dotenv

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Campaign Audit Tool")
    parser.add_argument("--customer", required=True, help="Google Ads Customer ID")
    parser.add_argument("--manager", help="Google Ads Manager Customer ID")
    parser.add_argument("--campaign", default="L.R - PMax - General", help="Campaign name to audit")
    parser.add_argument("--output", help="Output file for audit results")
    parser.add_argument("--verbose", action="store_true", help="Show detailed analysis")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    try:
        auditor = CampaignAuditor(args.customer, args.manager)
        
        print(f"🔍 Auditing campaign: {args.campaign}")
        print("=" * 60)
        
        result = auditor.audit_campaign(args.campaign)
        
        if result["success"]:
            print(f"✅ Campaign audit completed successfully!")
            print(f"   Campaign: {result['campaign_name']}")
            print(f"   Audit File: {auditor.audit_file}")
            
            # Show summary
            summary = result["summary"]
            print(f"\n📊 Audit Summary:")
            print(f"   Overall Status: {summary['overall_status']}")
            print(f"   Total Recommendations: {summary['total_recommendations']}")
            print(f"   High Priority: {summary['high_priority']}")
            print(f"   Medium Priority: {summary['medium_priority']}")
            print(f"   Low Priority: {summary['low_priority']}")
            
            # Show campaign data
            campaign_data = result["campaign_data"]
            print(f"\n📋 Campaign Data:")
            print(f"   Campaign ID: {campaign_data['id']}")
            print(f"   Status: {campaign_data['status']}")
            print(f"   Type: {campaign_data['channel_type']}")
            print(f"   Budget: ${campaign_data['budget_amount']}")
            print(f"   Bidding Strategy: {campaign_data['bidding_strategy']}")
            if campaign_data.get('target_cpa'):
                print(f"   Target CPA: ${campaign_data['target_cpa']}")
            if campaign_data.get('target_roas'):
                print(f"   Target ROAS: {campaign_data['target_roas']}")
            
            # Show performance data
            performance = result["analysis"]["performance"]
            if performance.get("status") != "no_data":
                print(f"\n📈 Performance Data:")
                print(f"   Total Impressions: {performance['total_impressions']:,}")
                print(f"   Total Clicks: {performance['total_clicks']:,}")
                print(f"   Total Cost: ${performance['total_cost']:.2f}")
                print(f"   Total Conversions: {performance['total_conversions']}")
                print(f"   Average CTR: {performance['avg_ctr']:.2f}%")
                print(f"   Average CPC: ${performance['avg_cpc']:.2f}")
                print(f"   Conversion Rate: {performance['conversion_rate']:.2f}%")
                print(f"   Cost per Conversion: ${performance['cost_per_conversion']:.2f}")
            else:
                print(f"\n📈 Performance Data: No data available (campaign too new)")
            
            # Show asset data
            assets = result["analysis"]["assets"]
            print(f"\n🖼️ Asset Data:")
            print(f"   Total Assets: {assets['total_assets']}")
            print(f"   Asset Types: {', '.join(assets['asset_types'].keys())}")
            print(f"   Asset Sets: {', '.join(assets['asset_sets'].keys())}")
            
            # Show targeting data
            targeting = result["analysis"]["targeting"]
            print(f"\n🎯 Targeting Data:")
            print(f"   Total Keywords: {targeting['total_keywords']}")
            if targeting['match_types']:
                print(f"   Match Types: {', '.join(targeting['match_types'].keys())}")
            print(f"   High Performing Keywords: {targeting['keyword_performance']['high_performing']}")
            print(f"   Low Performing Keywords: {targeting['keyword_performance']['low_performing']}")
            
            # Show recommendations
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result["recommendations"], 1):
                print(f"   {i}. [{rec['priority']}] {rec['recommendation']}")
                print(f"      Issue: {rec['issue']}")
                print(f"      Impact: {rec['impact']}")
                print()
            
            # Show strengths and issues
            if args.verbose:
                print(f"\n✅ Strengths:")
                for analysis_type, analysis in result["analysis"].items():
                    if analysis.get("strengths"):
                        print(f"   {analysis_type.title()}:")
                        for strength in analysis["strengths"]:
                            print(f"     • {strength}")
                
                print(f"\n⚠️ Issues:")
                for analysis_type, analysis in result["analysis"].items():
                    if analysis.get("issues"):
                        print(f"   {analysis_type.title()}:")
                        for issue in analysis["issues"]:
                            print(f"     • {issue}")
            
            # Save to output file if specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Audit results saved to: {args.output}")
            
        else:
            print(f"❌ Campaign audit failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
