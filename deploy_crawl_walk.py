#!/usr/bin/env python3
"""
Deploy Crawl/Walk Dashboard
===========================

Simple deployment script for the Crawl/Walk strategy dashboard.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying Crawl/Walk Strategy Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('crawl_walk_dashboard.py'):
        print("❌ Error: crawl_walk_dashboard.py not found")
        print("Please run this script from the WebTool directory")
        return False
    
    # Test imports
    print("\n📦 Testing imports...")
    test_commands = [
        "python3 -c 'import streamlit; print(\"✅ Streamlit OK\")'",
        "python3 -c 'import pandas; print(\"✅ Pandas OK\")'",
        "python3 -c 'import plotly; print(\"✅ Plotly OK\")'",
        "python3 -c 'from dotenv import load_dotenv; print(\"✅ Dotenv OK\")'"
    ]
    
    for cmd in test_commands:
        if not run_command(cmd, "Testing import"):
            return False
    
    # Test Crawl/Walk components
    print("\n🔧 Testing Crawl/Walk components...")
    crawl_walk_tests = [
        "cd google-ads-analysis/tools && python3 -c 'import crawl_walk_campaign_creator; print(\"✅ Campaign Creator OK\")'",
        "cd google-ads-analysis/tools && python3 -c 'import enhanced_quick_analysis; print(\"✅ Analysis OK\")'",
        "cd google-ads-analysis/tools && python3 -c 'import execute_crawl_walk; print(\"✅ CLI OK\")'"
    ]
    
    for cmd in crawl_walk_tests:
        if not run_command(cmd, "Testing Crawl/Walk component"):
            return False
    
    # Test dashboard
    print("\n📊 Testing dashboard...")
    if not run_command("python3 -c 'import crawl_walk_dashboard; print(\"✅ Dashboard OK\")'", "Testing dashboard import"):
        return False
    
    print("\n🎉 Deployment test completed successfully!")
    print("=" * 50)
    print("Next steps:")
    print("1. Set up GitHub Secrets (see GITHUB_SECRETS_SETUP.md)")
    print("2. Push to GitHub repository")
    print("3. Configure GitHub Actions")
    print("4. Run: streamlit run crawl_walk_dashboard.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
