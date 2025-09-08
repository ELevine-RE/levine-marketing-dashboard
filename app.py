"""
Park City Real Estate PPC Opportunity Dashboard
================================================
A comprehensive Streamlit dashboard for identifying and analyzing high-potential
keywords for PPC campaigns targeting Park City real estate market.

Author: Levine Real Estate Team
Website: levine.realestate
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
from pytrends.request import TrendReq
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from scipy import stats
import yaml
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Park City Real Estate PPC Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Better Styling ---
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .recommendation-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    .high-priority {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .low-cost {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    .low-priority {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    .high-value {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'keywords_df' not in st.session_state:
    st.session_state.keywords_df = None
if 'selected_keyword' not in st.session_state:
    st.session_state.selected_keyword = None
if 'trends_data' not in st.session_state:
    st.session_state.trends_data = None

# --- Constants ---
# Geographic targeting: Park City, Utah, United States
GEO_TARGET_ID = "1026481"  # Park City, UT, US
LANGUAGE_ID = "1000"  # English

# --- Helper Functions ---

@st.cache_resource
def load_google_ads_client():
    """
    Load Google Ads client from google-ads.yaml configuration file.
    
    Returns:
        tuple: (GoogleAdsClient, customer_id) or (None, None) if error
    """
    try:
        # First try to load from google-ads.yaml
        config_path = "google-ads.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            # Extract customer_id before creating client
            customer_id = config.get('login_customer_id', '')
            
            # Create client from YAML file
            client = GoogleAdsClient.load_from_storage(config_path)
            return client, customer_id
        else:
            st.error("⚠️ google-ads.yaml file not found. Please create it with your Google Ads API credentials.")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error loading Google Ads client: {str(e)}")
        return None, None

def get_keyword_ideas(client, customer_id, seed_keywords, max_keywords=50):
    """
    Fetch keyword ideas from Google Ads API based on seed keywords.
    
    Args:
        client: Google Ads API client
        customer_id: Google Ads customer ID
        seed_keywords: List of seed keywords to generate ideas from
        max_keywords: Maximum number of keyword ideas to return
        
    Returns:
        list: List of keyword data dictionaries
    """
    try:
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        googleads_service = client.get_service("GoogleAdsService")
        
        # Build the request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = googleads_service.language_constant_path(LANGUAGE_ID)
        request.geo_target_constants.append(
            googleads_service.geo_target_constant_path(GEO_TARGET_ID)
        )
        
        # Add seed keywords
        request.keyword_seed.keywords.extend(seed_keywords)
        request.include_adult_keywords = False
        
        # Set date range for historical metrics (last 12 months)
        current_date = datetime.now()
        request.historical_metrics_options.year_month_range.start.year = current_date.year - 1
        request.historical_metrics_options.year_month_range.start.month = client.enums.MonthOfYearEnum.JANUARY
        request.historical_metrics_options.year_month_range.end.year = current_date.year
        request.historical_metrics_options.year_month_range.end.month = client.enums.MonthOfYearEnum[current_date.strftime('%B').upper()]
        
        # Make the API call
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        # Process results
        keywords_data = []
        for idx, result in enumerate(response):
            if idx >= max_keywords:
                break
                
            metrics = result.keyword_idea_metrics
            
            # Extract competition level
            if metrics.competition:
                competition = metrics.competition.name
            else:
                competition = "UNSPECIFIED"
            
            # Convert micros to dollars for bid amounts
            low_bid = metrics.low_top_of_page_bid_micros / 1_000_000 if metrics.low_top_of_page_bid_micros else 0
            high_bid = metrics.high_top_of_page_bid_micros / 1_000_000 if metrics.high_top_of_page_bid_micros else 0
            
            keywords_data.append({
                "Keyword": result.text,
                "Avg Monthly Searches": metrics.avg_monthly_searches if metrics.avg_monthly_searches else 0,
                "Competition": competition,
                "Low Bid ($)": low_bid,
                "High Bid ($)": high_bid,
                "Competition Index": metrics.competition_index if metrics.competition_index else 0
            })
        
        return keywords_data
        
    except GoogleAdsException as ex:
        st.error(f"Google Ads API Error: {ex.error.code().name}")
        for error in ex.failure.errors:
            st.error(f"Error message: {error.message}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_trends_data(keyword, timeframe="today 5-y"):
    """
    Fetch Google Trends data for a specific keyword.
    
    Args:
        keyword: The keyword to analyze
        timeframe: Time range for trends data (default: 5 years)
        
    Returns:
        DataFrame: Trends data with dates and interest values
    """
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Build payload
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='US-UT')
        
        # Get interest over time
        trends_df = pytrends.interest_over_time()
        
        if not trends_df.empty:
            # Remove the 'isPartial' column if it exists
            if 'isPartial' in trends_df.columns:
                trends_df = trends_df.drop(columns=['isPartial'])
            
            # Reset index to make date a column
            trends_df = trends_df.reset_index()
            
            return trends_df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error fetching trends data: {str(e)}")
        return pd.DataFrame()

def calculate_momentum_score(trends_df, keyword_col):
    """
    Calculate momentum score: (Last 12 Months Avg / 5-Year Avg) - 1
    
    Args:
        trends_df: DataFrame with trends data
        keyword_col: Name of the keyword column
        
    Returns:
        float: Momentum score as a percentage
    """
    if trends_df.empty or keyword_col not in trends_df.columns:
        return 0
    
    # Get last 12 months data
    last_year = datetime.now() - timedelta(days=365)
    recent_data = trends_df[trends_df['date'] >= last_year][keyword_col].mean()
    
    # Get all data average
    all_data = trends_df[keyword_col].mean()
    
    if all_data == 0:
        return 0
    
    momentum = ((recent_data / all_data) - 1) * 100
    return momentum

def calculate_acceleration(trends_df, keyword_col):
    """
    Calculate acceleration using linear regression on last 12 months.
    
    Args:
        trends_df: DataFrame with trends data
        keyword_col: Name of the keyword column
        
    Returns:
        tuple: (slope, acceleration_status)
    """
    if trends_df.empty or keyword_col not in trends_df.columns:
        return 0, "Unknown"
    
    # Get last 12 months data
    last_year = datetime.now() - timedelta(days=365)
    recent_df = trends_df[trends_df['date'] >= last_year].copy()
    
    if len(recent_df) < 2:
        return 0, "Insufficient Data"
    
    # Prepare data for regression
    recent_df['days'] = (recent_df['date'] - recent_df['date'].min()).dt.days
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        recent_df['days'], 
        recent_df[keyword_col]
    )
    
    # Determine acceleration status
    if slope > 0.1:
        status = "Accelerating"
    elif slope < -0.1:
        status = "Decelerating"
    else:
        status = "Stable"
    
    return slope, status

def generate_recommendation(momentum, acceleration_status, competition, avg_cpc):
    """
    Generate PPC campaign recommendation based on metrics.
    
    Args:
        momentum: Momentum score percentage
        acceleration_status: "Accelerating", "Decelerating", or "Stable"
        competition: Competition level (LOW, MEDIUM, HIGH)
        avg_cpc: Average CPC (average of low and high bid)
        
    Returns:
        tuple: (recommendation_text, recommendation_class)
    """
    # High Priority: Strong growth with manageable competition
    if momentum > 20 and acceleration_status == "Accelerating" and competition in ["LOW", "MEDIUM"]:
        return (
            "🚀 **High Priority**: Strong growth trend with manageable competition. "
            "Ideal for a 'Growth Engine' campaign. Allocate significant budget and "
            "create dedicated landing pages to capture this momentum.",
            "high-priority"
        )
    
    # Low-Cost Opportunity
    elif avg_cpc < 1.00 and competition == "LOW":
        return (
            "💰 **Low-Cost Opportunity**: Capture affordable traffic and leads. "
            "Ideal for a 'Low-Cost Acquisition' campaign. Test with small budget "
            "and scale based on conversion rates.",
            "low-cost"
        )
    
    # Low Priority: Declining interest
    elif momentum < 0 and acceleration_status == "Decelerating":
        return (
            "⚠️ **Low Priority**: Declining interest trend. Monitor only or use in "
            "a 'Defensive' campaign with minimal budget. Consider seasonal factors.",
            "low-priority"
        )
    
    # High-Value Target
    elif competition == "HIGH" and avg_cpc > 5.00:
        return (
            "💎 **High-Value Target**: High cost and competition suggest valuable leads. "
            "Requires dedicated budget, optimized landing pages, and careful bid management. "
            "Focus on quality score improvements.",
            "high-value"
        )
    
    # Default: Moderate opportunity
    else:
        return (
            "📊 **Moderate Opportunity**: Standard keyword with balanced metrics. "
            "Include in general campaigns with regular monitoring and optimization.",
            "moderate"
        )

# --- Main Dashboard ---

def main():
    """Main dashboard application."""
    
    # Header
    st.title("🏔️ Park City Real Estate PPC Opportunity Dashboard")
    st.markdown("**For:** levine.realestate | **Market:** Park City, Utah")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Status Check
        client, customer_id = load_google_ads_client()
        
        if client:
            st.success("✅ Google Ads API Connected")
        else:
            st.warning("⚠️ Google Ads API Not Connected")
            st.info(
                "Please create a `google-ads.yaml` file with your credentials:\n\n"
                "```yaml\n"
                "developer_token: YOUR_DEVELOPER_TOKEN\n"
                "client_id: YOUR_CLIENT_ID\n"
                "client_secret: YOUR_CLIENT_SECRET\n"
                "refresh_token: YOUR_REFRESH_TOKEN\n"
                "login_customer_id: YOUR_LOGIN_CUSTOMER_ID\n"
                "```"
            )
        
        st.markdown("---")
        
        # Seed Keywords Input
        st.header("🔍 Keyword Discovery")
        
        seed_input = st.text_area(
            "Enter Seed Keywords (1-3)",
            value="Park City real estate\nluxury ski homes\nDeer Valley properties",
            help="Enter 1-3 broad seed keywords, one per line",
            height=100
        )
        
        # Parse seed keywords
        seed_keywords = [kw.strip() for kw in seed_input.split('\n') if kw.strip()][:3]
        
        # Number of keywords to generate
        max_keywords = st.slider(
            "Number of Keywords to Generate",
            min_value=10,
            max_value=100,
            value=50,
            step=10
        )
        
        # Generate Keywords Button
        if st.button("🚀 Generate Keywords", type="primary", disabled=(client is None)):
            with st.spinner("Fetching keyword data from Google Ads API..."):
                keywords_data = get_keyword_ideas(client, customer_id, seed_keywords, max_keywords)
                
                if keywords_data:
                    st.session_state.keywords_df = pd.DataFrame(keywords_data)
                    st.success(f"✅ Generated {len(keywords_data)} keyword ideas!")
                else:
                    st.error("Failed to generate keywords. Please check your API configuration.")
    
    # Main Content Area
    if st.session_state.keywords_df is not None:
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Keyword Metrics", "📈 Trend Analysis", "💡 Insights"])
        
        with tab1:
            st.header("Keyword Discovery & Metrics")
            
            # Display metrics summary
            col1, col2, col3, col4 = st.columns(4)
            
            df = st.session_state.keywords_df
            
            with col1:
                st.metric(
                    "Total Keywords",
                    len(df),
                    f"{len(df[df['Competition'] == 'LOW'])} low competition"
                )
            
            with col2:
                avg_searches = df['Avg Monthly Searches'].mean()
                st.metric(
                    "Avg Monthly Searches",
                    f"{avg_searches:,.0f}",
                    f"Total: {df['Avg Monthly Searches'].sum():,.0f}"
                )
            
            with col3:
                avg_cpc = (df['Low Bid ($)'] + df['High Bid ($)']) / 2
                st.metric(
                    "Avg CPC",
                    f"${avg_cpc.mean():.2f}",
                    f"Range: ${df['Low Bid ($)'].min():.2f} - ${df['High Bid ($)'].max():.2f}"
                )
            
            with col4:
                competition_dist = df['Competition'].value_counts()
                low_comp = competition_dist.get('LOW', 0)
                st.metric(
                    "Low Competition",
                    f"{low_comp}",
                    f"{(low_comp/len(df)*100):.1f}% of keywords"
                )
            
            st.markdown("---")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_filter = st.text_input("🔍 Search Keywords", placeholder="Type to filter...")
            
            with col2:
                competition_filter = st.multiselect(
                    "Competition Level",
                    options=df['Competition'].unique(),
                    default=df['Competition'].unique()
                )
            
            with col3:
                min_searches = st.number_input(
                    "Min Monthly Searches",
                    min_value=0,
                    value=0,
                    step=100
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_filter:
                filtered_df = filtered_df[
                    filtered_df['Keyword'].str.contains(search_filter, case=False, na=False)
                ]
            
            if competition_filter:
                filtered_df = filtered_df[filtered_df['Competition'].isin(competition_filter)]
            
            filtered_df = filtered_df[filtered_df['Avg Monthly Searches'] >= min_searches]
            
            # Sort options
            col1, col2 = st.columns([3, 1])
            with col1:
                sort_by = st.selectbox(
                    "Sort by",
                    options=['Avg Monthly Searches', 'Low Bid ($)', 'High Bid ($)', 'Competition Index'],
                    index=0
                )
            with col2:
                sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
            
            # Sort the dataframe
            ascending = (sort_order == "Ascending")
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
            
            # Display the dataframe with selection
            st.subheader(f"📋 Keyword Data ({len(filtered_df)} keywords)")
            
            # Format the display
            display_df = filtered_df.copy()
            display_df['Low Bid ($)'] = display_df['Low Bid ($)'].apply(lambda x: f"${x:.2f}")
            display_df['High Bid ($)'] = display_df['High Bid ($)'].apply(lambda x: f"${x:.2f}")
            display_df['Avg Monthly Searches'] = display_df['Avg Monthly Searches'].apply(lambda x: f"{x:,}")
            
            # Create selectable dataframe
            selected_indices = st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Handle selection
            if selected_indices and selected_indices.selection.rows:
                selected_row = selected_indices.selection.rows[0]
                st.session_state.selected_keyword = filtered_df.iloc[selected_row]['Keyword']
                st.info(f"📌 Selected Keyword: **{st.session_state.selected_keyword}**")
        
        with tab2:
            st.header("Trend & Momentum Analysis")
            
            if st.session_state.selected_keyword:
                keyword = st.session_state.selected_keyword
                st.subheader(f"Analyzing: {keyword}")
                
                # Fetch trends data
                with st.spinner(f"Fetching Google Trends data for '{keyword}'..."):
                    trends_df = get_trends_data(keyword)
                    
                    if not trends_df.empty:
                        st.session_state.trends_data = trends_df
                        
                        # Calculate metrics
                        momentum = calculate_momentum_score(trends_df, keyword)
                        slope, acceleration = calculate_acceleration(trends_df, keyword)
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(
                                f"""<div class="metric-card">
                                <h3>📈 Momentum Score</h3>
                                <h1>{momentum:+.1f}%</h1>
                                <p>Last 12mo vs 5yr avg</p>
                                </div>""",
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            emoji = "🚀" if acceleration == "Accelerating" else "📉" if acceleration == "Decelerating" else "➡️"
                            st.markdown(
                                f"""<div class="metric-card">
                                <h3>{emoji} Acceleration</h3>
                                <h1>{acceleration}</h1>
                                <p>Slope: {slope:.3f}</p>
                                </div>""",
                                unsafe_allow_html=True
                            )
                        
                        with col3:
                            # Get current interest
                            current_interest = trends_df[keyword].iloc[-1]
                            st.markdown(
                                f"""<div class="metric-card">
                                <h3>🎯 Current Interest</h3>
                                <h1>{current_interest}</h1>
                                <p>Google Trends Index</p>
                                </div>""",
                                unsafe_allow_html=True
                            )
                        
                        st.markdown("---")
                        
                        # Create trend chart
                        fig = go.Figure()
                        
                        # Add main trend line
                        fig.add_trace(go.Scatter(
                            x=trends_df['date'],
                            y=trends_df[keyword],
                            mode='lines',
                            name='Search Interest',
                            line=dict(color='#3B82F6', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(59, 130, 246, 0.1)'
                        ))
                        
                        # Add 12-month marker
                        last_year = datetime.now() - timedelta(days=365)
                        fig.add_vline(
                            x=last_year,
                            line_dash="dash",
                            line_color="gray",
                            annotation_text="12 Months Ago"
                        )
                        
                        # Add trend line for last 12 months
                        recent_df = trends_df[trends_df['date'] >= last_year].copy()
                        if len(recent_df) > 1:
                            recent_df['days'] = (recent_df['date'] - recent_df['date'].min()).dt.days
                            z = np.polyfit(recent_df['days'], recent_df[keyword], 1)
                            p = np.poly1d(z)
                            
                            fig.add_trace(go.Scatter(
                                x=recent_df['date'],
                                y=p(recent_df['days']),
                                mode='lines',
                                name='Trend Line',
                                line=dict(
                                    color='#EF4444' if acceleration == "Decelerating" else '#10B981',
                                    width=2,
                                    dash='dash'
                                )
                            ))
                        
                        # Update layout
                        fig.update_layout(
                            title=f"5-Year Search Trend: {keyword}",
                            xaxis_title="Date",
                            yaxis_title="Search Interest (0-100)",
                            hovermode='x unified',
                            height=500,
                            showlegend=True,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Additional trend insights
                        st.subheader("📊 Trend Insights")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Monthly breakdown for last year
                            st.markdown("**Monthly Average (Last 12 Months)**")
                            monthly_avg = recent_df.set_index('date')[keyword].resample('M').mean()
                            
                            fig_monthly = go.Figure(data=[
                                go.Bar(
                                    x=monthly_avg.index.strftime('%b %Y'),
                                    y=monthly_avg.values,
                                    marker_color='#3B82F6'
                                )
                            ])
                            fig_monthly.update_layout(
                                height=300,
                                showlegend=False,
                                template='plotly_white',
                                xaxis_title="Month",
                                yaxis_title="Avg Interest"
                            )
                            st.plotly_chart(fig_monthly, use_container_width=True)
                        
                        with col2:
                            # Year-over-year comparison
                            st.markdown("**Year-over-Year Comparison**")
                            
                            yearly_data = []
                            for i in range(5):
                                year_start = datetime.now() - timedelta(days=365*(i+1))
                                year_end = datetime.now() - timedelta(days=365*i)
                                year_data = trends_df[
                                    (trends_df['date'] >= year_start) & 
                                    (trends_df['date'] < year_end)
                                ][keyword].mean()
                                yearly_data.append({
                                    'Year': f"Year {5-i}",
                                    'Avg Interest': year_data
                                })
                            
                            yearly_df = pd.DataFrame(yearly_data)
                            
                            fig_yearly = go.Figure(data=[
                                go.Scatter(
                                    x=yearly_df['Year'],
                                    y=yearly_df['Avg Interest'],
                                    mode='lines+markers',
                                    marker=dict(size=10, color='#10B981'),
                                    line=dict(width=3, color='#10B981')
                                )
                            ])
                            fig_yearly.update_layout(
                                height=300,
                                showlegend=False,
                                template='plotly_white',
                                xaxis_title="Year",
                                yaxis_title="Avg Interest"
                            )
                            st.plotly_chart(fig_yearly, use_container_width=True)
                    
                    else:
                        st.warning("No trends data available for this keyword.")
            else:
                st.info("👆 Please select a keyword from the Keyword Metrics tab to analyze trends.")
        
        with tab3:
            st.header("Actionable Insights & Recommendations")
            
            if st.session_state.selected_keyword and st.session_state.trends_data is not None:
                keyword = st.session_state.selected_keyword
                trends_df = st.session_state.trends_data
                
                # Get keyword metrics
                keyword_row = df[df['Keyword'] == keyword].iloc[0]
                
                # Calculate metrics
                momentum = calculate_momentum_score(trends_df, keyword)
                slope, acceleration = calculate_acceleration(trends_df, keyword)
                competition = keyword_row['Competition']
                avg_cpc = (keyword_row['Low Bid ($)'] + keyword_row['High Bid ($)']) / 2
                
                # Generate recommendation
                recommendation, rec_class = generate_recommendation(
                    momentum, acceleration, competition, avg_cpc
                )
                
                # Display recommendation
                st.markdown(
                    f'<div class="recommendation-box {rec_class}">{recommendation}</div>',
                    unsafe_allow_html=True
                )
                
                st.markdown("---")
                
                # Detailed Analysis
                st.subheader("📋 Detailed Keyword Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Keyword Metrics")
                    st.write(f"**Keyword:** {keyword}")
                    st.write(f"**Monthly Searches:** {keyword_row['Avg Monthly Searches']:,}")
                    st.write(f"**Competition:** {competition}")
                    st.write(f"**CPC Range:** ${keyword_row['Low Bid ($)']:.2f} - ${keyword_row['High Bid ($)']:.2f}")
                    st.write(f"**Competition Index:** {keyword_row['Competition Index']:.0f}")
                
                with col2:
                    st.markdown("### Trend Metrics")
                    st.write(f"**Momentum Score:** {momentum:+.1f}%")
                    st.write(f"**Acceleration:** {acceleration}")
                    st.write(f"**Trend Slope:** {slope:.4f}")
                    st.write(f"**Current Interest:** {trends_df[keyword].iloc[-1]}")
                    st.write(f"**Peak Interest:** {trends_df[keyword].max()}")
                
                st.markdown("---")
                
                # Campaign Strategy Suggestions
                st.subheader("🎯 Campaign Strategy Suggestions")
                
                # Determine campaign type based on metrics
                if momentum > 20 and acceleration == "Accelerating":
                    campaign_type = "Growth Engine Campaign"
                    budget_suggestion = "High (15-25% of total PPC budget)"
                    bid_strategy = "Target Impression Share or Maximize Conversions"
                    landing_page = "Create dedicated, conversion-optimized landing page"
                elif avg_cpc < 1.00 and competition == "LOW":
                    campaign_type = "Low-Cost Acquisition Campaign"
                    budget_suggestion = "Low-Medium (5-10% of total PPC budget)"
                    bid_strategy = "Manual CPC or Enhanced CPC"
                    landing_page = "Use existing category page with tracking"
                elif momentum < 0 and acceleration == "Decelerating":
                    campaign_type = "Defensive Campaign"
                    budget_suggestion = "Minimal (1-3% of total PPC budget)"
                    bid_strategy = "Target CPA with conservative goals"
                    landing_page = "General property search page"
                else:
                    campaign_type = "Standard Campaign"
                    budget_suggestion = "Medium (8-12% of total PPC budget)"
                    bid_strategy = "Maximize Clicks or Target CPA"
                    landing_page = "Optimized category or neighborhood page"
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 📊 Campaign Type")
                    st.info(campaign_type)
                
                with col2:
                    st.markdown("#### 💰 Budget Allocation")
                    st.info(budget_suggestion)
                
                with col3:
                    st.markdown("#### 🎯 Bid Strategy")
                    st.info(bid_strategy)
                
                st.markdown("#### 🏠 Landing Page Strategy")
                st.info(landing_page)
                
                # Ad Copy Suggestions
                st.markdown("---")
                st.subheader("✍️ Ad Copy Suggestions")
                
                # Generate ad copy based on keyword
                if "luxury" in keyword.lower() or "ski" in keyword.lower():
                    headline1 = "Luxury Park City Properties"
                    headline2 = "Ski-In/Ski-Out Homes Available"
                    description = "Exclusive mountain estates. Private showings available. Your dream home awaits."
                elif "deer valley" in keyword.lower():
                    headline1 = "Deer Valley Real Estate Expert"
                    headline2 = "Premium Properties & Ski Access"
                    description = "Local expertise, exceptional properties. Schedule your private tour today."
                elif "heber" in keyword.lower():
                    headline1 = "Heber Valley's Top Properties"
                    headline2 = "Mountain Living, City Convenience"
                    description = "Discover your perfect home in Heber. Expert local guidance. View listings now."
                else:
                    headline1 = "Park City Real Estate Leaders"
                    headline2 = "Find Your Dream Mountain Home"
                    description = "Trusted local experts. Exclusive listings. Start your search today."
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Responsive Search Ad Headlines:**")
                    st.code(f"1. {headline1}\n2. {headline2}\n3. Levine Real Estate - Local Experts\n4. Browse {keyword_row['Avg Monthly Searches']:,}+ Listings")
                
                with col2:
                    st.markdown("**Descriptions:**")
                    st.code(f"1. {description}\n2. Visit levine.realestate for exclusive Park City properties and expert guidance.")
                
                # Negative Keywords Suggestions
                st.markdown("---")
                st.subheader("🚫 Suggested Negative Keywords")
                
                negative_keywords = [
                    "cheap", "foreclosure", "rental", "rent", "apartment",
                    "jobs", "weather", "news", "restaurants", "hotels",
                    "vacation rental", "airbnb", "vrbo", "timeshare"
                ]
                
                st.write("Add these negative keywords to avoid irrelevant traffic:")
                st.code(", ".join(negative_keywords))
                
            else:
                st.info("👆 Please select a keyword and run trend analysis to see recommendations.")
    
    else:
        # Welcome screen when no data is loaded
        st.markdown(
            """
            ## 👋 Welcome to the PPC Opportunity Dashboard
            
            This dashboard helps you identify and analyze high-potential keywords for your 
            Park City real estate PPC campaigns.
            
            ### 🚀 Getting Started:
            
            1. **Configure Google Ads API** - Add your credentials to `google-ads.yaml`
            2. **Enter Seed Keywords** - Use the sidebar to input 1-3 broad keywords
            3. **Generate Keywords** - Click the button to fetch keyword ideas
            4. **Analyze Trends** - Select keywords to see Google Trends data
            5. **Get Recommendations** - View actionable insights for your campaigns
            
            ### 📊 Features:
            
            - **Keyword Discovery** - Generate 50+ keyword ideas from seed terms
            - **Competitive Analysis** - See competition levels and CPC estimates
            - **Trend Analysis** - 5-year Google Trends data with momentum scoring
            - **Smart Recommendations** - AI-powered campaign suggestions
            - **Ad Copy Generator** - Customized ad copy for each keyword
            
            👈 **Use the sidebar to begin your keyword research!**
            """
        )
        
        # Sample data preview
        st.markdown("---")
        st.subheader("📝 Sample Keywords for Park City Real Estate")
        
        sample_data = pd.DataFrame({
            'Keyword': [
                'park city real estate',
                'deer valley homes for sale',
                'luxury ski properties utah',
                'park city condos',
                'utah mountain homes'
            ],
            'Avg Monthly Searches': [2900, 720, 390, 1300, 880],
            'Competition': ['HIGH', 'MEDIUM', 'LOW', 'HIGH', 'MEDIUM'],
            'Est. CPC': ['$8.50', '$6.20', '$4.80', '$7.10', '$5.50']
        })
        
        st.dataframe(sample_data, use_container_width=True, hide_index=True)

# --- Run the App ---
if __name__ == "__main__":
    main()
