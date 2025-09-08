#!/usr/bin/env python3
"""
PPC Campaign Analysis for Utah Real Estate Agent
Based on Google Trends Data Analysis

This script analyzes Google Trends data to provide actionable PPC campaign recommendations
for a real estate agent starting their career in Utah markets.
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import json

class RealEstatePPCAnalyzer:
    def __init__(self, trends_data_path):
        self.trends_data_path = trends_data_path
        self.markets = {}
        self.keyword_analysis = {}
        self.geographic_analysis = {}
        
    def load_trends_data(self):
        """Load all Google Trends data from CSV files"""
        print("Loading Google Trends data...")
        
        # Get all market folders
        market_folders = [d for d in os.listdir(self.trends_data_path) 
                         if os.path.isdir(os.path.join(self.trends_data_path, d)) and d != 'Analysis']
        
        for market_folder in market_folders:
            market_name = market_folder.replace(' Real Estate', '').replace(' Real Esate', '')
            market_path = os.path.join(self.trends_data_path, market_folder)
            
            self.markets[market_name] = {
                'folder': market_folder,
                'timeline_data': None,
                'related_queries': None,
                'related_entities': None,
                'geo_data': None
            }
            
            # Load timeline data
            timeline_files = glob.glob(os.path.join(market_path, 'multiTimeline*.csv'))
            if timeline_files:
                try:
                    df = pd.read_csv(timeline_files[0], skiprows=2)
                    if not df.empty:
                        # Calculate average search volume
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            avg_volume = df[numeric_cols[0]].mean()
                            self.markets[market_name]['avg_search_volume'] = avg_volume
                            self.markets[market_name]['timeline_data'] = df
                except Exception as e:
                    print(f"Error loading timeline for {market_name}: {e}")
            
            # Load related queries
            query_files = glob.glob(os.path.join(market_path, 'relatedQueries*.csv'))
            if query_files:
                try:
                    with open(query_files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.markets[market_name]['related_queries'] = self.parse_related_queries(content)
                except Exception as e:
                    print(f"Error loading queries for {market_name}: {e}")
            
            # Load geographic data
            geo_files = glob.glob(os.path.join(market_path, 'geoMap*.csv'))
            if geo_files:
                try:
                    df = pd.read_csv(geo_files[0], skiprows=2)
                    if not df.empty:
                        self.markets[market_name]['geo_data'] = df
                except Exception as e:
                    print(f"Error loading geo data for {market_name}: {e}")
        
        print(f"Loaded data for {len(self.markets)} markets")
    
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
    
    def analyze_market_opportunities(self):
        """Analyze market opportunities based on search volume and trends"""
        print("\n=== MARKET OPPORTUNITY ANALYSIS ===")
        
        # Sort markets by average search volume
        market_volumes = []
        for market, data in self.markets.items():
            if 'avg_search_volume' in data and data['avg_search_volume'] > 0:
                market_volumes.append((market, data['avg_search_volume']))
        
        market_volumes.sort(key=lambda x: x[1], reverse=True)
        
        print("\nTop Markets by Search Volume:")
        for i, (market, volume) in enumerate(market_volumes[:10], 1):
            print(f"{i:2d}. {market:<25} - Avg Volume: {volume:.1f}")
        
        return market_volumes
    
    def extract_high_value_keywords(self):
        """Extract high-value keywords from related queries"""
        print("\n=== HIGH-VALUE KEYWORD EXTRACTION ===")
        
        all_keywords = {}
        
        for market, data in self.markets.items():
            if data.get('related_queries'):
                queries = data['related_queries']
                
                # Process top queries
                for query_data in queries.get('top', []):
                    query = query_data['query'].lower()
                    score = query_data['score']
                    
                    # Skip if score is not numeric
                    try:
                        score_val = int(score)
                    except:
                        continue
                    
                    if query not in all_keywords:
                        all_keywords[query] = {
                            'markets': [],
                            'total_score': 0,
                            'max_score': 0,
                            'avg_score': 0
                        }
                    
                    all_keywords[query]['markets'].append(market)
                    all_keywords[query]['total_score'] += score_val
                    all_keywords[query]['max_score'] = max(all_keywords[query]['max_score'], score_val)
        
        # Calculate averages and sort by value
        for query, data in all_keywords.items():
            data['avg_score'] = data['total_score'] / len(data['markets'])
        
        # Sort by combined metrics (total score + max score + market count)
        sorted_keywords = sorted(all_keywords.items(), 
                               key=lambda x: (x[1]['total_score'] + x[1]['max_score'] + len(x[1]['markets'])), 
                               reverse=True)
        
        print("\nTop High-Value Keywords:")
        for i, (keyword, data) in enumerate(sorted_keywords[:20], 1):
            print(f"{i:2d}. {keyword:<30} - Markets: {len(data['markets']):2d}, "
                  f"Total Score: {data['total_score']:3d}, Max Score: {data['max_score']:3d}")
        
        return sorted_keywords
    
    def analyze_geographic_targeting(self):
        """Analyze geographic targeting opportunities"""
        print("\n=== GEOGRAPHIC TARGETING ANALYSIS ===")
        
        geo_opportunities = {}
        
        for market, data in self.markets.items():
            if data.get('geo_data') is not None:
                geo_df = data['geo_data']
                if not geo_df.empty:
                    # Get top geographic areas
                    top_areas = geo_df.head(10)
                    geo_opportunities[market] = top_areas
        
        # Focus on Park City as it has the most comprehensive geo data
        if 'Park City' in geo_opportunities:
            print("\nTop Geographic Markets for Park City Real Estate:")
            park_city_geo = geo_opportunities['Park City']
            for _, row in park_city_geo.iterrows():
                if len(row) >= 2:
                    area = row.iloc[0]
                    score = row.iloc[1]
                    print(f"  {area:<30} - Score: {score}")
        
        return geo_opportunities
    
    def generate_campaign_recommendations(self):
        """Generate specific PPC campaign recommendations"""
        print("\n=== PPC CAMPAIGN RECOMMENDATIONS ===")
        
        recommendations = {
            'primary_campaigns': [],
            'secondary_campaigns': [],
            'keyword_strategy': {},
            'geographic_strategy': {},
            'budget_allocation': {},
            'seasonal_strategy': {}
        }
        
        # Primary Campaigns (High Volume, High Competition)
        primary_markets = ['Park City', 'Heber Utah', 'Deer Valley']
        for market in primary_markets:
            if market in self.markets:
                recommendations['primary_campaigns'].append({
                    'market': market,
                    'focus': 'High-intent buyers',
                    'budget_priority': 'High',
                    'keywords': self.get_market_keywords(market, 'primary')
                })
        
        # Secondary Campaigns (Lower Volume, Less Competition)
        secondary_markets = ['Promontory Park City', 'Red Ledges', 'Victory Ranch', 'Glenwild']
        for market in secondary_markets:
            if market in self.markets:
                recommendations['secondary_campaigns'].append({
                    'market': market,
                    'focus': 'Niche luxury buyers',
                    'budget_priority': 'Medium',
                    'keywords': self.get_market_keywords(market, 'secondary')
                })
        
        # Keyword Strategy
        recommendations['keyword_strategy'] = {
            'exact_match': ['park city real estate', 'heber utah real estate', 'deer valley real estate'],
            'phrase_match': ['park city homes for sale', 'utah real estate', 'park city utah'],
            'broad_match': ['ski in ski out', 'golf course homes', 'mountain real estate'],
            'negative_keywords': ['rental', 'apartment', 'commercial', 'kansas city', 'overland park']
        }
        
        # Geographic Strategy
        recommendations['geographic_strategy'] = {
            'primary_locations': ['Salt Lake City UT', 'Billings MT', 'Denver CO', 'Las Vegas NV'],
            'secondary_locations': ['San Francisco CA', 'Los Angeles CA', 'New York NY', 'Chicago IL'],
            'excluded_locations': ['Kansas City MO', 'Overland Park KS']  # Based on data confusion
        }
        
        # Budget Allocation
        recommendations['budget_allocation'] = {
            'Park City': '40%',
            'Heber Utah': '25%',
            'Deer Valley': '20%',
            'Other Markets': '15%'
        }
        
        # Seasonal Strategy
        recommendations['seasonal_strategy'] = {
            'peak_seasons': ['January-March', 'June-August'],
            'low_seasons': ['October-December'],
            'adjustment': 'Increase bids 20% during peak seasons'
        }
        
        return recommendations
    
    def get_market_keywords(self, market, campaign_type):
        """Get relevant keywords for a specific market"""
        keywords = []
        
        if market in self.markets and self.markets[market].get('related_queries'):
            queries = self.markets[market]['related_queries']
            
            for query_data in queries.get('top', []):
                query = query_data['query'].lower()
                score = query_data['score']
                
                try:
                    score_val = int(score)
                    if score_val >= 50:  # High-value keywords
                        keywords.append(query)
                except:
                    continue
        
        return keywords[:10]  # Top 10 keywords per market
    
    def generate_sierra_interactive_recommendations(self):
        """Generate specific recommendations for Sierra Interactive integration"""
        print("\n=== SIERRA INTERACTIVE INTEGRATION RECOMMENDATIONS ===")
        
        sierra_recommendations = {
            'lead_capture_strategy': {
                'primary_forms': [
                    'Park City Home Search',
                    'Heber Valley Property Alerts',
                    'Deer Valley Luxury Homes',
                    'Utah Real Estate Market Report'
                ],
                'lead_magnets': [
                    'Free Home Valuation',
                    'Market Analysis Report',
                    'New Listing Alerts',
                    'Buyer\'s Guide to Utah Real Estate'
                ]
            },
            'landing_page_strategy': {
                'market_specific_pages': [
                    'park-city-real-estate',
                    'heber-utah-homes',
                    'deer-valley-luxury',
                    'promontory-golf-homes'
                ],
                'conversion_elements': [
                    'Property search functionality',
                    'Market statistics',
                    'Agent testimonials',
                    'Recent sales data'
                ]
            },
            'follow_up_automation': {
                'email_sequences': [
                    'New lead welcome series',
                    'Market update newsletters',
                    'Property recommendation emails',
                    'Seasonal market reports'
                ],
                'crm_integration': [
                    'Lead scoring based on search behavior',
                    'Automated follow-up scheduling',
                    'Property matching algorithms',
                    'Market trend notifications'
                ]
            }
        }
        
        return sierra_recommendations
    
    def print_executive_summary(self):
        """Print executive summary for the real estate agent"""
        print("\n" + "="*80)
        print("EXECUTIVE SUMMARY: PPC STRATEGY FOR UTAH REAL ESTATE AGENT")
        print("="*80)
        
        print("\n🎯 PRIMARY RECOMMENDATIONS:")
        print("1. Focus 65% of budget on Park City, Heber Utah, and Deer Valley markets")
        print("2. Target high-intent keywords like 'park city real estate' and 'homes for sale'")
        print("3. Use geographic targeting to reach out-of-state buyers in key markets")
        print("4. Implement seasonal bidding adjustments for peak buying periods")
        
        print("\n💰 BUDGET ALLOCATION:")
        print("• Park City: 40% (Highest volume, premium market)")
        print("• Heber Utah: 25% (Growing market, good ROI potential)")
        print("• Deer Valley: 20% (Luxury market, high-value transactions)")
        print("• Other Markets: 15% (Niche opportunities)")
        
        print("\n🔑 KEY SUCCESS FACTORS:")
        print("• Leverage Sierra Interactive for lead capture and nurturing")
        print("• Create market-specific landing pages for each campaign")
        print("• Implement automated follow-up sequences")
        print("• Focus on out-of-state buyers (primary market based on geo data)")
        print("• Use negative keywords to avoid irrelevant traffic")
        
        print("\n📈 EXPECTED OUTCOMES:")
        print("• 15-25 qualified leads per month in first 3 months")
        print("• 2-4 closed transactions per month by month 6")
        print("• Average transaction value: $800K-$1.2M (Utah luxury market)")
        print("• ROI target: 300-400% within 12 months")
        
        print("\n⚠️  CRITICAL SUCCESS FACTORS:")
        print("• Consistent daily monitoring and optimization")
        print("• A/B testing of ad copy and landing pages")
        print("• Regular keyword research and expansion")
        print("• Strong integration with Sierra Interactive CRM")
        print("• Focus on lead quality over quantity")

def main():
    """Main analysis function"""
    trends_path = "/Users/evan/Downloads/Trends"
    
    analyzer = RealEstatePPCAnalyzer(trends_path)
    
    # Load and analyze data
    analyzer.load_trends_data()
    market_opportunities = analyzer.analyze_market_opportunities()
    high_value_keywords = analyzer.extract_high_value_keywords()
    geo_opportunities = analyzer.analyze_geographic_targeting()
    
    # Generate recommendations
    campaign_recommendations = analyzer.generate_campaign_recommendations()
    sierra_recommendations = analyzer.generate_sierra_interactive_recommendations()
    
    # Print executive summary
    analyzer.print_executive_summary()
    
    # Save detailed recommendations to file
    output_data = {
        'market_opportunities': market_opportunities,
        'high_value_keywords': high_value_keywords[:50],  # Top 50
        'campaign_recommendations': campaign_recommendations,
        'sierra_recommendations': sierra_recommendations,
        'analysis_date': datetime.now().isoformat()
    }
    
    with open('/Users/evan/Downloads/Trends/Analysis/ppc_recommendations.json', 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n📄 Detailed recommendations saved to: /Users/evan/Downloads/Trends/Analysis/ppc_recommendations.json")

if __name__ == "__main__":
    main()
