# Google Cloud CLI Setup Guide

This guide will help you set up Google OAuth credentials using the Google Cloud CLI (gcloud) instead of the web interface.

## Prerequisites

1. **Install Google Cloud CLI**: https://cloud.google.com/sdk/docs/install
2. **Install GitHub CLI**: https://cli.github.com/

## Step 1: Install and Authenticate with gcloud

```bash
# Install gcloud (if not already installed)
# macOS
brew install google-cloud-sdk

# Ubuntu/Debian
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-sdk

# Authenticate with Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## Step 2: Create a New Project (if needed)

```bash
# List existing projects
gcloud projects list

# Create a new project
gcloud projects create google-ads-analysis-$(date +%s) --name="Google Ads Analysis"

# Set the project as default
gcloud config set project google-ads-analysis-$(date +%s)
```

## Step 3: Enable Required APIs

```bash
# Enable Google Ads API
gcloud services enable googleads.googleapis.com

# Enable OAuth2 API
gcloud services enable oauth2.googleapis.com

# List enabled APIs
gcloud services list --enabled
```

## Step 4: Create OAuth 2.0 Credentials

```bash
# Create OAuth 2.0 client credentials
gcloud auth application-default login

# Create OAuth 2.0 client ID for web application
gcloud auth application-default create-client-config \
  --client-type=web \
  --client-name="Google Ads API Client" \
  --redirect-uris="http://localhost:8080/" \
  --output-file=client_secret.json
```

## Step 5: Alternative Method - Create Credentials File Manually

If the above doesn't work, create the credentials file manually:

```bash
# Create client_secret.json manually
cat > client_secret.json << 'EOF'
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
EOF
```

## Step 6: Get Developer Token

```bash
# Go to Google Ads API Center (web interface required)
# https://developers.google.com/google-ads/api/docs/first-call/dev-token
echo "Please visit: https://developers.google.com/google-ads/api/docs/first-call/dev-token"
echo "Sign in and request a developer token"
echo "This step requires web interface - cannot be automated via CLI"
```

## Step 7: Generate Refresh Token

```bash
# Run the OAuth helper script to get refresh token
python oauth_helper.py
```

## Step 8: Find Customer IDs

```bash
# Login Customer ID (from Google Ads URL)
echo "Login Customer ID: Check Google Ads URL for 'cid=' parameter"

# Target Customer ID (from Google Ads Account access)
echo "Target Customer ID: Check Tools & Settings > Account access"
```

## Step 9: Automated Setup Script

Create a script to set up everything automatically:

```bash
#!/bin/bash
# setup_gcp_credentials.sh

set -e

echo "🔧 Setting up Google Cloud credentials for Google Ads API"
echo "=========================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Authenticating with Google Cloud..."
    gcloud auth login
fi

# Get or create project
PROJECT_ID=${1:-"google-ads-analysis-$(date +%s)"}
echo "📁 Using project: $PROJECT_ID"

# Create project if it doesn't exist
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    echo "Creating new project: $PROJECT_ID"
    gcloud projects create "$PROJECT_ID" --name="Google Ads Analysis"
fi

# Set project as default
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable googleads.googleapis.com
gcloud services enable oauth2.googleapis.com

# Create OAuth credentials
echo "🔑 Creating OAuth credentials..."
gcloud auth application-default login

# Create client_secret.json
echo "📄 Creating client_secret.json..."
gcloud auth application-default create-client-config \
  --client-type=web \
  --client-name="Google Ads API Client" \
  --redirect-uris="http://localhost:8080/" \
  --output-file=client_secret.json

echo "✅ Google Cloud setup complete!"
echo "📋 Next steps:"
echo "1. Get developer token from: https://developers.google.com/google-ads/api/docs/first-call/dev-token"
echo "2. Run: python oauth_helper.py to get refresh token"
echo "3. Run: ./setup_github_secrets.sh to set up GitHub secrets"
```

## Step 10: Complete Setup with All Credentials

Once you have all credentials, run the GitHub secrets setup:

```bash
# Set environment variables with your actual values
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
export GOOGLE_ADS_LOGIN_CUSTOMER_ID="your_login_customer_id"
export GOOGLE_ADS_CUSTOMER_ID="your_customer_id"
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_RECIPIENT="recipient@example.com"
export EMAIL_REPLY_TO="reply@example.com"

# Run the GitHub secrets setup
./setup_github_secrets_env.sh
```

## Troubleshooting

### Common gcloud Issues

1. **"gcloud command not found"**
   ```bash
   # Install gcloud
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **"Not authenticated"**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **"Project not found"**
   ```bash
   # List projects
   gcloud projects list
   
   # Create new project
   gcloud projects create PROJECT_ID --name="Project Name"
   ```

4. **"API not enabled"**
   ```bash
   gcloud services enable googleads.googleapis.com
   gcloud services enable oauth2.googleapis.com
   ```

### Verification Commands

```bash
# Check authentication
gcloud auth list

# Check project
gcloud config get-value project

# Check enabled APIs
gcloud services list --enabled --filter="name:googleads"

# Check OAuth credentials
gcloud auth application-default print-access-token
```

## Security Best Practices

1. **Use service accounts for production**
   ```bash
   # Create service account
   gcloud iam service-accounts create google-ads-api \
     --display-name="Google Ads API Service Account"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:google-ads-api@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/editor"
   ```

2. **Store credentials securely**
   - Never commit credentials to version control
   - Use environment variables or secret management
   - Rotate credentials regularly

3. **Monitor API usage**
   ```bash
   # Check API quotas
   gcloud compute quotas list --filter="name:googleads"
   ```

## Next Steps

After completing the CLI setup:

1. **Test the credentials**: Run `python test_connection.py`
2. **Set up GitHub secrets**: Run `./setup_github_secrets.sh`
3. **Test the workflow**: Trigger the GitHub Action manually
4. **Monitor execution**: Check workflow logs and artifacts
