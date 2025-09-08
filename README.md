# 🏔️ Park City Real Estate PPC Opportunity Dashboard

A powerful Streamlit-based dashboard for discovering and analyzing high-potential keywords for PPC campaigns in the Park City real estate market. Built for **levine.realestate**.

## 🎯 Features

### 1. 🔎 Keyword Discovery & Metrics Engine
- Input 1-3 seed keywords to generate 50+ related keyword ideas
- Fetches comprehensive metrics from Google Ads API:
  - Average Monthly Searches
  - Competition Level (Low/Medium/High)
  - CPC bid ranges
  - Competition Index
- Sortable and searchable data table with advanced filtering

### 2. 📈 Trend & Momentum Visualizer
- 5-year Google Trends analysis for any selected keyword
- **Momentum Score**: Compares last 12 months vs 5-year average
- **Acceleration Analysis**: Linear regression to identify growing/declining trends
- Interactive charts with monthly and yearly breakdowns

### 3. 💡 Actionable Insights & Recommendations
- AI-powered campaign recommendations based on combined metrics
- Campaign type suggestions (Growth Engine, Low-Cost Acquisition, etc.)
- Budget allocation guidance
- Bid strategy recommendations
- Custom ad copy generation
- Negative keyword suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Ads API access with valid credentials
- Active Google Ads account

### Installation

1. **Clone or download this repository**
```bash
cd /Users/evan/Downloads/Trends
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Google Ads API credentials**

Copy the template file and add your credentials:

```bash
cp google-ads.yaml.template google-ads.yaml
```

Then edit the `google-ads.yaml` file and replace the placeholder values with your actual credentials:

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
login_customer_id: YOUR_LOGIN_CUSTOMER_ID
```

**Note:** The `google-ads.yaml` file is in `.gitignore` for security - your credentials will not be committed to the repository.

### Getting Google Ads API Credentials

1. **Developer Token**
   - Log into your Google Ads account
   - Navigate to Tools & Settings → API Center
   - Apply for or copy your developer token

2. **OAuth2 Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Google Ads API
   - Create OAuth 2.0 credentials (Web application type)
   - Download credentials as JSON

3. **Refresh Token**
   - Use the [OAuth Playground](https://developers.google.com/oauthplayground/)
   - Or follow the [Python quickstart guide](https://developers.google.com/google-ads/api/docs/client-libs/python/oauth-web)

4. **Login Customer ID**
   - Your Google Ads Manager Account ID (without hyphens)
   - Found in the top right of your Google Ads interface

## 🎮 Running the Dashboard

Launch the dashboard with:

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Enter Seed Keywords
- Use the sidebar to input 1-3 broad seed keywords
- Examples:
  - "Park City real estate"
  - "luxury ski homes"
  - "Deer Valley properties"

### Step 2: Generate Keywords
- Click "🚀 Generate Keywords" to fetch related keywords
- Adjust the slider to control how many keywords to generate (10-100)

### Step 3: Analyze Keywords
- **Keyword Metrics Tab**: Browse and filter the generated keywords
- Click on any keyword row to select it for detailed analysis
- Use search and filters to find specific keyword types

### Step 4: View Trends
- **Trend Analysis Tab**: See 5-year Google Trends data
- Review momentum and acceleration scores
- Analyze monthly and yearly patterns

### Step 5: Get Recommendations
- **Insights Tab**: View AI-powered campaign recommendations
- Review suggested campaign strategies
- Copy ad copy suggestions
- Note negative keywords to add

## 🎨 Dashboard Components

### Metrics Explained

- **Momentum Score**: `(Last 12 Months Avg / 5-Year Avg) - 1`
  - Positive = Growing interest
  - Negative = Declining interest

- **Acceleration**: Linear regression slope of last 12 months
  - Accelerating = Positive trend
  - Decelerating = Negative trend
  - Stable = Minimal change

### Recommendation Logic

The dashboard provides recommendations based on:

1. **High Priority** (Growth Engine Campaign)
   - Momentum > 20%
   - Accelerating trend
   - Low/Medium competition

2. **Low-Cost Opportunity**
   - CPC < $1.00
   - Low competition

3. **Low Priority** (Defensive Campaign)
   - Negative momentum
   - Decelerating trend

4. **High-Value Target**
   - High competition
   - High CPC (> $5.00)

## 🔧 Customization

### Modify Target Location
Edit line 37 in `app.py`:
```python
GEO_TARGET_ID = "1026481"  # Park City, UT, US
```

Find other location IDs in the [Google Ads Geo Targets](https://developers.google.com/google-ads/api/data/geotargets)

### Adjust Keyword Generation
Modify the default number of keywords on line 167:
```python
max_keywords = st.slider("Number of Keywords to Generate", min_value=10, max_value=100, value=50)
```

### Customize Recommendation Thresholds
Edit the `generate_recommendation()` function starting at line 334 to adjust:
- Momentum thresholds
- CPC thresholds
- Competition levels

## 🐛 Troubleshooting

### Common Issues

1. **"Google Ads API Not Connected"**
   - Verify all credentials in `google-ads.yaml` are correct
   - Ensure your developer token is approved
   - Check that the API is enabled in Google Cloud Console

2. **"No trends data available"**
   - Some keywords may have insufficient search volume
   - Try broader keywords or remove special characters

3. **Empty keyword results**
   - Verify your customer ID has active campaigns
   - Check that your location targeting is valid
   - Try different seed keywords

### Debug Mode
Add this to the top of `app.py` for detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Data Export

To export keyword data:
1. Select and copy from the data table
2. Or add this code snippet to create a download button:

```python
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f"keywords_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
```

## 🔒 Security Notes

- **Never commit `google-ads.yaml` with real credentials to version control**
- Add `google-ads.yaml` to your `.gitignore` file
- Consider using environment variables for production deployments
- Rotate refresh tokens periodically

## 📚 Additional Resources

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [Streamlit Documentation](https://docs.streamlit.io)
- [pytrends Documentation](https://pypi.org/project/pytrends/)
- [Google Trends](https://trends.google.com)

## 💼 For levine.realestate

This dashboard is specifically configured for the Park City, Utah real estate market. It's optimized to help identify:
- Emerging neighborhood searches
- Luxury property keywords
- Seasonal search patterns
- Competitive gaps in PPC coverage

### Recommended Workflow
1. Run weekly keyword discovery sessions
2. Track momentum scores monthly
3. Adjust campaigns based on acceleration trends
4. A/B test ad copy suggestions
5. Monitor competitor keywords quarterly

## 📞 Support

For technical issues with the dashboard, refer to:
- Google Ads API [Support Forum](https://groups.google.com/g/adwords-api)
- Streamlit [Community Forum](https://discuss.streamlit.io)

---

**Built with ❤️ for Park City Real Estate Professionals**

*Version 1.0.0 | Last Updated: November 2024*
