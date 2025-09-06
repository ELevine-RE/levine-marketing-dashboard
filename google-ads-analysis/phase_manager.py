#!/usr/bin/env python3
"""
Google Ads Campaign Phase Manager
================================

Manages campaign progression through different phases with eligibility checks
and structured readiness signals for next phase transitions.
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

class CampaignPhase(Enum):
    """Campaign phases for progression tracking."""
    PHASE_1 = "phase_1"  # Initial setup and testing
    PHASE_2 = "phase_2"   # tCPA introduction
    PHASE_3 = "phase_3"   # Scaling and optimization

@dataclass
class PhaseEligibilityResult:
    """Structured result for phase eligibility checks."""
    eligible_for_next: bool
    current_phase: str
    recommended_action: str
    readiness_score: float  # 0-100
    blocking_factors: List[str]
    next_phase_targets: Dict
    estimated_timeline: str

class CampaignPhaseManager:
    """Manages campaign progression through different phases."""
    
    def __init__(self):
        """Initialize the phase manager."""
        self.manager = GoogleAdsManager()
        
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
        
        # Phase-specific recommendations
        self.PHASE_RECOMMENDATIONS = {
            'phase_1_to_2': {
                'tcpa_range': (100, 150),
                'budget_increase': (20, 30),
                'message': "Safe to introduce tCPA at ${min}-${max}"
            },
            'phase_2_to_3': {
                'budget_increase': (20, 30),
                'geo_expansion': True,
                'message': "Safe to scale budget by +{min}-{max}%"
            }
        }
    
    def check_phase_eligibility(self, metrics: Dict, phase: str) -> Dict:
        """
        Check if campaign is eligible to progress to the next phase.
        
        Args:
            metrics: Dictionary containing campaign metrics
            phase: Current phase ('phase_1', 'phase_2', 'phase_3')
            
        Returns:
            Dictionary with eligibility status and recommendations
        """
        try:
            if phase == CampaignPhase.PHASE_1.value:
                return self._check_phase_1_to_2_eligibility(metrics)
            elif phase == CampaignPhase.PHASE_2.value:
                return self._check_phase_2_to_3_eligibility(metrics)
            elif phase == CampaignPhase.PHASE_3.value:
                return self._check_phase_3_status(metrics)
            else:
                return {
                    "eligible_for_next": False,
                    "current_phase": phase,
                    "recommended_action": f"Unknown phase: {phase}",
                    "readiness_score": 0,
                    "blocking_factors": [f"Invalid phase: {phase}"],
                    "next_phase_targets": {},
                    "estimated_timeline": "Unknown"
                }
                
        except Exception as e:
            return {
                "eligible_for_next": False,
                "current_phase": phase,
                "recommended_action": f"Error checking eligibility: {str(e)}",
                "readiness_score": 0,
                "blocking_factors": [f"System error: {str(e)}"],
                "next_phase_targets": {},
                "estimated_timeline": "Unknown"
            }
    
    def _check_phase_1_to_2_eligibility(self, metrics: Dict) -> Dict:
        """Check eligibility for Phase 1 → Phase 2 transition."""
        blocking_factors = []
        readiness_score = 100
        
        # Check conversion requirements
        total_conversions = metrics.get('total_conversions', 0)
        campaign_age_days = metrics.get('campaign_age_days', 0)
        
        if total_conversions < self.PHASE_1_REQUIREMENTS['min_conversions']:
            blocking_factors.append(f"Insufficient conversions: {total_conversions}/{self.PHASE_1_REQUIREMENTS['min_conversions']}")
            readiness_score -= 30
        
        if campaign_age_days < self.PHASE_1_REQUIREMENTS['min_days']:
            blocking_factors.append(f"Campaign too new: {campaign_age_days}/{self.PHASE_1_REQUIREMENTS['min_days']} days")
            readiness_score -= 25
        
        # Check CPL stability
        cpl_stability = self._calculate_cpl_stability(metrics)
        if cpl_stability > self.PHASE_1_REQUIREMENTS['cpl_stability_threshold']:
            blocking_factors.append(f"CPL unstable: {cpl_stability:.1f}% variation (max {self.PHASE_1_REQUIREMENTS['cpl_stability_threshold']}%)")
            readiness_score -= 20
        
        # Check for recent changes
        days_since_last_change = metrics.get('days_since_last_change', 0)
        if days_since_last_change < self.PHASE_1_REQUIREMENTS['no_changes_days']:
            blocking_factors.append(f"Recent changes detected: {days_since_last_change} days ago (min {self.PHASE_1_REQUIREMENTS['no_changes_days']} days)")
            readiness_score -= 15
        
        # Determine eligibility
        eligible = len(blocking_factors) == 0
        readiness_score = max(0, readiness_score)
        
        # Generate recommendation
        if eligible:
            tcpa_range = self.PHASE_RECOMMENDATIONS['phase_1_to_2']['tcpa_range']
            recommended_action = f"Safe to introduce tCPA at ${tcpa_range[0]}-${tcpa_range[1]}"
        else:
            recommended_action = "Continue Phase 1 optimization - address blocking factors"
        
        # Calculate next phase targets
        next_phase_targets = {
            'target_tcpa_min': tcpa_range[0] if eligible else None,
            'target_tcpa_max': tcpa_range[1] if eligible else None,
            'budget_increase_percent': self.PHASE_RECOMMENDATIONS['phase_1_to_2']['budget_increase'][0] if eligible else None
        }
        
        # Estimate timeline
        estimated_timeline = self._estimate_phase_1_timeline(metrics, blocking_factors)
        
        return {
            "eligible_for_next": eligible,
            "current_phase": "phase_1",
            "recommended_action": recommended_action,
            "readiness_score": readiness_score,
            "blocking_factors": blocking_factors,
            "next_phase_targets": next_phase_targets,
            "estimated_timeline": estimated_timeline
        }
    
    def _check_phase_2_to_3_eligibility(self, metrics: Dict) -> Dict:
        """Check eligibility for Phase 2 → Phase 3 transition."""
        blocking_factors = []
        readiness_score = 100
        
        # Check tCPA duration
        days_under_tcpa = metrics.get('days_under_tcpa', 0)
        if days_under_tcpa < self.PHASE_2_REQUIREMENTS['min_tcpa_days']:
            blocking_factors.append(f"Insufficient tCPA time: {days_under_tcpa}/{self.PHASE_2_REQUIREMENTS['min_tcpa_days']} days")
            readiness_score -= 25
        
        # Check CPL range
        current_cpl = metrics.get('current_cpl', 0)
        if current_cpl < self.PHASE_2_REQUIREMENTS['cpl_min']:
            blocking_factors.append(f"CPL too low: ${current_cpl:.2f} (min ${self.PHASE_2_REQUIREMENTS['cpl_min']:.2f})")
            readiness_score -= 20
        elif current_cpl > self.PHASE_2_REQUIREMENTS['cpl_max']:
            blocking_factors.append(f"CPL too high: ${current_cpl:.2f} (max ${self.PHASE_2_REQUIREMENTS['cpl_max']:.2f})")
            readiness_score -= 20
        
        # Check lead quality
        lead_quality_percent = metrics.get('lead_quality_percent', 0)
        if lead_quality_percent < self.PHASE_2_REQUIREMENTS['lead_quality_threshold']:
            blocking_factors.append(f"Low lead quality: {lead_quality_percent:.1f}% (min {self.PHASE_2_REQUIREMENTS['lead_quality_threshold']}%)")
            readiness_score -= 20
        
        # Check pacing
        current_pacing = metrics.get('current_pacing', 0)
        if current_pacing < self.PHASE_2_REQUIREMENTS['pacing_threshold']:
            blocking_factors.append(f"Pacing constrained: {current_pacing:.1%} (min {self.PHASE_2_REQUIREMENTS['pacing_threshold']:.1%})")
            readiness_score -= 15
        
        # Determine eligibility
        eligible = len(blocking_factors) == 0
        readiness_score = max(0, readiness_score)
        
        # Generate recommendation
        if eligible:
            budget_range = self.PHASE_RECOMMENDATIONS['phase_2_to_3']['budget_increase']
            recommended_action = f"Safe to scale budget by +{budget_range[0]}-{budget_range[1]}%"
        else:
            recommended_action = "Continue Phase 2 optimization - address blocking factors"
        
        # Calculate next phase targets
        next_phase_targets = {
            'budget_increase_percent': budget_range[0] if eligible else None,
            'geo_expansion': self.PHASE_RECOMMENDATIONS['phase_2_to_3']['geo_expansion'] if eligible else None,
            'additional_asset_groups': True if eligible else None
        }
        
        # Estimate timeline
        estimated_timeline = self._estimate_phase_2_timeline(metrics, blocking_factors)
        
        return {
            "eligible_for_next": eligible,
            "current_phase": "phase_2",
            "recommended_action": recommended_action,
            "readiness_score": readiness_score,
            "blocking_factors": blocking_factors,
            "next_phase_targets": next_phase_targets,
            "estimated_timeline": estimated_timeline
        }
    
    def _check_phase_3_status(self, metrics: Dict) -> Dict:
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
        
        return {
            "eligible_for_next": False,  # Phase 3 is final
            "current_phase": "phase_3",
            "recommended_action": recommended_action,
            "readiness_score": 100,
            "blocking_factors": [],
            "next_phase_targets": {"optimization": True},
            "estimated_timeline": "Ongoing optimization"
        }
    
    def _calculate_cpl_stability(self, metrics: Dict) -> float:
        """Calculate CPL stability over time."""
        try:
            recent_cpls = metrics.get('recent_cpls', [])
            if len(recent_cpls) < 2:
                return 0.0
            
            # Calculate coefficient of variation
            mean_cpl = sum(recent_cpls) / len(recent_cpls)
            if mean_cpl == 0:
                return 0.0
            
            variance = sum((cpl - mean_cpl) ** 2 for cpl in recent_cpls) / len(recent_cpls)
            std_dev = variance ** 0.5
            cv = (std_dev / mean_cpl) * 100
            
            return cv
            
        except Exception:
            return 0.0
    
    def _estimate_phase_1_timeline(self, metrics: Dict, blocking_factors: List[str]) -> str:
        """Estimate timeline for Phase 1 completion."""
        if not blocking_factors:
            return "Ready now"
        
        timeline_estimates = []
        
        for factor in blocking_factors:
            if "conversions" in factor:
                current_conversions = metrics.get('total_conversions', 0)
                needed_conversions = self.PHASE_1_REQUIREMENTS['min_conversions']
                daily_conversion_rate = metrics.get('daily_conversion_rate', 1)
                
                if daily_conversion_rate > 0:
                    days_needed = (needed_conversions - current_conversions) / daily_conversion_rate
                    timeline_estimates.append(f"{max(1, int(days_needed))} days for conversions")
            
            elif "days" in factor and "new" in factor:
                current_age = metrics.get('campaign_age_days', 0)
                needed_age = self.PHASE_1_REQUIREMENTS['min_days']
                days_needed = needed_age - current_age
                timeline_estimates.append(f"{max(1, int(days_needed))} days for campaign age")
            
            elif "changes" in factor:
                days_since_change = metrics.get('days_since_last_change', 0)
                needed_days = self.PHASE_1_REQUIREMENTS['no_changes_days']
                days_needed = needed_days - days_since_change
                timeline_estimates.append(f"{max(1, int(days_needed))} days for stability")
        
        if timeline_estimates:
            return f"~{max(timeline_estimates)}"
        else:
            return "Unknown"
    
    def _estimate_phase_2_timeline(self, metrics: Dict, blocking_factors: List[str]) -> str:
        """Estimate timeline for Phase 2 completion."""
        if not blocking_factors:
            return "Ready now"
        
        timeline_estimates = []
        
        for factor in blocking_factors:
            if "tCPA time" in factor:
                current_days = metrics.get('days_under_tcpa', 0)
                needed_days = self.PHASE_2_REQUIREMENTS['min_tcpa_days']
                days_needed = needed_days - current_days
                timeline_estimates.append(f"{max(1, int(days_needed))} days for tCPA stability")
            
            elif "CPL" in factor:
                timeline_estimates.append("1-2 weeks for CPL optimization")
            
            elif "lead quality" in factor:
                timeline_estimates.append("2-4 weeks for lead quality improvement")
            
            elif "pacing" in factor:
                timeline_estimates.append("1 week for pacing adjustment")
        
        if timeline_estimates:
            return f"~{max(timeline_estimates)}"
        else:
            return "Unknown"
    
    def generate_readiness_notification(self, result: Dict) -> str:
        """Generate a structured readiness notification for Slack/email."""
        if result["eligible_for_next"]:
            # Next phase available notification
            notification = f"""
🎯 **Next Phase Available: {result['current_phase'].upper()} → {self._get_next_phase(result['current_phase']).upper()}**

✅ **Campaign Ready for Progression**
📊 **Readiness Score:** {result['readiness_score']}/100
🎯 **Recommended Action:** {result['recommended_action']}

📈 **Next Phase Targets:**
"""
            for target, value in result['next_phase_targets'].items():
                if value is not None:
                    notification += f"• {target.replace('_', ' ').title()}: {value}\n"
            
            notification += f"""
⏰ **Timeline:** {result['estimated_timeline']}
🚀 **Ready to execute when convenient**
"""
        else:
            # Not ready notification
            notification = f"""
⚠️ **Phase Progression Blocked: {result['current_phase'].upper()}**

📊 **Readiness Score:** {result['readiness_score']}/100
🎯 **Current Status:** {result['recommended_action']}

🚫 **Blocking Factors:**
"""
            for factor in result['blocking_factors']:
                notification += f"• {factor}\n"
            
            notification += f"""
⏰ **Estimated Timeline:** {result['estimated_timeline']}
📋 **Action Required:** Address blocking factors before progression
"""
        
        return notification
    
    def _get_next_phase(self, current_phase: str) -> str:
        """Get the next phase name."""
        phase_map = {
            'phase_1': 'phase_2',
            'phase_2': 'phase_3',
            'phase_3': 'phase_3'  # Phase 3 is final
        }
        return phase_map.get(current_phase, 'unknown')
    
    def check_phase_progress(self, start_date: datetime, current_date: datetime, phase: str, 
                           eligibility: dict, expected_days: int = None, max_days: int = None) -> dict:
        """
        Check phase progress and determine if campaign is lagging.
        
        Args:
            start_date: When the phase started
            current_date: Current date for comparison
            phase: Current phase ('phase_1', 'phase_2', 'phase_3')
            eligibility: Result from check_phase_eligibility
            expected_days: Override for expected days in phase
            max_days: Override for maximum days in phase
            
        Returns:
            Dictionary with lag status and messaging
        """
        try:
            # Calculate days in phase
            days_in_phase = (current_date - start_date).days
            
            # Get phase-specific defaults if not provided
            if expected_days is None or max_days is None:
                phase_defaults = self._get_phase_defaults(phase)
                expected_days = expected_days or phase_defaults['expected_days']
                max_days = max_days or phase_defaults['max_days']
            
            # Initialize result
            result = {
                "lagging": False,
                "lag_alert": False,
                "days_in_phase": days_in_phase,
                "message": "",
                "expected_days": expected_days,
                "max_days": max_days,
                "grace_period": 3  # 1-3 days tolerance
            }
            
            # Check if eligible for next phase
            is_eligible = eligibility.get('eligible_for_next', False)
            
            # Determine lag status
            if days_in_phase <= expected_days:
                # Within expected timeframe
                if is_eligible:
                    result["message"] = f"Phase progressing well - eligible for next phase after {expected_days - days_in_phase} more days"
                else:
                    result["message"] = f"Phase progressing normally - {expected_days - days_in_phase} days remaining to expected completion"
            
            elif days_in_phase <= expected_days + result["grace_period"]:
                # Within grace period (1-3 days past expected)
                if is_eligible:
                    result["message"] = f"Phase slightly behind but eligible for next phase"
                else:
                    result["message"] = f"Phase slightly behind expected timeline ({days_in_phase - expected_days} days over) - within grace period"
            
            elif days_in_phase <= max_days:
                # Lagging but within max days
                result["lagging"] = True
                if is_eligible:
                    result["message"] = f"Phase lagging but eligible for next phase ({days_in_phase - expected_days} days behind expected)"
                else:
                    result["message"] = f"Phase lagging - {days_in_phase - expected_days} days past expected completion. Address blocking factors."
            
            else:
                # Exceeded max days
                result["lagging"] = True
                result["lag_alert"] = True
                
                if is_eligible:
                    result["message"] = f"⚠️ CRITICAL: Phase exceeded maximum duration ({days_in_phase - max_days} days over max) but eligible for next phase. Proceed immediately."
                else:
                    # Generate detailed lag alert message
                    blocking_factors = eligibility.get('blocking_factors', [])
                    readiness_score = eligibility.get('readiness_score', 0)
                    
                    result["message"] = f"🚨 CRITICAL ALERT: Phase exceeded maximum duration by {days_in_phase - max_days} days!"
                    result["message"] += f"\n• Readiness Score: {readiness_score}/100"
                    result["message"] += f"\n• Blocking Factors: {', '.join(blocking_factors) if blocking_factors else 'None identified'}"
                    result["message"] += f"\n• Immediate Action Required: Review campaign performance and address issues"
            
            return result
            
        except Exception as e:
            return {
                "lagging": False,
                "lag_alert": False,
                "days_in_phase": 0,
                "message": f"Error checking phase progress: {str(e)}",
                "expected_days": expected_days or 0,
                "max_days": max_days or 0,
                "grace_period": 3
            }
    
    def _get_phase_defaults(self, phase: str) -> dict:
        """Get default expected and max days for each phase."""
        defaults = {
            'phase_1': {
                'expected_days': 21,
                'max_days': 35
            },
            'phase_2': {
                'expected_days': 45,
                'max_days': 70
            },
            'phase_3': {
                'expected_days': 90,  # Ongoing optimization
                'max_days': 365      # 1 year max for optimization phase
            }
        }
        return defaults.get(phase, {'expected_days': 30, 'max_days': 60})
    
    def generate_progress_notification(self, progress_result: dict, phase: str, campaign_name: str) -> str:
        """Generate a structured progress notification."""
        if progress_result["lag_alert"]:
            # Critical alert notification
            notification = f"""
🚨 **CRITICAL PHASE ALERT: {campaign_name}**

📊 **Phase Progress Status:**
• Current Phase: {phase.upper()}
• Days in Phase: {progress_result['days_in_phase']}
• Expected Duration: {progress_result['expected_days']} days
• Maximum Duration: {progress_result['max_days']} days
• Status: EXCEEDED MAXIMUM DURATION

⚠️ **IMMEDIATE ACTION REQUIRED**
{progress_result['message']}

🔧 **Recommended Actions:**
• Review campaign performance metrics
• Address blocking factors immediately
• Consider campaign pause if issues persist
• Schedule performance review meeting
"""
        elif progress_result["lagging"]:
            # Lagging notification
            notification = f"""
⚠️ **Phase Lagging Alert: {campaign_name}**

📊 **Phase Progress Status:**
• Current Phase: {phase.upper()}
• Days in Phase: {progress_result['days_in_phase']}
• Expected Duration: {progress_result['expected_days']} days
• Maximum Duration: {progress_result['max_days']} days
• Status: LAGGING BEHIND SCHEDULE

📋 **Action Required:**
{progress_result['message']}

🔧 **Recommended Actions:**
• Review blocking factors
• Optimize campaign performance
• Consider additional resources
"""
        else:
            # Normal progress notification
            notification = f"""
✅ **Phase Progress Update: {campaign_name}**

📊 **Phase Progress Status:**
• Current Phase: {phase.upper()}
• Days in Phase: {progress_result['days_in_phase']}
• Expected Duration: {progress_result['expected_days']} days
• Status: PROGRESSING NORMALLY

📈 **Current Status:**
{progress_result['message']}
"""
        
        return notification

def main():
    """Test the phase manager system."""
    console.print(Panel("🎯 Campaign Phase Manager", style="bold blue"))
    
    # Initialize phase manager
    phase_manager = CampaignPhaseManager()
    
    # Example test cases
    test_cases = [
        {
            'name': 'Phase 1 - Ready for Phase 2',
            'phase': 'phase_1',
            'start_date': datetime.now() - timedelta(days=16),
            'metrics': {
                'total_conversions': 35,
                'campaign_age_days': 16,
                'recent_cpls': [120, 125, 118, 122, 120],
                'days_since_last_change': 8,
                'daily_conversion_rate': 2.5
            }
        },
        {
            'name': 'Phase 1 - Not Ready (Low Conversions)',
            'phase': 'phase_1',
            'start_date': datetime.now() - timedelta(days=25),
            'metrics': {
                'total_conversions': 15,
                'campaign_age_days': 25,
                'recent_cpls': [120, 125, 118, 122, 120],
                'days_since_last_change': 10,
                'daily_conversion_rate': 1.0
            }
        },
        {
            'name': 'Phase 2 - Ready for Phase 3',
            'phase': 'phase_2',
            'start_date': datetime.now() - timedelta(days=40),
            'metrics': {
                'days_under_tcpa': 35,
                'current_cpl': 110,
                'lead_quality_percent': 7.5,
                'current_pacing': 0.85
            }
        },
        {
            'name': 'Phase 2 - Not Ready (Low Lead Quality)',
            'phase': 'phase_2',
            'start_date': datetime.now() - timedelta(days=55),
            'metrics': {
                'days_under_tcpa': 40,
                'current_cpl': 100,
                'lead_quality_percent': 3.0,
                'current_pacing': 0.90
            }
        },
        {
            'name': 'Phase 3 - Optimization',
            'phase': 'phase_3',
            'start_date': datetime.now() - timedelta(days=100),
            'metrics': {
                'current_cpl': 160,
                'current_pacing': 0.75,
                'lead_quality_percent': 6.0
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        console.print(f"\n[bold cyan]Testing: {test_case['name']}[/bold cyan]")
        
        result = phase_manager.check_phase_eligibility(
            test_case['metrics'],
            test_case['phase']
        )
        
        console.print(f"Phase: {result['current_phase']}")
        console.print(f"Eligible: {'✅ Yes' if result['eligible_for_next'] else '❌ No'}")
        console.print(f"Readiness Score: {result['readiness_score']}/100")
        console.print(f"Action: {result['recommended_action']}")
        
        if result['blocking_factors']:
            console.print("Blocking Factors:")
            for factor in result['blocking_factors']:
                console.print(f"  • {factor}")
        
        if result['next_phase_targets']:
            console.print("Next Phase Targets:")
            for target, value in result['next_phase_targets'].items():
                console.print(f"  • {target}: {value}")
        
        console.print(f"Timeline: {result['estimated_timeline']}")
        
        # Test progress tracking
        progress_result = phase_manager.check_phase_progress(
            test_case['start_date'],
            datetime.now(),
            test_case['phase'],
            result
        )
        
        console.print(f"\n[bold magenta]Progress Tracking:[/bold magenta]")
        console.print(f"Days in Phase: {progress_result['days_in_phase']}")
        console.print(f"Expected Days: {progress_result['expected_days']}")
        console.print(f"Max Days: {progress_result['max_days']}")
        console.print(f"Lagging: {'⚠️ Yes' if progress_result['lagging'] else '✅ No'}")
        console.print(f"Lag Alert: {'🚨 Yes' if progress_result['lag_alert'] else '✅ No'}")
        console.print(f"Message: {progress_result['message']}")
        
        # Generate progress notification
        progress_notification = phase_manager.generate_progress_notification(
            progress_result, 
            test_case['phase'], 
            test_case['name']
        )
        console.print(f"\n[bold yellow]Progress Notification:[/bold yellow]")
        console.print(progress_notification)
        
        # Generate readiness notification
        notification = phase_manager.generate_readiness_notification(result)
        console.print(f"\n[bold yellow]Readiness Notification:[/bold yellow]")
        console.print(notification)

if __name__ == "__main__":
    main()
