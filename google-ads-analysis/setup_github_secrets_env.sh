#!/bin/bash

# GitHub Actions Secrets Setup Script (Environment Variables Version)
# This script sets all required secrets using environment variables
# Usage: Set environment variables and run this script

set -e  # Exit on any error

echo "🔧 Setting up GitHub Secrets for Daily Google Ads Analysis"
echo "=========================================================="

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI is not authenticated. Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Function to set a secret with validation
set_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        echo "❌ $secret_name is empty. Please set the environment variable and run again."
        return 1
    fi
    
    echo "Setting $secret_name..."
    if gh secret set "$secret_name" --body "$secret_value"; then
        echo "✅ $secret_name set successfully"
    else
        echo "❌ Failed to set $secret_name"
        return 1
    fi
}

# Set Google Ads API Credentials
echo "📊 Setting Google Ads API Credentials"
echo "-------------------------------------"

set_secret "GOOGLE_ADS_DEVELOPER_TOKEN" "$GOOGLE_ADS_DEVELOPER_TOKEN"
set_secret "GOOGLE_ADS_CLIENT_ID" "$GOOGLE_ADS_CLIENT_ID"
set_secret "GOOGLE_ADS_CLIENT_SECRET" "$GOOGLE_ADS_CLIENT_SECRET"
set_secret "GOOGLE_ADS_REFRESH_TOKEN" "$GOOGLE_ADS_REFRESH_TOKEN"
set_secret "GOOGLE_ADS_LOGIN_CUSTOMER_ID" "$GOOGLE_ADS_LOGIN_CUSTOMER_ID"
set_secret "GOOGLE_ADS_CUSTOMER_ID" "$GOOGLE_ADS_CUSTOMER_ID"

# Handle client_secret.json file
echo "📄 Setting GOOGLE_CLIENT_SECRET_JSON"
echo "------------------------------------"
if [ -f "client_secret.json" ]; then
    echo "Found client_secret.json file, reading contents..."
    CLIENT_SECRET_JSON=$(cat client_secret.json)
    set_secret "GOOGLE_CLIENT_SECRET_JSON" "$CLIENT_SECRET_JSON"
else
    echo "Using GOOGLE_CLIENT_SECRET_JSON environment variable..."
    set_secret "GOOGLE_CLIENT_SECRET_JSON" "$GOOGLE_CLIENT_SECRET_JSON"
fi

# Set Email Configuration
echo "📧 Setting Email Configuration"
echo "------------------------------"

set_secret "EMAIL_SMTP_SERVER" "${EMAIL_SMTP_SERVER:-smtp.gmail.com}"
set_secret "EMAIL_SMTP_PORT" "${EMAIL_SMTP_PORT:-587}"
set_secret "EMAIL_SENDER" "$EMAIL_SENDER"
set_secret "EMAIL_PASSWORD" "$EMAIL_PASSWORD"
set_secret "EMAIL_RECIPIENT" "$EMAIL_RECIPIENT"
set_secret "EMAIL_REPLY_TO" "$EMAIL_REPLY_TO"

echo ""
echo "🎉 All GitHub Secrets have been set successfully!"
echo ""
echo "📋 Summary of secrets set:"
echo "=========================="
echo "✅ GOOGLE_ADS_DEVELOPER_TOKEN"
echo "✅ GOOGLE_ADS_CLIENT_ID"
echo "✅ GOOGLE_ADS_CLIENT_SECRET"
echo "✅ GOOGLE_ADS_REFRESH_TOKEN"
echo "✅ GOOGLE_ADS_LOGIN_CUSTOMER_ID"
echo "✅ GOOGLE_ADS_CUSTOMER_ID"
echo "✅ GOOGLE_CLIENT_SECRET_JSON"
echo "✅ EMAIL_SMTP_SERVER"
echo "✅ EMAIL_SMTP_PORT"
echo "✅ EMAIL_SENDER"
echo "✅ EMAIL_PASSWORD"
echo "✅ EMAIL_RECIPIENT"
echo "✅ EMAIL_REPLY_TO"
echo ""
echo "🚀 Next steps:"
echo "1. Push your workflow file to trigger the setup"
echo "2. Test the workflow manually using GitHub Actions UI"
echo "3. Monitor the first scheduled run at 15:00 UTC"
