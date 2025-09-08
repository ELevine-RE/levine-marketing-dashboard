# Updated Google Ads Strategic Brief Analysis

This notebook analyzes Google Trends data across multiple timeframes (1-year, 2-year, and 5-year) to create an updated strategic brief for new Google Ads campaigns in Park City.




```python
import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set plot style
sns.set_style("whitegrid")


```


```python
# --- Data Loading ---

base_path = Path.cwd()
data_path = base_path

themes = [
    'Deer Valley East Real Estate', 'Deer Valley Real Estate', 'Glenwild',
    'Heber Utah Real Estate', 'Kamas Real Estate', 'Park City Real Estate',
    'Promontory Park City /', 'Red Ledges Real Estate', 
    'Ski in Ski Out Home for Sale', 'Victory Ranch Real Esate'
]
timeframes = ['1 year', '2 year', '5 year']

def clean_theme_name(theme):
    return theme.replace(' /', '').replace(' Esate', ' Estate')

# Load multiTimeline data
timeline_dfs = []
for theme in themes:
    for timeframe in timeframes:
        files = glob.glob(str(data_path / theme / timeframe / 'multiTimeline*.csv'))
        for file in files:
            try:
                df = pd.read_csv(file, skiprows=2)
                df.columns = ['Week', 'Interest']
                df['Theme'] = clean_theme_name(theme)
                df['Timeframe'] = timeframe
                df['Interest'] = pd.to_numeric(df['Interest'], errors='coerce').fillna(0.5)
                df['Week'] = pd.to_datetime(df['Week'].str.split(' - ').str[0])
                timeline_dfs.append(df)
            except Exception as e:
                print(f"Could not read {file}: {e}")

if timeline_dfs:
    master_timeline_df = pd.concat(timeline_dfs, ignore_index=True).drop_duplicates()
    print("Timeline data loaded successfully.")
    print(f"Loaded {len(master_timeline_df)} rows of timeline data.")
else:
    print("No timeline data loaded.")
    master_timeline_df = pd.DataFrame()

# Load geoMap data
geomap_dfs = []
for theme in themes:
    for timeframe in timeframes:
        files = glob.glob(str(data_path / theme / timeframe / 'geoMap*.csv'))
        for file in files:
            try:
                df = pd.read_csv(file, skiprows=2)
                df.columns = ['Metro', 'Interest']
                df['Theme'] = clean_theme_name(theme)
                df['Timeframe'] = timeframe
                df['Interest'] = pd.to_numeric(df['Interest'], errors='coerce').fillna(0)
                geomap_dfs.append(df)
            except Exception as e:
                print(f"Could not read {file}: {e}")

if geomap_dfs:
    master_geomap_df = pd.concat(geomap_dfs, ignore_index=True).drop_duplicates()
    master_geomap_df = master_geomap_df[master_geomap_df['Metro'].str.contains('Metro', na=False)]
    master_geomap_df['Metro'] = master_geomap_df['Metro'].str.replace(' Metro', '')
    print("\nGeoMap data loaded successfully.")
    print(f"Loaded {len(master_geomap_df)} rows of geomap data.")
else:
    print("No GeoMap data loaded.")
    master_geomap_df = pd.DataFrame()


```

    No timeline data loaded.
    No GeoMap data loaded.


## 1. Campaign & Ad Group Clustering

Here we'll identify themes that behave similarly to group them into effective campaigns. We'll run this analysis for each timeframe (5-year, 2-year, 1-year) to see how groupings evolve.




```python
def perform_clustering(timeframe, timeline_df, geomap_df):
    """Performs seasonal and geographic clustering for a given timeframe."""
    print(f"--- Clustering Analysis for {timeframe} ---")

    # Filter data for the timeframe
    timeline_subset = timeline_df[timeline_df['Timeframe'] == timeframe]
    geomap_subset = geomap_df[geomap_df['Timeframe'] == timeframe]

    if timeline_subset.empty or geomap_subset.empty:
        print(f"Not enough data for {timeframe} to perform clustering.\\n")
        return

    # --- Seasonality Clustering ---
    timeline_subset['Month'] = timeline_subset['Week'].dt.month
    seasonal_pivot = timeline_subset.pivot_table(index='Theme', columns='Month', values='Interest', aggfunc='mean').fillna(0)
    
    scaler = StandardScaler()
    seasonal_scaled = scaler.fit_transform(seasonal_pivot)
    
    # Using k=3 as determined in the initial analysis for consistency
    k_seasonal = 3
    kmeans_seasonal = KMeans(n_clusters=k_seasonal, random_state=42, n_init=10)
    seasonal_pivot['Seasonal_Cluster'] = kmeans_seasonal.fit_predict(seasonal_scaled)

    # --- Geographic Clustering ---
    geo_pivot = geomap_subset.pivot_table(index='Theme', columns='Metro', values='Interest').fillna(0)
    geo_scaled = scaler.fit_transform(geo_pivot)
    
    k_geo = 3
    kmeans_geo = KMeans(n_clusters=k_geo, random_state=42, n_init=10)
    # Ensure geo_pivot has themes that are also in seasonal_pivot
    geo_pivot_aligned = geo_pivot.reindex(seasonal_pivot.index).fillna(0)
    geo_scaled_aligned = scaler.fit_transform(geo_pivot_aligned)
    geo_pivot_aligned['Geo_Cluster'] = kmeans_geo.fit_predict(geo_scaled_aligned)

    # --- Combined Analysis & Recommendation ---
    clusters = pd.DataFrame({
        'Seasonal_Cluster': seasonal_pivot['Seasonal_Cluster'],
        'Geo_Cluster': geo_pivot_aligned['Geo_Cluster']
    })
    
    print("\\n**Strategic Recommendation: Campaign Structure**")
    for i in range(k_seasonal):
        for j in range(k_geo):
            cluster_group = clusters[(clusters['Seasonal_Cluster'] == i) & (clusters['Geo_Cluster'] == j)]
            if not cluster_group.empty:
                print(f"\\n*   **Campaign: Seasonal Cluster {i} / Geo Cluster {j}**")
                print(f"    *   **Themes:** {', '.join(cluster_group.index)}")
    print("\\n" + "="*50 + "\\n")

# Run clustering for each timeframe
if not master_timeline_df.empty and not master_geomap_df.empty:
    for tf in timeframes:
        perform_clustering(tf, master_timeline_df, master_geomap_df)
else:
    print("Master dataframes are empty. Skipping clustering.")


```

    Master dataframes are empty. Skipping clustering.


## 2. Market Prioritization

Here we'll identify the top 5 themes by search volume and year-over-year growth. This will be done for each timeframe to track how market priorities are shifting.




```python
def perform_market_prioritization(timeframe, timeline_df):
    """Performs market prioritization analysis for a given timeframe."""
    print(f"--- Market Prioritization for {timeframe} ---")

    timeline_subset = timeline_df[timeline_df['Timeframe'] == timeframe]
    if timeline_subset.empty:
        print(f"No timeline data for {timeframe}.\\n")
        return
        
    # a) Top 5 by Volume
    avg_volume = timeline_subset.groupby('Theme')['Interest'].mean().sort_values(ascending=False)
    top5_volume = avg_volume.head(5)
    print("\\n**Top 5 Themes by Average Search Volume:**")
    print(top5_volume.to_string())

    # b) Top 5 by Growth (CAGR)
    timeline_subset['Year'] = timeline_subset['Week'].dt.year
    yearly_interest = timeline_subset.groupby(['Theme', 'Year'])['Interest'].mean().reset_index()

    def calculate_cagr(df):
        df = df.sort_values('Year')
        if len(df) < 2: return np.nan
        start_row = df.iloc[0]
        end_row = df.iloc[-1]
        start_value, end_value = start_row['Interest'], end_row['Interest']
        num_years = end_row['Year'] - start_row['Year']
        if num_years > 0 and start_value > 0:
            return ((end_value / start_value) ** (1 / num_years)) - 1
        return np.nan

    cagr_results = yearly_interest.groupby('Theme').apply(calculate_cagr).dropna()
    top5_growth = cagr_results.sort_values(ascending=False).head(5)
    if not top5_growth.empty:
        print("\\n**Top 5 Themes by Year-over-Year Growth (CAGR):**")
        print(top5_growth.to_string())
    else:
        print("\\n**Growth data not sufficient for CAGR calculation.**")
        
    # Strategic Recommendation
    print("\\n**Strategic Recommendation: Budget Allocation**")
    print(f"For the **{timeframe}** perspective:")
    print(f"- Focus immediate budget on high-volume themes: **{', '.join(top5_volume.index)}**.")
    if not top5_growth.empty:
        print(f"- Invest in future growth with themes like: **{', '.join(top5_growth.index)}**.")
    print("Comparing timeframes will show which high-growth themes are sustainable.")
    print("\\n" + "="*50 + "\\n")

# Run analysis for each timeframe
if not master_timeline_df.empty:
    for tf in timeframes:
        perform_market_prioritization(tf, master_timeline_df)
else:
    print("Master timeline dataframe is empty. Skipping market prioritization.")


```

    Master timeline dataframe is empty. Skipping market prioritization.


## 3. Detailed Thematic Analysis

This section provides a summary card for each theme, detailing peak seasonality and the top metro area for search interest. We'll compare these across timeframes to see how user behavior is changing.




```python
def perform_thematic_analysis(timeframe, timeline_df, geomap_df):
    """Performs detailed thematic analysis for a given timeframe."""
    print(f"--- Detailed Thematic Analysis for {timeframe} ---")

    timeline_subset = timeline_df[timeline_df['Timeframe'] == timeframe]
    geomap_subset = geomap_df[geomap_df['Timeframe'] == timeframe]
    
    if timeline_subset.empty or geomap_subset.empty:
        print(f"Not enough data for {timeframe} to perform thematic analysis.\\n")
        return

    all_themes = sorted(timeline_subset['Theme'].unique())

    for theme in all_themes:
        print(f"\\n**Theme: {theme}**")
        
        # Peak Seasonality
        theme_timeline = timeline_subset[timeline_subset['Theme'] == theme]
        theme_timeline['Week_of_Year'] = theme_timeline['Week'].dt.isocalendar().week
        peak_week = theme_timeline.groupby('Week_of_Year')['Interest'].mean().idxmax()
        
        # Top Metro Area
        theme_geomap = geomap_subset[geomap_subset['Theme'] == theme]
        top_metro_name = "N/A"
        if not theme_geomap.empty:
            top_metro = theme_geomap.loc[theme_geomap['Interest'].idxmax()]
            top_metro_name = top_metro['Metro']

        print(f"*   **Peak Seasonality:** Week {peak_week}")
        print(f"*   **Top Metro Area:** {top_metro_name}")
        print(f"*   **Strategic Recommendation:** For the {timeframe} view, focus ad scheduling around week {peak_week} and prioritize the {top_metro_name} metro area.")

    print("\\n" + "="*50 + "\\n")


# Run analysis for each timeframe
if not master_timeline_df.empty and not master_geomap_df.empty:
    for tf in timeframes:
        perform_thematic_analysis(tf, master_timeline_df, master_geomap_df)
else:
    print("Master dataframes are empty. Skipping thematic analysis.")


```

    Master dataframes are empty. Skipping thematic analysis.


## 4. Geographic Deep Dive: Top Metro Areas

This section identifies the top 5 metro areas by overall search volume and the most popular themes within those metros. Comparing this across timeframes will reveal shifts in geographic market importance.




```python
def perform_geographic_deep_dive(timeframe, geomap_df):
    """Performs a geographic deep dive for a given timeframe."""
    print(f"--- Geographic Deep Dive for {timeframe} ---")

    geomap_subset = geomap_df[geomap_df['Timeframe'] == timeframe]
    if geomap_subset.empty:
        print(f"No geomap data for {timeframe}.\\n")
        return

    # a) Top 5 metro areas overall
    metro_total_interest = geomap_subset.groupby('Metro')['Interest'].sum().sort_values(ascending=False)
    top5_metros = metro_total_interest.head(5)

    print("\\n**Top 5 Metro Areas by Overall Search Volume:**")
    print(top5_metros.to_string())

    # b) Top themes within each top metro
    print("\\n**Top Themes within Top 5 Metro Areas:**")
    for metro in top5_metros.index:
        print(f"\\n*   **Metro: {metro}**")
        metro_themes = geomap_subset[geomap_subset['Metro'] == metro]
        top3_themes = metro_themes.sort_values('Interest', ascending=False).head(3)
        for _, row in top3_themes.iterrows():
            print(f"    *   {row['Theme']} (Interest: {row['Interest']})")
            
    print("\\n**Strategic Recommendation: Geo-Targeted Ad Copy**")
    print(f"Based on the {timeframe} data, tailor ad copy for these top metros. For example, for users in **{top5_metros.index[0]}**, focus on themes like **{geomap_subset[geomap_subset['Metro'] == top5_metros.index[0]].sort_values('Interest', ascending=False).iloc[0]['Theme']}**.")
    print("\\n" + "="*50 + "\\n")

# Run analysis for each timeframe
if not master_geomap_df.empty:
    for tf in timeframes:
        perform_geographic_deep_dive(tf, master_geomap_df)
else:
    print("Master geomap dataframe is empty. Skipping geographic deep dive.")


```

    Master geomap dataframe is empty. Skipping geographic deep dive.


## 5. Final Report Generation

This final step will consolidate all the analysis and recommendations into a clean, well-structured markdown report.




```python
print("Analysis notebook complete. Ready to generate report.")


```

    Analysis notebook complete. Ready to generate report.

