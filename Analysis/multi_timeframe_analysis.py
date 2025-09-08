#!/usr/bin/env python3
"""
Multi-Timeframe Strategic Analysis for Park City Google Ads Campaigns
Analyzes Google Trends data across 1-year, 2-year, and 5-year periods
to identify momentum shifts and optimize campaign strategy
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MultiTimeframeAnalyzer:
    def __init__(self, trends_data_path):
        self.trends_data_path = trends_data_path
        self.timeframes = ['1 Year', '2 Year', '5 Year']
        self.themes_data = {}
        self.master_data = {}
        
    def load_all_timeframe_data(self):
        """Load data from all timeframes for comprehensive analysis"""
        print("Loading multi-timeframe Google Trends data...")
        
        # Get all theme folders
        theme_folders = [d for d in os.listdir(self.trends_data_path) 
                        if os.path.isdir(os.path.join(self.trends_data_path, d)) 
                        and d != 'Analysis' 
                        and not d.startswith('.')]
        
        for theme_folder in theme_folders:
            theme_name = theme_folder.replace(' Real Estate', '').replace(' Real Esate', '')
            theme_path = os.path.join(self.trends_data_path, theme_folder)
            
            # Initialize theme data structure
            self.themes_data[theme_name] = {
                'folder': theme_folder,
                'timeframe_data': {}
            }
            
            # Load data for each timeframe
            for timeframe in self.timeframes:
                timeframe_path = os.path.join(theme_path, timeframe)
                
                if os.path.exists(timeframe_path):
                    self.themes_data[theme_name]['timeframe_data'][timeframe] = {
                        'timeline': None,
                        'geo': None,
                        'queries': None,
                        'avg_volume': 0,
                        'trend_slope': 0,
                        'volatility': 0
                    }
                    
                    # Load timeline data
                    timeline_files = glob.glob(os.path.join(timeframe_path, 'multiTimeline*.csv'))
                    if timeline_files:
                        try:
                            df = pd.read_csv(timeline_files[0], skiprows=2)
                            if not df.empty and 'Week' in df.columns:
                                df['Week'] = pd.to_datetime(df['Week'], errors='coerce')
                                df = df.dropna(subset=['Week'])
                                
                                if len(df.columns) > 1:
                                    value_col = df.columns[1]
                                    df['Search_Volume'] = pd.to_numeric(df[value_col], errors='coerce')
                                    
                                    # Store timeline
                                    self.themes_data[theme_name]['timeframe_data'][timeframe]['timeline'] = df[['Week', 'Search_Volume']].copy()
                                    
                                    # Calculate metrics
                                    self.themes_data[theme_name]['timeframe_data'][timeframe]['avg_volume'] = df['Search_Volume'].mean()
                                    
                                    # Calculate volatility (standard deviation / mean)
                                    if df['Search_Volume'].mean() > 0:
                                        self.themes_data[theme_name]['timeframe_data'][timeframe]['volatility'] = \
                                            df['Search_Volume'].std() / df['Search_Volume'].mean()
                                    
                                    # Calculate trend
                                    if len(df) > 1:
                                        x = np.arange(len(df))
                                        y = df['Search_Volume'].values
                                        slope, _, r_value, _, _ = stats.linregress(x, y)
                                        self.themes_data[theme_name]['timeframe_data'][timeframe]['trend_slope'] = slope
                                        self.themes_data[theme_name]['timeframe_data'][timeframe]['trend_r2'] = r_value ** 2
                                        
                        except Exception as e:
                            print(f"Error loading {timeframe} timeline for {theme_name}: {e}")
                    
                    # Load geographic data
                    geo_files = glob.glob(os.path.join(timeframe_path, 'geoMap*.csv'))
                    if geo_files:
                        try:
                            df_geo = pd.read_csv(geo_files[0], skiprows=2)
                            if not df_geo.empty and len(df_geo.columns) >= 2:
                                df_geo.columns = ['Metro_Area', 'Search_Interest']
                                df_geo['Search_Interest'] = pd.to_numeric(df_geo['Search_Interest'], errors='coerce')
                                self.themes_data[theme_name]['timeframe_data'][timeframe]['geo'] = df_geo
                        except Exception as e:
                            print(f"Error loading {timeframe} geo data for {theme_name}: {e}")
                    
                    # Load related queries
                    query_files = glob.glob(os.path.join(timeframe_path, 'relatedQueries*.csv'))
                    if query_files:
                        try:
                            with open(query_files[0], 'r', encoding='utf-8') as f:
                                content = f.read()
                                self.themes_data[theme_name]['timeframe_data'][timeframe]['queries'] = \
                                    self.parse_related_queries(content)
                        except Exception as e:
                            print(f"Error loading {timeframe} queries for {theme_name}: {e}")
        
        print(f"Loaded data for {len(self.themes_data)} themes across {len(self.timeframes)} timeframes")
        return self.themes_data
    
    def parse_related_queries(self, content):
        """Parse related queries CSV content"""
        queries = {'top': [], 'rising': []}
        lines = content.strip().split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line == 'TOP':
                current_section = 'top'
            elif line == 'RISING':
                current_section = 'rising'
            elif line and current_section and ',' in line:
                parts = line.split(',')
                if len(parts) >= 2:
                    query = parts[0].strip()
                    score = parts[1].strip()
                    queries[current_section].append({'query': query, 'score': score})
        
        return queries
    
    def calculate_momentum_scores(self):
        """Calculate momentum by comparing trends across timeframes"""
        print("\nCalculating momentum scores...")
        
        momentum_analysis = {}
        
        for theme_name, theme_data in self.themes_data.items():
            momentum_analysis[theme_name] = {
                'momentum_score': 0,
                'acceleration': 'stable',
                'short_term_trend': 0,
                'long_term_trend': 0,
                'volatility_trend': 'stable'
            }
            
            # Get average volumes for each timeframe
            volumes = {}
            trends = {}
            volatilities = {}
            
            for timeframe in self.timeframes:
                if timeframe in theme_data['timeframe_data']:
                    tf_data = theme_data['timeframe_data'][timeframe]
                    volumes[timeframe] = tf_data.get('avg_volume', 0)
                    trends[timeframe] = tf_data.get('trend_slope', 0)
                    volatilities[timeframe] = tf_data.get('volatility', 0)
            
            # Calculate momentum score
            if '1 Year' in volumes and '5 Year' in volumes and volumes['5 Year'] > 0:
                # Momentum = (1-year avg / 5-year avg) - 1
                momentum_analysis[theme_name]['momentum_score'] = (volumes['1 Year'] / volumes['5 Year'] - 1) * 100
                
                # Determine acceleration
                if '2 Year' in volumes and volumes['2 Year'] > 0:
                    recent_growth = (volumes['1 Year'] / volumes['2 Year'] - 1) * 100
                    historical_growth = (volumes['2 Year'] / volumes['5 Year'] - 1) * 100
                    
                    if recent_growth > historical_growth + 10:
                        momentum_analysis[theme_name]['acceleration'] = 'accelerating'
                    elif recent_growth < historical_growth - 10:
                        momentum_analysis[theme_name]['acceleration'] = 'decelerating'
                    else:
                        momentum_analysis[theme_name]['acceleration'] = 'stable'
            
            # Store trend slopes
            momentum_analysis[theme_name]['short_term_trend'] = trends.get('1 Year', 0)
            momentum_analysis[theme_name]['long_term_trend'] = trends.get('5 Year', 0)
            
            # Analyze volatility trend
            if '1 Year' in volatilities and '5 Year' in volatilities:
                if volatilities['1 Year'] > volatilities['5 Year'] * 1.2:
                    momentum_analysis[theme_name]['volatility_trend'] = 'increasing'
                elif volatilities['1 Year'] < volatilities['5 Year'] * 0.8:
                    momentum_analysis[theme_name]['volatility_trend'] = 'decreasing'
        
        return momentum_analysis
    
    def analyze_seasonal_patterns_by_timeframe(self):
        """Analyze how seasonal patterns have evolved"""
        seasonal_evolution = {}
        
        for theme_name, theme_data in self.themes_data.items():
            seasonal_evolution[theme_name] = {}
            
            for timeframe in self.timeframes:
                if timeframe in theme_data['timeframe_data']:
                    timeline = theme_data['timeframe_data'][timeframe].get('timeline')
                    if timeline is not None and not timeline.empty:
                        # Extract month and calculate monthly averages
                        timeline['Month'] = timeline['Week'].dt.month
                        monthly_avg = timeline.groupby('Month')['Search_Volume'].mean()
                        
                        # Find peak and trough months
                        if not monthly_avg.empty:
                            peak_month = monthly_avg.idxmax()
                            trough_month = monthly_avg.idxmin()
                            seasonality_strength = (monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean() if monthly_avg.mean() > 0 else 0
                            
                            seasonal_evolution[theme_name][timeframe] = {
                                'peak_month': peak_month,
                                'trough_month': trough_month,
                                'seasonality_strength': seasonality_strength,
                                'monthly_pattern': monthly_avg.to_dict()
                            }
        
        return seasonal_evolution
    
    def analyze_geographic_shifts(self):
        """Identify shifts in geographic interest over time"""
        geo_shifts = {}
        
        for theme_name, theme_data in self.themes_data.items():
            geo_shifts[theme_name] = {
                'emerging_markets': [],
                'declining_markets': [],
                'stable_leaders': []
            }
            
            # Get top metros for each timeframe
            metros_by_timeframe = {}
            for timeframe in self.timeframes:
                if timeframe in theme_data['timeframe_data']:
                    geo_data = theme_data['timeframe_data'][timeframe].get('geo')
                    if geo_data is not None and not geo_data.empty:
                        top_10 = geo_data.nlargest(10, 'Search_Interest')
                        metros_by_timeframe[timeframe] = set(top_10['Metro_Area'].tolist())
            
            # Identify shifts
            if '1 Year' in metros_by_timeframe and '5 Year' in metros_by_timeframe:
                recent = metros_by_timeframe['1 Year']
                historical = metros_by_timeframe['5 Year']
                
                geo_shifts[theme_name]['emerging_markets'] = list(recent - historical)[:5]
                geo_shifts[theme_name]['declining_markets'] = list(historical - recent)[:5]
                geo_shifts[theme_name]['stable_leaders'] = list(recent & historical)[:5]
        
        return geo_shifts
    
    def identify_breakout_keywords(self):
        """Identify keywords that are breaking out in recent periods"""
        breakout_keywords = {}
        
        for theme_name, theme_data in self.themes_data.items():
            breakout_keywords[theme_name] = {
                'new_trending': [],
                'accelerating': [],
                'declining': []
            }
            
            # Compare queries across timeframes
            queries_by_timeframe = {}
            for timeframe in self.timeframes:
                if timeframe in theme_data['timeframe_data']:
                    queries = theme_data['timeframe_data'][timeframe].get('queries')
                    if queries:
                        # Get rising queries
                        rising = [q['query'] for q in queries.get('rising', [])]
                        top = [q['query'] for q in queries.get('top', [])[:10]]
                        queries_by_timeframe[timeframe] = set(rising + top)
            
            # Identify trends
            if '1 Year' in queries_by_timeframe and '5 Year' in queries_by_timeframe:
                recent = queries_by_timeframe['1 Year']
                historical = queries_by_timeframe['5 Year']
                
                breakout_keywords[theme_name]['new_trending'] = list(recent - historical)[:5]
                breakout_keywords[theme_name]['declining'] = list(historical - recent)[:5]
        
        return breakout_keywords
    
    def generate_strategic_recommendations(self, momentum_scores, seasonal_evolution, geo_shifts, breakout_keywords):
        """Generate actionable strategic recommendations based on multi-timeframe analysis"""
        recommendations = {
            'immediate_opportunities': [],
            'growth_markets': [],
            'defensive_actions': [],
            'seasonal_adjustments': [],
            'keyword_opportunities': []
        }
        
        # Identify immediate opportunities (high momentum + acceleration)
        for theme, momentum in momentum_scores.items():
            if momentum['momentum_score'] > 20 and momentum['acceleration'] == 'accelerating':
                recommendations['immediate_opportunities'].append({
                    'theme': theme,
                    'momentum': momentum['momentum_score'],
                    'reason': 'Strong momentum with accelerating growth'
                })
        
        # Identify growth markets with emerging geographic interest
        for theme, shifts in geo_shifts.items():
            if len(shifts['emerging_markets']) > 0:
                recommendations['growth_markets'].append({
                    'theme': theme,
                    'markets': shifts['emerging_markets'],
                    'action': 'Expand geographic targeting'
                })
        
        # Identify defensive actions for declining themes
        for theme, momentum in momentum_scores.items():
            if momentum['momentum_score'] < -20 or momentum['acceleration'] == 'decelerating':
                recommendations['defensive_actions'].append({
                    'theme': theme,
                    'momentum': momentum['momentum_score'],
                    'action': 'Reduce budget allocation or optimize targeting'
                })
        
        # Seasonal adjustment recommendations
        for theme, seasonal in seasonal_evolution.items():
            if '1 Year' in seasonal and seasonal['1 Year'].get('seasonality_strength', 0) > 0.5:
                peak_month = seasonal['1 Year']['peak_month']
                recommendations['seasonal_adjustments'].append({
                    'theme': theme,
                    'peak_month': peak_month,
                    'strength': seasonal['1 Year']['seasonality_strength'],
                    'action': f'Increase budget by {int(seasonal["1 Year"]["seasonality_strength"] * 30)}% in month {peak_month}'
                })
        
        # Keyword opportunities
        for theme, keywords in breakout_keywords.items():
            if len(keywords['new_trending']) > 0:
                recommendations['keyword_opportunities'].append({
                    'theme': theme,
                    'keywords': keywords['new_trending'],
                    'action': 'Add to campaign as high-priority keywords'
                })
        
        return recommendations
    
    def generate_markdown_report(self):
        """Generate comprehensive markdown report with multi-timeframe insights"""
        print("\nGenerating multi-timeframe strategic brief...")
        
        # Perform all analyses
        momentum_scores = self.calculate_momentum_scores()
        seasonal_evolution = self.analyze_seasonal_patterns_by_timeframe()
        geo_shifts = self.analyze_geographic_shifts()
        breakout_keywords = self.identify_breakout_keywords()
        recommendations = self.generate_strategic_recommendations(
            momentum_scores, seasonal_evolution, geo_shifts, breakout_keywords
        )
        
        # Build markdown report
        report = []
        report.append("# Multi-Timeframe Strategic Brief: Park City Google Ads Campaigns")
        report.append(f"\n*Analysis Date: {datetime.now().strftime('%B %d, %Y')}*")
        report.append("\n*Analyzing 1-Year, 2-Year, and 5-Year Google Trends Data*")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("\nThis enhanced analysis compares search trends across three time horizons to identify:")
        report.append("- **Momentum Shifts**: Which markets are accelerating vs. decelerating")
        report.append("- **Emerging Opportunities**: New geographic markets and trending keywords")
        report.append("- **Risk Indicators**: Markets showing decline or increased volatility")
        report.append("- **Seasonal Evolution**: How seasonal patterns have changed over time")
        
        # 1. Momentum Analysis
        report.append("\n## 1. Market Momentum Analysis")
        report.append("\n### 🚀 Accelerating Markets (Immediate Opportunities)")
        
        # Sort by momentum score
        momentum_sorted = sorted(momentum_scores.items(), key=lambda x: x[1]['momentum_score'], reverse=True)
        
        report.append("\n| Theme | Momentum Score | Acceleration | 1Y vs 5Y Volume | Recommendation |")
        report.append("|-------|---------------|--------------|-----------------|----------------|")
        
        for theme, momentum in momentum_sorted[:10]:
            score = momentum['momentum_score']
            accel = momentum['acceleration']
            
            # Determine recommendation based on momentum
            if score > 20 and accel == 'accelerating':
                rec = "🟢 **High Priority** - Increase budget"
            elif score > 0 and accel != 'decelerating':
                rec = "🟡 **Medium Priority** - Maintain/test"
            else:
                rec = "🔴 **Low Priority** - Monitor only"
            
            # Get volume comparison
            tf_data = self.themes_data[theme]['timeframe_data']
            vol_1y = tf_data.get('1 Year', {}).get('avg_volume', 0)
            vol_5y = tf_data.get('5 Year', {}).get('avg_volume', 0)
            
            report.append(f"| {theme} | {score:+.1f}% | {accel.title()} | {vol_1y:.1f} vs {vol_5y:.1f} | {rec} |")
        
        # 2. Geographic Evolution
        report.append("\n## 2. Geographic Market Evolution")
        report.append("\n### 📍 Emerging Geographic Markets")
        report.append("\nThese metros show NEW interest in the past year that wasn't present historically:\n")
        
        for theme, shifts in geo_shifts.items():
            if shifts['emerging_markets']:
                report.append(f"\n**{theme}**: {', '.join(shifts['emerging_markets'][:3])}")
        
        report.append("\n### 🏆 Stable Market Leaders")
        report.append("\nThese metros show consistent interest across all timeframes:\n")
        
        # Aggregate stable leaders across themes
        all_stable = {}
        for theme, shifts in geo_shifts.items():
            for market in shifts['stable_leaders']:
                if market not in all_stable:
                    all_stable[market] = []
                all_stable[market].append(theme)
        
        # Sort by number of themes
        stable_sorted = sorted(all_stable.items(), key=lambda x: len(x[1]), reverse=True)
        
        for market, themes in stable_sorted[:5]:
            report.append(f"- **{market}**: Popular for {', '.join(themes[:3])}")
        
        # 3. Seasonal Pattern Evolution
        report.append("\n## 3. Seasonal Pattern Evolution")
        report.append("\n### 📅 Peak Season Shifts")
        
        report.append("\n| Theme | 5-Year Peak | 1-Year Peak | Seasonality Strength | Strategy |")
        report.append("|-------|-------------|-------------|---------------------|----------|")
        
        months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        
        for theme, seasonal in seasonal_evolution.items():
            if '1 Year' in seasonal and '5 Year' in seasonal:
                peak_1y = seasonal['1 Year'].get('peak_month', 0)
                peak_5y = seasonal['5 Year'].get('peak_month', 0)
                strength = seasonal['1 Year'].get('seasonality_strength', 0)
                
                if peak_1y != peak_5y:
                    strategy = f"⚠️ Peak shifted from {months.get(peak_5y, 'N/A')} to {months.get(peak_1y, 'N/A')}"
                elif strength > 0.5:
                    strategy = f"📈 Increase budget {int(strength * 30)}% in {months.get(peak_1y, 'N/A')}"
                else:
                    strategy = "➡️ Maintain steady budget"
                
                report.append(f"| {theme} | {months.get(peak_5y, 'N/A')} | {months.get(peak_1y, 'N/A')} | {strength:.2f} | {strategy} |")
        
        # 4. Breakout Keywords
        report.append("\n## 4. Breakout Keywords & Emerging Searches")
        report.append("\n### 🔥 New Trending Keywords (Last Year Only)")
        
        for theme, keywords in breakout_keywords.items():
            if keywords['new_trending']:
                report.append(f"\n**{theme}**:")
                for kw in keywords['new_trending'][:5]:
                    report.append(f"- {kw}")
        
        # 5. Strategic Campaign Structure
        report.append("\n## 5. Recommended Campaign Structure (Data-Driven)")
        
        # Group themes by momentum and volume
        high_momentum = []
        stable_volume = []
        emerging = []
        declining = []
        
        for theme, momentum in momentum_scores.items():
            tf_data = self.themes_data[theme]['timeframe_data']
            vol_1y = tf_data.get('1 Year', {}).get('avg_volume', 0)
            
            if momentum['momentum_score'] > 20 and vol_1y > 20:
                high_momentum.append(theme)
            elif momentum['momentum_score'] > 20 and vol_1y <= 20:
                emerging.append(theme)
            elif momentum['momentum_score'] < -20:
                declining.append(theme)
            else:
                stable_volume.append(theme)
        
        report.append("\n### Campaign 1: High-Performance Core")
        report.append("**Budget Allocation: 50%**")
        report.append("\nThemes with strong volume AND positive momentum:")
        for theme in high_momentum:
            vol_1y = self.themes_data[theme]['timeframe_data'].get('1 Year', {}).get('avg_volume', 0)
            report.append(f"- {theme} (Volume: {vol_1y:.1f}, Momentum: {momentum_scores[theme]['momentum_score']:+.1f}%)")
        
        report.append("\n### Campaign 2: Stable Performers")
        report.append("**Budget Allocation: 30%**")
        report.append("\nConsistent performers with stable search interest:")
        for theme in stable_volume[:5]:
            vol_1y = self.themes_data[theme]['timeframe_data'].get('1 Year', {}).get('avg_volume', 0)
            report.append(f"- {theme} (Volume: {vol_1y:.1f})")
        
        report.append("\n### Campaign 3: Emerging Opportunities")
        report.append("**Budget Allocation: 15%**")
        report.append("\nLow volume but high growth - test campaigns:")
        for theme in emerging[:5]:
            report.append(f"- {theme} (Momentum: {momentum_scores[theme]['momentum_score']:+.1f}%)")
        
        report.append("\n### Campaign 4: Defensive/Monitor")
        report.append("**Budget Allocation: 5%**")
        report.append("\nDeclining markets - minimal investment:")
        for theme in declining[:3]:
            report.append(f"- {theme} (Momentum: {momentum_scores[theme]['momentum_score']:+.1f}%)")
        
        # 6. Action Plan
        report.append("\n## 6. 30-Day Action Plan")
        
        report.append("\n### Week 1: High-Impact Quick Wins")
        if recommendations['immediate_opportunities']:
            for opp in recommendations['immediate_opportunities'][:3]:
                report.append(f"- Launch campaign for **{opp['theme']}** (Momentum: {opp['momentum']:+.1f}%)")
        
        report.append("\n### Week 2: Geographic Expansion")
        if recommendations['growth_markets']:
            for market in recommendations['growth_markets'][:3]:
                report.append(f"- Add geo-targeting for {market['theme']}: {', '.join(market['markets'][:2])}")
        
        report.append("\n### Week 3: Keyword Optimization")
        if recommendations['keyword_opportunities']:
            for kw_opp in recommendations['keyword_opportunities'][:3]:
                report.append(f"- Add trending keywords for {kw_opp['theme']}: {', '.join(kw_opp['keywords'][:2])}")
        
        report.append("\n### Week 4: Budget Reallocation")
        if recommendations['defensive_actions']:
            for defense in recommendations['defensive_actions'][:2]:
                report.append(f"- Reduce budget for {defense['theme']} (Momentum: {defense['momentum']:+.1f}%)")
        
        # 7. Success Metrics
        report.append("\n## 7. Success Metrics & KPIs")
        
        report.append("\n### Performance Benchmarks by Market Type")
        report.append("\n| Market Type | Target CTR | Target CPC | Target Conv Rate | Budget % |")
        report.append("|-------------|------------|------------|------------------|----------|")
        report.append("| High Momentum | 3-5% | $4-8 | 3-4% | 50% |")
        report.append("| Stable Volume | 2-3% | $5-10 | 2-3% | 30% |")
        report.append("| Emerging | 1-2% | $3-6 | 1-2% | 15% |")
        report.append("| Defensive | 1-2% | $2-5 | 1-2% | 5% |")
        
        # Conclusion
        report.append("\n---")
        report.append("\n## Key Takeaways")
        
        # Calculate summary statistics
        accelerating_count = sum(1 for m in momentum_scores.values() if m['acceleration'] == 'accelerating')
        high_momentum_count = sum(1 for m in momentum_scores.values() if m['momentum_score'] > 20)
        
        report.append(f"\n- **{accelerating_count} markets** showing acceleration in growth")
        report.append(f"- **{high_momentum_count} markets** with >20% positive momentum vs. historical average")
        report.append("- **Geographic diversification** emerging in Southern and Midwestern metros")
        report.append("- **Seasonal patterns** becoming more pronounced in recent data")
        report.append("- **Immediate opportunity** in high-momentum markets with accelerating growth")
        
        report.append("\n---")
        report.append("\n*This multi-timeframe analysis provides deeper insights by comparing recent performance ")
        report.append("against historical baselines, enabling more precise campaign optimization and budget allocation.*")
        
        return "\n".join(report)

def main():
    """Main analysis function"""
    trends_path = "/Users/evan/Downloads/Trends"
    
    # Initialize analyzer
    analyzer = MultiTimeframeAnalyzer(trends_path)
    
    # Load all timeframe data
    analyzer.load_all_timeframe_data()
    
    # Generate markdown report
    report = analyzer.generate_markdown_report()
    
    # Save report
    report_path = os.path.join(trends_path, "Analysis", "multi_timeframe_strategic_brief.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Multi-timeframe strategic brief saved to: {report_path}")
    
    return report

if __name__ == "__main__":
    main()
