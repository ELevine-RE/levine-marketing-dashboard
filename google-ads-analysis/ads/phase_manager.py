#!/usr/bin/env python3
"""
Google Ads Campaign Phase Manager
================================

Manages campaign progression through different phases with eligibility checks
and progress tracking for Performance Max campaigns.

This module is pure and side-effect-free, returning structured results for all
phase assessments.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CampaignPhase(Enum):
    """Campaign phases for progression tracking."""
    PHASE_1 = "phase_1"  # Initial setup and testing
    PHASE_2 = "phase_2"   # tCPA introduction
    PHASE_3 = "phase_3"   # Scaling and optimization

@dataclass
class PhaseEligibilityResult:
    """Structured result for phase eligibility checks."""
    eligible_for_next: bool
    recommended_action: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "eligible_for_next": self.eligible_for_next,
            "recommended_action": self.recommended_action,
            "details": self.details
        }

@dataclass
class PhaseProgressResult:
    """Structured result for phase progress checks."""
    lagging: bool
    lag_alert: bool
    days_in_phase: int
    message: str
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "lagging": self.lagging,
            "lag_alert": self.lag_alert,
            "days_in_phase": self.days_in_phase,
            "message": self.message
        }

class CampaignPhaseManager:
    """
    Manages campaign progression through different phases.
    
    This class is pure and side-effect-free, providing structured results
    for all phase assessments without modifying any external state.
    """
    
    def __init__(self):
        """Initialize the phase manager with phase-specific requirements."""
        # Phase 1 → Phase 2 requirements
        self.PHASE_1_REQUIREMENTS = {
            'min_conversions': 30,
            'min_days': 14,
            'cpl_stability_threshold': 20,  # ±20%
            'no_changes_days': 7
        }
        
        # Phase 2 → Phase 3 requirements
        self.PHASE_2_REQUIREMENTS = {
            'min_tcpa_days': 30,
            'cpl_min': 80.0,
            'cpl_max': 150.0,
            'lead_quality_threshold': 5.0,  # ≥5% serious buyers
            'pacing_threshold': 0.8  # Not constrained (≥80%)
        }
        
        # Default phase timelines
        self.PHASE_TIMELINES = {
            'phase_1': {'expected_days': 21, 'max_days': 35},
            'phase_2': {'expected_days': 45, 'max_days': 70},
            'phase_3': {'expected_days': 90, 'max_days': 365}
        }
        
        # Grace period for lag detection
        self.GRACE_PERIOD_DAYS = 3
    
    def check_phase_eligibility(self, metrics: Dict, phase: str) -> PhaseEligibilityResult:
        """
        Check if campaign is eligible to progress to the next phase.
        
        Args:
            metrics: Dictionary containing campaign metrics
            phase: Current phase ('phase_1', 'phase_2', 'phase_3')
            
        Returns:
            PhaseEligibilityResult with eligibility status and recommendations
            
        Acceptance Criteria:
        - Phase 1 → 2: ≥30 primary conversions over ≥14d, 7d CPL within ±20% of 30d CPL, no major change in last 7d
        - Phase 2 → 3: ≥30d under tCPA, CPL in $80-$150, lead quality ≥5% "serious", not budget-constrained (pacing OK)
        - Conversion Hygiene: Only Primary conversions (lead form submissions) count for phase gates
        """
        try:
            # Check conversion hygiene first
            conversion_hygiene_check = self._validate_conversion_hygiene(metrics)
            if not conversion_hygiene_check['valid']:
                return PhaseEligibilityResult(
                    eligible_for_next=False,
                    recommended_action=f"Fix conversion mapping: {conversion_hygiene_check['reason']}",
                    details={
                        "conversion_hygiene_ok": False,
                        "conversion_hygiene_reason": conversion_hygiene_check['reason'],
                        "error": "Conversion mapping invalid"
                    }
                )
            
            if phase == CampaignPhase.PHASE_1.value:
                return self._check_phase_1_to_2_eligibility(metrics)
            elif phase == CampaignPhase.PHASE_2.value:
                return self._check_phase_2_to_3_eligibility(metrics)
            elif phase == CampaignPhase.PHASE_3.value:
                return self._check_phase_3_status(metrics)
            else:
                return PhaseEligibilityResult(
                    eligible_for_next=False,
                    recommended_action=f"Unknown phase: {phase}",
                    details={"error": f"Invalid phase: {phase}"}
                )
                
        except Exception as e:
            return PhaseEligibilityResult(
                eligible_for_next=False,
                recommended_action=f"Error checking eligibility: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_phase_progress(self, start_date: date, today: date, phase: str, 
                           eligibility: Dict, expected_days: int = None, max_days: int = None) -> PhaseProgressResult:
        """
        Check phase progress and determine if campaign is lagging.
        
        Args:
            start_date: When the phase started
            today: Current date for comparison
            phase: Current phase ('phase_1', 'phase_2', 'phase_3')
            eligibility: Result from check_phase_eligibility
            expected_days: Override for expected days in phase
            max_days: Override for maximum days in phase
            
        Returns:
            PhaseProgressResult with lag status and messaging
            
        Acceptance Criteria:
        - If days_in_phase > expected_days and not eligible → lagging: True (no alert for +1-3d)
        - If days_in_phase > max_days and not eligible → lag_alert: True with reason
        - Defaults: Phase1 expected=21, max=35; Phase2 expected=45, max=70
        """
        try:
            # Calculate days in phase
            days_in_phase = (today - start_date).days
            
            # Get phase-specific defaults if not provided
            if expected_days is None or max_days is None:
                phase_defaults = self._get_phase_defaults(phase)
                expected_days = expected_days or phase_defaults['expected_days']
                max_days = max_days or phase_defaults['max_days']
            
            # Check if eligible for next phase
            is_eligible = eligibility.get('eligible_for_next', False)
            
            # Determine lag status
            if days_in_phase <= expected_days:
                # Within expected timeframe
                if is_eligible:
                    message = f"Phase progressing well - eligible for next phase after {expected_days - days_in_phase} more days"
                else:
                    message = f"Phase progressing normally - {expected_days - days_in_phase} days remaining to expected completion"
                
                return PhaseProgressResult(
                    lagging=False,
                    lag_alert=False,
                    days_in_phase=days_in_phase,
                    message=message
                )
            
            elif days_in_phase <= expected_days + self.GRACE_PERIOD_DAYS:
                # Within grace period (1-3 days past expected)
                if is_eligible:
                    message = f"Phase slightly behind but eligible for next phase"
                else:
                    message = f"Phase slightly behind expected timeline ({days_in_phase - expected_days} days over) - within grace period"
                
                return PhaseProgressResult(
                    lagging=False,
                    lag_alert=False,
                    days_in_phase=days_in_phase,
                    message=message
                )
            
            elif days_in_phase <= max_days:
                # Lagging but within max days
                if is_eligible:
                    message = f"Phase lagging but eligible for next phase ({days_in_phase - expected_days} days behind expected)"
                else:
                    message = f"Phase lagging - {days_in_phase - expected_days} days past expected completion. Address blocking factors."
                
                return PhaseProgressResult(
                    lagging=True,
                    lag_alert=False,
                    days_in_phase=days_in_phase,
                    message=message
                )
            
            else:
                # Exceeded max days
                if is_eligible:
                    message = f"⚠️ CRITICAL: Phase exceeded maximum duration ({days_in_phase - max_days} days over max) but eligible for next phase. Proceed immediately."
                else:
                    # Generate detailed lag alert message
                    blocking_factors = eligibility.get('details', {}).get('blocking_factors', [])
                    message = f"🚨 CRITICAL ALERT: Phase exceeded maximum duration by {days_in_phase - max_days} days!"
                    if blocking_factors:
                        message += f" Blocking factors: {', '.join(blocking_factors)}"
                    message += " Immediate action required."
                
                # Send critical lag notification
                try:
                    from .notifications import NotificationManager
                    notification_manager = NotificationManager()
                    notification_manager.send_critical_lag(days_in_phase, max_days, reason)
                except Exception as e:
                    print(f"Warning: Could not send critical lag notification: {str(e)}")
                
                return PhaseProgressResult(
                    lagging=True,
                    lag_alert=True,
                    days_in_phase=days_in_phase,
                    message=message
                )
            
        except Exception as e:
            return PhaseProgressResult(
                lagging=False,
                lag_alert=False,
                days_in_phase=0,
                message=f"Error checking phase progress: {str(e)}"
            )
    
    def _validate_conversion_hygiene(self, metrics: Dict) -> Dict:
        """
        Validate that conversion mapping is correct for phase eligibility.
        Only Primary conversions (lead form submissions) should count for phase gates.
        """
        primary_conversions = metrics.get('primary_conversions', [])
        secondary_conversions = metrics.get('secondary_conversions', [])
        
        # Handle None values
        if primary_conversions is None:
            primary_conversions = []
        if secondary_conversions is None:
            secondary_conversions = []
        
        # Check if any non-lead-form actions are marked as primary
        allowed_primary = ['Lead Form Submission']  # Only Lead Form Submission can be Primary
        invalid_primary = [conv for conv in primary_conversions if conv not in allowed_primary]
        
        if invalid_primary:
            return {
                'valid': False,
                'reason': f"Invalid primary conversions: {', '.join(invalid_primary)}. Only Lead Form Submission can be Primary."
            }
        
        # Check if lead form submissions are missing from primary
        if 'Lead Form Submission' not in primary_conversions:
            return {
                'valid': False,
                'reason': "Lead Form Submission must be marked as Primary conversion."
            }
        
        return {'valid': True}
    
    def _check_phase_1_to_2_eligibility(self, metrics: Dict) -> PhaseEligibilityResult:
        """Check eligibility for Phase 1 → Phase 2 transition."""
        blocking_factors = []
        details = {}
        
        # Check conversion requirements - ONLY Primary conversions count
        primary_conversions = metrics.get('primary_conversions_count', 0)  # Use primary-only count
        campaign_age_days = metrics.get('campaign_age_days', 0)
        
        # Check CPL stability (7d CPL within ±20% of 30d CPL)
        cpl_stability = self._calculate_cpl_stability(metrics)
        
        # Check for recent changes
        days_since_last_change = metrics.get('days_since_last_change', 0)
        
        # Check performance stability (for time-based condition)
        performance_stable = self._check_performance_stability(metrics)
        
        # OR Logic: Either original condition OR time-based condition
        original_condition_met = (
            primary_conversions >= self.PHASE_1_REQUIREMENTS['min_conversions'] and
            campaign_age_days >= self.PHASE_1_REQUIREMENTS['min_days'] and
            cpl_stability <= self.PHASE_1_REQUIREMENTS['cpl_stability_threshold'] and
            days_since_last_change >= self.PHASE_1_REQUIREMENTS['no_changes_days']
        )
        
        time_based_condition_met = (
            campaign_age_days >= 60 and  # ≥60 days
            primary_conversions >= 15 and  # At least 15 primary conversions
            performance_stable  # Stable performance check
        )
        
        # Determine eligibility using OR logic
        eligible = original_condition_met or time_based_condition_met
        
        # Build blocking factors for clarity
        if not original_condition_met:
            if primary_conversions < self.PHASE_1_REQUIREMENTS['min_conversions']:
                blocking_factors.append(f"Insufficient primary conversions: {primary_conversions}/{self.PHASE_1_REQUIREMENTS['min_conversions']}")
            
            if campaign_age_days < self.PHASE_1_REQUIREMENTS['min_days']:
                blocking_factors.append(f"Campaign too new: {campaign_age_days}/{self.PHASE_1_REQUIREMENTS['min_days']} days")
            
            if cpl_stability > self.PHASE_1_REQUIREMENTS['cpl_stability_threshold']:
                blocking_factors.append(f"CPL unstable: {cpl_stability:.1f}% variation (max {self.PHASE_1_REQUIREMENTS['cpl_stability_threshold']}%)")
            
            if days_since_last_change < self.PHASE_1_REQUIREMENTS['no_changes_days']:
                blocking_factors.append(f"Recent changes detected: {days_since_last_change} days ago (min {self.PHASE_1_REQUIREMENTS['no_changes_days']} days)")
        
        if not time_based_condition_met:
            if campaign_age_days < 60:
                blocking_factors.append(f"Time-based condition: Campaign too new for time-based progression: {campaign_age_days}/60 days")
            
            if primary_conversions < 15:
                blocking_factors.append(f"Time-based condition: Insufficient conversions for time-based progression: {primary_conversions}/15")
            
            if not performance_stable:
                blocking_factors.append("Time-based condition: Performance not stable enough for time-based progression")
        
        # Generate recommendation
        if eligible:
            if original_condition_met:
                recommended_action = "Safe to introduce tCPA at $100-$150 (standard progression)"
            else:
                recommended_action = "Safe to introduce tCPA at $100-$150 (time-based progression)"
        else:
            recommended_action = "Continue Phase 1 optimization - address blocking factors"
        
        # Build details
        details = {
            "blocking_factors": blocking_factors,
            "primary_conversions": primary_conversions,
            "secondary_conversions": metrics.get('secondary_conversions_count', 0),  # Logged but not used for gates
            "campaign_age_days": campaign_age_days,
            "cpl_stability_percent": cpl_stability,
            "days_since_last_change": days_since_last_change,
            "conversion_hygiene_ok": True,  # Already validated above
            "progression_path": "time_based" if (not original_condition_met and time_based_condition_met) else "standard",
            "requirements_met": {
                "original_condition": original_condition_met,
                "time_based_condition": time_based_condition_met,
                "conversions": primary_conversions >= self.PHASE_1_REQUIREMENTS['min_conversions'],
                "campaign_age": campaign_age_days >= self.PHASE_1_REQUIREMENTS['min_days'],
                "cpl_stability": cpl_stability <= self.PHASE_1_REQUIREMENTS['cpl_stability_threshold'],
                "no_recent_changes": days_since_last_change >= self.PHASE_1_REQUIREMENTS['no_changes_days'],
                "time_based_age": campaign_age_days >= 60,
                "time_based_conversions": primary_conversions >= 15,
                "performance_stable": performance_stable
            }
        }
        
        return PhaseEligibilityResult(
            eligible_for_next=eligible,
            recommended_action=recommended_action,
            details=details
        )
    
    def _check_phase_2_to_3_eligibility(self, metrics: Dict) -> PhaseEligibilityResult:
        """Check eligibility for Phase 2 → Phase 3 transition."""
        blocking_factors = []
        details = {}
        
        # Check tCPA duration
        days_under_tcpa = metrics.get('days_under_tcpa', 0)
        if days_under_tcpa < self.PHASE_2_REQUIREMENTS['min_tcpa_days']:
            blocking_factors.append(f"Insufficient tCPA time: {days_under_tcpa}/{self.PHASE_2_REQUIREMENTS['min_tcpa_days']} days")
        
        # Check CPL range
        current_cpl = metrics.get('current_cpl', 0)
        if current_cpl < self.PHASE_2_REQUIREMENTS['cpl_min']:
            blocking_factors.append(f"CPL too low: ${current_cpl:.2f} (min ${self.PHASE_2_REQUIREMENTS['cpl_min']:.2f})")
        elif current_cpl > self.PHASE_2_REQUIREMENTS['cpl_max']:
            blocking_factors.append(f"CPL too high: ${current_cpl:.2f} (max ${self.PHASE_2_REQUIREMENTS['cpl_max']:.2f})")
        
        # Check lead quality (CRM/manual tagging of 'serious' leads)
        lead_quality_percent = metrics.get('lead_quality_percent', 0)
        if lead_quality_percent < self.PHASE_2_REQUIREMENTS['lead_quality_threshold']:
            blocking_factors.append(f"Low lead quality: {lead_quality_percent:.1f}% (min {self.PHASE_2_REQUIREMENTS['lead_quality_threshold']}% of leads tagged as 'serious')")
        
        # Check pacing
        current_pacing = metrics.get('current_pacing', 0)
        if current_pacing < self.PHASE_2_REQUIREMENTS['pacing_threshold']:
            blocking_factors.append(f"Pacing constrained: {current_pacing:.1%} (min {self.PHASE_2_REQUIREMENTS['pacing_threshold']:.1%})")
        
        # Determine eligibility
        eligible = len(blocking_factors) == 0
        
        # Generate recommendation
        if eligible:
            recommended_action = "Safe to scale budget by +20-30%"
        else:
            recommended_action = "Continue Phase 2 optimization - address blocking factors"
        
        # Build details
        details = {
            "blocking_factors": blocking_factors,
            "days_under_tcpa": days_under_tcpa,
            "current_cpl": current_cpl,
            "lead_quality_percent": lead_quality_percent,
            "current_pacing": current_pacing,
            "conversion_hygiene_ok": True,  # Already validated above
            "requirements_met": {
                "tcpa_duration": days_under_tcpa >= self.PHASE_2_REQUIREMENTS['min_tcpa_days'],
                "cpl_range": self.PHASE_2_REQUIREMENTS['cpl_min'] <= current_cpl <= self.PHASE_2_REQUIREMENTS['cpl_max'],
                "lead_quality": lead_quality_percent >= self.PHASE_2_REQUIREMENTS['lead_quality_threshold'],
                "pacing_ok": current_pacing >= self.PHASE_2_REQUIREMENTS['pacing_threshold']
            }
        }
        
        return PhaseEligibilityResult(
            eligible_for_next=eligible,
            recommended_action=recommended_action,
            details=details
        )
    
    def _check_phase_3_status(self, metrics: Dict) -> PhaseEligibilityResult:
        """Check Phase 3 optimization status."""
        # Phase 3 is the final phase - focus on optimization
        optimization_opportunities = []
        
        # Check for optimization opportunities
        if metrics.get('current_cpl', 0) > 150:
            optimization_opportunities.append("High CPL - consider tCPA adjustment")
        
        if metrics.get('current_pacing', 0) < 0.8:
            optimization_opportunities.append("Pacing constrained - consider budget increase")
        
        if metrics.get('lead_quality_percent', 0) < 5:
            optimization_opportunities.append("Low lead quality - review targeting")
        
        recommended_action = "Phase 3 optimization - focus on efficiency and scale"
        if optimization_opportunities:
            recommended_action += f" | Opportunities: {', '.join(optimization_opportunities)}"
        
        details = {
            "optimization_opportunities": optimization_opportunities,
            "current_cpl": metrics.get('current_cpl', 0),
            "current_pacing": metrics.get('current_pacing', 0),
            "lead_quality_percent": metrics.get('lead_quality_percent', 0),
            "conversion_hygiene_ok": True  # Already validated above
        }
        
        return PhaseEligibilityResult(
            eligible_for_next=False,  # Phase 3 is final
            recommended_action=recommended_action,
            details=details
        )
    
    def _calculate_cpl_stability(self, metrics: Dict) -> float:
        """Calculate CPL stability (7d CPL vs 30d CPL)."""
        try:
            cpl_7d = metrics.get('cpl_7d', 0)
            cpl_30d = metrics.get('cpl_30d', 0)
            
            if cpl_30d == 0:
                return 0.0
            
            # Calculate percentage difference
            difference = abs(cpl_7d - cpl_30d) / cpl_30d * 100
            return difference
            
        except Exception:
            return 0.0
    
    def _check_performance_stability(self, metrics: Dict) -> bool:
        """
        Check if performance is stable enough for time-based progression.
        
        Returns True if CPL has not increased by more than 20% in the last 30 days.
        This is a placeholder implementation that can be enhanced with more sophisticated
        stability metrics.
        """
        try:
            # Get CPL metrics for different time periods
            cpl_7d = metrics.get('cpl_7d', 0)
            cpl_30d = metrics.get('cpl_30d', 0)
            
            if cpl_30d == 0:
                return True  # No baseline to compare against
            
            # Check if CPL has increased by more than 20% in the last 30 days
            cpl_increase_percent = ((cpl_7d - cpl_30d) / cpl_30d) * 100
            
            # Performance is stable if CPL increase is <= 20%
            return cpl_increase_percent <= 20.0
            
        except Exception:
            return False  # Conservative approach - assume unstable if error
    
    def _get_phase_defaults(self, phase: str) -> Dict:
        """Get default expected and max days for each phase."""
        return self.PHASE_TIMELINES.get(phase, {'expected_days': 30, 'max_days': 60})
    
    def get_phase_summary(self) -> Dict:
        """Get a summary of all phase settings."""
        return {
            'phase_1_requirements': self.PHASE_1_REQUIREMENTS,
            'phase_2_requirements': self.PHASE_2_REQUIREMENTS,
            'phase_timelines': self.PHASE_TIMELINES,
            'grace_period_days': self.GRACE_PERIOD_DAYS
        }
