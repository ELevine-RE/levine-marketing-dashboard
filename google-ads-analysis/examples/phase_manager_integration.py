#!/usr/bin/env python3
"""
Phase Manager Integration Example
================================

Example of how to integrate the phase manager with email summaries
and guardrails for comprehensive campaign management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase_manager import CampaignPhaseManager
from guardrails import PerformanceMaxGuardrails
from email_summary_generator import EmailSummaryGenerator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timedelta

console = Console()

def main():
    """Example of integrating phase manager with other systems."""
    console.print(Panel("🎯 Phase Manager Integration", style="bold blue"))
    
    # Initialize systems
    phase_manager = CampaignPhaseManager()
    guardrails = PerformanceMaxGuardrails()
    email_generator = EmailSummaryGenerator()
    
    # Example campaign data
    campaigns = [
        {
            'campaign_id': '123456789',
            'campaign_name': 'L.R - PMax - General',
            'phase': 'phase_1',
            'metrics': {
                'total_conversions': 35,
                'campaign_age_days': 16,
                'recent_cpls': [120, 125, 118, 122, 120],
                'days_since_last_change': 8,
                'daily_conversion_rate': 2.5,
                'daily_budget': 50.0,
                'recent_7d_spend': 350.0,
                'recent_7d_conversions': 5,
                'days_since_last_conversion': 2
            }
        },
        {
            'campaign_id': '987654321',
            'campaign_name': 'L.R - PMax - Scaling',
            'phase': 'phase_2',
            'metrics': {
                'days_under_tcpa': 35,
                'current_cpl': 110,
                'lead_quality_percent': 7.5,
                'current_pacing': 0.85,
                'daily_budget': 75.0,
                'target_cpa': 120.0,
                'recent_7d_spend': 525.0,
                'recent_7d_conversions': 4,
                'days_since_last_conversion': 1
            }
        }
    ]
    
    # Process each campaign
    console.print("\n[bold cyan]Campaign Phase Analysis[/bold cyan]")
    
    phase_results = []
    
    for campaign in campaigns:
        console.print(f"\n[bold yellow]Campaign: {campaign['campaign_name']}[/bold yellow]")
        
        # Check phase eligibility
        phase_result = phase_manager.check_phase_eligibility(
            campaign['metrics'],
            campaign['phase']
        )
        
        phase_results.append({
            'campaign': campaign,
            'phase_result': phase_result
        })
        
        console.print(f"Current Phase: {phase_result['current_phase']}")
        console.print(f"Eligible for Next: {'✅ Yes' if phase_result['eligible_for_next'] else '❌ No'}")
        console.print(f"Readiness Score: {phase_result['readiness_score']}/100")
        console.print(f"Action: {phase_result['recommended_action']}")
        
        # If eligible, check guardrails for recommended changes
        if phase_result['eligible_for_next']:
            console.print("\n[bold green]Checking Guardrails for Recommended Changes[/bold green]")
            
            # Generate change request based on phase targets
            change_request = _generate_change_request(phase_result)
            
            # Check guardrails
            guardrail_result = guardrails.enforce_guardrails(
                change_request,
                campaign['metrics']
            )
            
            console.print(f"Guardrail Verdict: {guardrail_result.verdict.value.upper()}")
            console.print(f"Reason: {guardrail_result.reason}")
            
            if guardrail_result.modified_request:
                console.print(f"Modified Request: {guardrail_result.modified_request}")
    
    # Generate summary report
    console.print("\n[bold cyan]Phase Progression Summary[/bold cyan]")
    
    summary_table = Table(title="Campaign Phase Status")
    summary_table.add_column("Campaign", style="bold")
    summary_table.add_column("Current Phase", justify="center")
    summary_table.add_column("Readiness Score", justify="center")
    summary_table.add_column("Status", justify="center")
    summary_table.add_column("Next Action")
    
    ready_campaigns = []
    blocked_campaigns = []
    
    for result in phase_results:
        campaign = result['campaign']
        phase_result = result['phase_result']
        
        status = "✅ Ready" if phase_result['eligible_for_next'] else "❌ Blocked"
        status_style = "green" if phase_result['eligible_for_next'] else "red"
        
        summary_table.add_row(
            campaign['campaign_name'],
            phase_result['current_phase'].upper(),
            f"{phase_result['readiness_score']}/100",
            status,
            phase_result['recommended_action'][:50] + "..." if len(phase_result['recommended_action']) > 50 else phase_result['recommended_action']
        )
        
        if phase_result['eligible_for_next']:
            ready_campaigns.append(result)
        else:
            blocked_campaigns.append(result)
    
    console.print(summary_table)
    
    # Generate notifications for ready campaigns
    if ready_campaigns:
        console.print("\n[bold green]🎯 Next Phase Available Notifications[/bold green]")
        
        for result in ready_campaigns:
            campaign = result['campaign']
            phase_result = result['phase_result']
            
            notification = phase_manager.generate_readiness_notification(phase_result)
            console.print(f"\n[bold]Campaign: {campaign['campaign_name']}[/bold]")
            console.print(notification)
    
    # Show blocking factors for blocked campaigns
    if blocked_campaigns:
        console.print("\n[bold yellow]⚠️ Blocked Campaigns - Action Required[/bold yellow]")
        
        for result in blocked_campaigns:
            campaign = result['campaign']
            phase_result = result['phase_result']
            
            console.print(f"\n[bold]Campaign: {campaign['campaign_name']}[/bold]")
            console.print(f"Phase: {phase_result['current_phase'].upper()}")
            console.print(f"Readiness Score: {phase_result['readiness_score']}/100")
            console.print(f"Timeline: {phase_result['estimated_timeline']}")
            
            if phase_result['blocking_factors']:
                console.print("Blocking Factors:")
                for factor in phase_result['blocking_factors']:
                    console.print(f"  • {factor}")
    
    # Email integration example
    console.print("\n[bold cyan]Email Integration Example[/bold cyan]")
    
    if ready_campaigns:
        console.print("📧 The following would be included in daily email summary:")
        console.print("• Next phase available notifications")
        console.print("• Recommended actions with guardrail approval")
        console.print("• Timeline for execution")
        
        for result in ready_campaigns:
            campaign = result['campaign']
            phase_result = result['phase_result']
            console.print(f"  - {campaign['campaign_name']}: {phase_result['recommended_action']}")
    
    if blocked_campaigns:
        console.print("📧 Blocked campaigns would include:")
        console.print("• Blocking factors and timelines")
        console.print("• Required actions to progress")
        console.print("• Optimization recommendations")

def _generate_change_request(phase_result: dict) -> dict:
    """Generate a change request based on phase targets."""
    if phase_result['current_phase'] == 'phase_1' and phase_result['eligible_for_next']:
        # Phase 1 → Phase 2: Introduce tCPA
        return {
            'type': 'target_cpa_adjustment',
            'new_target_cpa': phase_result['next_phase_targets']['target_tcpa_min'],
            'reason': 'Phase 1 → Phase 2 progression: Introducing tCPA'
        }
    elif phase_result['current_phase'] == 'phase_2' and phase_result['eligible_for_next']:
        # Phase 2 → Phase 3: Scale budget
        return {
            'type': 'budget_adjustment',
            'new_daily_budget': 90.0,  # Example: increase from 75 to 90
            'reason': 'Phase 2 → Phase 3 progression: Scaling budget'
        }
    else:
        return {
            'type': 'budget_adjustment',
            'new_daily_budget': 50.0,
            'reason': 'General optimization'
        }

if __name__ == "__main__":
    main()
