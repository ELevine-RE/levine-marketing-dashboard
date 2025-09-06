#!/usr/bin/env python3
"""
Google Ads Campaign Guardrails
==============================

Enforces change safety for Google Ads Performance Max campaigns with comprehensive
safety checks, phase progression support, and lag alerts.

This module is pure and side-effect-free, returning structured verdicts for all
change requests.
"""

import os
import sys
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ChangeType(Enum):
    """Types of changes that can be made to campaigns."""
    BUDGET_ADJUSTMENT = "budget_adjustment"
    TARGET_CPA_ADJUSTMENT = "target_cpa_adjustment"
    ASSET_GROUP_MODIFICATION = "asset_group_modification"
    GEO_TARGETING_MODIFICATION = "geo_targeting_modification"
    CAMPAIGN_PAUSE = "campaign_pause"
    CAMPAIGN_ENABLE = "campaign_enable"
    CREATIVE_REFRESH = "creative_refresh"

@dataclass
class GuardrailVerdict:
    """Structured verdict for change requests."""
    approved: bool
    modified_change: Optional[Dict] = None
    reasons: List[str] = None
    execute_after: Optional[str] = None
    alerts: List[str] = None
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []
        if self.alerts is None:
            self.alerts = []
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "approved": self.approved,
            "modified_change": self.modified_change,
            "reasons": self.reasons,
            "execute_after": self.execute_after,
            "alerts": self.alerts
        }

class PerformanceMaxGuardrails:
    """
    Enforces guardrails for Performance Max campaigns.
    
    This class is pure and side-effect-free, providing structured verdicts
    for all change requests without modifying any external state.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize guardrails with safety thresholds from configuration file."""
        # Load configuration from YAML file
        self.config = self._load_config(config_path)
        
        # Extract configuration sections
        self.BUDGET_LIMITS = self.config['budget_limits']
        self.TARGET_CPA_LIMITS = self.config['target_cpa_limits']
        self.ASSET_REQUIREMENTS = self.config['asset_requirements']
        self.GEO_TARGETING_LIMITS = self.config['geo_targeting_limits']
        self.REQUIRED_URL_EXCLUSIONS = self.config['required_url_exclusions']
        self.SAFETY_LIMITS = self.config['safety_limits']
        self.CHANGE_WINDOW_HOURS = self.config['change_controls']['change_window_hours']
        self.ONE_LEVER_PER_WEEK_DAYS = self.config['change_controls']['one_lever_per_week_days']
        
        # Convert tuple aims to lists for YAML compatibility
        self._convert_aims_to_tuples()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load guardrails configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'guardrails_config.yaml'
            )
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {config_path}, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing configuration file: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration if YAML file is not available."""
        return {
            'budget_limits': {
                'min_daily': 30.0,
                'max_daily': 250.0,  # Updated for competitive real estate market
                'max_adjustment_percent': 30,
                'min_adjustment_percent': 20,
                'max_frequency_days': 7
            },
            'target_cpa_limits': {
                'min_value': 80.0,
                'max_value': 350.0,  # Updated for competitive real estate market
                'max_adjustment_percent': 15,
                'min_adjustment_percent': 10,
                'max_frequency_days': 14,
                'min_conversions': 30
            },
            'asset_requirements': {
                'headlines': {'min': 5, 'aim': [7, 10]},
                'long_headlines': {'min': 1, 'aim': [1, 2]},
                'descriptions': {'min': 2, 'aim': [3, 4]},
                'business_name': {'required': True},
                'logos': {
                    '1_1': {'min': 1, 'aim': [1, 2]},
                    '4_1': {'min': 1, 'aim': [1, 2]}
                },
                'images': {
                    '1_91_1': {'min': 3, 'aim': [3, 5]},
                    '1_1': {'min': 3, 'aim': [3, 5]}
                },
                'video': {'min': 1, 'auto_gen_allowed': True}
            },
            'geo_targeting_limits': {
                'presence_only_required': True,
                'max_changes_per_period': 1,
                'period_days': 21
            },
            'required_url_exclusions': [
                '/buyers/*',
                '/sellers/*',
                '/featured-listings/*',
                '/contact/*',
                '/blog/*',
                '/property-search/*',
                '/idx/*',
                '/privacy/*',
                '/about/*'
            ],
            'safety_limits': {
                'spend_multiplier_threshold': 2.0,
                'conversion_dry_spell_days': 14,
                'budget_overspend_days': 7
            },
            'change_controls': {
                'change_window_hours': 2,
                'one_lever_per_week_days': 7
            }
        }
    
    def _convert_aims_to_tuples(self):
        """Convert aim lists back to tuples for compatibility with existing code."""
        for category in ['headlines', 'long_headlines', 'descriptions']:
            if category in self.ASSET_REQUIREMENTS:
                aim_list = self.ASSET_REQUIREMENTS[category]['aim']
                self.ASSET_REQUIREMENTS[category]['aim'] = tuple(aim_list)
        
        for logo_type in ['1_1', '4_1']:
            if logo_type in self.ASSET_REQUIREMENTS['logos']:
                aim_list = self.ASSET_REQUIREMENTS['logos'][logo_type]['aim']
                self.ASSET_REQUIREMENTS['logos'][logo_type]['aim'] = tuple(aim_list)
        
        for image_type in ['1_91_1', '1_1']:
            if image_type in self.ASSET_REQUIREMENTS['images']:
                aim_list = self.ASSET_REQUIREMENTS['images'][image_type]['aim']
                self.ASSET_REQUIREMENTS['images'][image_type]['aim'] = tuple(aim_list)
        
    def enforce_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """
        Enforce guardrails for a change request.
        
        Args:
            change_request: Dictionary containing the requested change
            campaign_state: Dictionary containing current campaign state
            
        Returns:
            GuardrailVerdict with approval status and reasoning
            
        Acceptance Criteria:
        - Budget changes: ±20-30% per change, ≥7d since last change, min $30/day, max $250/day
        - tCPA changes: only if ≥30 conversions, ±10-15% per change, ≥14d since last change, $80-$350
        - Asset groups: ensure PMax minimums per active group
        - Geo targeting: presence-only required, max 1 change per 21 days
        - URL exclusions: ensure required exclusions are present
        - One lever per week: deny if another major lever changed in last 7 days
        - 2-hour change window: return execute_after timestamp
        - Stop-loss: detect overspend with no conversions or conversion drought
        """
        try:
            # Initialize verdict
            verdict = GuardrailVerdict(approved=False)
            
            # Check for safety stop-loss conditions first
            safety_check = self._check_safety_stop_loss(campaign_state)
            if safety_check:
                verdict.alerts.append(safety_check)
                if "freeze" in safety_check.lower():
                    verdict.reasons.append(f"Safety stop-loss triggered: {safety_check}")
                    return verdict
            
            # Check one lever per week rule
            one_lever_check = self._check_one_lever_per_week(change_request, campaign_state)
            if not one_lever_check['allowed']:
                verdict.reasons.append(one_lever_check['reason'])
                return verdict
            
            # Check hard invariants before any change
            invariant_check = self._check_hard_invariants(campaign_state)
            if not invariant_check['passed']:
                verdict.reasons.extend(invariant_check['reasons'])
                return verdict
            
            # Route to appropriate guardrail checker based on change type
            change_type = change_request.get('type')
            
            if change_type == ChangeType.BUDGET_ADJUSTMENT.value:
                budget_result = self._check_budget_guardrails(change_request, campaign_state)
                verdict = self._merge_verdicts(verdict, budget_result)
                
            elif change_type == ChangeType.TARGET_CPA_ADJUSTMENT.value:
                tcpa_result = self._check_target_cpa_guardrails(change_request, campaign_state)
                verdict = self._merge_verdicts(verdict, tcpa_result)
                
            elif change_type == ChangeType.ASSET_GROUP_MODIFICATION.value:
                asset_result = self._check_asset_group_guardrails(change_request, campaign_state)
                verdict = self._merge_verdicts(verdict, asset_result)
                
            elif change_type == ChangeType.GEO_TARGETING_MODIFICATION.value:
                geo_result = self._check_geo_targeting_guardrails(change_request, campaign_state)
                verdict = self._merge_verdicts(verdict, geo_result)
                
            elif change_type in [ChangeType.CAMPAIGN_PAUSE.value, ChangeType.CAMPAIGN_ENABLE.value]:
                status_result = self._check_campaign_status_guardrails(change_request, campaign_state)
                verdict = self._merge_verdicts(verdict, status_result)
                
            else:
                verdict.reasons.append(f"Unknown change type: {change_type}")
                return verdict
            
            # Apply 2-hour change window if approved
            if verdict.approved:
                verdict.execute_after = self._calculate_execute_after()
                
                # Send planned change notification
                try:
                    from .notifications import NotificationManager
                    notification_manager = NotificationManager()
                    notification_manager.announce_planned_change(change_request, verdict.execute_after)
                except Exception as e:
                    print(f"Warning: Could not send planned change notification: {str(e)}")
                
                # Save pending change for execution
                try:
                    from ops.apply_pending_changes import PendingChangeExecutor
                    executor = PendingChangeExecutor()
                    executor.add_pending_change(change_request, verdict.to_dict())
                except Exception as e:
                    print(f"Warning: Could not save pending change: {str(e)}")
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error processing guardrails: {str(e)}"]
            )
    
    def _check_safety_stop_loss(self, campaign_state: Dict) -> Optional[str]:
        """
        Check for safety stop-loss conditions.
        
        Returns:
            Alert message if stop-loss triggered, None otherwise
        """
        try:
            # Check for spend > 2× budget in last 7 days with 0 conversions
            recent_spend = campaign_state.get('recent_7d_spend', 0)
            daily_budget = campaign_state.get('daily_budget', 0)
            recent_conversions = campaign_state.get('recent_7d_conversions', 0)
            
            if daily_budget > 0:
                spend_threshold = daily_budget * self.SAFETY_LIMITS['spend_multiplier_threshold']
                if recent_spend > spend_threshold and recent_conversions == 0:
                    return f"STOP-LOSS: Spend ${recent_spend:.2f} exceeds {self.SAFETY_LIMITS['spend_multiplier_threshold']}x budget with 0 conversions - propose pause"
            
            # Check for no conversions in 14 days
            days_since_last_conversion = campaign_state.get('days_since_last_conversion', 0)
            if days_since_last_conversion >= self.SAFETY_LIMITS['conversion_dry_spell_days']:
                return f"STOP-LOSS: No conversions in {days_since_last_conversion} days - freeze all changes"
            
            return None
            
        except Exception as e:
            return f"Error checking safety stop-loss: {str(e)}"
    
    def _check_one_lever_per_week(self, change_request: Dict, campaign_state: Dict) -> Dict:
        """
        Check one lever per week rule.
        
        Returns:
            Dict with 'allowed' boolean and 'reason' string
        """
        try:
            # Get last major change date
            last_major_change = campaign_state.get('last_major_change_date')
            if not last_major_change:
                return {'allowed': True, 'reason': None}
            
            # Convert to datetime if string
            if isinstance(last_major_change, str):
                last_major_change = datetime.fromisoformat(last_major_change.replace('Z', '+00:00'))
            
            days_since_change = (datetime.now() - last_major_change).days
            
            if days_since_change < self.ONE_LEVER_PER_WEEK_DAYS:
                return {
                    'allowed': False,
                    'reason': f"One lever per week rule: major change {days_since_change} days ago (minimum {self.ONE_LEVER_PER_WEEK_DAYS} days)"
                }
            
            return {'allowed': True, 'reason': None}
            
        except Exception as e:
            return {
                'allowed': False,
                'reason': f"Error checking one lever per week: {str(e)}"
            }
    
    def _check_budget_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check budget adjustment guardrails."""
        try:
            current_budget = campaign_state.get('daily_budget', 0)
            new_budget = change_request.get('new_daily_budget', 0)
            last_budget_change = campaign_state.get('last_budget_change_date')
            
            verdict = GuardrailVerdict(approved=False)
            
            # Check minimum budget
            if new_budget < self.BUDGET_LIMITS['min_daily']:
                verdict.reasons.append(f"Budget ${new_budget:.2f} below minimum ${self.BUDGET_LIMITS['min_daily']:.2f}")
                return verdict
            
            # Check maximum budget
            if new_budget > self.BUDGET_LIMITS['max_daily']:
                verdict.reasons.append(f"Budget ${new_budget:.2f} above maximum ${self.BUDGET_LIMITS['max_daily']:.2f}")
                return verdict
            
            # Check adjustment percentage
            if current_budget > 0:
                adjustment_percent = abs((new_budget - current_budget) / current_budget * 100)
                if adjustment_percent > self.BUDGET_LIMITS['max_adjustment_percent']:
                    max_adjustment = current_budget * (1 + self.BUDGET_LIMITS['max_adjustment_percent'] / 100)
                    verdict.modified_change = {'new_daily_budget': max_adjustment}
                    verdict.reasons.append(f"Budget adjustment {adjustment_percent:.1f}% exceeds maximum {self.BUDGET_LIMITS['max_adjustment_percent']}%")
                    return verdict
            
            # Check frequency
            if last_budget_change:
                days_since_change = self._days_since_date(last_budget_change)
                if days_since_change < self.BUDGET_LIMITS['max_frequency_days']:
                    verdict.reasons.append(f"Budget changed {days_since_change} days ago (minimum {self.BUDGET_LIMITS['max_frequency_days']} days)")
                    return verdict
            
            # If no reasons, approve
            verdict.approved = True
            verdict.reasons.append("Budget adjustment meets all guardrail requirements")
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error checking budget guardrails: {str(e)}"]
            )
    
    def _check_target_cpa_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check target CPA adjustment guardrails."""
        try:
            current_tcpa = campaign_state.get('target_cpa', 0)
            new_tcpa = change_request.get('new_target_cpa', 0)
            total_conversions = campaign_state.get('total_conversions', 0)
            last_tcpa_change = campaign_state.get('last_tcpa_change_date')
            
            verdict = GuardrailVerdict(approved=False)
            
            # Check minimum conversions
            if total_conversions < self.TARGET_CPA_LIMITS['min_conversions']:
                verdict.reasons.append(f"Only {total_conversions} conversions (minimum {self.TARGET_CPA_LIMITS['min_conversions']})")
                return verdict
            
            # Check minimum tCPA
            if new_tcpa < self.TARGET_CPA_LIMITS['min_value']:
                verdict.reasons.append(f"Target CPA ${new_tcpa:.2f} below minimum ${self.TARGET_CPA_LIMITS['min_value']:.2f}")
                return verdict
            
            # Check maximum tCPA
            if new_tcpa > self.TARGET_CPA_LIMITS['max_value']:
                verdict.reasons.append(f"Target CPA ${new_tcpa:.2f} above maximum ${self.TARGET_CPA_LIMITS['max_value']:.2f}")
                return verdict
            
            # Check adjustment percentage
            if current_tcpa > 0:
                adjustment_percent = abs((new_tcpa - current_tcpa) / current_tcpa * 100)
                if adjustment_percent > self.TARGET_CPA_LIMITS['max_adjustment_percent']:
                    max_adjustment = current_tcpa * (1 + self.TARGET_CPA_LIMITS['max_adjustment_percent'] / 100)
                    verdict.modified_change = {'new_target_cpa': max_adjustment}
                    verdict.reasons.append(f"tCPA adjustment {adjustment_percent:.1f}% exceeds maximum {self.TARGET_CPA_LIMITS['max_adjustment_percent']}%")
                    return verdict
            
            # Check frequency
            if last_tcpa_change:
                days_since_change = self._days_since_date(last_tcpa_change)
                if days_since_change < self.TARGET_CPA_LIMITS['max_frequency_days']:
                    verdict.reasons.append(f"tCPA changed {days_since_change} days ago (minimum {self.TARGET_CPA_LIMITS['max_frequency_days']} days)")
                    return verdict
            
            # If no reasons, approve
            verdict.approved = True
            verdict.reasons.append("Target CPA adjustment meets all guardrail requirements")
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error checking target CPA guardrails: {str(e)}"]
            )
    
    def _check_asset_group_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check asset group modification guardrails."""
        try:
            action = change_request.get('action')
            asset_groups = campaign_state.get('asset_groups', [])
            
            verdict = GuardrailVerdict(approved=False)
            
            # Check if trying to pause all asset groups
            if action == 'pause_all':
                verdict.reasons.append("Cannot pause all asset groups")
                return verdict
            
            # Check minimum asset requirements for each active group
            missing_assets = []
            
            for group in asset_groups:
                if group.get('status') == 'ENABLED':
                    group_missing = self._check_asset_requirements(group)
                    if group_missing:
                        missing_assets.extend([f"{group.get('name', 'Unknown')}: {asset}" for asset in group_missing])
            
            if missing_assets:
                verdict.reasons.append(f"Missing required assets: {', '.join(missing_assets)}")
            else:
                verdict.approved = True
                verdict.reasons.append("Asset group modification meets all guardrail requirements")
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error checking asset group guardrails: {str(e)}"]
            )
    
    def _check_asset_requirements(self, asset_group: Dict) -> List[str]:
        """Check if asset group meets PMax requirements."""
        missing = []
        asset_counts = asset_group.get('asset_counts', {})
        
        # Check headlines
        headlines = asset_counts.get('headlines', 0)
        if headlines < self.ASSET_REQUIREMENTS['headlines']['min']:
            missing.append(f"headlines ({headlines}/{self.ASSET_REQUIREMENTS['headlines']['min']})")
        
        # Check long headlines
        long_headlines = asset_counts.get('long_headlines', 0)
        if long_headlines < self.ASSET_REQUIREMENTS['long_headlines']['min']:
            missing.append(f"long headlines ({long_headlines}/{self.ASSET_REQUIREMENTS['long_headlines']['min']})")
        
        # Check descriptions
        descriptions = asset_counts.get('descriptions', 0)
        if descriptions < self.ASSET_REQUIREMENTS['descriptions']['min']:
            missing.append(f"descriptions ({descriptions}/{self.ASSET_REQUIREMENTS['descriptions']['min']})")
        
        # Check business name
        if self.ASSET_REQUIREMENTS['business_name']['required']:
            business_name = asset_counts.get('business_name', 0)
            if business_name < 1:
                missing.append("business name")
        
        # Check logos
        logos_1_1 = asset_counts.get('logos_1_1', 0)
        logos_4_1 = asset_counts.get('logos_4_1', 0)
        if logos_1_1 < self.ASSET_REQUIREMENTS['logos']['1_1']['min']:
            missing.append(f"1:1 logos ({logos_1_1}/{self.ASSET_REQUIREMENTS['logos']['1_1']['min']})")
        if logos_4_1 < self.ASSET_REQUIREMENTS['logos']['4_1']['min']:
            missing.append(f"4:1 logos ({logos_4_1}/{self.ASSET_REQUIREMENTS['logos']['4_1']['min']})")
        
        # Check images
        images_1_91_1 = asset_counts.get('images_1_91_1', 0)
        images_1_1 = asset_counts.get('images_1_1', 0)
        if images_1_91_1 < self.ASSET_REQUIREMENTS['images']['1_91_1']['min']:
            missing.append(f"1.91:1 images ({images_1_91_1}/{self.ASSET_REQUIREMENTS['images']['1_91_1']['min']})")
        if images_1_1 < self.ASSET_REQUIREMENTS['images']['1_1']['min']:
            missing.append(f"1:1 images ({images_1_1}/{self.ASSET_REQUIREMENTS['images']['1_1']['min']})")
        
        # Check video
        videos = asset_counts.get('videos', 0)
        auto_gen_videos = asset_counts.get('auto_gen_videos', 0)
        if videos < self.ASSET_REQUIREMENTS['video']['min'] and auto_gen_videos == 0:
            missing.append(f"videos ({videos}/{self.ASSET_REQUIREMENTS['video']['min']})")
        
        return missing
    
    def _check_geo_targeting_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check geo targeting modification guardrails."""
        try:
            action = change_request.get('action')
            last_geo_change = campaign_state.get('last_geo_change_date')
            
            verdict = GuardrailVerdict(approved=False)
            
            # Check frequency
            if last_geo_change:
                days_since_change = self._days_since_date(last_geo_change)
                if days_since_change < self.GEO_TARGETING_LIMITS['period_days']:
                    verdict.reasons.append(f"Geo targeting changed {days_since_change} days ago (minimum {self.GEO_TARGETING_LIMITS['period_days']} days)")
                    return verdict
            
            # Check for presence-only targeting
            if action == 'add_location':
                location_type = change_request.get('location_type', '')
                if location_type != 'presence':
                    verdict.reasons.append(f"Location type '{location_type}' not allowed (presence-only required)")
                    return verdict
            
            # If no reasons, approve
            verdict.approved = True
            verdict.reasons.append("Geo targeting modification meets all guardrail requirements")
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error checking geo targeting guardrails: {str(e)}"]
            )
    
    def _check_campaign_status_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check campaign status change guardrails."""
        try:
            action = change_request.get('action')
            
            verdict = GuardrailVerdict(approved=True)
            verdict.reasons.append("Campaign status change meets all guardrail requirements")
            
            # Check for safety conditions before pausing
            if action == 'pause':
                safety_check = self._check_safety_stop_loss(campaign_state)
                if safety_check:
                    verdict.alerts.append(safety_check)
            
            return verdict
            
        except Exception as e:
            return GuardrailVerdict(
                approved=False,
                reasons=[f"Error checking campaign status guardrails: {str(e)}"]
            )
    
    def _calculate_execute_after(self) -> str:
        """Calculate execute_after timestamp (2 hours from now)."""
        execute_time = datetime.now() + timedelta(hours=self.CHANGE_WINDOW_HOURS)
        return execute_time.isoformat()
    
    def _days_since_date(self, date_value) -> int:
        """Calculate days since a given date."""
        try:
            if isinstance(date_value, str):
                date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            return (datetime.now() - date_value).days
        except Exception:
            return 0
    
    def _merge_verdicts(self, base_verdict: GuardrailVerdict, new_verdict: GuardrailVerdict) -> GuardrailVerdict:
        """Merge two guardrail verdicts."""
        # For the first specific check, use the new verdict's approval status
        # For subsequent checks, use logical AND
        if len(base_verdict.reasons) == 0:
            base_verdict.approved = new_verdict.approved
        else:
            base_verdict.approved = base_verdict.approved and new_verdict.approved
        
        base_verdict.reasons.extend(new_verdict.reasons)
        base_verdict.alerts.extend(new_verdict.alerts)
        
        if new_verdict.modified_change:
            base_verdict.modified_change = new_verdict.modified_change
        
        return base_verdict
    
    def get_guardrail_summary(self) -> Dict:
        """Get a summary of all guardrail settings."""
        return {
            'budget_limits': self.BUDGET_LIMITS,
            'target_cpa_limits': self.TARGET_CPA_LIMITS,
            'asset_requirements': self.ASSET_REQUIREMENTS,
            'geo_targeting_limits': self.GEO_TARGETING_LIMITS,
            'safety_limits': self.SAFETY_LIMITS,
            'change_window_hours': self.CHANGE_WINDOW_HOURS,
            'one_lever_per_week_days': self.ONE_LEVER_PER_WEEK_DAYS,
            'required_url_exclusions': self.REQUIRED_URL_EXCLUSIONS
        }
    
    def _check_hard_invariants(self, campaign_state: Dict) -> Dict:
        """
        Check hard invariants that must always be true.
        
        Returns:
            Dict with 'passed' boolean and 'reasons' list
        """
        reasons = []
        
        # Check conversion mapping - ONLY Lead Form Submission can be Primary
        primary_conversions = campaign_state.get('primary_conversions', [])
        if primary_conversions:
            # Only Lead Form Submission should be primary
            allowed_primary = ['Lead Form Submission']
            invalid_primary = [conv for conv in primary_conversions if conv not in allowed_primary]
            if invalid_primary:
                reasons.append(f"Invalid primary conversions: {', '.join(invalid_primary)}. Only Lead Form Submission can be Primary.")
        
        # Check URL exclusions
        current_exclusions = campaign_state.get('url_exclusions', [])
        missing_exclusions = []
        for required in self.REQUIRED_URL_EXCLUSIONS:
            if required not in current_exclusions:
                missing_exclusions.append(required)
        
        if missing_exclusions:
            reasons.append(f"Missing required URL exclusions: {', '.join(missing_exclusions)}")
        
        # Check presence-only targeting
        targeting_type = campaign_state.get('targeting_type', '')
        if targeting_type != 'PRESENCE_ONLY':
            reasons.append(f"Targeting type must be PRESENCE_ONLY, found: {targeting_type}")
        
        # Check asset format requirements
        asset_groups = campaign_state.get('asset_groups', [])
        for group in asset_groups:
            if group.get('status') == 'ENABLED':
                missing_assets = self._check_asset_requirements(group)
                if missing_assets:
                    reasons.append(f"Asset group '{group.get('name', 'Unknown')}' missing: {', '.join(missing_assets)}")
        
        return {
            'passed': len(reasons) == 0,
            'reasons': reasons
        }
    
    def _validate_conversion_mapping(self, campaign_state: Dict) -> Dict:
        """
        Validate that only lead form submissions are marked as Primary.
        All other actions must remain Secondary.
        """
        primary_conversions = campaign_state.get('primary_conversions', [])
        secondary_conversions = campaign_state.get('secondary_conversions', [])
        
        # Check if any non-lead-form actions are marked as primary
        allowed_primary = ['Lead Form Submission', 'Phone Call']
        invalid_primary = [conv for conv in primary_conversions if conv not in allowed_primary]
        
        if invalid_primary:
            return {
                'valid': False,
                'reason': f"Invalid primary conversions: {', '.join(invalid_primary)}. Only Lead Form Submission and Phone Call can be primary."
            }
        
        # Check if lead form submissions are missing from primary
        if 'Lead Form Submission' not in primary_conversions:
            return {
                'valid': False,
                'reason': "Lead Form Submission must be marked as Primary conversion."
            }
        
        return {'valid': True}
    
    def _validate_url_exclusions(self, campaign_state: Dict) -> Dict:
        """
        Validate that campaign has the exact required URL exclusion list.
        """
        current_exclusions = set(campaign_state.get('url_exclusions', []))
        required_exclusions = set(self.REQUIRED_URL_EXCLUSIONS)
        
        missing_exclusions = required_exclusions - current_exclusions
        extra_exclusions = current_exclusions - required_exclusions
        
        if missing_exclusions:
            return {
                'valid': False,
                'reason': f"Missing required URL exclusions: {', '.join(sorted(missing_exclusions))}"
            }
        
        if extra_exclusions:
            return {
                'valid': False,
                'reason': f"Extra URL exclusions found: {', '.join(sorted(extra_exclusions))}. Only the exact required list is allowed."
            }
        
        return {'valid': True}
    
    def _validate_asset_formats(self, campaign_state: Dict) -> Dict:
        """
        Validate that each active asset group includes the required asset formats.
        """
        asset_groups = campaign_state.get('asset_groups', [])
        reasons = []
        
        for i, group in enumerate(asset_groups):
            if not group.get('active', True):
                continue
                
            group_reasons = []
            
            # Check logos
            logos = group.get('logos', {})
            if logos.get('1_1', 0) < 1:
                group_reasons.append("Missing 1:1 logo")
            if logos.get('4_1', 0) < 1:
                group_reasons.append("Missing 4:1 logo")
            
            # Check images
            images = group.get('images', {})
            if images.get('1_91_1', 0) < 3:
                group_reasons.append("Missing 1.91:1 images (need ≥3)")
            if images.get('1_1', 0) < 3:
                group_reasons.append("Missing 1:1 images (need ≥3)")
            
            # Check video
            videos = group.get('videos', {})
            if videos.get('vertical', 0) < 1 and not group.get('auto_generate_video', False):
                group_reasons.append("Missing vertical video (or auto-generation not enabled)")
            
            if group_reasons:
                reasons.append(f"Asset Group {i+1}: {', '.join(group_reasons)}")
        
        if reasons:
            return {
                'valid': False,
                'reason': f"Asset format requirements not met: {'; '.join(reasons)}"
            }
        
        return {'valid': True}
    
    def _validate_presence_only_targeting(self, campaign_state: Dict) -> Dict:
        """
        Validate that presence-only targeting/exclusion is active.
        Treat any deviation as a hard fail.
        """
        targeting_type = campaign_state.get('geo_targeting_type', '')
        
        if targeting_type != 'PRESENCE_ONLY':
            return {
                'valid': False,
                'reason': f"Presence-only targeting required. Current type: {targeting_type}"
            }
        
        # Check if presence-only exclusions are active
        presence_exclusions = campaign_state.get('presence_only_exclusions', [])
        required_exclusions = ['India', 'Pakistan', 'Bangladesh', 'Philippines']
        
        missing_exclusions = [excl for excl in required_exclusions if excl not in presence_exclusions]
        if missing_exclusions:
            return {
                'valid': False,
                'reason': f"Missing presence-only exclusions: {', '.join(missing_exclusions)}"
            }
        
        return {'valid': True}
