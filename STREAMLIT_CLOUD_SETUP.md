# Streamlit Cloud Setup Instructions

## Google Ads API Environment Variables

To deploy this dashboard to Streamlit Cloud, you need to set up the following environment variables in your Streamlit Cloud app settings:

### Required Environment Variables:

1. **GOOGLE_ADS_DEVELOPER_TOKEN**
   - Value: `YOUR_DEVELOPER_TOKEN_HERE`
   - Description: Your Google Ads Developer Token

2. **GOOGLE_ADS_CLIENT_ID**
   - Value: `YOUR_CLIENT_ID_HERE`
   - Description: OAuth2 Client ID from Google Cloud Console

3. **GOOGLE_ADS_CLIENT_SECRET**
   - Value: `YOUR_CLIENT_SECRET_HERE`
   - Description: OAuth2 Client Secret from Google Cloud Console

4. **GOOGLE_ADS_REFRESH_TOKEN**
   - Value: `YOUR_REFRESH_TOKEN_HERE`
   - Description: OAuth2 Refresh Token

5. **GOOGLE_ADS_LOGIN_CUSTOMER_ID**
   - Value: `YOUR_LOGIN_CUSTOMER_ID_HERE`
   - Description: Google Ads Login Customer ID (MCC Account ID)

### How to Set Environment Variables in Streamlit Cloud:

1. Go to your Streamlit Cloud dashboard
2. Select your app
3. Click on "Settings" or "Secrets"
4. Add each environment variable with its corresponding value
5. Save the settings
6. Redeploy your app

### Alternative: Using Streamlit Secrets

You can also use Streamlit's built-in secrets management by creating a `.streamlit/secrets.toml` file:

```toml
[google_ads]
developer_token = "YOUR_DEVELOPER_TOKEN_HERE"
client_id = "YOUR_CLIENT_ID_HERE"
client_secret = "YOUR_CLIENT_SECRET_HERE"
refresh_token = "YOUR_REFRESH_TOKEN_HERE"
login_customer_id = "YOUR_LOGIN_CUSTOMER_ID_HERE"
```

### Security Notes:

- Never commit these credentials to your repository
- Use environment variables for production deployments
- Keep your credentials secure and rotate them regularly
- The `google-ads.yaml` file should only be used for local development

### Troubleshooting:

If you're still getting "invalid login customer ID" errors:
- Ensure the `GOOGLE_ADS_LOGIN_CUSTOMER_ID` is exactly your 10-digit customer ID (no quotes, no spaces)
- Verify all environment variables are set correctly
- Check that your Google Ads API access is properly configured
- Ensure your Google Cloud project has the Google Ads API enabled
