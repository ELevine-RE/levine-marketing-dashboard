# 🔐 GitHub Secrets Setup for Crawl/Walk Automation

This guide shows you how to set up GitHub Secrets for automated Crawl/Walk strategy execution.

## 📋 **Required Secrets**

### **Google Ads API Secrets**
```
GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_ADS_CLIENT_ID
GOOGLE_ADS_CLIENT_SECRET
GOOGLE_ADS_REFRESH_TOKEN
GOOGLE_ADS_LOGIN_CUSTOMER_ID
GOOGLE_ADS_CUSTOMER_ID
```

### **Google Drive API Secrets**
```
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
```

### **Email Notification Secrets**
```
EMAIL_SENDER
EMAIL_PASSWORD
EMAIL_RECIPIENT
```

## 🛠️ **Setup Instructions**

### **Step 1: Access Repository Settings**
1. Go to your GitHub repository: `https://github.com/ELevine-RE/levine-marketing-dashboard`
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### **Step 2: Add Google Ads API Secrets**
Click **New repository secret** for each secret:

#### **GOOGLE_ADS_DEVELOPER_TOKEN**
- **Name:** `GOOGLE_ADS_DEVELOPER_TOKEN`
- **Value:** `eAOe2DUSSgK2zGY4vQly3w`

#### **GOOGLE_ADS_CLIENT_ID**
- **Name:** `GOOGLE_ADS_CLIENT_ID`
- **Value:** `[Your Google Ads Client ID]`

#### **GOOGLE_ADS_CLIENT_SECRET**
- **Name:** `GOOGLE_ADS_CLIENT_SECRET`
- **Value:** `[Your Google Ads Client Secret]`

#### **GOOGLE_ADS_REFRESH_TOKEN**
- **Name:** `GOOGLE_ADS_REFRESH_TOKEN`
- **Value:** `[Your Google Ads Refresh Token]`

#### **GOOGLE_ADS_LOGIN_CUSTOMER_ID**
- **Name:** `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- **Value:** `5426234549`

#### **GOOGLE_ADS_CUSTOMER_ID**
- **Name:** `GOOGLE_ADS_CUSTOMER_ID`
- **Value:** `5426234549`

### **Step 3: Add Google Drive API Secrets**
#### **GOOGLE_CLIENT_ID**
- **Name:** `GOOGLE_CLIENT_ID`
- **Value:** `[Your Google Drive Client ID]`

#### **GOOGLE_CLIENT_SECRET**
- **Name:** `GOOGLE_CLIENT_SECRET`
- **Value:** `[Your Google Drive Client Secret]`

#### **GOOGLE_REFRESH_TOKEN**
- **Name:** `GOOGLE_REFRESH_TOKEN`
- **Value:** `[Your Google Drive Refresh Token]`

### **Step 4: Add Email Notification Secrets**
#### **EMAIL_SENDER**
- **Name:** `EMAIL_SENDER`
- **Value:** `evan@levine.realestate`

#### **EMAIL_PASSWORD**
- **Name:** `EMAIL_PASSWORD`
- **Value:** `[Your Gmail App Password]`

#### **EMAIL_RECIPIENT**
- **Name:** `EMAIL_RECIPIENT`
- **Value:** `evan@levine.realestate`

## 🔑 **Gmail App Password Setup**

### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**

### **Step 2: Generate App Password**
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Other (Custom name)**
3. Enter name: `Crawl Walk Automation`
4. Copy the generated 16-character password
5. Use this password for `EMAIL_PASSWORD` secret

## ✅ **Verification Checklist**

- [ ] All 12 secrets added to GitHub repository
- [ ] Gmail app password generated and configured
- [ ] Google Ads API credentials verified
- [ ] Google Drive API credentials verified
- [ ] Email credentials tested

## 🚀 **Testing the Setup**

### **Manual Test**
1. Go to **Actions** tab in your repository
2. Click **Crawl/Walk Strategy Automation**
3. Click **Run workflow**
4. Select **test** action
5. Click **Run workflow**

### **Expected Results**
- ✅ Workflow runs successfully
- ✅ All modules import without errors
- ✅ No authentication failures
- ✅ Logs show successful initialization

## 📊 **Automation Schedule**

The workflow is configured to run:
- **Daily at 9 AM UTC** (2 AM PST / 3 AM PDT)
- **Manual trigger** available anytime
- **Three actions available:**
  - `analyze` - Run daily milestone analysis
  - `execute` - Execute full Crawl/Walk strategy
  - `test` - Test system components

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Authentication Errors**
- ✅ Verify all secrets are correctly set
- ✅ Check Google Ads API permissions
- ✅ Ensure refresh tokens are valid

#### **Import Errors**
- ✅ Check Python dependencies in `requirements.txt`
- ✅ Verify file paths in workflow
- ✅ Test imports locally first

#### **Email Failures**
- ✅ Verify Gmail app password
- ✅ Check SMTP settings
- ✅ Test email credentials manually

### **Debug Commands**
```bash
# Test Google Ads API
python -c "from google.ads.googleads.client import GoogleAdsClient; print('✅ Google Ads OK')"

# Test email
python -c "import smtplib; print('✅ Email OK')"

# Test all imports
python -c "
import crawl_walk_campaign_creator
import enhanced_quick_analysis
import execute_crawl_walk
print('✅ All OK')
"
```

## 📋 **Next Steps**

1. **Set up all secrets** using this guide
2. **Test the workflow** manually
3. **Monitor daily runs** for milestone detection
4. **Review logs** for any issues
5. **Adjust schedule** if needed

**Your Crawl/Walk automation is ready for GitHub Actions!** 🚀
