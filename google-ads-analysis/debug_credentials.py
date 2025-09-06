#!/usr/bin/env python3
"""
Debug script to test Google Ads OAuth credentials
"""

import os
import json

def test_credentials():
    """Test the OAuth credentials."""
    print("🔍 Testing Google Ads OAuth Credentials")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID", 
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
        "GOOGLE_ADS_CUSTOMER_ID"
    ]
    
    print("📋 Environment Variables:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Show first and last few characters
            masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
    
    # Check if client_secret.json exists
    if os.path.exists("client_secret.json"):
        print("\n📄 client_secret.json found")
        try:
            with open("client_secret.json", "r") as f:
                data = json.load(f)
            print("  ✅ JSON is valid")
            if "installed" in data:
                print(f"  📝 Client ID: {data['installed']['client_id'][:20]}...")
        except Exception as e:
            print(f"  ❌ JSON error: {e}")
    else:
        print("\n❌ client_secret.json not found")
    
    # Check if google-ads.yaml exists
    if os.path.exists("google-ads.yaml"):
        print("\n📄 google-ads.yaml found")
        try:
            with open("google-ads.yaml", "r") as f:
                content = f.read()
            print("  ✅ YAML file exists")
            print(f"  📝 Content length: {len(content)} characters")
        except Exception as e:
            print(f"  ❌ YAML error: {e}")
    else:
        print("\n❌ google-ads.yaml not found")
    
    print("\n🔧 Recommendations:")
    print("1. Check if refresh token is expired")
    print("2. Verify client_id and client_secret match")
    print("3. Ensure developer token is valid")
    print("4. Run: python oauth_helper.py to generate new refresh token")

if __name__ == "__main__":
    test_credentials()
