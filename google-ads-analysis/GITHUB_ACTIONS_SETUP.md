# GitHub Actions Setup Guide

## Overview

This guide explains how to set up the automated daily Google Ads analysis using GitHub Actions. The workflow runs every day at 15:00 UTC (9:00 AM MDT) and executes the `quick_analysis.py` script.

## Workflow Details

- **Workflow File**: `.github/workflows/daily_analysis.yml`
- **Schedule**: Daily at 15:00 UTC (9:00 AM MDT)
- **Manual Trigger**: Available via GitHub Actions UI
- **Python Version**: 3.10
- **Script**: `examples/quick_analysis.py`

## Required GitHub Secrets

You must add the following secrets to your GitHub repository settings:

### Google Ads API Credentials

1. **GOOGLE_ADS_DEVELOPER_TOKEN**
   - Your Google Ads API developer token
   - Example: `YOUR_DEVELOPER_TOKEN`

2. **GOOGLE_ADS_CLIENT_ID**
   - OAuth 2.0 client ID from Google Cloud Console
   - Example: `YOUR_CLIENT_ID.apps.googleusercontent.com`

3. **GOOGLE_ADS_CLIENT_SECRET**
   - OAuth 2.0 client secret from Google Cloud Console
   - Example: `YOUR_CLIENT_SECRET`

4. **GOOGLE_ADS_REFRESH_TOKEN**
   - OAuth 2.0 refresh token for API access
   - Example: `YOUR_REFRESH_TOKEN`

5. **GOOGLE_ADS_LOGIN_CUSTOMER_ID**
   - Manager account customer ID
   - Example: `YOUR_LOGIN_CUSTOMER_ID`

6. **GOOGLE_ADS_CUSTOMER_ID**
   - Target customer ID for analysis
   - Example: `YOUR_CUSTOMER_ID`

7. **GOOGLE_CLIENT_SECRET_JSON**
   - The entire contents of your `client_secret.json` file
   - This is the JSON file downloaded from Google Cloud Console

### Email Configuration

8. **EMAIL_SMTP_SERVER**
   - SMTP server for sending email notifications
   - Example: `smtp.gmail.com`

9. **EMAIL_SMTP_PORT**
   - SMTP port number
   - Example: `587`

10. **EMAIL_SENDER**
    - Email address used to send notifications
    - Example: `elevine17@gmail.com`

11. **EMAIL_PASSWORD**
    - App password for the sender email (not regular password)
    - Example: `fklk uwuh fakt tcio`

12. **EMAIL_RECIPIENT**
    - Email address to receive daily analysis reports
    - Example: `evan@levine.realestate`

13. **EMAIL_REPLY_TO**
    - Reply-to email address for notifications
    - Example: `developer@levine.realestate`

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the exact name listed above
6. Paste the corresponding value
7. Click **Add secret**

## Workflow Features

### Automatic Execution
- Runs daily at 15:00 UTC (9:00 AM MDT)
- Can be manually triggered from GitHub Actions UI

### Dependency Management
- Uses Python 3.10
- Installs all dependencies from `requirements.txt`
- Caches pip dependencies for faster builds

### Security
- All sensitive data stored as GitHub Secrets
- No credentials exposed in logs
- Secure environment variable handling

### Artifacts
- Uploads analysis results as artifacts
- Includes HTML reports and logs
- Retains artifacts for 7 days

## Monitoring

### Check Workflow Status
1. Go to your GitHub repository
2. Click **Actions** tab
3. Look for "Daily Google Ads Analysis" workflow
4. Check the latest run status

### View Logs
1. Click on the workflow run
2. Click on the "Run Daily Google Ads Analysis" job
3. Expand individual steps to view logs

### Download Artifacts
1. Go to the workflow run page
2. Scroll down to "Artifacts" section
3. Download `daily-analysis-results-{run_number}`

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify all Google Ads secrets are correct
   - Check that refresh token is valid
   - Ensure developer token has proper permissions

2. **Email Sending Failures**
   - Verify email credentials
   - Check that app password is used (not regular password)
   - Ensure SMTP settings are correct

3. **Script Errors**
   - Check workflow logs for Python errors
   - Verify all dependencies are installed
   - Ensure script path is correct

### Debug Mode
- Add `workflow_dispatch` trigger to run manually
- Check logs in GitHub Actions UI
- Review artifact uploads for output files

## Security Notes

- Never commit secrets to the repository
- Use GitHub Secrets for all sensitive data
- Regularly rotate refresh tokens
- Monitor workflow access permissions
- Review workflow logs for sensitive data exposure

## Next Steps

1. Add all required secrets to your GitHub repository
2. Push the workflow file to trigger initial setup
3. Test the workflow manually using the "workflow_dispatch" trigger
4. Monitor the first scheduled run
5. Review and adjust email recipients as needed

## Support

If you encounter issues:
1. Check the workflow logs in GitHub Actions
2. Verify all secrets are correctly set
3. Test the script locally first
4. Review the `quick_analysis.py` script for specific error handling
