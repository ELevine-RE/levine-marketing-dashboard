# Daily Email Setup Instructions

## 📧 Setting Up Daily Google Ads Summaries for evan@levine.realestate

### Overview
- **Recipient**: evan@levine.realestate
- **Time**: 8 AM Mountain Time daily
- **Content**: Google Ads performance summary with AI recommendations

### ⚠️ Important: Gmail Requirement

To send emails automatically, you need a **Gmail account** because:
1. Gmail provides reliable SMTP service
2. Other email providers have stricter security requirements
3. Gmail allows app passwords for automated sending

### 🛠️ Setup Options

#### Option 1: Use Your Personal Gmail (Recommended)
1. Use your personal Gmail account as the sender
2. Set up an app password for security
3. Configure reply-to as developer@levine.realestate

#### Option 2: Create a Gmail for Business
1. Create a new Gmail account like `levine.realestate.ads@gmail.com`
2. Use this for sending automated emails
3. Set reply-to as developer@levine.realestate

#### Option 3: Use Gmail with Custom Domain
1. Set up Gmail with your domain (requires Google Workspace)
2. Use developer@levine.realestate directly
3. Configure SMTP settings

### 📋 Step-by-Step Setup

#### 1. Choose Your Gmail Account
Decide which Gmail account to use for sending:
- Personal Gmail: `yourname@gmail.com`
- Business Gmail: `levine.realestate.ads@gmail.com` (recommended)

#### 2. Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Generate an app password
4. Copy the 16-character password

#### 3. Update Configuration
Edit `daily_email_config.py` and update:
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-gmail@gmail.com',  # Your Gmail
    'sender_password': 'your-16-char-app-password',  # App password
    'recipient_email': 'evan@levine.realestate',
    'reply_to': 'developer@levine.realestate'  # Reply-to address
}
```

#### 4. Test the Setup
```bash
python daily_email_config.py --test
```

#### 5. Set Up Automated Schedule
```bash
# Add to crontab
crontab -e

# Add this line:
0 8 * * * cd /tmp/google-ads-setup && /tmp/google-ads-setup/.venv/bin/python daily_email_config.py
```

### 🎯 Email Format

The daily email will include:
- **Performance Summary**: Last 24h, 7d, 14d, 30d
- **Planned Changes**: AI recommendations
- **Impact Assessment**: Medium and long-term effects
- **Intervention Options**: 2-hour response window

### 🔧 Troubleshooting

#### Common Issues:
1. **Authentication Error**: Check app password
2. **SMTP Error**: Verify Gmail settings
3. **Permission Denied**: Ensure API access is granted

#### Test Commands:
```bash
# Test email sending
python daily_email_config.py --test

# Test configuration
python daily_email_config.py --setup

# Manual run
python daily_email_config.py
```

### 📞 Support
If you need help setting up the Gmail account or app password, I can guide you through the process.
