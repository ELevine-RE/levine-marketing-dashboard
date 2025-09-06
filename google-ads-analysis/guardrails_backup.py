#!/usr/bin/env python3
"""
Google Ads Performance Max Campaign Guardrails
============================================

Enforces change guardrails for Google Ads Performance Max campaigns to ensure
safe, controlled modifications with proper safety measures.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_ads_manager import GoogleAdsManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class ChangeType(Enum):
    """Types of changes that can be made to campaigns."""
    BUDGET_ADJUSTMENT = "budget_adjustment"
    TARGET_CPA_ADJUSTMENT = "target_cpa_adjustment"
    ASSET_GROUP_MODIFICATION = "asset_group_modification"
    GEO_TARGETING_MODIFICATION = "geo_targeting_modification"
    CAMPAIGN_PAUSE = "campaign_pause"
    CAMPAIGN_ENABLE = "campaign_enable"

class VerdictType(Enum):
    """Possible verdicts for change requests."""
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"
    DELAYED = "delayed"

@dataclass
class GuardrailVerdict:
    """Structured verdict for change requests."""
    verdict: VerdictType
    reason: str
    modified_request: Optional[Dict] = None
    delay_hours: Optional[int] = None
    safety_alert: Optional[str] = None
    recommendations: List[str] = None

class PerformanceMaxGuardrails:
    """Enforces guardrails for Performance Max campaigns."""
    
    def __init__(self):
        """Initialize the guardrails system."""
        self.manager = GoogleAdsManager()
        
        # Guardrail constants
        self.BUDGET_LIMITS = {
            'min_daily': 30.0,
            'max_daily': 100.0,
            'max_adjustment_percent': 30,
            'min_adjustment_percent': 20,
            'max_frequency_days': 7
        }
        
        self.TARGET_CPA_LIMITS = {
            'min_value': 80.0,
            'max_value': 200.0,
            'max_adjustment_percent': 15,
            'min_adjustment_percent': 10,
            'max_frequency_days': 14,
            'min_conversions': 30
        }
        
        self.ASSET_REQUIREMENTS = {
            'headlines': 5,
            'long_headlines': 1,
            'descriptions': 2,
            'logos': 1,
            'images': 3,
            'videos': 1
        }
        
        self.GEO_TARGETING_LIMITS = {
            'max_changes_per_period': 1,
            'period_days': 21  # 3 weeks
        }
        
        self.SAFETY_LIMITS = {
            'spend_multiplier_threshold': 2.0,
            'conversion_dry_spell_days': 14,
            'budget_overspend_days': 7
        }
        
        self.CHANGE_WINDOW_HOURS = 2
        
    def enforce_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """
        Enforce guardrails for a change request.
        
        Args:
            change_request: Dictionary containing the requested change
            campaign_state: Dictionary containing current campaign state
            
        Returns:
            GuardrailVerdict with approval status and reasoning
        """
        try:
            change_type = change_request.get('type')
            
            # Check for safety stop-loss conditions first
            safety_check = self._check_safety_stop_loss(campaign_state)
            if safety_check:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Safety stop-loss triggered: {safety_check}",
                    safety_alert=safety_check,
                    recommendations=["Review campaign performance", "Check conversion tracking"]
                )
            
            # Route to appropriate guardrail checker
            if change_type == ChangeType.BUDGET_ADJUSTMENT.value:
                return self._check_budget_guardrails(change_request, campaign_state)
            elif change_type == ChangeType.TARGET_CPA_ADJUSTMENT.value:
                return self._check_target_cpa_guardrails(change_request, campaign_state)
            elif change_type == ChangeType.ASSET_GROUP_MODIFICATION.value:
                return self._check_asset_group_guardrails(change_request, campaign_state)
            elif change_type == ChangeType.GEO_TARGETING_MODIFICATION.value:
                return self._check_geo_targeting_guardrails(change_request, campaign_state)
            elif change_type in [ChangeType.CAMPAIGN_PAUSE.value, ChangeType.CAMPAIGN_ENABLE.value]:
                return self._check_campaign_status_guardrails(change_request, campaign_state)
            else:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Unknown change type: {change_type}",
                    recommendations=["Specify a valid change type"]
                )
                
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error processing guardrails: {str(e)}",
                recommendations=["Check request format", "Verify campaign state data"]
            )
    
    def _check_safety_stop_loss(self, campaign_state: Dict) -> Optional[str]:
        """Check for safety stop-loss conditions."""
        try:
            # Check for spend > 2x budget in last 7 days with 0 conversions
            recent_spend = campaign_state.get('recent_7d_spend', 0)
            daily_budget = campaign_state.get('daily_budget', 0)
            recent_conversions = campaign_state.get('recent_7d_conversions', 0)
            
            if daily_budget > 0:
                spend_threshold = daily_budget * self.SAFETY_LIMITS['spend_multiplier_threshold']
                if recent_spend > spend_threshold and recent_conversions == 0:
                    return f"Spend (${recent_spend:.2f}) exceeds {self.SAFETY_LIMITS['spend_multiplier_threshold']}x budget (${daily_budget:.2f}) with 0 conversions"
            
            # Check for no conversions in 14 days
            days_since_last_conversion = campaign_state.get('days_since_last_conversion', 0)
            if days_since_last_conversion >= self.SAFETY_LIMITS['conversion_dry_spell_days']:
                return f"No conversions in {days_since_last_conversion} days (threshold: {self.SAFETY_LIMITS['conversion_dry_spell_days']} days)"
            
            return None
            
        except Exception as e:
            return f"Error checking safety stop-loss: {str(e)}"
    
    def _check_budget_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check budget adjustment guardrails."""
        try:
            current_budget = campaign_state.get('daily_budget', 0)
            new_budget = change_request.get('new_daily_budget', 0)
            last_budget_change = campaign_state.get('last_budget_change_date')
            
            # Check minimum budget
            if new_budget < self.BUDGET_LIMITS['min_daily']:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Budget ${new_budget:.2f} below minimum ${self.BUDGET_LIMITS['min_daily']:.2f}",
                    recommendations=[f"Increase budget to at least ${self.BUDGET_LIMITS['min_daily']:.2f}"]
                )
            
            # Check maximum budget
            if new_budget > self.BUDGET_LIMITS['max_daily']:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Budget ${new_budget:.2f} above maximum ${self.BUDGET_LIMITS['max_daily']:.2f}",
                    recommendations=[f"Reduce budget to at most ${self.BUDGET_LIMITS['max_daily']:.2f}"]
                )
            
            # Check adjustment percentage
            if current_budget > 0:
                adjustment_percent = abs((new_budget - current_budget) / current_budget * 100)
                if adjustment_percent > self.BUDGET_LIMITS['max_adjustment_percent']:
                    max_adjustment = current_budget * (1 + self.BUDGET_LIMITS['max_adjustment_percent'] / 100)
                    return GuardrailVerdict(
                        verdict=VerdictType.MODIFIED,
                        reason=f"Budget adjustment {adjustment_percent:.1f}% exceeds maximum {self.BUDGET_LIMITS['max_adjustment_percent']}%",
                        modified_request={'new_daily_budget': max_adjustment},
                        recommendations=[f"Consider smaller adjustments over time"]
                    )
            
            # Check frequency
            if last_budget_change:
                days_since_change = (datetime.now() - last_budget_change).days
                if days_since_change < self.BUDGET_LIMITS['max_frequency_days']:
                    return GuardrailVerdict(
                        verdict=VerdictType.DELAYED,
                        reason=f"Budget changed {days_since_change} days ago (minimum {self.BUDGET_LIMITS['max_frequency_days']} days)",
                        delay_hours=self.CHANGE_WINDOW_HOURS,
                        recommendations=["Wait for frequency period to expire"]
                    )
            
            # All checks passed
            return GuardrailVerdict(
                verdict=VerdictType.APPROVED,
                reason="Budget adjustment meets all guardrail requirements",
                recommendations=["Monitor performance after adjustment"]
            )
            
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error checking budget guardrails: {str(e)}",
                recommendations=["Verify budget data format"]
            )
    
    def _check_target_cpa_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check target CPA adjustment guardrails."""
        try:
            current_tcpa = campaign_state.get('target_cpa', 0)
            new_tcpa = change_request.get('new_target_cpa', 0)
            total_conversions = campaign_state.get('total_conversions', 0)
            last_tcpa_change = campaign_state.get('last_tcpa_change_date')
            
            # Check minimum conversions
            if total_conversions < self.TARGET_CPA_LIMITS['min_conversions']:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Only {total_conversions} conversions (minimum {self.TARGET_CPA_LIMITS['min_conversions']})",
                    recommendations=["Wait for more conversion data before adjusting tCPA"]
                )
            
            # Check minimum tCPA
            if new_tcpa < self.TARGET_CPA_LIMITS['min_value']:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Target CPA ${new_tcpa:.2f} below minimum ${self.TARGET_CPA_LIMITS['min_value']:.2f}",
                    recommendations=[f"Increase target CPA to at least ${self.TARGET_CPA_LIMITS['min_value']:.2f}"]
                )
            
            # Check maximum tCPA
            if new_tcpa > self.TARGET_CPA_LIMITS['max_value']:
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason=f"Target CPA ${new_tcpa:.2f} above maximum ${self.TARGET_CPA_LIMITS['max_value']:.2f}",
                    recommendations=[f"Reduce target CPA to at most ${self.TARGET_CPA_LIMITS['max_value']:.2f}"]
                )
            
            # Check adjustment percentage
            if current_tcpa > 0:
                adjustment_percent = abs((new_tcpa - current_tcpa) / current_tcpa * 100)
                if adjustment_percent > self.TARGET_CPA_LIMITS['max_adjustment_percent']:
                    max_adjustment = current_tcpa * (1 + self.TARGET_CPA_LIMITS['max_adjustment_percent'] / 100)
                    return GuardrailVerdict(
                        verdict=VerdictType.MODIFIED,
                        reason=f"tCPA adjustment {adjustment_percent:.1f}% exceeds maximum {self.TARGET_CPA_LIMITS['max_adjustment_percent']}%",
                        modified_request={'new_target_cpa': max_adjustment},
                        recommendations=["Consider smaller adjustments over time"]
                    )
            
            # Check frequency
            if last_tcpa_change:
                days_since_change = (datetime.now() - last_tcpa_change).days
                if days_since_change < self.TARGET_CPA_LIMITS['max_frequency_days']:
                    return GuardrailVerdict(
                        verdict=VerdictType.DELAYED,
                        reason=f"tCPA changed {days_since_change} days ago (minimum {self.TARGET_CPA_LIMITS['max_frequency_days']} days)",
                        delay_hours=self.CHANGE_WINDOW_HOURS,
                        recommendations=["Wait for frequency period to expire"]
                    )
            
            # All checks passed
            return GuardrailVerdict(
                verdict=VerdictType.APPROVED,
                reason="Target CPA adjustment meets all guardrail requirements",
                recommendations=["Monitor conversion performance after adjustment"]
            )
            
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error checking target CPA guardrails: {str(e)}",
                recommendations=["Verify target CPA data format"]
            )
    
    def _check_asset_group_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check asset group modification guardrails."""
        try:
            action = change_request.get('action')
            asset_groups = campaign_state.get('asset_groups', [])
            
            # Check if trying to pause all asset groups
            if action == 'pause_all':
                return GuardrailVerdict(
                    verdict=VerdictType.REJECTED,
                    reason="Cannot pause all asset groups",
                    recommendations=["Keep at least one asset group active", "Pause individual groups instead"]
                )
            
            # Check minimum asset requirements for each group
            for group in asset_groups:
                if group.get('status') == 'ENABLED':
                    asset_counts = group.get('asset_counts', {})
                    
                    # Check headlines
                    if asset_counts.get('headlines', 0) < self.ASSET_REQUIREMENTS['headlines']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' has insufficient headlines ({asset_counts.get('headlines', 0)}/{self.ASSET_REQUIREMENTS['headlines']})",
                            recommendations=["Add more headlines to meet minimum requirements"]
                        )
                    
                    # Check long headlines
                    if asset_counts.get('long_headlines', 0) < self.ASSET_REQUIREMENTS['long_headlines']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' missing long headline",
                            recommendations=["Add a long headline to meet requirements"]
                        )
                    
                    # Check descriptions
                    if asset_counts.get('descriptions', 0) < self.ASSET_REQUIREMENTS['descriptions']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' has insufficient descriptions ({asset_counts.get('descriptions', 0)}/{self.ASSET_REQUIREMENTS['descriptions']})",
                            recommendations=["Add more descriptions to meet minimum requirements"]
                        )
                    
                    # Check logos
                    if asset_counts.get('logos', 0) < self.ASSET_REQUIREMENTS['logos']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' missing logo",
                            recommendations=["Add a logo to meet requirements"]
                        )
                    
                    # Check images
                    if asset_counts.get('images', 0) < self.ASSET_REQUIREMENTS['images']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' has insufficient images ({asset_counts.get('images', 0)}/{self.ASSET_REQUIREMENTS['images']})",
                            recommendations=["Add more images to meet minimum requirements"]
                        )
                    
                    # Check videos
                    if asset_counts.get('videos', 0) < self.ASSET_REQUIREMENTS['videos']:
                        return GuardrailVerdict(
                            verdict=VerdictType.REJECTED,
                            reason=f"Asset group '{group.get('name')}' missing video",
                            recommendations=["Add a video to meet requirements"]
                        )
            
            # All checks passed
            return GuardrailVerdict(
                verdict=VerdictType.APPROVED,
                reason="Asset group modification meets all guardrail requirements",
                recommendations=["Monitor asset performance after changes"]
            )
            
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error checking asset group guardrails: {str(e)}",
                recommendations=["Verify asset group data format"]
            )
    
    def _check_geo_targeting_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check geo targeting modification guardrails."""
        try:
            action = change_request.get('action')
            last_geo_change = campaign_state.get('last_geo_change_date')
            
            # Check frequency
            if last_geo_change:
                days_since_change = (datetime.now() - last_geo_change).days
                if days_since_change < self.GEO_TARGETING_LIMITS['period_days']:
                    return GuardrailVerdict(
                        verdict=VerdictType.DELAYED,
                        reason=f"Geo targeting changed {days_since_change} days ago (minimum {self.GEO_TARGETING_LIMITS['period_days']} days)",
                        delay_hours=self.CHANGE_WINDOW_HOURS,
                        recommendations=["Wait for frequency period to expire"]
                    )
            
            # Check for presence-only targeting
            if action == 'add_location':
                location_type = change_request.get('location_type', '')
                if location_type != 'presence':
                    return GuardrailVerdict(
                        verdict=VerdictType.REJECTED,
                        reason=f"Location type '{location_type}' not allowed (presence-only required)",
                        recommendations=["Use presence-only targeting for all locations"]
                    )
            
            # All checks passed
            return GuardrailVerdict(
                verdict=VerdictType.APPROVED,
                reason="Geo targeting modification meets all guardrail requirements",
                recommendations=["Monitor performance in new locations"]
            )
            
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error checking geo targeting guardrails: {str(e)}",
                recommendations=["Verify geo targeting data format"]
            )
    
    def _check_campaign_status_guardrails(self, change_request: Dict, campaign_state: Dict) -> GuardrailVerdict:
        """Check campaign status change guardrails."""
        try:
            action = change_request.get('action')
            current_status = campaign_state.get('status', '')
            
            # Check for safety conditions before pausing
            if action == 'pause':
                safety_check = self._check_safety_stop_loss(campaign_state)
                if safety_check:
                    return GuardrailVerdict(
                        verdict=VerdictType.APPROVED,
                        reason=f"Campaign pause approved due to safety conditions: {safety_check}",
                        safety_alert=safety_check,
                        recommendations=["Review campaign performance", "Check conversion tracking"]
                    )
            
            # All checks passed
            return GuardrailVerdict(
                verdict=VerdictType.APPROVED,
                reason="Campaign status change meets all guardrail requirements",
                recommendations=["Monitor campaign performance after status change"]
            )
            
        except Exception as e:
            return GuardrailVerdict(
                verdict=VerdictType.REJECTED,
                reason=f"Error checking campaign status guardrails: {str(e)}",
                recommendations=["Verify campaign status data format"]
            )
    
    def get_guardrail_summary(self) -> Dict:
        """Get a summary of all guardrail settings."""
        return {
            'budget_limits': self.BUDGET_LIMITS,
            'target_cpa_limits': self.TARGET_CPA_LIMITS,
            'asset_requirements': self.ASSET_REQUIREMENTS,
            'geo_targeting_limits': self.GEO_TARGETING_LIMITS,
            'safety_limits': self.SAFETY_LIMITS,
            'change_window_hours': self.CHANGE_WINDOW_HOURS
        }

def main():
    """Test the guardrails system."""
    console.print(Panel("🛡️ Performance Max Campaign Guardrails", style="bold blue"))
    
    # Initialize guardrails
    guardrails = PerformanceMaxGuardrails()
    
    # Example test cases
    test_cases = [
        {
            'name': 'Budget Increase (Valid)',
            'change_request': {
                'type': 'budget_adjustment',
                'new_daily_budget': 50.0
            },
            'campaign_state': {
                'daily_budget': 40.0,
                'last_budget_change_date': datetime.now() - timedelta(days=10),
                'recent_7d_spend': 280.0,
                'recent_7d_conversions': 5,
                'days_since_last_conversion': 2
            }
        },
        {
            'name': 'Budget Increase (Too Large)',
            'change_request': {
                'type': 'budget_adjustment',
                'new_daily_budget': 80.0
            },
            'campaign_state': {
                'daily_budget': 40.0,
                'last_budget_change_date': datetime.now() - timedelta(days=10),
                'recent_7d_spend': 280.0,
                'recent_7d_conversions': 5,
                'days_since_last_conversion': 2
            }
        },
        {
            'name': 'Target CPA (Insufficient Conversions)',
            'change_request': {
                'type': 'target_cpa_adjustment',
                'new_target_cpa': 100.0
            },
            'campaign_state': {
                'target_cpa': 90.0,
                'total_conversions': 20,
                'last_tcpa_change_date': datetime.now() - timedelta(days=20),
                'recent_7d_spend': 280.0,
                'recent_7d_conversions': 5,
                'days_since_last_conversion': 2
            }
        },
        {
            'name': 'Safety Stop-Loss (High Spend, No Conversions)',
            'change_request': {
                'type': 'budget_adjustment',
                'new_daily_budget': 50.0
            },
            'campaign_state': {
                'daily_budget': 40.0,
                'recent_7d_spend': 100.0,  # 2.5x budget
                'recent_7d_conversions': 0,
                'days_since_last_conversion': 10
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        console.print(f"\n[bold cyan]Testing: {test_case['name']}[/bold cyan]")
        
        verdict = guardrails.enforce_guardrails(
            test_case['change_request'],
            test_case['campaign_state']
        )
        
        console.print(f"Verdict: {verdict.verdict.value.upper()}")
        console.print(f"Reason: {verdict.reason}")
        
        if verdict.modified_request:
            console.print(f"Modified Request: {verdict.modified_request}")
        
        if verdict.delay_hours:
            console.print(f"Delay: {verdict.delay_hours} hours")
        
        if verdict.safety_alert:
            console.print(f"Safety Alert: {verdict.safety_alert}")
        
        if verdict.recommendations:
            console.print("Recommendations:")
            for rec in verdict.recommendations:
                console.print(f"  • {rec}")

if __name__ == "__main__":
    main()
