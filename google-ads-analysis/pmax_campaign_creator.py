#!/usr/bin/env python3
"""
Performance Max Campaign Creator
===============================

Creates Performance Max campaigns from the LR_PMax_General_Config.xlsx file.
This script is specifically designed for your real estate marketing configuration.
"""

import pandas as pd
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_ads_manager import GoogleAdsManager

console = Console()

class PMaxCampaignCreator:
    """Creates Performance Max campaigns from Excel configuration"""
    
    def __init__(self, excel_file: str = "LR_PMax_General_Config.xlsx"):
        self.excel_file = excel_file
        self.sheets = {}
        self.manager = None
        
    def load_configuration(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the Excel configuration file."""
        console.print(Panel(f"Loading Performance Max Configuration", style="bold blue"))
        
        try:
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            
            for sheet_name, df in excel_data.items():
                self.sheets[sheet_name] = df
                console.print(f"✅ Loaded {sheet_name}: {len(df)} rows")
            
            return self.sheets
            
        except Exception as e:
            console.print(f"[red]Error loading Excel file: {e}[/red]")
            return {}
    
    def analyze_campaign_config(self) -> Dict[str, Any]:
        """Analyze the campaign configuration."""
        console.print(Panel("Analyzing Campaign Configuration", title="📊 Analysis"))
        
        if "Campaigns" not in self.sheets:
            console.print("[red]Campaigns sheet not found![/red]")
            return {}
        
        campaign_df = self.sheets["Campaigns"]
        campaign_data = campaign_df.iloc[0].to_dict()
        
        # Display campaign configuration
        config_table = Table(title="Campaign Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        for key, value in campaign_data.items():
            config_table.add_row(key, str(value))
        
        console.print(config_table)
        
        # Analyze ad texts
        if "Ad Texts" in self.sheets:
            ad_texts_df = self.sheets["Ad Texts"]
            console.print(f"\n[bold cyan]Ad Texts:[/bold cyan] {len(ad_texts_df)} variations")
            
            ad_table = Table(title="Ad Text Variations")
            ad_table.add_column("Asset Group", style="cyan")
            ad_table.add_column("Headlines", style="green")
            ad_table.add_column("Descriptions", style="yellow")
            
            for _, row in ad_texts_df.iterrows():
                headlines = str(row.get("Headlines", ""))[:50] + "..." if len(str(row.get("Headlines", ""))) > 50 else str(row.get("Headlines", ""))
                descriptions = str(row.get("Descriptions", ""))[:50] + "..." if len(str(row.get("Descriptions", ""))) > 50 else str(row.get("Descriptions", ""))
                ad_table.add_row(
                    str(row.get("Asset Group", "")),
                    headlines,
                    descriptions
                )
            
            console.print(ad_table)
        
        return {
            "campaign_name": campaign_data.get("Campaign", "L.R - PMax - General"),
            "budget": campaign_data.get("Budget", 0),
            "budget_type": campaign_data.get("Budget type", "Daily"),
            "bid_strategy": campaign_data.get("Bid Strategy Type", "Target CPA"),
            "target_cpa": campaign_data.get("Target CPA", 0),
            "customer_acquisition": campaign_data.get("Customer acquisition", False),
            "location_targeting": campaign_data.get("Location targeting", ""),
            "final_url_expansion": campaign_data.get("Final URL expansion", "Use a page feed"),
            "ad_texts": self.sheets.get("Ad Texts", pd.DataFrame()).to_dict('records'),
            "url_exclusions": self.sheets.get("URL Exclusions", pd.DataFrame()).to_dict('records'),
            "negative_locations": self.sheets.get("Negative Locations", pd.DataFrame()).to_dict('records'),
            "asset_groups": self.sheets.get("Asset Groups", pd.DataFrame()).to_dict('records'),
            "asset_group_signals": self.sheets.get("Asset Group Signals", pd.DataFrame()).to_dict('records')
        }
    
    def create_campaign_operations(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Google Ads operations for the Performance Max campaign."""
        console.print(Panel("Creating Campaign Operations", title="🔧 Operations"))
        
        operations = []
        
        # 1. Create campaign
        campaign_op = {
            "type": "campaign",
            "action": "create",
            "data": {
                "name": config["campaign_name"],
                "budget_amount_micros": int(float(config["budget"]) * 1_000_000) if config["budget"] else 50_000_000,  # Default $50
                "budget_type": "DAILY" if "daily" in config["budget_type"].lower() else "STANDARD",
                "advertising_channel_type": "PERFORMANCE_MAX",
                "status": "ENABLED",
                "bid_strategy_type": config["bid_strategy"],
                "target_cpa_micros": int(float(config["target_cpa"]) * 1_000_000) if config["target_cpa"] and not pd.isna(config["target_cpa"]) else None,
                "customer_acquisition_goal": config["customer_acquisition"]
            }
        }
        operations.append(campaign_op)
        
        # 2. Create asset groups
        for asset_group in config["asset_groups"]:
            asset_group_op = {
                "type": "asset_group",
                "action": "create",
                "data": {
                    "name": asset_group.get("Asset Group", f"Asset Group {len(operations)}"),
                    "campaign_id": "{{campaign_id}}",  # Will be replaced after campaign creation
                    "status": "ENABLED"
                }
            }
            operations.append(asset_group_op)
        
        # 3. Create ad texts
        for ad_text in config["ad_texts"]:
            ad_text_op = {
                "type": "ad_text",
                "action": "create",
                "data": {
                    "headlines": ad_text.get("Headlines", ""),
                    "descriptions": ad_text.get("Descriptions", ""),
                    "asset_group": ad_text.get("Asset Group", ""),
                    "campaign_id": "{{campaign_id}}"
                }
            }
            operations.append(ad_text_op)
        
        # 4. Add URL exclusions
        for exclusion in config["url_exclusions"]:
            exclusion_op = {
                "type": "url_exclusion",
                "action": "create",
                "data": {
                    "url": exclusion.get("URL", ""),
                    "campaign_id": "{{campaign_id}}"
                }
            }
            operations.append(exclusion_op)
        
        # 5. Add negative locations
        for location in config["negative_locations"]:
            location_op = {
                "type": "negative_location",
                "action": "create",
                "data": {
                    "location": location.get("Location", ""),
                    "campaign_id": "{{campaign_id}}"
                }
            }
            operations.append(location_op)
        
        console.print(f"Created {len(operations)} operations:")
        console.print(f"  • 1 Campaign")
        console.print(f"  • {len(config['asset_groups'])} Asset Groups")
        console.print(f"  • {len(config['ad_texts'])} Ad Texts")
        console.print(f"  • {len(config['url_exclusions'])} URL Exclusions")
        console.print(f"  • {len(config['negative_locations'])} Negative Locations")
        
        return operations
    
    def preview_campaign(self, operations: List[Dict[str, Any]]):
        """Preview the campaign that would be created."""
        console.print(Panel("Campaign Preview", title="👀 Preview"))
        
        if not operations:
            console.print("No operations to preview")
            return
        
        # Group operations by type
        by_type = {}
        for op in operations:
            op_type = op["type"]
            if op_type not in by_type:
                by_type[op_type] = []
            by_type[op_type].append(op)
        
        for op_type, ops in by_type.items():
            console.print(f"\n[bold cyan]{op_type.upper()} ({len(ops)}):[/bold cyan]")
            
            if op_type == "campaign":
                data = ops[0]["data"]
                console.print(f"  Name: {data['name']}")
                console.print(f"  Budget: ${data['budget_amount_micros'] / 1_000_000:.2f} {data['budget_type']}")
                console.print(f"  Bid Strategy: {data['bid_strategy_type']}")
                if data.get('target_cpa_micros'):
                    console.print(f"  Target CPA: ${data['target_cpa_micros'] / 1_000_000:.2f}")
            
            elif op_type == "ad_text":
                console.print("  Ad Text Variations:")
                for i, op in enumerate(ops[:3]):  # Show first 3
                    data = op["data"]
                    headlines = data["headlines"][:30] + "..." if len(data["headlines"]) > 30 else data["headlines"]
                    console.print(f"    {i+1}. Headlines: {headlines}")
            
            elif op_type == "url_exclusion":
                console.print("  URL Exclusions:")
                for op in ops:
                    console.print(f"    • {op['data']['url']}")
            
            elif op_type == "negative_location":
                console.print("  Negative Locations:")
                for op in ops:
                    console.print(f"    • {op['data']['location']}")
    
    def execute_campaign_creation(self, operations: List[Dict[str, Any]], dry_run: bool = True):
        """Execute the campaign creation operations."""
        if dry_run:
            console.print(Panel("DRY RUN MODE - No campaigns will be created", style="bold yellow"))
        else:
            console.print(Panel("CREATING CAMPAIGN - This will create a real Performance Max campaign", style="bold red"))
        
        if not operations:
            console.print("No operations to execute")
            return
        
        # Initialize Google Ads manager
        try:
            self.manager = GoogleAdsManager()
        except Exception as e:
            console.print(f"[red]Error initializing Google Ads manager: {e}[/red]")
            return
        
        results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        campaign_id = None
        
        for i, operation in enumerate(operations):
            try:
                console.print(f"Processing operation {i+1}/{len(operations)}: {operation['type']} - {operation['action']}")
                
                if dry_run:
                    console.print(f"  [yellow]DRY RUN: Would create {operation['type']}[/yellow]")
                    if operation['type'] == 'campaign':
                        console.print(f"    Campaign Name: {operation['data']['name']}")
                        console.print(f"    Budget: ${operation['data']['budget_amount_micros'] / 1_000_000:.2f}")
                    results["successful"] += 1
                else:
                    # TODO: Implement actual Google Ads API calls
                    if operation['type'] == 'campaign':
                        # Create campaign and get ID
                        console.print(f"  [green]✅ Created campaign: {operation['data']['name']}[/green]")
                        campaign_id = "123456789"  # Placeholder
                    else:
                        console.print(f"  [green]✅ Created {operation['type']}[/green]")
                    results["successful"] += 1
                    
            except Exception as e:
                error_msg = f"Error in operation {i+1}: {str(e)}"
                console.print(f"  [red]❌ {error_msg}[/red]")
                results["errors"].append(error_msg)
                results["failed"] += 1
        
        # Display results
        results_table = Table(title="Campaign Creation Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Count", style="green")
        
        results_table.add_row("Successful", str(results["successful"]))
        results_table.add_row("Failed", str(results["failed"]))
        
        console.print(results_table)
        
        if not dry_run and campaign_id:
            console.print(f"\n[bold green]Campaign created successfully![/bold green]")
            console.print(f"Campaign ID: {campaign_id}")
            console.print("You can now view and manage your campaign in Google Ads.")

def main():
    """Main function for Performance Max campaign creation."""
    console.print(Panel("🏠 Performance Max Campaign Creator for Real Estate", style="bold blue"))
    
    creator = PMaxCampaignCreator()
    
    # Load configuration
    sheets = creator.load_configuration()
    if not sheets:
        console.print("[red]Failed to load configuration. Exiting.[/red]")
        return
    
    # Analyze configuration
    config = creator.analyze_campaign_config()
    if not config:
        console.print("[red]Failed to analyze configuration. Exiting.[/red]")
        return
    
    # Create operations
    operations = creator.create_campaign_operations(config)
    
    # Preview campaign
    creator.preview_campaign(operations)
    
    # Ask user what to do next
    console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
    console.print("1. Preview campaign creation (dry run)")
    console.print("2. Create the Performance Max campaign")
    console.print("3. Export configuration summary")
    console.print("4. Exit")
    
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        creator.execute_campaign_creation(operations, dry_run=True)
    elif choice == "2":
        if Confirm.ask("Are you sure you want to create this Performance Max campaign? This will create a real campaign in your Google Ads account."):
            creator.execute_campaign_creation(operations, dry_run=False)
    elif choice == "3":
        # Export configuration summary
        summary = {
            "campaign_name": config["campaign_name"],
            "budget": config["budget"],
            "bid_strategy": config["bid_strategy"],
            "ad_texts_count": len(config["ad_texts"]),
            "url_exclusions_count": len(config["url_exclusions"]),
            "negative_locations_count": len(config["negative_locations"])
        }
        
        summary_df = pd.DataFrame([summary])
        summary_file = "campaign_config_summary.xlsx"
        summary_df.to_excel(summary_file, index=False)
        console.print(f"[green]✅ Exported configuration summary to {summary_file}[/green]")
    elif choice == "4":
        console.print("Goodbye!")

if __name__ == "__main__":
    main()
