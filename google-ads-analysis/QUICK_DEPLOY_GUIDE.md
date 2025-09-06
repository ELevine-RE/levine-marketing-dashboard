# 🚀 Quick Dashboard Deployment Guide

## Deploy to Streamlit Cloud (Recommended)

### **Step 1: Go to Streamlit Cloud**
1. Visit: https://share.streamlit.io/
2. Sign in with your GitHub account

### **Step 2: Create New App**
1. Click "New app"
2. Repository: `ELevine-RE/google-ads-analysis`
3. Branch: `main`
4. Main file path: `dashboard.py`
5. Click "Deploy"

### **Step 3: Add Environment Variables**
In the Streamlit Cloud dashboard, add these secrets:
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

### **Step 4: Access Your Dashboard**
Your dashboard will be live at:
`https://share.streamlit.io/ELevine-RE/google-ads-analysis/main/dashboard.py`

## Alternative: Railway Deployment

### **Step 1: Go to Railway**
1. Visit: https://railway.app/
2. Sign in with GitHub

### **Step 2: Deploy**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `ELevine-RE/google-ads-analysis`
4. Add environment variables
5. Deploy automatically

## Alternative: Heroku Deployment

### **Step 1: Install Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### **Step 2: Deploy**
```bash
heroku login
heroku create your-dashboard-name
git push heroku main
heroku config:set GOOGLE_ADS_DEVELOPER_TOKEN=your_token
heroku config:set GOOGLE_ADS_CLIENT_ID=your_client_id
heroku config:set GOOGLE_ADS_CLIENT_SECRET=your_client_secret
heroku config:set GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
heroku config:set GOOGLE_ADS_LOGIN_CUSTOMER_ID=5426234549
heroku open
```

## Environment Variables Required

Make sure to set these in your chosen platform:

| Variable | Description |
|----------|-------------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Your Google Ads API developer token |
| `GOOGLE_ADS_CLIENT_ID` | OAuth 2.0 client ID |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth 2.0 client secret |
| `GOOGLE_ADS_REFRESH_TOKEN` | OAuth 2.0 refresh token |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Your Google Ads customer ID (5426234549) |

## Dashboard Features

Once deployed, you'll have access to:

✅ **Real-time Google Ads metrics** for both campaigns  
✅ **Google Analytics integration**  
✅ **Goal progression tracking**  
✅ **A/B test comparison**  
✅ **Alerts & recommendations**  
✅ **Trend analysis**  
✅ **Mobile-responsive design**  

## Troubleshooting

### **Build Fails**
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility

### **No Data Showing**
- Verify environment variables are set correctly
- Check Google Ads API credentials
- Ensure campaigns are active

### **Charts Not Loading**
- Check internet connection
- Verify Plotly installation
- Clear browser cache

## Support

If you encounter issues:
1. Check the build logs in your deployment platform
2. Verify all environment variables are set
3. Test locally first with `streamlit run dashboard.py`

---

**Your dashboard will be accessible from anywhere in the world! 🌍**
