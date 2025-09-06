#!/bin/bash

# Marketing Dashboard Startup Script
# =================================

echo "🚀 Starting Marketing Dashboard..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dashboard dependencies
echo "📥 Installing dashboard dependencies..."
pip install -r dashboard_requirements.txt

# Check if environment variables are set
echo "🔍 Checking environment variables..."
if [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    echo "⚠️  Warning: GOOGLE_ADS_DEVELOPER_TOKEN not set"
fi

if [ -z "$GOOGLE_ADS_CLIENT_ID" ]; then
    echo "⚠️  Warning: GOOGLE_ADS_CLIENT_ID not set"
fi

if [ -z "$GOOGLE_ADS_CLIENT_SECRET" ]; then
    echo "⚠️  Warning: GOOGLE_ADS_CLIENT_SECRET not set"
fi

if [ -z "$GOOGLE_ADS_REFRESH_TOKEN" ]; then
    echo "⚠️  Warning: GOOGLE_ADS_REFRESH_TOKEN not set"
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the dashboard
echo "🌐 Starting Streamlit dashboard..."
echo "📊 Dashboard will be available at: http://localhost:8501"
echo "🔄 Press Ctrl+C to stop the dashboard"
echo ""

streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
