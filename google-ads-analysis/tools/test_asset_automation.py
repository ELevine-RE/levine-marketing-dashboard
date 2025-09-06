#!/usr/bin/env python3
"""
Test Asset Automation
====================

Demonstrate the automated asset extraction and upload system.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.asset_extractor import AssetExtractor, extract_assets_from_saved_searches

def test_asset_automation():
    """Test the automated asset extraction and upload system."""
    
    print("🖼️ Asset Automation Test")
    print("=" * 50)
    
    # Sample saved search results (your actual URLs would go here)
    sample_search_results = [
        "https://levine.realestate/deer-valley-east-village/",
        "https://levine.realestate/property-search/results/",
        "https://levine.realestate/communities/",
        "https://levine.realestate/about/",
        "https://levine.realestate/contact/"
    ]
    
    print("📝 Sample saved search results:")
    for url in sample_search_results:
        print(f"   • {url}")
    
    print("\n🔄 Starting automated asset extraction...")
    
    # Extract assets from saved searches
    extraction_results = extract_assets_from_saved_searches(sample_search_results)
    
    print(f"\n✅ Asset Extraction Complete:")
    print(f"   Pages processed: {extraction_results['pages_processed']}")
    print(f"   Total assets found: {extraction_results['total_assets']}")
    
    # Show assets by type
    for asset_type, assets in extraction_results['assets_by_type'].items():
        print(f"   {asset_type.title()}: {len(assets)} assets")
    
    # Show recommendations
    if extraction_results['recommendations']:
        print(f"\n📋 Asset Recommendations:")
        for rec in extraction_results['recommendations']:
            print(f"   • {rec}")
    
    # Show sample extracted assets
    print(f"\n📊 Sample Extracted Assets:")
    
    # Show images
    images = extraction_results['assets_by_type'].get('images', [])
    if images:
        print(f"   Images ({len(images)} found):")
        for i, img in enumerate(images[:3]):  # Show first 3
            print(f"     {i+1}. {img['filename']} ({img['width']}x{img['height']}) - {img['asset_type']}")
    
    # Show text content
    text_content = extraction_results['assets_by_type'].get('text_content', [])
    if text_content:
        print(f"   Text Content ({len(text_content)} found):")
        for i, text in enumerate(text_content[:3]):  # Show first 3
            print(f"     {i+1}. {text['type']}: {text['text'][:50]}...")
    
    print(f"\n🎯 Automation Benefits:")
    print("• No manual asset creation needed")
    print("• Automatic Google Ads compliance checking")
    print("• Direct upload to campaigns")
    print("• Continuous asset refresh from website")
    print("• Eliminates manual intervention for assets")

def test_single_page_extraction():
    """Test extraction from a single page."""
    
    print("\n🔍 Single Page Extraction Test")
    print("-" * 30)
    
    extractor = AssetExtractor()
    
    # Test with a single page
    test_url = "https://levine.realestate/deer-valley-east-village/"
    print(f"Testing extraction from: {test_url}")
    
    page_assets = extractor.extract_assets_from_page(test_url)
    
    if "error" not in page_assets:
        print(f"✅ Successfully extracted:")
        print(f"   Images: {len(page_assets.get('images', []))}")
        print(f"   Videos: {len(page_assets.get('videos', []))}")
        print(f"   Text content: {len(page_assets.get('text_content', []))}")
        
        # Show sample image details
        images = page_assets.get('images', [])
        if images:
            print(f"\n📸 Sample Image Details:")
            for i, img in enumerate(images[:2]):
                print(f"   {i+1}. {img['filename']}")
                print(f"      Size: {img['width']}x{img['height']}")
                print(f"      Type: {img['asset_type']}")
                print(f"      Meets requirements: {img['meets_requirements']}")
    else:
        print(f"❌ Error: {page_assets['error']}")

if __name__ == '__main__':
    test_asset_automation()
    test_single_page_extraction()
