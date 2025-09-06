#!/usr/bin/env python3
"""
Execute Crawl/Walk Strategy
==========================

Command-line interface to execute the Crawl/Walk campaign strategy.
"""

import os
import sys
import argparse
from datetime import datetime

# Add the tools directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from crawl_walk_campaign_creator import CrawlWalkCampaignCreator
from enhanced_quick_analysis import EnhancedQuickAnalysis

def execute_crawl_walk():
    """Execute the complete Crawl/Walk strategy"""
    print("🚀 Executing Crawl/Walk Strategy")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize creator
    creator = CrawlWalkCampaignCreator()
    
    # Part 1: Create Crawl Campaign
    print("📊 Part 1: Creating 'Crawl' Campaign (Local Presence)")
    print("-" * 50)
    
    crawl_result = creator.create_crawl_campaign()
    
    if crawl_result["success"]:
        print("✅ Crawl campaign created successfully!")
        print(f"   Campaign ID: {crawl_result['campaign_id']}")
        print(f"   Campaign Name: {crawl_result['campaign_name']}")
        print(f"   Budget: {crawl_result['budget']}")
        print(f"   Status: {crawl_result['status']}")
    else:
        print(f"❌ Failed to create crawl campaign: {crawl_result['error']}")
        return False
    
    print()
    
    # Part 2: Create Walk Schedule Document
    print("📝 Part 2: Creating 'Walk' Schedule Document (Feeder Markets)")
    print("-" * 50)
    
    walk_result = creator.create_walk_schedule_doc()
    
    if walk_result["success"]:
        print("✅ Walk schedule document created successfully!")
        print(f"   Document URL: {walk_result['doc_url']}")
        print(f"   Document Title: {walk_result['title']}")
    else:
        print(f"❌ Failed to create walk schedule document: {walk_result['error']}")
        return False
    
    print()
    
    # Part 3: Test Milestone Detection
    print("🔍 Part 3: Testing Milestone Detection System")
    print("-" * 50)
    
    analyzer = EnhancedQuickAnalysis()
    analysis_result = analyzer.analyze_campaigns()
    
    if analysis_result.get('success', True):
        print("✅ Milestone detection system is working!")
        print(f"   Campaigns analyzed: {len(analysis_result['campaigns'])}")
        print(f"   Milestones detected: {len(analysis_result['milestones'])}")
        
        # Show campaign phases
        for campaign in analysis_result['campaigns']:
            print(f"   {campaign['campaign_info']['name']}: {campaign['phase']}")
    else:
        print(f"❌ Milestone detection failed: {analysis_result.get('error', 'Unknown error')}")
    
    print()
    print("🎉 Crawl/Walk Strategy Execution Complete!")
    print("=" * 50)
    print("Next Steps:")
    print("1. Monitor 'Local Presence' campaign performance")
    print("2. Wait for Phase 1 exit (15-30 conversions)")
    print("3. Review scheduled document when ready to launch 'Feeder Markets'")
    print("4. Run daily analysis to detect milestones")
    
    return True

def run_daily_analysis():
    """Run daily analysis for milestone detection"""
    print("🔍 Running Daily Analysis")
    print("=" * 30)
    
    analyzer = EnhancedQuickAnalysis()
    results = analyzer.run_daily_analysis()
    
    if results.get('success', True):
        print("✅ Daily analysis completed successfully")
        
        # Print summary
        summary = results['summary']
        print(f"\n📊 Summary:")
        print(f"   Total Campaigns: {summary['total_campaigns']}")
        print(f"   Active Campaigns: {summary['active_campaigns']}")
        print(f"   Total Cost: ${summary['total_cost']:.2f}")
        print(f"   Total Conversions: {summary['total_conversions']}")
        print(f"   Milestones Detected: {summary['milestones_detected']}")
        
        # Print milestones
        if results['milestones']:
            print(f"\n🚨 Milestones Detected:")
            for milestone in results['milestones']:
                print(f"   {milestone['campaign_name']}: {milestone['message']}")
                print(f"   Action Required: {milestone['action_required']}")
        
    else:
        print(f"❌ Daily analysis failed: {results.get('error', 'Unknown error')}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Execute Crawl/Walk Campaign Strategy')
    parser.add_argument('command', choices=['execute', 'analyze'], 
                       help='Command to run: execute (full strategy) or analyze (daily analysis)')
    
    args = parser.parse_args()
    
    if args.command == 'execute':
        success = execute_crawl_walk()
        sys.exit(0 if success else 1)
    elif args.command == 'analyze':
        run_daily_analysis()
        sys.exit(0)

if __name__ == "__main__":
    main()
