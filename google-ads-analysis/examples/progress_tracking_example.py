#!/usr/bin/env python3
"""
Progress Tracking Integration Example
===================================

Example of how progress tracking integrates with email summaries
and provides comprehensive campaign monitoring with lag alerts.
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
    """Example of progress tracking integration."""
    console.print(Panel("📊 Progress Tracking Integration", style="bold blue"))
    
    # Initialize systems
    phase_manager = CampaignPhaseManager()
    guardrails = PerformanceMaxGuardrails()
    email_generator = EmailSummaryGenerator()
    
    # Example campaign data with start dates
    campaigns = [
        {
            'campaign_id': '123456789',
            'campaign_name': 'L.R - PMax - General',
            'phase': 'phase_1',
            'start_date': datetime.now() - timedelta(days=25),  # Lagging
            'metrics': {
                'total_conversions': 15,
                'campaign_age_days': 25,
                'recent_cpls': [120, 125, 118, 122, 120],
                'days_since_last_change': 10,
                'daily_conversion_rate': 1.0
            }
        },
        {
            'campaign_id': '987654321',
            'campaign_name': 'L.R - PMax - Scaling',
            'phase': 'phase_2',
            'start_date': datetime.now() - timedelta(days=75),  # Critical lag
            'metrics': {
                'days_under_tcpa': 40,
                'current_cpl': 100,
                'lead_quality_percent': 3.0,
                'current_pacing': 0.90,
                'daily_budget': 75.0,
                'target_cpa': 120.0,
                'recent_7d_spend': 525.0,
                'recent_7d_conversions': 4,
                'days_since_last_conversion': 1
            }
        },
        {
            'campaign_id': '555666777',
            'campaign_name': 'L.R - PMax - Optimized',
            'phase': 'phase_1',
            'start_date': datetime.now() - timedelta(days=16),  # On track
            'metrics': {
                'total_conversions': 35,
                'campaign_age_days': 16,
                'recent_cpls': [120, 125, 118, 122, 120],
                'days_since_last_change': 8,
                'daily_conversion_rate': 2.5
            }
        }
    ]
    
    # Process each campaign
    console.print("\n[bold cyan]Campaign Progress Analysis[/bold cyan]")
    
    progress_results = []
    
    for campaign in campaigns:
        console.print(f"\n[bold yellow]Campaign: {campaign['campaign_name']}[/bold yellow]")
        
        # Check phase eligibility
        eligibility_result = phase_manager.check_phase_eligibility(
            campaign['metrics'],
            campaign['phase']
        )
        
        # Check progress tracking
        progress_result = phase_manager.check_phase_progress(
            campaign['start_date'],
            datetime.now(),
            campaign['phase'],
            eligibility_result
        )
        
        progress_results.append({
            'campaign': campaign,
            'eligibility': eligibility_result,
            'progress': progress_result
        })
        
        console.print(f"Phase: {eligibility_result['current_phase']}")
        console.print(f"Days in Phase: {progress_result['days_in_phase']}")
        console.print(f"Expected: {progress_result['expected_days']} | Max: {progress_result['max_days']}")
        console.print(f"Eligible: {'✅ Yes' if eligibility_result['eligible_for_next'] else '❌ No'}")
        console.print(f"Lagging: {'⚠️ Yes' if progress_result['lagging'] else '✅ No'}")
        console.print(f"Lag Alert: {'🚨 Yes' if progress_result['lag_alert'] else '✅ No'}")
        console.print(f"Status: {progress_result['message']}")
    
    # Generate summary report
    console.print("\n[bold cyan]Progress Summary Report[/bold cyan]")
    
    summary_table = Table(title="Campaign Progress Status")
    summary_table.add_column("Campaign", style="bold")
    summary_table.add_column("Phase", justify="center")
    summary_table.add_column("Days", justify="center")
    summary_table.add_column("Expected", justify="center")
    summary_table.add_column("Status", justify="center")
    summary_table.add_column("Alert", justify="center")
    
    critical_alerts = []
    lagging_campaigns = []
    on_track_campaigns = []
    
    for result in progress_results:
        campaign = result['campaign']
        progress = result['progress']
        eligibility = result['eligibility']
        
        # Determine status
        if progress['lag_alert']:
            status = "🚨 CRITICAL"
            alert = "MAX EXCEEDED"
            critical_alerts.append(result)
        elif progress['lagging']:
            status = "⚠️ LAGGING"
            alert = "BEHIND SCHEDULE"
            lagging_campaigns.append(result)
        else:
            status = "✅ ON TRACK"
            alert = "NORMAL"
            on_track_campaigns.append(result)
        
        summary_table.add_row(
            campaign['campaign_name'],
            eligibility['current_phase'].upper(),
            str(progress['days_in_phase']),
            str(progress['expected_days']),
            status,
            alert
        )
    
    console.print(summary_table)
    
    # Generate critical alerts
    if critical_alerts:
        console.print("\n[bold red]🚨 CRITICAL ALERTS - IMMEDIATE ACTION REQUIRED[/bold red]")
        
        for result in critical_alerts:
            campaign = result['campaign']
            progress = result['progress']
            eligibility = result['eligibility']
            
            notification = phase_manager.generate_progress_notification(
                progress,
                campaign['phase'],
                campaign['campaign_name']
            )
            console.print(notification)
            
            # Check guardrails for emergency actions
            console.print("\n[bold yellow]Emergency Guardrail Check:[/bold yellow]")
            
            # Generate emergency change request
            emergency_request = _generate_emergency_request(eligibility, campaign)
            
            guardrail_result = guardrails.enforce_guardrails(
                emergency_request,
                campaign['metrics']
            )
            
            console.print(f"Emergency Action: {guardrail_result.verdict.value.upper()}")
            console.print(f"Reason: {guardrail_result.reason}")
            
            if guardrail_result.safety_alert:
                console.print(f"Safety Alert: {guardrail_result.safety_alert}")
    
    # Generate lagging alerts
    if lagging_campaigns:
        console.print("\n[bold yellow]⚠️ LAGGING CAMPAIGNS - ACTION REQUIRED[/bold yellow]")
        
        for result in lagging_campaigns:
            campaign = result['campaign']
            progress = result['progress']
            eligibility = result['eligibility']
            
            notification = phase_manager.generate_progress_notification(
                progress,
                campaign['phase'],
                campaign['campaign_name']
            )
            console.print(notification)
            
            # Show blocking factors
            if eligibility['blocking_factors']:
                console.print("Blocking Factors:")
                for factor in eligibility['blocking_factors']:
                    console.print(f"  • {factor}")
    
    # Show on-track campaigns
    if on_track_campaigns:
        console.print("\n[bold green]✅ ON-TRACK CAMPAIGNS[/bold green]")
        
        for result in on_track_campaigns:
            campaign = result['campaign']
            progress = result['progress']
            eligibility = result['eligibility']
            
            if eligibility['eligible_for_next']:
                notification = phase_manager.generate_readiness_notification(eligibility)
                console.print(f"\n[bold]Campaign: {campaign['campaign_name']}[/bold]")
                console.print(notification)
    
    # Email integration example
    console.print("\n[bold cyan]Email Integration Summary[/bold cyan]")
    
    if critical_alerts:
        console.print("📧 CRITICAL ALERTS would be sent immediately:")
        for result in critical_alerts:
            campaign = result['campaign']
            console.print(f"  - {campaign['campaign_name']}: MAXIMUM DURATION EXCEEDED")
    
    if lagging_campaigns:
        console.print("📧 LAGGING ALERTS would be included in daily summary:")
        for result in lagging_campaigns:
            campaign = result['campaign']
            progress = result['progress']
            console.print(f"  - {campaign['campaign_name']}: {progress['days_in_phase'] - progress['expected_days']} days behind")
    
    if on_track_campaigns:
        console.print("📧 ON-TRACK updates would be included in daily summary:")
        for result in on_track_campaigns:
            campaign = result['campaign']
            eligibility = result['eligibility']
            if eligibility['eligible_for_next']:
                console.print(f"  - {campaign['campaign_name']}: Ready for next phase")
            else:
                console.print(f"  - {campaign['campaign_name']}: Progressing normally")

def _generate_emergency_request(eligibility: dict, campaign: dict) -> dict:
    """Generate emergency change request for critical alerts."""
    if campaign['phase'] == 'phase_1':
        return {
            'type': 'campaign_pause',
            'action': 'pause',
            'reason': 'Emergency pause due to critical phase lag'
        }
    elif campaign['phase'] == 'phase_2':
        return {
            'type': 'target_cpa_adjustment',
            'new_target_cpa': 150.0,  # Increase tCPA to improve performance
            'reason': 'Emergency tCPA adjustment due to critical phase lag'
        }
    else:
        return {
            'type': 'budget_adjustment',
            'new_daily_budget': campaign['metrics'].get('daily_budget', 50) * 0.8,  # Reduce budget
            'reason': 'Emergency budget reduction due to critical phase lag'
        }

if __name__ == "__main__":
    main()
