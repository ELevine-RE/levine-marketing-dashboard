"""
Park City Real Estate Campaign Strategy Dashboard
================================================
Integrates existing Google Trends data with Google Ads API to generate
comprehensive campaign strategies with audience, timing, and spend recommendations.

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
import json
import glob
from pathlib import Path
from pytrends.request import TrendReq
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from scipy import stats
import yaml

# --- Page Configuration ---
st.set_page_config(
    page_title="Park City Real Estate Campaign Strategy Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .strategy-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .market-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .budget-card {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .timing-card {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-highlight {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'trends_data' not in st.session_state:
    st.session_state.trends_data = None
if 'ppc_recommendations' not in st.session_state:
    st.session_state.ppc_recommendations = None
if 'master_dataframe' not in st.session_state:
    st.session_state.master_dataframe = None

# --- Constants ---
GEO_TARGET_ID = "1026481"  # Park City, UT, US
LANGUAGE_ID = "1000"  # English

# --- Data Loading Functions ---

def load_existing_trends_data():
    """Load existing Google Trends data from CSV files."""
    trends_data = {}
    
    # Define the markets and their directories
    markets = [
        "Deer Valley East Real Estate",
        "Deer Valley Real Estate", 
        "Glenwild",
        "Heber Utah Real Estate",
        "Kamas Real Estate",
        "Park City Real Estate",
        "Promontory Park City ",
        "Red Ledges Real Estate",
        "Ski in Ski Out Home for Sale",
        "Victory Ranch Real Esate"
    ]
    
    for market in markets:
        market_data = {}
        
        # Load data for different timeframes
        for timeframe in ["1 Year", "2 Year", "5 Year"]:
            timeframe_dir = f"{market}/{timeframe}"
            if os.path.exists(timeframe_dir):
                # Load multiTimeline data (main trends data)
                timeline_files = glob.glob(f"{timeframe_dir}/multiTimeline*.csv")
                if timeline_files:
                    try:
                        # Google Trends CSV files have a specific structure
                        df = pd.read_csv(timeline_files[0], skiprows=2)  # Skip header rows
                        market_data[timeframe] = df
                    except Exception as e:
                        st.warning(f"Could not load {timeframe_dir}/multiTimeline data: {e}")
                
                # Load related queries
                query_files = glob.glob(f"{timeframe_dir}/relatedQueries*.csv")
                if query_files:
                    try:
                        # Related queries CSV has a specific structure with category header
                        queries_df = pd.read_csv(query_files[0], skiprows=3)  # Skip category and header rows
                        market_data[f"{timeframe}_queries"] = queries_df
                    except Exception as e:
                        st.warning(f"Could not load {timeframe_dir}/relatedQueries data: {e}")
                
                # Load geo data
                geo_files = glob.glob(f"{timeframe_dir}/geoMap*.csv")
                if geo_files:
                    try:
                        geo_df = pd.read_csv(geo_files[0], skiprows=1)  # Skip header row
                        market_data[f"{timeframe}_geo"] = geo_df
                    except Exception as e:
                        st.warning(f"Could not load {timeframe_dir}/geoMap data: {e}")
        
        if market_data:
            trends_data[market] = market_data
    
    return trends_data

def load_existing_analysis():
    """Load existing analysis files."""
    analysis_data = {}
    
    # Load PPC recommendations
    if os.path.exists("Analysis/ppc_recommendations.json"):
        try:
            with open("Analysis/ppc_recommendations.json", 'r') as f:
                analysis_data['ppc_recommendations'] = json.load(f)
        except Exception as e:
            st.warning(f"Could not load PPC recommendations: {e}")
    
    # Load master dataframe
    if os.path.exists("Analysis/master_dataframe.csv"):
        try:
            analysis_data['master_dataframe'] = pd.read_csv("Analysis/master_dataframe.csv")
        except Exception as e:
            st.warning(f"Could not load master dataframe: {e}")
    
    return analysis_data

@st.cache_resource
def load_google_ads_client():
    """Load Google Ads client from google-ads.yaml configuration file."""
    try:
        config_path = "google-ads.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            customer_id = config.get('login_customer_id', '')
            client = GoogleAdsClient.load_from_storage(config_path)
            return client, customer_id
        else:
            st.error("⚠️ google-ads.yaml file not found. Please create it with your Google Ads API credentials.")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error loading Google Ads client: {str(e)}")
        return None, None

def get_keyword_ideas(client, customer_id, seed_keywords, max_keywords=50):
    """Fetch keyword ideas from Google Ads API."""
    try:
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        googleads_service = client.get_service("GoogleAdsService")
        
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = googleads_service.language_constant_path(LANGUAGE_ID)
        request.geo_target_constants.append(
            googleads_service.geo_target_constant_path(GEO_TARGET_ID)
        )
        
        request.keyword_seed.keywords.extend(seed_keywords)
        request.include_adult_keywords = False
        
        current_date = datetime.now()
        request.historical_metrics_options.year_month_range.start.year = current_date.year - 1
        request.historical_metrics_options.year_month_range.start.month = client.enums.MonthOfYearEnum.JANUARY
        request.historical_metrics_options.year_month_range.end.year = current_date.year
        request.historical_metrics_options.year_month_range.end.month = client.enums.MonthOfYearEnum[current_date.strftime('%B').upper()]
        
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        
        keywords_data = []
        for idx, result in enumerate(response):
            if idx >= max_keywords:
                break
                
            metrics = result.keyword_idea_metrics
            
            if metrics.competition:
                competition = metrics.competition.name
            else:
                competition = "UNSPECIFIED"
            
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

def generate_comprehensive_strategy(trends_data, ppc_data, google_ads_data):
    """Generate comprehensive campaign strategy combining all data sources."""
    
    strategy = {
        "executive_summary": {},
        "market_priorities": [],
        "campaign_structure": {},
        "budget_allocation": {},
        "audience_targeting": {},
        "timing_strategy": {},
        "keyword_strategy": {},
        "creative_recommendations": {},
        "performance_metrics": {}
    }
    
    # Analyze market priorities from trends data
    market_scores = {}
    for market, data in trends_data.items():
        if "1 Year" in data and "5 Year" in data:
            recent_avg = data["1 Year"].iloc[:, 1].mean() if len(data["1 Year"].columns) > 1 else 0
            historical_avg = data["5 Year"].iloc[:, 1].mean() if len(data["5 Year"].columns) > 1 else 0
            
            if historical_avg > 0:
                growth_rate = ((recent_avg / historical_avg) - 1) * 100
                market_scores[market] = {
                    "growth_rate": growth_rate,
                    "recent_volume": recent_avg,
                    "priority_score": growth_rate * recent_avg / 100
                }
    
    # Sort markets by priority
    sorted_markets = sorted(market_scores.items(), key=lambda x: x[1]["priority_score"], reverse=True)
    
    strategy["market_priorities"] = [
        {
            "market": market,
            "priority_level": "High" if i < 3 else "Medium" if i < 6 else "Low",
            "growth_rate": f"{data['growth_rate']:.1f}%",
            "recent_volume": f"{data['recent_volume']:.0f}",
            "recommended_budget": f"{min(40, max(5, data['priority_score']/10)):.0f}%"
        }
        for i, (market, data) in enumerate(sorted_markets[:8])
    ]
    
    # Campaign structure based on existing PPC recommendations
    if ppc_data and 'campaign_recommendations' in ppc_data:
        strategy["campaign_structure"] = ppc_data['campaign_recommendations']
    
    # Budget allocation
    total_budget = 100
    high_priority_markets = [m for m in strategy["market_priorities"] if m["priority_level"] == "High"]
    medium_priority_markets = [m for m in strategy["market_priorities"] if m["priority_level"] == "Medium"]
    
    strategy["budget_allocation"] = {
        "high_priority": f"{len(high_priority_markets) * 25}%",
        "medium_priority": f"{len(medium_priority_markets) * 15}%",
        "testing_budget": "10%",
        "seasonal_adjustments": "±20%"
    }
    
    # Audience targeting
    strategy["audience_targeting"] = {
        "primary_demographics": [
            "Age: 35-65",
            "Income: $150k+",
            "Interests: Luxury real estate, Skiing, Golf",
            "Life events: Recently married, Empty nesters"
        ],
        "geographic_focus": [
            "Salt Lake City, UT (40%)",
            "Los Angeles, CA (20%)",
            "New York, NY (15%)",
            "Denver, CO (10%)",
            "Other metros (15%)"
        ],
        "device_targeting": [
            "Desktop: 60% (high-intent research)",
            "Mobile: 40% (location-based searches)"
        ]
    }
    
    # Timing strategy
    strategy["timing_strategy"] = {
        "peak_seasons": [
            "January-March: Ski season (increase bids 30%)",
            "June-August: Summer activities (increase bids 20%)",
            "September-November: Fall foliage (increase bids 15%)"
        ],
        "optimal_times": [
            "Weekdays: 9 AM - 5 PM (business hours)",
            "Weekends: 10 AM - 4 PM (leisure browsing)",
            "Avoid: Late night hours (10 PM - 6 AM)"
        ],
        "bid_adjustments": {
            "peak_season": "+30%",
            "off_season": "-20%",
            "weekends": "+15%",
            "mobile": "+10%"
        }
    }
    
    # Keyword strategy
    strategy["keyword_strategy"] = {
        "match_types": {
            "exact_match": "High-intent, branded terms (30% of budget)",
            "phrase_match": "Market-specific terms (50% of budget)", 
            "broad_match": "Discovery terms (20% of budget)"
        },
        "negative_keywords": [
            "rental", "apartment", "commercial", "jobs", "weather",
            "kansas city", "overland park", "foreclosure", "cheap"
        ],
        "keyword_themes": [
            "Luxury ski properties",
            "Golf course communities", 
            "Mountain view homes",
            "Investment properties"
        ]
    }
    
    # Creative recommendations
    strategy["creative_recommendations"] = {
        "headlines": [
            "Exclusive Park City Properties",
            "Luxury Ski-In/Ski-Out Homes",
            "Deer Valley Dream Homes",
            "Heber Valley Golf Communities"
        ],
        "descriptions": [
            "Discover your perfect mountain retreat. Expert local guidance.",
            "Luxury properties with ski access. Private showings available.",
            "Golf course homes with mountain views. Schedule your tour today."
        ],
        "landing_pages": [
            "Market-specific property search pages",
            "Virtual tour galleries",
            "Market trend reports",
            "Agent testimonials"
        ]
    }
    
    # Performance metrics
    strategy["performance_metrics"] = {
        "target_cpa": "$150-300 per lead",
        "target_roas": "4:1 minimum",
        "quality_score_target": "7+ average",
        "conversion_rate_target": "3-5%",
        "monthly_lead_goal": "50-100 qualified leads"
    }
    
    return strategy

# --- NEW PRACTICAL FUNCTIONS ---

def show_keyword_recommendations(trends_data, budget):
    """Show practical keyword recommendations based on budget."""
    
    if not trends_data:
        st.warning("No trends data available")
        return
    
    # Extract top keywords from all markets
    all_keywords = []
    for market, data in trends_data.items():
        for timeframe in ['1_year', '2_year', '5_year']:
            if f"{timeframe}_queries" in data:
                queries_df = data[f"{timeframe}_queries"]
                if not queries_df.empty:
                    # Get top keywords (assuming first column has keywords)
                    keywords = queries_df.iloc[:, 0].dropna().head(5)
                    for keyword in keywords:
                        all_keywords.append({
                            'keyword': keyword,
                            'market': market,
                            'timeframe': timeframe
                        })
    
    if not all_keywords:
        st.warning("No keywords found in trends data")
        return
    
    # Create keyword recommendations based on budget
    st.subheader(f"🎯 Top Keywords for ${budget}/month Budget")
    
    # Budget-based recommendations
    if budget <= 1500:
        st.info("**Starting Phase:** Focus on 2-3 high-volume, low-competition keywords")
        top_keywords = all_keywords[:3]
    elif budget <= 2200:
        st.info("**Growing Phase:** Target 3-4 keywords with good search volume")
        top_keywords = all_keywords[:4]
    else:
        st.info("**Scaling Phase:** Multiple keyword groups across markets")
        top_keywords = all_keywords[:6]
    
    # Display recommendations
    for i, kw in enumerate(top_keywords, 1):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{i}. {kw['keyword']}**")
        with col2:
            st.write(f"Market: {kw['market']}")
        with col3:
            st.write(f"Trend: {kw['timeframe']}")
    
    st.markdown("**💡 Next Steps:**")
    st.markdown("1. Set up Google Ads campaigns for these keywords")
    st.markdown("2. Start with $50-100 daily budget per keyword")
    st.markdown("3. Monitor performance for 2 weeks before scaling")

def show_market_trends(trends_data):
    """Show market trend analysis."""
    
    if not trends_data:
        st.warning("No trends data available")
        return
    
    st.subheader("📈 Market Performance Overview")
    
    # Create a simple market comparison
    market_summary = []
    for market, data in trends_data.items():
        # Count available data points
        data_points = sum(1 for key in data.keys() if 'year' in key)
        market_summary.append({
            'Market': market,
            'Data Points': data_points,
            'Status': '✅ Active' if data_points >= 2 else '⚠️ Limited'
        })
    
    df = pd.DataFrame(market_summary)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("**🎯 Recommended Markets to Target:**")
    st.markdown("1. **Park City Real Estate** - Highest search volume")
    st.markdown("2. **Deer Valley Real Estate** - Premium market")
    st.markdown("3. **Heber Utah Real Estate** - Growing market")

def show_budget_allocation(budget, phase):
    """Show practical budget allocation strategy."""
    
    st.subheader(f"💰 Budget Allocation for {phase}")
    
    # Calculate allocations based on budget
    if budget <= 1500:
        allocations = {
            "Google Ads": budget * 0.8,  # 80% to ads
            "Testing & Optimization": budget * 0.15,  # 15% for testing
            "Tools & Software": budget * 0.05  # 5% for tools
        }
    elif budget <= 2200:
        allocations = {
            "Google Ads": budget * 0.75,  # 75% to ads
            "Testing & Optimization": budget * 0.20,  # 20% for testing
            "Tools & Software": budget * 0.05  # 5% for tools
        }
    else:
        allocations = {
            "Google Ads": budget * 0.70,  # 70% to ads
            "Testing & Optimization": budget * 0.25,  # 25% for testing
            "Tools & Software": budget * 0.05  # 5% for tools
        }
    
    # Display allocation chart
    fig = go.Figure(data=[go.Pie(
        labels=list(allocations.keys()),
        values=list(allocations.values()),
        hole=0.3
    )])
    fig.update_layout(title="Monthly Budget Allocation")
    st.plotly_chart(fig, use_container_width=True)
    
    # Show detailed breakdown
    st.subheader("📊 Detailed Breakdown")
    for category, amount in allocations.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{category}**")
        with col2:
            st.write(f"${amount:.0f}")
    
    st.markdown("**🎯 Action Items:**")
    st.markdown(f"1. **Set daily budget:** ${budget/30:.0f}/day")
    st.markdown(f"2. **Max CPC target:** ${budget/100:.0f}")
    st.markdown("3. **Monitor daily:** Check performance every morning")
    st.markdown("4. **Weekly review:** Adjust bids and keywords")

# --- Main Dashboard ---

def main():
    """Main dashboard application."""
    
    # Header
    st.title("🏔️ Evan Levine Real Estate - PPC Campaign Planner")
    st.markdown("**Budget: $1.5k-$3k | Single Agent | Actionable Next Steps**")
    
    # Budget input
    col1, col2 = st.columns(2)
    with col1:
        monthly_budget = st.number_input("Monthly PPC Budget ($)", min_value=500, max_value=5000, value=2000, step=100)
    with col2:
        campaign_phase = st.selectbox("Campaign Phase", ["Starting Out ($1.5k)", "Growing ($2.2k)", "Scaling ($3k+)"])
    
    st.markdown("---")
    
    # Load existing data
    with st.spinner("Loading existing Google Trends data..."):
        trends_data = load_existing_trends_data()
        analysis_data = load_existing_analysis()
        
        if trends_data:
            st.success(f"✅ Loaded trends data for {len(trends_data)} markets")
        else:
            st.warning("⚠️ No trends data found")
        
        if analysis_data:
            st.success("✅ Loaded existing analysis and recommendations")
        else:
            st.warning("⚠️ No existing analysis found")
    
    # PRACTICAL NEXT STEPS SECTION
    st.header("🎯 What To Do Next (Your Action Plan)")
    
    # Budget breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Daily Budget", f"${monthly_budget/30:.0f}")
    with col2:
        st.metric("Weekly Budget", f"${monthly_budget/4:.0f}")
    with col3:
        st.metric("Max CPC (Est.)", f"${monthly_budget/100:.0f}")
    
    # Action steps based on budget
    if monthly_budget <= 1500:
        st.info("**🚀 Starting Phase ($1.5k):** Focus on 2-3 high-converting keywords, test 1 market")
    elif monthly_budget <= 2200:
        st.info("**📈 Growing Phase ($2.2k):** Expand to 3-4 keywords, test 2 markets")
    else:
        st.info("**🎯 Scaling Phase ($3k+):** Multiple campaigns, 5+ keywords, full market coverage")
    
    # Quick action buttons
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Find Top Keywords", use_container_width=True):
            st.session_state.show_keywords = True
    
    with col2:
        if st.button("📊 View Market Trends", use_container_width=True):
            st.session_state.show_trends = True
    
    with col3:
        if st.button("💰 Budget Allocation", use_container_width=True):
            st.session_state.show_budget = True
    
    st.markdown("---")
    
    # CONDITIONAL SECTIONS BASED ON BUTTON CLICKS
    if st.session_state.get('show_keywords', False):
        st.header("🔍 Top Keywords for Your Budget")
        show_keyword_recommendations(trends_data, monthly_budget)
        st.markdown("---")
    
    if st.session_state.get('show_trends', False):
        st.header("📊 Market Trends Analysis")
        show_market_trends(trends_data)
        st.markdown("---")
    
    if st.session_state.get('show_budget', False):
        st.header("💰 Budget Allocation Strategy")
        show_budget_allocation(monthly_budget, campaign_phase)
        st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Google Ads API Status
        client, customer_id = load_google_ads_client()
        if client:
            st.success("✅ Google Ads API Connected")
        else:
            st.warning("⚠️ Google Ads API Not Connected")
        
        st.markdown("---")
        
        # Strategy Options
        st.header("🎯 Strategy Options")
        
        strategy_type = st.selectbox(
            "Campaign Strategy Type",
            ["Comprehensive Analysis", "Market-Specific Focus", "Seasonal Campaign", "New Market Entry"]
        )
        
        budget_range = st.selectbox(
            "Monthly Budget Range",
            ["$5,000 - $10,000", "$10,000 - $25,000", "$25,000 - $50,000", "$50,000+"]
        )
        
        campaign_duration = st.selectbox(
            "Campaign Duration",
            ["3 months", "6 months", "12 months", "Ongoing"]
        )
    
    # Main Content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Analysis", "🎯 Campaign Strategy", "💰 Budget Planning", "📈 Performance Tracking"])
    
    with tab1:
        st.header("Market Analysis & Trends")
        
        if trends_data:
            # Market Overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📈 Markets Analyzed")
                st.metric("Total Markets", len(trends_data))
            
            with col2:
                st.markdown("### 📅 Data Timeframes")
                timeframes = set()
                for market_data in trends_data.values():
                    timeframes.update(market_data.keys())
                st.metric("Available Timeframes", len([t for t in timeframes if "Year" in t]))
            
            with col3:
                st.markdown("### 🎯 Priority Markets")
                if analysis_data and 'ppc_recommendations' in analysis_data:
                    priority_markets = len(analysis_data['ppc_recommendations'].get('market_opportunities', []))
                    st.metric("High Priority", priority_markets)
            
            st.markdown("---")
            
            # Market Selection
            selected_market = st.selectbox(
                "Select Market for Detailed Analysis",
                list(trends_data.keys())
            )
            
            if selected_market and selected_market in trends_data:
                market_data = trends_data[selected_market]
                
                # Display trends data
                if "1 Year" in market_data:
                    st.subheader(f"📊 {selected_market} - 1 Year Trends")
                    
                    df = market_data["1 Year"]
                    if len(df.columns) > 1:
                        # Create trend chart
                        fig = go.Figure()
                        
                        # Plot the trend data
                        if len(df.columns) >= 2:
                            fig.add_trace(go.Scatter(
                                x=df.iloc[:, 0],
                                y=df.iloc[:, 1],
                                mode='lines',
                                name='Search Interest',
                                line=dict(color='#3B82F6', width=2),
                                fill='tozeroy',
                                fillcolor='rgba(59, 130, 246, 0.1)'
                            ))
                        
                        fig.update_layout(
                            title=f"{selected_market} - Search Interest Over Time",
                            xaxis_title="Date",
                            yaxis_title="Search Interest (0-100)",
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, width='stretch')
                        
                        # Show related queries
                        if "1 Year_queries" in market_data:
                            st.subheader("🔍 Related Search Queries")
                            queries_df = market_data["1 Year_queries"]
                            st.dataframe(queries_df, width='stretch')
                
                # Geographic data
                if "1 Year_geo" in market_data:
                    st.subheader("🌍 Geographic Interest")
                    geo_df = market_data["1 Year_geo"]
                    st.dataframe(geo_df, width='stretch')
        
        else:
            st.info("No trends data available. Please ensure CSV files are in the correct directory structure.")
    
    with tab2:
        st.header("🎯 Comprehensive Campaign Strategy")
        
        # Generate strategy
        if st.button("🚀 Generate Campaign Strategy", type="primary"):
            with st.spinner("Generating comprehensive campaign strategy..."):
                strategy = generate_comprehensive_strategy(
                    trends_data, 
                    analysis_data.get('ppc_recommendations') if analysis_data else None,
                    None  # Google Ads data would go here
                )
                
                st.session_state.strategy = strategy
        
        if 'strategy' in st.session_state:
            strategy = st.session_state.strategy
            
            # Executive Summary
            st.markdown("### 📋 Executive Summary")
            st.markdown(
                f"""
                <div class="strategy-card">
                <h3>Campaign Strategy Overview</h3>
                <p><strong>Strategy Type:</strong> {strategy_type}</p>
                <p><strong>Budget Range:</strong> {budget_range}</p>
                <p><strong>Duration:</strong> {campaign_duration}</p>
                <p><strong>Primary Focus:</strong> High-intent luxury real estate buyers</p>
                <p><strong>Geographic Focus:</strong> Salt Lake City, Los Angeles, New York, Denver</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Market Priorities
            st.markdown("### 🎯 Market Priorities")
            for market in strategy["market_priorities"]:
                st.markdown(
                    f"""
                    <div class="market-card">
                    <h4>{market['market']}</h4>
                    <p><strong>Priority:</strong> {market['priority_level']} | 
                    <strong>Growth Rate:</strong> {market['growth_rate']} | 
                    <strong>Budget:</strong> {market['recommended_budget']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Campaign Structure
            st.markdown("### 🏗️ Campaign Structure")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Primary Campaigns")
                if 'campaign_structure' in strategy and 'primary_campaigns' in strategy['campaign_structure']:
                    for campaign in strategy['campaign_structure']['primary_campaigns']:
                        st.markdown(f"**{campaign['market']}**")
                        st.markdown(f"- Focus: {campaign['focus']}")
                        st.markdown(f"- Budget: {campaign['budget_priority']}")
                        st.markdown(f"- Keywords: {len(campaign['keywords'])} terms")
            
            with col2:
                st.markdown("#### Secondary Campaigns")
                if 'campaign_structure' in strategy and 'secondary_campaigns' in strategy['campaign_structure']:
                    for campaign in strategy['campaign_structure']['secondary_campaigns']:
                        st.markdown(f"**{campaign['market']}**")
                        st.markdown(f"- Focus: {campaign['focus']}")
                        st.markdown(f"- Budget: {campaign['budget_priority']}")
                        st.markdown(f"- Keywords: {len(campaign['keywords'])} terms")
            
            # Audience Targeting
            st.markdown("### 👥 Audience Targeting")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Demographics")
                for demo in strategy["audience_targeting"]["primary_demographics"]:
                    st.markdown(f"• {demo}")
            
            with col2:
                st.markdown("#### Geographic Focus")
                for geo in strategy["audience_targeting"]["geographic_focus"]:
                    st.markdown(f"• {geo}")
            
            with col3:
                st.markdown("#### Device Targeting")
                for device in strategy["audience_targeting"]["device_targeting"]:
                    st.markdown(f"• {device}")
            
            # Timing Strategy
            st.markdown("### ⏰ Timing Strategy")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Peak Seasons")
                for season in strategy["timing_strategy"]["peak_seasons"]:
                    st.markdown(f"• {season}")
            
            with col2:
                st.markdown("#### Optimal Times")
                for time in strategy["timing_strategy"]["optimal_times"]:
                    st.markdown(f"• {time}")
            
            # Creative Recommendations
            st.markdown("### ✍️ Creative Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Headlines")
                for headline in strategy["creative_recommendations"]["headlines"]:
                    st.code(headline)
            
            with col2:
                st.markdown("#### Descriptions")
                for desc in strategy["creative_recommendations"]["descriptions"]:
                    st.code(desc)
    
    with tab3:
        st.header("💰 Budget Planning & Allocation")
        
        if 'strategy' in st.session_state:
            strategy = st.session_state.strategy
            
            # Budget Allocation Chart
            budget_data = strategy["budget_allocation"]
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(budget_data.keys()),
                    values=[int(v.replace('%', '')) for v in budget_data.values()],
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title="Budget Allocation Strategy",
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')
            
            # Detailed Budget Breakdown
            st.markdown("### 📊 Detailed Budget Breakdown")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(
                    f"""
                    <div class="budget-card">
                    <h3>High Priority</h3>
                    <div class="metric-highlight">{budget_data['high_priority']}</div>
                    <p>Core markets with highest ROI potential</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f"""
                    <div class="budget-card">
                    <h3>Medium Priority</h3>
                    <div class="metric-highlight">{budget_data['medium_priority']}</div>
                    <p>Emerging markets for growth</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                st.markdown(
                    f"""
                    <div class="budget-card">
                    <h3>Testing</h3>
                    <div class="metric-highlight">{budget_data['testing_budget']}</div>
                    <p>New keywords and audiences</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col4:
                st.markdown(
                    f"""
                    <div class="budget-card">
                    <h3>Seasonal</h3>
                    <div class="metric-highlight">{budget_data['seasonal_adjustments']}</div>
                    <p>Peak season adjustments</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Budget Calculator
            st.markdown("### 🧮 Budget Calculator")
            
            monthly_budget = st.number_input(
                "Enter Monthly Budget ($)",
                min_value=1000,
                max_value=100000,
                value=10000,
                step=1000
            )
            
            if monthly_budget:
                high_priority_budget = monthly_budget * 0.4
                medium_priority_budget = monthly_budget * 0.3
                testing_budget = monthly_budget * 0.1
                seasonal_buffer = monthly_budget * 0.2
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("High Priority", f"${high_priority_budget:,.0f}")
                with col2:
                    st.metric("Medium Priority", f"${medium_priority_budget:,.0f}")
                with col3:
                    st.metric("Testing", f"${testing_budget:,.0f}")
                with col4:
                    st.metric("Seasonal Buffer", f"${seasonal_buffer:,.0f}")
        
        else:
            st.info("Please generate a campaign strategy first.")
    
    with tab4:
        st.header("📈 Performance Tracking & KPIs")
        
        if 'strategy' in st.session_state:
            strategy = st.session_state.strategy
            
            # Performance Metrics
            metrics = strategy["performance_metrics"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Target CPA", metrics["target_cpa"])
            with col2:
                st.metric("Target ROAS", metrics["target_roas"])
            with col3:
                st.metric("Quality Score Target", metrics["quality_score_target"])
            with col4:
                st.metric("Conversion Rate Target", metrics["conversion_rate_target"])
            
            # Monthly Goals
            st.markdown("### 🎯 Monthly Goals")
            st.metric("Lead Goal", metrics["monthly_lead_goal"])
            
            # Performance Tracking Dashboard
            st.markdown("### 📊 Performance Dashboard")
            
            # Create sample performance data
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            leads = [45, 52, 38, 67, 73, 58]
            cost = [8500, 9200, 7200, 11200, 12800, 9800]
            conversions = [3, 4, 2, 5, 6, 4]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=months,
                y=leads,
                mode='lines+markers',
                name='Leads',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=months,
                y=cost,
                mode='lines+markers',
                name='Cost ($)',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Monthly Performance Trends',
                xaxis_title='Month',
                yaxis=dict(title='Leads', side='left'),
                yaxis2=dict(title='Cost ($)', side='right', overlaying='y'),
                height=400
            )
            
            st.plotly_chart(fig, width='stretch')
            
            # ROI Analysis
            st.markdown("### 💰 ROI Analysis")
            
            roi_data = pd.DataFrame({
                'Month': months,
                'Leads': leads,
                'Cost': cost,
                'Conversions': conversions,
                'CPA': [c/l for c, l in zip(cost, leads)],
                'ROI': [(c*500000)/cost[i] for i, c in enumerate(conversions)]  # Assuming $500k avg sale
            })
            
            st.dataframe(roi_data, width='stretch')
        
        else:
            st.info("Please generate a campaign strategy first.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>🏔️ Park City Real Estate Campaign Strategy Dashboard | Built for levine.realestate</p>
        <p>Data Sources: Google Trends CSV + Google Ads API | Last Updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")),
        unsafe_allow_html=True
    )

# --- Run the App ---
if __name__ == "__main__":
    main()
