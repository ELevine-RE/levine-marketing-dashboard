#!/usr/bin/env python3
"""
Test Sitemap Automation
========================

Comprehensive test suite for the sitemap automation system.
Tests all components individually and as an integrated system.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sitemap_parser import SitemapParser
from tools.page_feed_creator import PageFeedCreator
from tools.sitemap_automation import SitemapAutomation
from dotenv import load_dotenv

def test_sitemap_parser():
    """Test the sitemap parser functionality."""
    print("🗺️ Testing Sitemap Parser")
    print("=" * 50)
    
    try:
        parser = SitemapParser()
        
        # Test 1: Fetch sitemap
        print("📋 Test 1: Fetching sitemap...")
        sitemap_content = parser.fetch_sitemap()
        if sitemap_content:
            print(f"✅ Successfully fetched sitemap ({len(sitemap_content)} characters)")
        else:
            print("❌ Failed to fetch sitemap")
            return False
        
        # Test 2: Parse sitemap
        print("\n📊 Test 2: Parsing sitemap...")
        urls = parser.parse_sitemap(sitemap_content)
        if urls:
            print(f"✅ Successfully parsed {len(urls)} URLs")
        else:
            print("❌ Failed to parse sitemap")
            return False
        
        # Test 3: Filter URLs
        print("\n🔍 Test 3: Filtering URLs...")
        filtered_urls = parser.filter_urls(urls)
        print(f"✅ Filtered to {len(filtered_urls)} relevant URLs")
        
        # Test 4: Show top URLs
        print(f"\n🎯 Top 10 URLs by Priority:")
        for i, url_data in enumerate(filtered_urls[:10], 1):
            print(f"  {i:2d}. {url_data['url']} (Score: {url_data['priority_score']:.1f})")
        
        # Test 5: Get statistics
        print(f"\n📈 URL Statistics:")
        stats = parser.get_url_statistics(filtered_urls)
        print(f"  Total URLs: {stats.get('total_urls', 0)}")
        print(f"  Unique Domains: {stats.get('unique_domains', 0)}")
        print(f"  Top Path Patterns:")
        for pattern, count in sorted(stats.get('path_patterns', {}).items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {pattern}: {count} URLs")
        
        return True
        
    except Exception as e:
        print(f"❌ Sitemap parser test failed: {e}")
        return False

def test_page_feed_creator():
    """Test the page feed creator functionality."""
    print("\n🎯 Testing Page Feed Creator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return False
    
    try:
        creator = PageFeedCreator(customer_id)
        
        # Test 1: Get existing page feeds
        print("📋 Test 1: Getting existing page feeds...")
        existing_feeds = creator.get_existing_page_feeds()
        print(f"✅ Found {len(existing_feeds)} existing page feeds")
        for feed in existing_feeds:
            print(f"   • {feed['name']} (ID: {feed['id']})")
        
        # Test 2: Create test page feed (dry run)
        print(f"\n🚀 Test 2: Creating test page feed...")
        result = creator.create_page_feed_from_sitemap(
            campaign_name="L.R - PMax - General",
            max_urls=5,  # Very small number for testing
            asset_set_name="Test Page Feed - " + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        
        if result["success"]:
            print(f"✅ Page feed created successfully!")
            print(f"   Asset Set ID: {result['asset_set_id']}")
            print(f"   URLs Processed: {result['urls_processed']}")
            print(f"   Assets Created: {result['assets_created']}")
            print(f"   Campaign Linked: {result['campaign_linked']}")
            
            # Test 3: Get URLs from created page feed
            print(f"\n📋 Test 3: Getting URLs from created page feed...")
            feed_urls = creator.get_page_feed_urls(result['asset_set_id'], limit=10)
            print(f"✅ Retrieved {len(feed_urls)} URLs from page feed")
            for i, url in enumerate(feed_urls[:5], 1):
                print(f"   {i}. {url}")
            
            return True
        else:
            print(f"❌ Page feed creation failed: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Page feed creator test failed: {e}")
        return False

def test_sitemap_automation():
    """Test the complete sitemap automation system."""
    print("\n🤖 Testing Sitemap Automation")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return False
    
    try:
        automation = SitemapAutomation(customer_id)
        
        # Test 1: Get status
        print("📊 Test 1: Getting automation status...")
        status = automation.get_status()
        print(f"✅ Automation status retrieved")
        print(f"   Total Runs: {status['total_runs']}")
        print(f"   Successful Runs: {status['successful_runs']}")
        print(f"   Success Rate: {status['success_rate']:.1f}%")
        print(f"   Last Run: {status['last_run']}")
        
        # Test 2: Run test automation
        print(f"\n🧪 Test 2: Running test automation...")
        result = automation.test_automation()
        
        if result["success"]:
            print(f"✅ Test automation completed successfully!")
            print(f"   URLs Processed: {result.get('urls_processed', 0)}")
            print(f"   Duration: {result.get('duration_seconds', 0):.1f} seconds")
        else:
            print(f"❌ Test automation failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test 3: Update configuration
        print(f"\n⚙️ Test 3: Testing configuration update...")
        automation.update_config({
            "max_urls": 50,
            "update_frequency_hours": 12
        })
        print(f"✅ Configuration updated successfully")
        
        # Test 4: Get updated status
        print(f"\n📊 Test 4: Getting updated status...")
        updated_status = automation.get_status()
        print(f"✅ Updated status retrieved")
        print(f"   Next Run Due: {updated_status['next_run_due']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sitemap automation test failed: {e}")
        return False

def test_integration():
    """Test the complete integration workflow."""
    print("\n🔗 Testing Complete Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return False
    
    try:
        print("🚀 Running complete integration test...")
        
        # Step 1: Initialize automation
        automation = SitemapAutomation(customer_id)
        
        # Step 2: Configure for test
        automation.update_config({
            "max_urls": 20,
            "asset_set_name": "Integration Test Page Feed - " + datetime.now().strftime("%Y%m%d_%H%M%S"),
            "campaign_name": "L.R - PMax - General"
        })
        
        # Step 3: Run automation
        result = automation.run_automation()
        
        if result["success"]:
            print(f"✅ Integration test completed successfully!")
            print(f"   URLs Processed: {result.get('urls_processed', 0)}")
            print(f"   Duration: {result.get('duration_seconds', 0):.1f} seconds")
            print(f"   Campaign: {result['config']['campaign_name']}")
            print(f"   Asset Set: {result['config']['asset_set_name']}")
            
            # Step 4: Verify results
            print(f"\n🔍 Verifying results...")
            
            # Check if page feed was created
            creator = PageFeedCreator(customer_id)
            existing_feeds = creator.get_existing_page_feeds()
            
            test_feed = None
            for feed in existing_feeds:
                if automation.config["asset_set_name"] in feed["name"]:
                    test_feed = feed
                    break
            
            if test_feed:
                print(f"✅ Test page feed found: {test_feed['name']}")
                
                # Get URLs from the feed
                feed_urls = creator.get_page_feed_urls(test_feed["id"], limit=10)
                print(f"✅ Retrieved {len(feed_urls)} URLs from test page feed")
                
                return True
            else:
                print(f"❌ Test page feed not found")
                return False
        else:
            print(f"❌ Integration test failed: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Sitemap Automation Test Suite")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID", 
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return
    
    print("✅ All required environment variables found")
    
    # Run tests
    tests = [
        ("Sitemap Parser", test_sitemap_parser),
        ("Page Feed Creator", test_page_feed_creator),
        ("Sitemap Automation", test_sitemap_automation),
        ("Complete Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Sitemap automation is ready to use.")
        print("\nNext steps:")
        print("1. Run: python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --run")
        print("2. Schedule: python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --schedule")
        print("3. Monitor: python tools/sitemap_automation.py --customer YOUR_CUSTOMER_ID --status")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please check the errors above.")

if __name__ == '__main__':
    main()
