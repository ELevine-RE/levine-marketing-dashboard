# Google OAuth Setup Guide

This guide will help you find and set up your Google OAuth credentials for the Google Ads API.

## Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Select your project (or create a new one)

## Step 2: Enable Google Ads API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Ads API"
3. Click on "Google Ads API"
4. Click **Enable**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the required fields (App name, User support email, Developer contact information)
   - Add scopes: `https://www.googleapis.com/auth/adwords`
   - Save and continue

4. Create the OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: "Google Ads API Client"
   - Authorized redirect URIs: Add `http://localhost:8080/` (for local testing)
   - Click **Create**

## Step 4: Download Client Secret

1. After creating the OAuth 2.0 Client ID, you'll see a popup with your credentials
2. Click **Download JSON** to download the `client_secret.json` file
3. **Save this file securely** - it contains your client secret

## Step 5: Get Your Credentials

From the downloaded `client_secret.json` file, you'll find:

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

**Extract these values:**
- `client_id` → Use as `GOOGLE_ADS_CLIENT_ID`
- `client_secret` → Use as `GOOGLE_ADS_CLIENT_SECRET`
- The entire JSON content → Use as `GOOGLE_CLIENT_SECRET_JSON`

## Step 6: Get Developer Token

1. Go to [Google Ads API Center](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
2. Sign in with your Google Ads account
3. Click **Get a developer token**
4. Fill out the application form
5. Wait for approval (usually 1-2 business days)
6. Once approved, you'll receive your developer token

## Step 7: Get Refresh Token

You'll need to run a one-time script to get your refresh token:

```bash
# Run the OAuth helper script
python oauth_helper.py
```

This will:
1. Open a browser window for authentication
2. Ask you to authorize the application
3. Generate a refresh token
4. Save it for future use

## Step 8: Find Your Customer IDs

### Login Customer ID (Manager Account)
1. Log into [Google Ads](https://ads.google.com/)
2. Look at the URL: `https://ads.google.com/um/Welcome/Home?cid=XXXXXXXXXX`
3. The number after `cid=` is your login customer ID

### Target Customer ID
1. In Google Ads, go to **Tools & Settings** → **Account access**
2. Look for the customer ID of the account you want to analyze
3. This is your target customer ID

## Complete Credentials Checklist

Make sure you have all these values:

- [ ] **GOOGLE_ADS_DEVELOPER_TOKEN** (from API Center)
- [ ] **GOOGLE_ADS_CLIENT_ID** (from client_secret.json)
- [ ] **GOOGLE_ADS_CLIENT_SECRET** (from client_secret.json)
- [ ] **GOOGLE_ADS_REFRESH_TOKEN** (from oauth_helper.py)
- [ ] **GOOGLE_ADS_LOGIN_CUSTOMER_ID** (from Google Ads URL)
- [ ] **GOOGLE_ADS_CUSTOMER_ID** (from Account access)
- [ ] **GOOGLE_CLIENT_SECRET_JSON** (entire client_secret.json content)

## Troubleshooting

### Common Issues

1. **"API not enabled" error**
   - Make sure Google Ads API is enabled in Google Cloud Console

2. **"Invalid client" error**
   - Check that your client_id and client_secret are correct
   - Ensure you're using the right OAuth 2.0 client ID

3. **"Developer token not approved"**
   - Wait for approval from Google Ads API Center
   - Check your email for approval notification

4. **"Invalid refresh token"**
   - Run oauth_helper.py again to generate a new refresh token
   - Refresh tokens can expire if not used regularly

### Getting Help

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [Google Cloud Console Help](https://cloud.google.com/docs)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

## Security Notes

- Never commit `client_secret.json` to version control
- Store credentials securely
- Use environment variables or GitHub Secrets
- Rotate refresh tokens regularly
- Monitor API usage and quotas
