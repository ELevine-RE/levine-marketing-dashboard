#!/bin/bash

# GitHub Actions Secrets Setup Script
# This script sets all required secrets for the Daily Google Ads Analysis workflow
# Make sure you have GitHub CLI installed and authenticated: gh auth login

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
    local description=$3
    
    if [ -z "$secret_value" ]; then
        echo "❌ $secret_name is empty. Please set the value and run again."
        return 1
    fi
    
    echo "Setting $secret_name..."
    if gh secret set "$secret_name" --body "$secret_value"; then
        echo "✅ $secret_name set successfully"
    else
        echo "❌ Failed to set $secret_name"
        return 1
    fi
    echo ""
}

# Google Ads API Credentials
echo "📊 Setting Google Ads API Credentials"
echo "-------------------------------------"

# Get values from environment or prompt user
GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN:-}
GOOGLE_ADS_CLIENT_ID=${GOOGLE_ADS_CLIENT_ID:-}
GOOGLE_ADS_CLIENT_SECRET=${GOOGLE_ADS_CLIENT_SECRET:-}
GOOGLE_ADS_REFRESH_TOKEN=${GOOGLE_ADS_REFRESH_TOKEN:-}
GOOGLE_ADS_LOGIN_CUSTOMER_ID=${GOOGLE_ADS_LOGIN_CUSTOMER_ID:-}
GOOGLE_ADS_CUSTOMER_ID=${GOOGLE_ADS_CUSTOMER_ID:-}

# Prompt for values if not set
if [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ]; then
    read -p "Enter GOOGLE_ADS_DEVELOPER_TOKEN: " GOOGLE_ADS_DEVELOPER_TOKEN
fi

if [ -z "$GOOGLE_ADS_CLIENT_ID" ]; then
    read -p "Enter GOOGLE_ADS_CLIENT_ID: " GOOGLE_ADS_CLIENT_ID
fi

if [ -z "$GOOGLE_ADS_CLIENT_SECRET" ]; then
    read -p "Enter GOOGLE_ADS_CLIENT_SECRET: " GOOGLE_ADS_CLIENT_SECRET
fi

if [ -z "$GOOGLE_ADS_REFRESH_TOKEN" ]; then
    read -p "Enter GOOGLE_ADS_REFRESH_TOKEN: " GOOGLE_ADS_REFRESH_TOKEN
fi

if [ -z "$GOOGLE_ADS_LOGIN_CUSTOMER_ID" ]; then
    read -p "Enter GOOGLE_ADS_LOGIN_CUSTOMER_ID: " GOOGLE_ADS_LOGIN_CUSTOMER_ID
fi

if [ -z "$GOOGLE_ADS_CUSTOMER_ID" ]; then
    read -p "Enter GOOGLE_ADS_CUSTOMER_ID: " GOOGLE_ADS_CUSTOMER_ID
fi

# Set Google Ads secrets
set_secret "GOOGLE_ADS_DEVELOPER_TOKEN" "$GOOGLE_ADS_DEVELOPER_TOKEN" "Google Ads API developer token"
set_secret "GOOGLE_ADS_CLIENT_ID" "$GOOGLE_ADS_CLIENT_ID" "OAuth 2.0 client ID"
set_secret "GOOGLE_ADS_CLIENT_SECRET" "$GOOGLE_ADS_CLIENT_SECRET" "OAuth 2.0 client secret"
set_secret "GOOGLE_ADS_REFRESH_TOKEN" "$GOOGLE_ADS_REFRESH_TOKEN" "OAuth 2.0 refresh token"
set_secret "GOOGLE_ADS_LOGIN_CUSTOMER_ID" "$GOOGLE_ADS_LOGIN_CUSTOMER_ID" "Manager account customer ID"
set_secret "GOOGLE_ADS_CUSTOMER_ID" "$GOOGLE_ADS_CUSTOMER_ID" "Target customer ID"

# Handle client_secret.json file
echo "📄 Setting GOOGLE_CLIENT_SECRET_JSON"
echo "------------------------------------"
if [ -f "client_secret.json" ]; then
    echo "Found client_secret.json file, reading contents..."
    CLIENT_SECRET_JSON=$(cat client_secret.json)
    set_secret "GOOGLE_CLIENT_SECRET_JSON" "$CLIENT_SECRET_JSON" "Google OAuth client secret JSON"
else
    echo "❌ client_secret.json file not found in current directory"
    echo "Please ensure the file exists or provide the JSON content manually"
    read -p "Enter the contents of client_secret.json: " CLIENT_SECRET_JSON
    set_secret "GOOGLE_CLIENT_SECRET_JSON" "$CLIENT_SECRET_JSON" "Google OAuth client secret JSON"
fi

# Email Configuration
echo "📧 Setting Email Configuration"
echo "------------------------------"

# Get email values from environment or prompt user
EMAIL_SMTP_SERVER=${EMAIL_SMTP_SERVER:-"smtp.gmail.com"}
EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT:-"587"}
EMAIL_SENDER=${EMAIL_SENDER:-}
EMAIL_PASSWORD=${EMAIL_PASSWORD:-}
EMAIL_RECIPIENT=${EMAIL_RECIPIENT:-}
EMAIL_REPLY_TO=${EMAIL_REPLY_TO:-}

# Prompt for email values if not set
if [ -z "$EMAIL_SENDER" ]; then
    read -p "Enter EMAIL_SENDER (e.g., elevine17@gmail.com): " EMAIL_SENDER
fi

if [ -z "$EMAIL_PASSWORD" ]; then
    read -s -p "Enter EMAIL_PASSWORD (Gmail app password): " EMAIL_PASSWORD
    echo ""
fi

if [ -z "$EMAIL_RECIPIENT" ]; then
    read -p "Enter EMAIL_RECIPIENT (e.g., evan@levine.realestate): " EMAIL_RECIPIENT
fi

if [ -z "$EMAIL_REPLY_TO" ]; then
    read -p "Enter EMAIL_REPLY_TO (e.g., developer@levine.realestate): " EMAIL_REPLY_TO
fi

# Set email secrets
set_secret "EMAIL_SMTP_SERVER" "$EMAIL_SMTP_SERVER" "SMTP server"
set_secret "EMAIL_SMTP_PORT" "$EMAIL_SMTP_PORT" "SMTP port"
set_secret "EMAIL_SENDER" "$EMAIL_SENDER" "Sender email address"
set_secret "EMAIL_PASSWORD" "$EMAIL_PASSWORD" "Email app password"
set_secret "EMAIL_RECIPIENT" "$EMAIL_RECIPIENT" "Recipient email address"
set_secret "EMAIL_REPLY_TO" "$EMAIL_REPLY_TO" "Reply-to email address"

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
echo ""
echo "📚 For more information, see: GITHUB_ACTIONS_SETUP.md"
