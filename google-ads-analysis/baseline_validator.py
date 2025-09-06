#!/usr/bin/env python3
"""
Baseline Validator
=================

Consolidated baseline validation system that handles URL exclusions,
geo-targeting requirements, and asset requirements for Google Ads campaigns.
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

class BaselineValidator:
    """Consolidated baseline validation for Google Ads campaigns."""
    
    def __init__(self):
        # Required URL exclusions
        self.required_exclusions = [
            '/buyers/*',
            '/sellers/*', 
            '/blog/*',
            '/admin/*',
            '/login/*',
            '/register/*',
            '/checkout/*',
            '/cart/*'
        ]
        
        # Geo-targeting requirements
        self.geo_requirements = {
            'presence_only': True,
            'allowed_countries': ['US'],
            'excluded_locations': []
        }
        
        # Asset requirements for PMax
        self.asset_requirements = {
            'headlines': {'min': 5, 'max': 15},
            'long_headlines': {'min': 1, 'max': 5},
            'descriptions': {'min': 2, 'max': 5},
            'business_name': {'required': True},
            'logos': {
                '1_1': {'min': 1, 'max': 5},
                '4_1': {'min': 1, 'max': 5}
            },
            'images': {
                '1_91_1': {'min': 3, 'max': 20},
                '1_1': {'min': 3, 'max': 20},
                '4_3': {'min': 1, 'max': 20}
            },
            'videos': {'min': 1, 'max': 10}
        }
        
        # Campaign naming conventions
        self.naming_conventions = {
            'prefix': 'L.R',
            'campaign_type': 'PMax',
            'separator': ' - ',
            'required_parts': ['prefix', 'campaign_type', 'audience']
        }
    
    def validate_url_exclusions(self, current_exclusions: List[str]) -> Dict:
        """Validate that all required URL exclusions are present."""
        missing_exclusions = []
        present_exclusions = []
        
        for required_exclusion in self.required_exclusions:
            # Convert wildcard pattern to regex
            pattern = required_exclusion.replace('*', '.*')
            regex = re.compile(pattern)
            
            found = False
            for current_exclusion in current_exclusions:
                if regex.match(current_exclusion):
                    found = True
                    present_exclusions.append(current_exclusion)
                    break
            
            if not found:
                missing_exclusions.append(required_exclusion)
        
        return {
            'valid': len(missing_exclusions) == 0,
            'missing_exclusions': missing_exclusions,
            'present_exclusions': present_exclusions,
            'total_required': len(self.required_exclusions),
            'total_present': len(present_exclusions)
        }
    
    def validate_geo_targeting(self, geo_settings: Dict) -> Dict:
        """Validate geo-targeting settings."""
        issues = []
        warnings = []
        
        # Check for presence_only requirement
        if not geo_settings.get('presence_only', False):
            issues.append("Geo-targeting must be set to PRESENCE_ONLY")
        
        # Check for allowed countries
        if 'targeted_countries' in geo_settings:
            targeted = geo_settings['targeted_countries']
            for country in targeted:
                if country not in self.geo_requirements['allowed_countries']:
                    warnings.append(f"Country '{country}' may not be optimal for targeting")
        
        # Check for excluded locations
        if 'excluded_locations' in geo_settings:
            excluded = geo_settings['excluded_locations']
            for location in excluded:
                if location in self.geo_requirements['excluded_locations']:
                    warnings.append(f"Location '{location}' is already in global exclusions")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'settings': geo_settings
        }
    
    def validate_asset_requirements(self, asset_counts: Dict) -> Dict:
        """Validate that asset group meets minimum requirements."""
        missing = []
        warnings = []
        valid_assets = []
        
        # Check headlines
        headlines = asset_counts.get('headlines', 0)
        if headlines < self.asset_requirements['headlines']['min']:
            missing.append(f"headlines ({headlines}/{self.asset_requirements['headlines']['min']})")
        elif headlines > self.asset_requirements['headlines']['max']:
            warnings.append(f"Too many headlines ({headlines}/{self.asset_requirements['headlines']['max']})")
        else:
            valid_assets.append(f"headlines ({headlines})")
        
        # Check long headlines
        long_headlines = asset_counts.get('long_headlines', 0)
        if long_headlines < self.asset_requirements['long_headlines']['min']:
            missing.append(f"long headlines ({long_headlines}/{self.asset_requirements['long_headlines']['min']})")
        elif long_headlines > self.asset_requirements['long_headlines']['max']:
            warnings.append(f"Too many long headlines ({long_headlines}/{self.asset_requirements['long_headlines']['max']})")
        else:
            valid_assets.append(f"long headlines ({long_headlines})")
        
        # Check descriptions
        descriptions = asset_counts.get('descriptions', 0)
        if descriptions < self.asset_requirements['descriptions']['min']:
            missing.append(f"descriptions ({descriptions}/{self.asset_requirements['descriptions']['min']})")
        elif descriptions > self.asset_requirements['descriptions']['max']:
            warnings.append(f"Too many descriptions ({descriptions}/{self.asset_requirements['descriptions']['max']})")
        else:
            valid_assets.append(f"descriptions ({descriptions})")
        
        # Check business name
        if self.asset_requirements['business_name']['required']:
            business_name = asset_counts.get('business_name', 0)
            if business_name < 1:
                missing.append("business name")
            else:
                valid_assets.append("business name")
        
        # Check logos
        logos_1_1 = asset_counts.get('logos_1_1', 0)
        logos_4_1 = asset_counts.get('logos_4_1', 0)
        
        if logos_1_1 < self.asset_requirements['logos']['1_1']['min']:
            missing.append(f"1:1 logos ({logos_1_1}/{self.asset_requirements['logos']['1_1']['min']})")
        elif logos_1_1 > self.asset_requirements['logos']['1_1']['max']:
            warnings.append(f"Too many 1:1 logos ({logos_1_1}/{self.asset_requirements['logos']['1_1']['max']})")
        else:
            valid_assets.append(f"1:1 logos ({logos_1_1})")
        
        if logos_4_1 < self.asset_requirements['logos']['4_1']['min']:
            missing.append(f"4:1 logos ({logos_4_1}/{self.asset_requirements['logos']['4_1']['min']})")
        elif logos_4_1 > self.asset_requirements['logos']['4_1']['max']:
            warnings.append(f"Too many 4:1 logos ({logos_4_1}/{self.asset_requirements['logos']['4_1']['max']})")
        else:
            valid_assets.append(f"4:1 logos ({logos_4_1})")
        
        # Check images
        images_1_91_1 = asset_counts.get('images_1_91_1', 0)
        images_1_1 = asset_counts.get('images_1_1', 0)
        images_4_3 = asset_counts.get('images_4_3', 0)
        
        if images_1_91_1 < self.asset_requirements['images']['1_91_1']['min']:
            missing.append(f"1.91:1 images ({images_1_91_1}/{self.asset_requirements['images']['1_91_1']['min']})")
        elif images_1_91_1 > self.asset_requirements['images']['1_91_1']['max']:
            warnings.append(f"Too many 1.91:1 images ({images_1_91_1}/{self.asset_requirements['images']['1_91_1']['max']})")
        else:
            valid_assets.append(f"1.91:1 images ({images_1_91_1})")
        
        if images_1_1 < self.asset_requirements['images']['1_1']['min']:
            missing.append(f"1:1 images ({images_1_1}/{self.asset_requirements['images']['1_1']['min']})")
        elif images_1_1 > self.asset_requirements['images']['1_1']['max']:
            warnings.append(f"Too many 1:1 images ({images_1_1}/{self.asset_requirements['images']['1_1']['max']})")
        else:
            valid_assets.append(f"1:1 images ({images_1_1})")
        
        if images_4_3 < self.asset_requirements['images']['4_3']['min']:
            missing.append(f"4:3 images ({images_4_3}/{self.asset_requirements['images']['4_3']['min']})")
        elif images_4_3 > self.asset_requirements['images']['4_3']['max']:
            warnings.append(f"Too many 4:3 images ({images_4_3}/{self.asset_requirements['images']['4_3']['max']})")
        else:
            valid_assets.append(f"4:3 images ({images_4_3})")
        
        # Check videos
        videos = asset_counts.get('videos', 0)
        if videos < self.asset_requirements['videos']['min']:
            missing.append(f"videos ({videos}/{self.asset_requirements['videos']['min']})")
        elif videos > self.asset_requirements['videos']['max']:
            warnings.append(f"Too many videos ({videos}/{self.asset_requirements['videos']['max']})")
        else:
            valid_assets.append(f"videos ({videos})")
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'warnings': warnings,
            'valid_assets': valid_assets,
            'requirements': self.asset_requirements
        }
    
    def validate_campaign_naming(self, campaign_name: str) -> Dict:
        """Validate campaign naming convention."""
        issues = []
        warnings = []
        
        # Check for required prefix
        if not campaign_name.startswith(self.naming_conventions['prefix']):
            issues.append(f"Campaign name must start with '{self.naming_conventions['prefix']}'")
        
        # Check for campaign type
        if self.naming_conventions['campaign_type'] not in campaign_name:
            issues.append(f"Campaign name must include '{self.naming_conventions['campaign_type']}'")
        
        # Check for proper separator
        if self.naming_conventions['separator'] not in campaign_name:
            warnings.append(f"Consider using '{self.naming_conventions['separator']}' as separator")
        
        # Check for audience identifier
        if not any(part in campaign_name.lower() for part in ['general', 'specific', 'audience', 'target']):
            warnings.append("Consider adding audience identifier to campaign name")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'conventions': self.naming_conventions
        }
    
    def validate_budget_settings(self, budget_settings: Dict) -> Dict:
        """Validate budget settings."""
        issues = []
        warnings = []
        
        daily_budget = budget_settings.get('daily_budget', 0)
        
        # Check minimum daily budget
        if daily_budget < 30.0:
            issues.append(f"Daily budget ${daily_budget} is below minimum of $30.00")
        elif daily_budget < 50.0:
            warnings.append(f"Daily budget ${daily_budget} is low, consider increasing to $50+")
        
        # Check maximum daily budget
        if daily_budget > 100.0:
            issues.append(f"Daily budget ${daily_budget} exceeds maximum of $100.00")
        elif daily_budget > 80.0:
            warnings.append(f"Daily budget ${daily_budget} is high, monitor performance closely")
        
        # Check budget type
        budget_type = budget_settings.get('budget_type', '')
        if budget_type != 'DAILY':
            issues.append(f"Budget type must be 'DAILY', not '{budget_type}'")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'settings': budget_settings
        }
    
    def validate_tcpa_settings(self, tcpa_settings: Dict) -> Dict:
        """Validate tCPA settings."""
        issues = []
        warnings = []
        
        tcpa_value = tcpa_settings.get('tcpa_value', 0)
        
        # Check minimum tCPA
        if tcpa_value < 80.0:
            issues.append(f"tCPA ${tcpa_value} is below minimum of $80.00")
        elif tcpa_value < 100.0:
            warnings.append(f"tCPA ${tcpa_value} is low, consider increasing to $100+")
        
        # Check maximum tCPA
        if tcpa_value > 200.0:
            issues.append(f"tCPA ${tcpa_value} exceeds maximum of $200.00")
        elif tcpa_value > 150.0:
            warnings.append(f"tCPA ${tcpa_value} is high, monitor conversion quality")
        
        # Check if tCPA is enabled
        if not tcpa_settings.get('tcpa_enabled', False):
            warnings.append("tCPA is not enabled, consider enabling for better performance")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'settings': tcpa_settings
        }
    
    def validate_campaign_structure(self, campaign_config: Dict) -> Dict:
        """Validate overall campaign structure."""
        validation_results = {
            'url_exclusions': self.validate_url_exclusions(campaign_config.get('url_exclusions', [])),
            'geo_targeting': self.validate_geo_targeting(campaign_config.get('geo_targeting', {})),
            'asset_requirements': self.validate_asset_requirements(campaign_config.get('asset_counts', {})),
            'campaign_naming': self.validate_campaign_naming(campaign_config.get('campaign_name', '')),
            'budget_settings': self.validate_budget_settings(campaign_config.get('budget_settings', {})),
            'tcpa_settings': self.validate_tcpa_settings(campaign_config.get('tcpa_settings', {}))
        }
        
        # Overall validation
        all_valid = all(result['valid'] for result in validation_results.values())
        
        # Collect all issues and warnings
        all_issues = []
        all_warnings = []
        
        for category, result in validation_results.items():
            all_issues.extend([f"{category}: {issue}" for issue in result.get('issues', [])])
            all_warnings.extend([f"{category}: {warning}" for warning in result.get('warnings', [])])
        
        return {
            'valid': all_valid,
            'issues': all_issues,
            'warnings': all_warnings,
            'details': validation_results,
            'summary': {
                'total_checks': len(validation_results),
                'passed_checks': sum(1 for result in validation_results.values() if result['valid']),
                'failed_checks': sum(1 for result in validation_results.values() if not result['valid'])
            }
        }
    
    def generate_validation_report(self, campaign_config: Dict) -> str:
        """Generate HTML validation report."""
        validation = self.validate_campaign_structure(campaign_config)
        
        html = '<div class="baseline-validation-report">'
        html += '<h5 class="text-primary mb-4">🔍 Baseline Validation Report</h5>'
        
        # Overall status
        status_class = 'success' if validation['valid'] else 'danger'
        status_icon = '✅' if validation['valid'] else '❌'
        
        html += f'''
        <div class="alert alert-{status_class} mb-4">
            <h6 class="mb-2">{status_icon} Overall Validation Status</h6>
            <p class="mb-1"><strong>Status:</strong> {'PASSED' if validation['valid'] else 'FAILED'}</p>
            <p class="mb-1"><strong>Checks Passed:</strong> {validation['summary']['passed_checks']}/{validation['summary']['total_checks']}</p>
            <p class="mb-0"><strong>Issues Found:</strong> {len(validation['issues'])}</p>
        </div>
        '''
        
        # Issues section
        if validation['issues']:
            html += '''
            <div class="card mb-3 border-danger">
                <div class="card-header bg-danger text-white">
                    <h6 class="mb-0">❌ Critical Issues</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
            '''
            for issue in validation['issues']:
                html += f'<li>• {issue}</li>'
            html += '</ul></div></div>'
        
        # Warnings section
        if validation['warnings']:
            html += '''
            <div class="card mb-3 border-warning">
                <div class="card-header bg-warning text-dark">
                    <h6 class="mb-0">⚠️ Warnings</h6>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled mb-0">
            '''
            for warning in validation['warnings']:
                html += f'<li>• {warning}</li>'
            html += '</ul></div></div>'
        
        # Detailed results
        html += '''
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0">📋 Detailed Validation Results</h6>
            </div>
            <div class="card-body">
        '''
        
        for category, result in validation['details'].items():
            category_icon = '✅' if result['valid'] else '❌'
            category_class = 'success' if result['valid'] else 'danger'
            
            html += f'''
            <div class="row mb-3">
                <div class="col-md-3">
                    <span class="badge bg-{category_class}">{category_icon} {category.replace('_', ' ').title()}</span>
                </div>
                <div class="col-md-9">
                    <small class="text-muted">
                        {'Valid' if result['valid'] else f"Issues: {len(result.get('issues', []))}"}
                    </small>
                </div>
            </div>
            '''
        
        html += '</div></div>'
        html += '</div>'
        
        return html
    
    def get_required_exclusions(self) -> List[str]:
        """Get list of required URL exclusions."""
        return self.required_exclusions.copy()
    
    def get_asset_requirements(self) -> Dict:
        """Get asset requirements specification."""
        return self.asset_requirements.copy()
    
    def get_geo_requirements(self) -> Dict:
        """Get geo-targeting requirements."""
        return self.geo_requirements.copy()

def validate_campaign_baseline(campaign_config: Dict) -> Dict:
    """Validate campaign baseline requirements."""
    validator = BaselineValidator()
    return validator.validate_campaign_structure(campaign_config)

def generate_baseline_report(campaign_config: Dict) -> str:
    """Generate baseline validation report HTML."""
    validator = BaselineValidator()
    return validator.generate_validation_report(campaign_config)

def get_required_url_exclusions() -> List[str]:
    """Get required URL exclusions."""
    validator = BaselineValidator()
    return validator.get_required_exclusions()

def get_asset_requirements() -> Dict:
    """Get asset requirements."""
    validator = BaselineValidator()
    return validator.get_asset_requirements()

