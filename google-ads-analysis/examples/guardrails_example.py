#!/usr/bin/env python3
"""
Guardrails Integration Example
=============================

Example of how to integrate the guardrails system with email summaries
and campaign management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardrails import PerformanceMaxGuardrails, GuardrailVerdict
from email_summary_generator import EmailSummaryGenerator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timedelta

console = Console()

def main():
    """Example of integrating guardrails with campaign management."""
    console.print(Panel("🛡️ Guardrails Integration Example", style="bold blue"))
    
    # Initialize systems
    guardrails = PerformanceMaxGuardrails()
    email_generator = EmailSummaryGenerator()
    
    # Example campaign state
    campaign_state = {
        'campaign_id': '123456789',
        'campaign_name': 'L.R - PMax - General',
        'daily_budget': 50.0,
        'target_cpa': 120.0,
        'status': 'ENABLED',
        'recent_7d_spend': 350.0,
        'recent_7d_conversions': 3,
        'total_conversions': 45,
        'days_since_last_conversion': 5,
        'last_budget_change_date': datetime.now() - timedelta(days=5),
        'last_tcpa_change_date': datetime.now() - timedelta(days=10),
        'asset_groups': [
            {
                'name': 'Main Asset Group',
                'status': 'ENABLED',
                'asset_counts': {
                    'headlines': 6,
                    'long_headlines': 1,
                    'descriptions': 3,
                    'logos': 1,
                    'images': 4,
                    'videos': 1
                }
            }
        ]
    }
    
    # Example change requests
    change_requests = [
        {
            'type': 'budget_adjustment',
            'new_daily_budget': 75.0,
            'reason': 'Increase budget due to good performance'
        },
        {
            'type': 'target_cpa_adjustment',
            'new_target_cpa': 110.0,
            'reason': 'Lower tCPA to improve efficiency'
        },
        {
            'type': 'asset_group_modification',
            'action': 'pause_all',
            'reason': 'Pause all asset groups for maintenance'
        }
    ]
    
    # Process each change request
    console.print("\n[bold cyan]Processing Change Requests[/bold cyan]")
    
    approved_changes = []
    rejected_changes = []
    modified_changes = []
    delayed_changes = []
    
    for i, change_request in enumerate(change_requests, 1):
        console.print(f"\n[bold yellow]Change Request {i}:[/bold yellow] {change_request['reason']}")
        
        # Apply guardrails
        verdict = guardrails.enforce_guardrails(change_request, campaign_state)
        
        # Categorize result
        if verdict.verdict.value == 'approved':
            approved_changes.append({
                'request': change_request,
                'verdict': verdict
            })
            console.print(f"[green]✅ APPROVED[/green]")
        elif verdict.verdict.value == 'rejected':
            rejected_changes.append({
                'request': change_request,
                'verdict': verdict
            })
            console.print(f"[red]❌ REJECTED[/red]")
        elif verdict.verdict.value == 'modified':
            modified_changes.append({
                'request': change_request,
                'verdict': verdict
            })
            console.print(f"[yellow]⚠️ MODIFIED[/yellow]")
        elif verdict.verdict.value == 'delayed':
            delayed_changes.append({
                'request': change_request,
                'verdict': verdict
            })
            console.print(f"[blue]⏰ DELAYED[/blue]")
        
        console.print(f"Reason: {verdict.reason}")
        
        if verdict.modified_request:
            console.print(f"Modified to: {verdict.modified_request}")
        
        if verdict.delay_hours:
            console.print(f"Delay: {verdict.delay_hours} hours")
        
        if verdict.safety_alert:
            console.print(f"Safety Alert: {verdict.safety_alert}")
    
    # Generate summary report
    console.print("\n[bold cyan]Guardrails Summary Report[/bold cyan]")
    
    summary_table = Table(title="Change Request Summary")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Count", justify="center")
    summary_table.add_column("Details")
    
    summary_table.add_row("✅ Approved", str(len(approved_changes)), "Changes that meet all guardrail requirements")
    summary_table.add_row("❌ Rejected", str(len(rejected_changes)), "Changes that violate guardrails")
    summary_table.add_row("⚠️ Modified", str(len(modified_changes)), "Changes adjusted to meet guardrails")
    summary_table.add_row("⏰ Delayed", str(len(delayed_changes)), "Changes delayed due to frequency limits")
    
    console.print(summary_table)
    
    # Show guardrail settings
    console.print("\n[bold cyan]Guardrail Settings[/bold cyan]")
    
    settings = guardrails.get_guardrail_summary()
    
    for category, limits in settings.items():
        console.print(f"\n[bold]{category.replace('_', ' ').title()}:[/bold]")
        if isinstance(limits, dict):
            for key, value in limits.items():
                console.print(f"  {key}: {value}")
        else:
            console.print(f"  {limits}")
    
    # Example of integrating with email summary
    console.print("\n[bold cyan]Email Integration Example[/bold cyan]")
    
    if rejected_changes or modified_changes:
        console.print("⚠️ Some changes were rejected or modified - this would be included in the email summary")
        console.print("The email would include:")
        console.print("• List of rejected changes with reasons")
        console.print("• Modified changes with adjustments")
        console.print("• Safety alerts if any")
        console.print("• Recommendations for next steps")
    
    # Example of automated action
    console.print("\n[bold cyan]Automated Actions[/bold cyan]")
    
    for change in approved_changes:
        console.print(f"✅ Would automatically apply: {change['request']['reason']}")
    
    for change in delayed_changes:
        console.print(f"⏰ Would schedule for later: {change['request']['reason']}")

if __name__ == "__main__":
    main()
