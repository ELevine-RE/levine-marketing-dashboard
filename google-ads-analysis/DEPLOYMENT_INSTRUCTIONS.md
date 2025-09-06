# 🚀 Dashboard Deployment Instructions

## Option 1: Streamlit Cloud (Recommended)

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select this repository: `ELevine-RE/google-ads-analysis`
5. Set main file path: `dashboard.py`
6. Click "Deploy"

Your dashboard will be available at: `https://share.streamlit.io/ELevine-RE/google-ads-analysis/main/dashboard.py`

## Option 2: Heroku

1. Install Heroku CLI
2. Run: `heroku create your-dashboard-name`
3. Run: `git push heroku main`
4. Set environment variables in Heroku dashboard

## Option 3: Railway

1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Deploy automatically

## Environment Variables Required

Set these in your deployment platform:
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

