#!/bin/bash
# Google Analytics Setup Script

echo "🔧 Setting up Google Analytics integration..."

# Set Google Analytics Property ID
export GOOGLE_ANALYTICS_PROPERTY_ID=490979145

# Enable Google Analytics Data API
echo "📊 Enabling Google Analytics Data API..."
gcloud services enable analyticsdata.googleapis.com

# Authenticate with proper scopes
echo "🔐 Authenticating with Google Analytics..."
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly

echo "✅ Google Analytics setup complete!"
echo "📊 Property ID: $GOOGLE_ANALYTICS_PROPERTY_ID"
echo ""
echo "🚀 Test the integration:"
echo "   python tools/collect_unified_data.py"
echo "   python tools/generate_unified_dashboard.py"
echo ""
echo "🌐 View dashboard:"
echo "   

open dashboard/index.html"
