#!/usr/bin/env python3
"""
Bulk Operations Script
======================

Perform bulk operations on Google Ads campaigns.
Examples: pause underperforming campaigns, adjust budgets, etc.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_ads_manager import GoogleAdsManager
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import pandas as pd

console = Console()

def pause_underperforming_campaigns(manager: GoogleAdsManager, min_cost: float = 50.0, min_conversions: int = 1):
    """Pause campaigns that spend money but don't convert."""
    console.print(Panel("Pausing Underperforming Campaigns", style="bold red"))
    
    campaigns_df = manager.get_campaigns()
    if campaigns_df.empty:
        console.print("No campaigns found")
        return
    
    # Find underperforming campaigns
    underperforming = campaigns_df[
        (campaigns_df['status'] == 'ENABLED') &
        (campaigns_df['cost'] >= min_cost) &
        (campaigns_df['conversions'] < min_conversions)
    ]
    
    if underperforming.empty:
        console.print("✅ No underperforming campaigns found")
        return
    
    console.print(f"Found {len(underperforming)} underperforming campaigns:")
    for _, campaign in underperforming.iterrows():
        console.print(f"  • {campaign['name']} (ID: {campaign['campaign_id']})")
        console.print(f"    Cost: ${campaign['cost']:.2f}, Conversions: {campaign['conversions']:.2f}")
    
    if Confirm.ask("Do you want to pause these campaigns?"):
        updates = []
        for _, campaign in underperforming.iterrows():
            updates.append({
                "campaign_id": str(campaign['campaign_id']),
                "field": "status",
                "value": "PAUSED"
            })
        
        results = manager.bulk_update_campaigns(updates)
        console.print(f"✅ Paused {results['successful']} campaigns")
    else:
        console.print("Operation cancelled")

def adjust_budgets_by_performance(manager: GoogleAdsManager):
    """Adjust campaign budgets based on performance."""
    console.print(Panel("Adjusting Budgets by Performance", style="bold yellow"))
    
    campaigns_df = manager.get_campaigns()
    if campaigns_df.empty:
        console.print("No campaigns found")
        return
    
    # Calculate performance metrics
    campaigns_df['ctr'] = (campaigns_df['clicks'] / campaigns_df['impressions'] * 100).fillna(0)
    campaigns_df['conversion_rate'] = (campaigns_df['conversions'] / campaigns_df['clicks'] * 100).fillna(0)
    campaigns_df['roas'] = (campaigns_df['conversions'] * 100) / campaigns_df['cost'].replace(0, 1)  # Simplified ROAS
    
    # Find high-performing campaigns (above average)
    avg_ctr = campaigns_df['ctr'].mean()
    avg_conversion_rate = campaigns_df['conversion_rate'].mean()
    
    high_performing = campaigns_df[
        (campaigns_df['status'] == 'ENABLED') &
        (campaigns_df['ctr'] > avg_ctr) &
        (campaigns_df['conversion_rate'] > avg_conversion_rate)
    ]
    
    low_performing = campaigns_df[
        (campaigns_df['status'] == 'ENABLED') &
        (campaigns_df['ctr'] < avg_ctr * 0.5) &
        (campaigns_df['conversion_rate'] < avg_conversion_rate * 0.5)
    ]
    
    console.print(f"High-performing campaigns: {len(high_performing)}")
    console.print(f"Low-performing campaigns: {len(low_performing)}")
    
    if Confirm.ask("Do you want to adjust budgets?"):
        updates = []
        
        # Increase budgets for high performers by 20%
        for _, campaign in high_performing.iterrows():
            new_budget = campaign['budget'] * 1.2
            updates.append({
                "campaign_id": str(campaign['campaign_id']),
                "field": "budget",
                "value": new_budget
            })
        
        # Decrease budgets for low performers by 30%
        for _, campaign in low_performing.iterrows():
            new_budget = campaign['budget'] * 0.7
            updates.append({
                "campaign_id": str(campaign['campaign_id']),
                "field": "budget",
                "value": new_budget
            })
        
        if updates:
            results = manager.bulk_update_campaigns(updates)
            console.print(f"✅ Updated {results['successful']} campaign budgets")
        else:
            console.print("No budget updates needed")

def main():
    """Main function for bulk operations."""
    console.print(Panel("🔧 Google Ads Bulk Operations", style="bold blue"))
    
    try:
        manager = GoogleAdsManager()
        
        # Show menu
        console.print("\n[bold cyan]Available Operations:[/bold cyan]")
        console.print("1. Pause underperforming campaigns")
        console.print("2. Adjust budgets by performance")
        console.print("3. Quick analysis")
        console.print("4. Exit")
        
        choice = Prompt.ask("Choose an operation", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            min_cost = Prompt.ask("Minimum cost threshold", default="50.0", type=float)
            min_conversions = Prompt.ask("Minimum conversions", default="1", type=int)
            pause_underperforming_campaigns(manager, min_cost, min_conversions)
            
        elif choice == "2":
            adjust_budgets_by_performance(manager)
            
        elif choice == "3":
            manager.analyze_performance()
            
        elif choice == "4":
            console.print("Goodbye!")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    main()
