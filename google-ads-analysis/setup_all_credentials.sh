#!/bin/bash

# Complete Credentials Setup Script
# This script sets up all GitHub Secrets using existing credentials

set -e

echo "🚀 Complete Google Ads API & GitHub Secrets Setup"
echo "=================================================="

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

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
    local description=$3
    
    if [ -z "$secret_value" ]; then
        echo "❌ $secret_name is empty. Please check your .env file."
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

# Extract values from .env file
echo "📊 Extracting Google Ads credentials from .env file..."
source .env

# Extract email configuration from daily_email_config.py
echo "📧 Extracting email configuration..."
EMAIL_SMTP_SERVER="smtp.gmail.com"
EMAIL_SMTP_PORT="587"
EMAIL_SENDER=$(grep "'sender_email'" daily_email_config.py | cut -d"'" -f4)
EMAIL_PASSWORD=$(grep "'sender_password'" daily_email_config.py | cut -d"'" -f4)
EMAIL_RECIPIENT=$(grep "'recipient_email'" daily_email_config.py | cut -d"'" -f4)
EMAIL_REPLY_TO=$(grep "'reply_to'" daily_email_config.py | cut -d"'" -f4)

# Extract client_secret.json content
echo "📄 Reading client_secret.json..."
if [ -f "client_secret.json" ]; then
    GOOGLE_CLIENT_SECRET_JSON=$(cat client_secret.json)
    echo "✅ client_secret.json found"
else
    echo "❌ client_secret.json not found"
    exit 1
fi

# Set Google Ads API Credentials
echo ""
echo "📊 Setting Google Ads API Credentials"
echo "-------------------------------------"

set_secret "GOOGLE_ADS_DEVELOPER_TOKEN" "$GOOGLE_ADS_DEVELOPER_TOKEN" "Google Ads API developer token"
set_secret "GOOGLE_ADS_CLIENT_ID" "$GOOGLE_ADS_CLIENT_ID" "OAuth 2.0 client ID"
set_secret "GOOGLE_ADS_CLIENT_SECRET" "$GOOGLE_ADS_CLIENT_SECRET" "OAuth 2.0 client secret"
set_secret "GOOGLE_ADS_REFRESH_TOKEN" "$GOOGLE_ADS_REFRESH_TOKEN" "OAuth 2.0 refresh token"
set_secret "GOOGLE_ADS_LOGIN_CUSTOMER_ID" "$GOOGLE_ADS_LOGIN_CUSTOMER_ID" "Manager account customer ID"
set_secret "GOOGLE_ADS_CUSTOMER_ID" "$GOOGLE_ADS_CUSTOMER_ID" "Target customer ID"
set_secret "GOOGLE_CLIENT_SECRET_JSON" "$GOOGLE_CLIENT_SECRET_JSON" "Google OAuth client secret JSON"

# Set Email Configuration
echo ""
echo "📧 Setting Email Configuration"
echo "------------------------------"

set_secret "EMAIL_SMTP_SERVER" "$EMAIL_SMTP_SERVER" "SMTP server"
set_secret "EMAIL_SMTP_PORT" "$EMAIL_SMTP_PORT" "SMTP port"
set_secret "EMAIL_SENDER" "$EMAIL_SENDER" "Sender email address"
set_secret "EMAIL_PASSWORD" "$EMAIL_PASSWORD" "Email app password"
set_secret "EMAIL_RECIPIENT" "$EMAIL_RECIPIENT" "Recipient email address"
set_secret "EMAIL_REPLY_TO" "$EMAIL_REPLY_TO" "Reply-to email address"

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
echo "🔍 Verification:"
echo "gh secret list"
echo ""
echo "🚀 Next steps:"
echo "1. Push your workflow file to trigger the setup"
echo "2. Test the workflow manually using GitHub Actions UI"
echo "3. Monitor the first scheduled run at 15:00 UTC"
echo ""
echo "📚 For more information, see: GITHUB_ACTIONS_SETUP.md"
