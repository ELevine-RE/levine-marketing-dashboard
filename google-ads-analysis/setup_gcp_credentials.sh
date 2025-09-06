#!/bin/bash

# Google Cloud CLI Setup Script for Google Ads API
# This script automates the setup of Google Cloud credentials

set -e

echo "🔧 Setting up Google Cloud credentials for Google Ads API"
echo "=========================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed"
    echo "Installing Google Cloud SDK..."
    
    # Detect OS and install
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install google-cloud-sdk
        else
            echo "Please install Homebrew first: https://brew.sh/"
            echo "Then run: brew install google-cloud-sdk"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl https://sdk.cloud.google.com | bash
        exec -l $SHELL
    else
        echo "Please install Google Cloud SDK manually:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
fi

echo "✅ Google Cloud CLI is installed"

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Authenticating with Google Cloud..."
    gcloud auth login
else
    echo "✅ Already authenticated with Google Cloud"
fi

# Get or create project
PROJECT_ID=${1:-"google-ads-analysis-$(date +%s)"}
echo "📁 Using project: $PROJECT_ID"

# Create project if it doesn't exist
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    echo "Creating new project: $PROJECT_ID"
    gcloud projects create "$PROJECT_ID" --name="Google Ads Analysis"
    echo "✅ Project created successfully"
else
    echo "✅ Project already exists"
fi

# Set project as default
gcloud config set project "$PROJECT_ID"
echo "✅ Project set as default"

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable googleads.googleapis.com
gcloud services enable oauth2.googleapis.com
echo "✅ APIs enabled successfully"

# Create OAuth credentials
echo "🔑 Setting up OAuth credentials..."
gcloud auth application-default login

# Create client_secret.json
echo "📄 Creating client_secret.json..."
if gcloud auth application-default create-client-config \
  --client-type=web \
  --client-name="Google Ads API Client" \
  --redirect-uris="http://localhost:8080/" \
  --output-file=client_secret.json 2>/dev/null; then
    echo "✅ client_secret.json created successfully"
else
    echo "⚠️ Could not create client_secret.json automatically"
    echo "You may need to create it manually from the Google Cloud Console"
    echo "Or use the existing client_secret.json file"
fi

# Display current configuration
echo ""
echo "📋 Current Configuration:"
echo "=========================="
echo "Project ID: $(gcloud config get-value project)"
echo "Account: $(gcloud config get-value account)"
echo "Region: $(gcloud config get-value compute/region 2>/dev/null || echo 'Not set')"

# Check if client_secret.json exists
if [ -f "client_secret.json" ]; then
    echo "✅ client_secret.json found"
    echo "Client ID: $(python3 -c "import json; print(json.load(open('client_secret.json'))['installed']['client_id'])")"
else
    echo "❌ client_secret.json not found"
fi

echo ""
echo "🎉 Google Cloud setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get developer token from: https://developers.google.com/google-ads/api/docs/first-call/dev-token"
echo "2. Run: python oauth_helper.py to get refresh token"
echo "3. Run: ./setup_github_secrets.sh to set up GitHub secrets"
echo ""
echo "🔍 Verification commands:"
echo "gcloud auth list"
echo "gcloud config get-value project"
echo "gcloud services list --enabled --filter='name:googleads'"
