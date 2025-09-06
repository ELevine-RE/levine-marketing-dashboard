#!/usr/bin/env python3
"""Fix dashboard to remove mock data fallback"""

# Read the dashboard file
with open('dashboard.py', 'r') as f:
    content = f.read()

# Find the load_google_ads_data method and replace it
import re

# Pattern to match the entire method
pattern = r'def load_google_ads_data\(self\) -> Dict:.*?(?=def \w+\(self\)|$)'
method_content = '''def load_google_ads_data(self) -> Dict:
        """Load Google Ads campaign data."""
        logger.info("🎯 Loading Google Ads data")
        
        # Try to use real Google Ads data first
        if self.google_ads_manager:
            try:
                logger.info("📡 Attempting to fetch real Google Ads data")
                real_data = self.google_ads_manager.get_campaign_data(days=30)
                if real_data:
                    logger.info(f"✅ Successfully loaded real data for {len(real_data)} campaigns")
                    return real_data
                else:
                    logger.error("❌ No real data returned from Google Ads API")
                    return {"error": "No campaigns found in Google Ads account"}
            except Exception as e:
                logger.error(f"❌ Failed to load real Google Ads data: {e}")
                return {"error": f"Google Ads API Error: {str(e)}"}
        
        # No Google Ads manager available
        logger.error("❌ Google Ads integration not available")
        return {"error": "Google Ads integration not configured"}
    '''

# Replace the method
new_content = re.sub(pattern, method_content, content, flags=re.DOTALL)

# Write the fixed content
with open('dashboard.py', 'w') as f:
    f.write(new_content)

print("✅ Dashboard fixed - removed mock data fallback")
