"""
AI Campaign Builder with Guardrails
Automatically creates campaigns with intelligent defaults and safety checks
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import core systems
sys.path.append('google-ads-analysis')
from google_ads_integration import SimpleGoogleAdsManager

class AICampaignBuilder:
    def __init__(self):
        self.ads_manager = SimpleGoogleAdsManager()
        
    def create_campaign_from_name(self, campaign_name, budget=None, target_location=None):
        """
        Create a campaign intelligently based on name
        AI infers settings from campaign name
        """
        try:
            # Parse campaign name for intelligence
            campaign_config = self.parse_campaign_name(campaign_name)
            
            # Apply intelligent defaults
            if budget:
                campaign_config['budget'] = budget
            if target_location:
                campaign_config['target_location'] = target_location
            
            # Validate with guardrails
            validation_result = self.validate_campaign_config(campaign_config)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Campaign validation failed: {validation_result['errors']}"
                }
            
            # Create campaign via Google Ads API
            campaign_result = self.create_campaign_via_api(campaign_config)
            
            if campaign_result['success']:
                # Log the creation
                self.log_campaign_creation(campaign_config, campaign_result)
                
                return {
                    'success': True,
                    'campaign_id': campaign_result['campaign_id'],
                    'message': f"Campaign '{campaign_name}' created successfully"
                }
            else:
                return {
                    'success': False,
                    'error': campaign_result['error']
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error creating campaign: {str(e)}"
            }
    
    def parse_campaign_name(self, campaign_name):
        """
        Parse campaign name to infer intelligent settings
        """
        config = {
            'name': campaign_name,
            'type': 'PERFORMANCE_MAX',
            'status': 'ENABLED',
            'budget': 50,  # Default daily budget
            'bidding_strategy': 'MAXIMIZE_CONVERSIONS',
            'target_location': 'Park City, UT',  # Default
            'conversion_goals': ['Lead Form Submission', 'Phone Call'],
            'url_expansion': True,
            'url_exclusions': [
                '/buyers/*', '/sellers/*', '/featured-listings/*', 
                '/contact/*', '/blog/*', '/property-search/*', 
                '/idx/*', '/privacy/*', '/about/*'
            ]
        }
        
        # AI parsing logic based on campaign name
        name_lower = campaign_name.lower()
        
        # Infer location
        if 'local' in name_lower or 'park city' in name_lower:
            config['target_location'] = 'Park City, UT'
        elif 'feeder' in name_lower or 'dallas' in name_lower:
            config['target_location'] = 'Dallas, TX'
        elif 'la' in name_lower or 'los angeles' in name_lower:
            config['target_location'] = 'Los Angeles, CA'
        elif 'nyc' in name_lower or 'new york' in name_lower:
            config['target_location'] = 'New York, NY'
        
        # Infer budget based on location
        if 'feeder' in name_lower or any(city in name_lower for city in ['dallas', 'la', 'nyc', 'los angeles', 'new york']):
            config['budget'] = 41  # Feeder market budget
        elif 'local' in name_lower or 'park city' in name_lower:
            config['budget'] = 49  # Local market budget
        
        # Infer campaign type
        if 'pmax' in name_lower:
            config['type'] = 'PERFORMANCE_MAX'
        elif 'search' in name_lower:
            config['type'] = 'SEARCH'
        
        return config
    
    def validate_campaign_config(self, config):
        """
        Validate campaign configuration against guardrails
        """
        errors = []
        
        # Budget validation
        if config['budget'] < 30:
            errors.append("Budget must be at least $30/day")
        if config['budget'] > 250:
            errors.append("Budget must not exceed $250/day")
        
        # Required fields
        if not config.get('name'):
            errors.append("Campaign name is required")
        if not config.get('target_location'):
            errors.append("Target location is required")
        
        # URL exclusions validation
        required_exclusions = [
            '/buyers/*', '/sellers/*', '/featured-listings/*', 
            '/contact/*', '/blog/*', '/property-search/*', 
            '/idx/*', '/privacy/*', '/about/*'
        ]
        
        if not all(exclusion in config.get('url_exclusions', []) for exclusion in required_exclusions):
            errors.append("Required URL exclusions missing")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def create_campaign_via_api(self, config):
        """
        Create campaign via Google Ads API
        """
        try:
            # This would integrate with the actual Google Ads API
            # For now, return a mock success
            
            # In real implementation, you would:
            # 1. Create campaign
            # 2. Set budget
            # 3. Configure targeting
            # 4. Set up conversion tracking
            # 5. Create asset groups
            # 6. Enable URL expansion with page feed
            
            return {
                'success': True,
                'campaign_id': f"campaign_{int(datetime.now().timestamp())}",
                'message': "Campaign created via API"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_campaign_creation(self, config, result):
        """
        Log campaign creation for audit trail
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'campaign_created',
            'config': config,
            'result': result
        }
        
        # Save to log file
        os.makedirs('data', exist_ok=True)
        log_file = 'data/campaign_creation_log.json'
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
    
    def get_campaign_suggestions(self):
        """
        Get AI-suggested campaign ideas based on current performance
        """
        try:
            # Analyze current campaigns
            ads_data = self.ads_manager.get_campaign_data()
            
            suggestions = []
            
            if ads_data and 'campaigns' in ads_data:
                campaigns = ads_data['campaigns']
                
                # Check for opportunities
                for campaign in campaigns:
                    if campaign.get('status') == 'ENABLED':
                        # Suggest optimizations
                        if campaign.get('cpl', 0) > 200:
                            suggestions.append({
                                'type': 'optimization',
                                'campaign': campaign.get('name'),
                                'suggestion': 'Consider reducing budget or improving targeting - CPL is high',
                                'priority': 'high'
                            })
                        
                        if campaign.get('conversions', 0) == 0 and campaign.get('cost', 0) > 50:
                            suggestions.append({
                                'type': 'optimization',
                                'campaign': campaign.get('name'),
                                'suggestion': 'No conversions with significant spend - review targeting',
                                'priority': 'critical'
                            })
            
            # Add strategic suggestions
            suggestions.extend([
                {
                    'type': 'expansion',
                    'campaign': 'New Campaign',
                    'suggestion': 'Consider creating feeder market campaigns for Dallas, LA, NYC',
                    'priority': 'medium'
                },
                {
                    'type': 'optimization',
                    'campaign': 'All Campaigns',
                    'suggestion': 'Review asset quality and add more property-specific images',
                    'priority': 'low'
                }
            ])
            
            return suggestions
            
        except Exception as e:
            return [{
                'type': 'error',
                'campaign': 'System',
                'suggestion': f'Error generating suggestions: {str(e)}',
                'priority': 'critical'
            }]

def main():
    """Test the AI Campaign Builder"""
    builder = AICampaignBuilder()
    
    # Test campaign creation
    result = builder.create_campaign_from_name("L.R - PMax - Local Presence", budget=49)
    print(f"Campaign creation result: {result}")
    
    # Test suggestions
    suggestions = builder.get_campaign_suggestions()
    print(f"Campaign suggestions: {suggestions}")

if __name__ == "__main__":
    main()
