# GitHub Secrets Setup Guide

This guide provides two methods for setting up all required GitHub Secrets for the Daily Google Ads Analysis workflow.

## Prerequisites

1. **Install GitHub CLI**: https://cli.github.com/
2. **Authenticate**: Run `gh auth login`
3. **Navigate to your repository directory**

## Method 1: Interactive Setup (Recommended for first-time setup)

Use the interactive script that will prompt you for each value:

```bash
./setup_github_secrets.sh
```

This script will:
- Check if GitHub CLI is installed and authenticated
- Prompt you for each secret value
- Automatically read `client_secret.json` if it exists
- Set all 13 required secrets
- Provide validation and error handling

## Method 2: Environment Variables Setup (Recommended for automation)

Set environment variables and run the automated script:

```bash
# Set your secret values here
export GOOGLE_ADS_DEVELOPER_TOKEN="your_developer_token"
export GOOGLE_ADS_CLIENT_ID="your_client_id"
export GOOGLE_ADS_CLIENT_SECRET="your_client_secret"
export GOOGLE_ADS_REFRESH_TOKEN="your_refresh_token"
export GOOGLE_ADS_LOGIN_CUSTOMER_ID="your_login_customer_id"
export GOOGLE_ADS_CUSTOMER_ID="your_customer_id"
export GOOGLE_CLIENT_SECRET_JSON='{"web":{"client_id":"...","client_secret":"..."}}'
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_RECIPIENT="recipient@example.com"
export EMAIL_REPLY_TO="reply@example.com"

# Run the setup script
./setup_github_secrets_env.sh
```

## Method 3: Manual Setup with GitHub CLI

If you prefer to set secrets individually:

```bash
# Google Ads API Credentials
gh secret set GOOGLE_ADS_DEVELOPER_TOKEN --body "your_developer_token"
gh secret set GOOGLE_ADS_CLIENT_ID --body "your_client_id"
gh secret set GOOGLE_ADS_CLIENT_SECRET --body "your_client_secret"
gh secret set GOOGLE_ADS_REFRESH_TOKEN --body "your_refresh_token"
gh secret set GOOGLE_ADS_LOGIN_CUSTOMER_ID --body "your_login_customer_id"
gh secret set GOOGLE_ADS_CUSTOMER_ID --body "your_customer_id"

# Google OAuth JSON (read from file)
gh secret set GOOGLE_CLIENT_SECRET_JSON --body "$(cat client_secret.json)"

# Email Configuration
gh secret set EMAIL_SMTP_SERVER --body "smtp.gmail.com"
gh secret set EMAIL_SMTP_PORT --body "587"
gh secret set EMAIL_SENDER --body "your_email@gmail.com"
gh secret set EMAIL_PASSWORD --body "your_app_password"
gh secret set EMAIL_RECIPIENT --body "recipient@example.com"
gh secret set EMAIL_REPLY_TO --body "reply@example.com"
```

## Required Secrets Reference

### Google Ads API Credentials (7 secrets)
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads API developer token | `YOUR_DEVELOPER_TOKEN` |
| `GOOGLE_ADS_CLIENT_ID` | OAuth 2.0 client ID | `YOUR_CLIENT_ID.apps.googleusercontent.com` |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth 2.0 client secret | `YOUR_CLIENT_SECRET` |
| `GOOGLE_ADS_REFRESH_TOKEN` | OAuth 2.0 refresh token | `YOUR_REFRESH_TOKEN` |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Manager account customer ID | `YOUR_LOGIN_CUSTOMER_ID` |
| `GOOGLE_ADS_CUSTOMER_ID` | Target customer ID | `YOUR_CUSTOMER_ID` |
| `GOOGLE_CLIENT_SECRET_JSON` | Google OAuth client secret JSON | Contents of `client_secret.json` |

### Email Configuration (6 secrets)
| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EMAIL_SMTP_SERVER` | SMTP server | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP port | `587` |
| `EMAIL_SENDER` | Sender email address | `elevine17@gmail.com` |
| `EMAIL_PASSWORD` | Gmail app password | `fklk uwuh fakt tcio` |
| `EMAIL_RECIPIENT` | Recipient email address | `evan@levine.realestate` |
| `EMAIL_REPLY_TO` | Reply-to email address | `developer@levine.realestate` |

## Verification

After setting up secrets, verify they were created correctly:

```bash
# List all secrets (names only)
gh secret list

# Check if specific secret exists
gh secret list | grep GOOGLE_ADS_DEVELOPER_TOKEN
```

## Troubleshooting

### Common Issues

1. **GitHub CLI not installed**
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

2. **Not authenticated**
   ```bash
   gh auth login
   ```

3. **Wrong repository**
   ```bash
   # Check current repository
   gh repo view
   
   # Switch to correct repository
   cd /path/to/your/repo
   ```

4. **Permission denied**
   - Ensure you have write access to the repository
   - Check if you're a collaborator or owner

### Error Messages

- `❌ GitHub CLI (gh) is not installed`: Install GitHub CLI
- `❌ GitHub CLI is not authenticated`: Run `gh auth login`
- `❌ [SECRET_NAME] is empty`: Set the environment variable or provide the value
- `❌ Failed to set [SECRET_NAME]`: Check permissions and try again

## Security Best Practices

1. **Never commit secrets to the repository**
2. **Use environment variables for automation**
3. **Rotate refresh tokens regularly**
4. **Use app passwords for Gmail (not regular passwords)**
5. **Monitor workflow logs for sensitive data exposure**

## Next Steps

After setting up secrets:

1. **Push the workflow file** to trigger the setup
2. **Test manually** using GitHub Actions UI
3. **Monitor the first scheduled run** at 15:00 UTC
4. **Review workflow logs** for any issues

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all secrets are correctly set
3. Test the workflow manually first
4. Review the workflow logs in GitHub Actions
