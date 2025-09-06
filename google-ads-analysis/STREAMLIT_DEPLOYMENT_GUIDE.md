# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy Steps

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Repository: `ELevine-RE/google-ads-analysis`
   - Branch: `main`
   - Main file path: `dashboard.py`

3. **Configure Environment Variables**
   In the Streamlit Cloud dashboard, add these secrets:
   - `GOOGLE_ADS_DEVELOPER_TOKEN`
   - `GOOGLE_ADS_CLIENT_ID`
   - `GOOGLE_ADS_CLIENT_SECRET`
   - `GOOGLE_ADS_REFRESH_TOKEN`
   - `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your dashboard will be live!

## Dashboard URL
Your dashboard will be available at:
`https://share.streamlit.io/ELevine-RE/google-ads-analysis/main/dashboard.py`

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility

### No Data Showing
- Verify environment variables are set correctly
- Check Google Ads API credentials
- Ensure campaigns are active

### Charts Not Loading
- Check internet connection
- Verify Plotly installation
- Clear browser cache

## Support
If you encounter issues:
1. Check the build logs in Streamlit Cloud
2. Verify all environment variables are set
3. Test locally first with `streamlit run dashboard.py`
