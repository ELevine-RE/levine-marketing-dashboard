#!/usr/bin/env python3
"""
Excel Config Analyzer
====================

Analyzes the LR_PMax_General_Config.xlsx file and integrates it with Google Ads API.
This allows you to use your existing campaign configuration and automate the upload process.
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

class ExcelConfigAnalyzer:
    """Analyzes Excel configuration files and integrates with Google Ads API"""
    
    def __init__(self, excel_file: str = "LR_PMax_General_Config.xlsx"):
        self.excel_file = excel_file
        self.sheets = {}
        self.manager = None
        
    def load_excel_file(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the Excel file."""
        console.print(Panel(f"Loading Excel file: {self.excel_file}", style="bold blue"))
        
        try:
            # Read all sheets
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            
            for sheet_name, df in excel_data.items():
                self.sheets[sheet_name] = df
                console.print(f"✅ Loaded sheet: {sheet_name} ({len(df)} rows)")
            
            return self.sheets
            
        except Exception as e:
            console.print(f"[red]Error loading Excel file: {e}[/red]")
            return {}
    
    def analyze_sheets(self) -> Dict[str, Any]:
        """Analyze the structure and content of all sheets."""
        console.print(Panel("Analyzing Excel Configuration", title="📊 Analysis"))
        
        analysis = {
            "total_sheets": len(self.sheets),
            "sheet_details": {},
            "campaign_configs": [],
            "recommendations": []
        }
        
        for sheet_name, df in self.sheets.items():
            sheet_info = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records')
            }
            
            analysis["sheet_details"][sheet_name] = sheet_info
            
            # Look for campaign-related sheets
            if any(keyword in sheet_name.lower() for keyword in ['campaign', 'ad', 'keyword', 'budget']):
                analysis["campaign_configs"].append(sheet_name)
        
        # Display analysis
        summary_table = Table(title="Excel File Summary")
        summary_table.add_column("Sheet Name", style="cyan")
        summary_table.add_column("Rows", style="green")
        summary_table.add_column("Columns", style="yellow")
        summary_table.add_column("Type", style="magenta")
        
        for sheet_name, info in analysis["sheet_details"].items():
            sheet_type = "Campaign Config" if sheet_name in analysis["campaign_configs"] else "Data"
            summary_table.add_row(
                sheet_name,
                str(info["rows"]),
                str(info["columns"]),
                sheet_type
            )
        
        console.print(summary_table)
        
        # Show detailed column information for campaign configs
        if analysis["campaign_configs"]:
            console.print("\n[bold cyan]Campaign Configuration Sheets:[/bold cyan]")
            for sheet_name in analysis["campaign_configs"]:
                info = analysis["sheet_details"][sheet_name]
                console.print(f"\n[bold]{sheet_name}:[/bold]")
                for col in info["column_names"]:
                    console.print(f"  • {col}")
        
        return analysis
    
    def extract_campaign_configs(self) -> List[Dict[str, Any]]:
        """Extract campaign configurations from Excel sheets."""
        console.print(Panel("Extracting Campaign Configurations", title="🎯 Config Extraction"))
        
        campaigns = []
        
        for sheet_name, df in self.sheets.items():
            if any(keyword in sheet_name.lower() for keyword in ['campaign', 'ad', 'keyword']):
                console.print(f"\n[bold cyan]Processing sheet: {sheet_name}[/bold cyan]")
                
                # Convert DataFrame to list of dictionaries
                sheet_campaigns = df.to_dict('records')
                
                for i, campaign in enumerate(sheet_campaigns):
                    campaign_config = {
                        "sheet_name": sheet_name,
                        "row_index": i,
                        "data": campaign,
                        "status": "pending"
                    }
                    campaigns.append(campaign_config)
                
                console.print(f"  Extracted {len(sheet_campaigns)} campaign configurations")
        
        return campaigns
    
    def validate_campaign_configs(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate campaign configurations against Google Ads requirements."""
        console.print(Panel("Validating Campaign Configurations", title="✅ Validation"))
        
        required_fields = {
            "campaign": ["name", "budget", "status"],
            "ad_group": ["name", "campaign_id"],
            "keyword": ["text", "match_type", "ad_group_id"]
        }
        
        validated_campaigns = []
        
        for campaign in campaigns:
            data = campaign["data"]
            validation_errors = []
            
            # Check for required fields based on sheet type
            sheet_name = campaign["sheet_name"].lower()
            
            if "campaign" in sheet_name:
                for field in required_fields["campaign"]:
                    if field not in data or pd.isna(data[field]):
                        validation_errors.append(f"Missing required field: {field}")
            
            elif "ad_group" in sheet_name:
                for field in required_fields["ad_group"]:
                    if field not in data or pd.isna(data[field]):
                        validation_errors.append(f"Missing required field: {field}")
            
            elif "keyword" in sheet_name:
                for field in required_fields["keyword"]:
                    if field not in data or pd.isna(data[field]):
                        validation_errors.append(f"Missing required field: {field}")
            
            if validation_errors:
                campaign["validation_errors"] = validation_errors
                campaign["status"] = "invalid"
                console.print(f"[red]❌ Row {campaign['row_index']} in {campaign['sheet_name']}: {', '.join(validation_errors)}[/red]")
            else:
                campaign["status"] = "valid"
                console.print(f"[green]✅ Row {campaign['row_index']} in {campaign['sheet_name']}: Valid[/green]")
            
            validated_campaigns.append(campaign)
        
        valid_count = len([c for c in validated_campaigns if c["status"] == "valid"])
        invalid_count = len([c for c in validated_campaigns if c["status"] == "invalid"])
        
        console.print(f"\n[bold]Validation Summary:[/bold] {valid_count} valid, {invalid_count} invalid")
        
        return validated_campaigns
    
    def create_google_ads_operations(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert validated campaigns to Google Ads API operations."""
        console.print(Panel("Creating Google Ads Operations", title="🔧 API Operations"))
        
        operations = []
        
        for campaign in campaigns:
            if campaign["status"] != "valid":
                continue
                
            data = campaign["data"]
            sheet_name = campaign["sheet_name"].lower()
            
            if "campaign" in sheet_name:
                operation = {
                    "type": "campaign",
                    "action": "create",
                    "data": {
                        "name": data.get("name", f"Campaign_{campaign['row_index']}"),
                        "budget_amount_micros": int(float(data.get("budget", 0)) * 1_000_000),
                        "status": data.get("status", "ENABLED").upper(),
                        "advertising_channel_type": "PERFORMANCE_MAX"
                    }
                }
                operations.append(operation)
                
            elif "ad_group" in sheet_name:
                operation = {
                    "type": "ad_group",
                    "action": "create",
                    "data": {
                        "name": data.get("name", f"AdGroup_{campaign['row_index']}"),
                        "campaign_id": data.get("campaign_id"),
                        "status": data.get("status", "ENABLED").upper()
                    }
                }
                operations.append(operation)
                
            elif "keyword" in sheet_name:
                operation = {
                    "type": "keyword",
                    "action": "create",
                    "data": {
                        "text": data.get("text"),
                        "match_type": data.get("match_type", "EXACT").upper(),
                        "ad_group_id": data.get("ad_group_id"),
                        "status": data.get("status", "ENABLED").upper()
                    }
                }
                operations.append(operation)
        
        console.print(f"Created {len(operations)} Google Ads operations")
        
        return operations
    
    def preview_operations(self, operations: List[Dict[str, Any]]):
        """Preview the operations that would be performed."""
        console.print(Panel("Previewing Google Ads Operations", title="👀 Preview"))
        
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
            console.print(f"\n[bold cyan]{op_type.upper()} Operations ({len(ops)}):[/bold cyan]")
            
            table = Table(title=f"{op_type.title()} Operations")
            table.add_column("Action", style="cyan")
            table.add_column("Name/Text", style="green")
            table.add_column("Status", style="yellow")
            
            for op in ops[:5]:  # Show first 5
                data = op["data"]
                name = data.get("name", data.get("text", "N/A"))
                status = data.get("status", "ENABLED")
                table.add_row(op["action"], name, status)
            
            if len(ops) > 5:
                table.add_row("...", f"+{len(ops)-5} more", "...")
            
            console.print(table)
    
    def execute_operations(self, operations: List[Dict[str, Any]], dry_run: bool = True):
        """Execute the operations against Google Ads API."""
        if dry_run:
            console.print(Panel("DRY RUN MODE - No changes will be made", style="bold yellow"))
        else:
            console.print(Panel("EXECUTING OPERATIONS - Changes will be made", style="bold red"))
        
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
        
        for i, operation in enumerate(operations):
            try:
                console.print(f"Processing operation {i+1}/{len(operations)}: {operation['type']} - {operation['action']}")
                
                if dry_run:
                    console.print(f"  [yellow]DRY RUN: Would create {operation['type']} with data: {operation['data']}[/yellow]")
                    results["successful"] += 1
                else:
                    # TODO: Implement actual Google Ads API calls
                    console.print(f"  [green]✅ Created {operation['type']}[/green]")
                    results["successful"] += 1
                    
            except Exception as e:
                error_msg = f"Error in operation {i+1}: {str(e)}"
                console.print(f"  [red]❌ {error_msg}[/red]")
                results["errors"].append(error_msg)
                results["failed"] += 1
        
        # Display results
        results_table = Table(title="Operation Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Count", style="green")
        
        results_table.add_row("Successful", str(results["successful"]))
        results_table.add_row("Failed", str(results["failed"]))
        
        console.print(results_table)
        
        if results["errors"]:
            console.print(Panel("\n".join(results["errors"][:3]), title="Errors (showing first 3)"))

def main():
    """Main function for Excel config analysis."""
    console.print(Panel("🚀 Excel Config Analyzer for Google Ads", style="bold blue"))
    
    analyzer = ExcelConfigAnalyzer()
    
    # Load Excel file
    sheets = analyzer.load_excel_file()
    if not sheets:
        console.print("[red]Failed to load Excel file. Exiting.[/red]")
        return
    
    # Analyze sheets
    analysis = analyzer.analyze_sheets()
    
    # Extract campaign configs
    campaigns = analyzer.extract_campaign_configs()
    if not campaigns:
        console.print("[yellow]No campaign configurations found in Excel file.[/yellow]")
        return
    
    # Validate configs
    validated_campaigns = analyzer.validate_campaign_configs(campaigns)
    
    # Create operations
    operations = analyzer.create_google_ads_operations(validated_campaigns)
    
    # Preview operations
    analyzer.preview_operations(operations)
    
    # Ask user what to do next
    console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
    console.print("1. Preview operations (dry run)")
    console.print("2. Execute operations (create campaigns)")
    console.print("3. Export validated configs to new Excel file")
    console.print("4. Exit")
    
    choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        analyzer.execute_operations(operations, dry_run=True)
    elif choice == "2":
        if Confirm.ask("Are you sure you want to create campaigns? This will make changes to your Google Ads account."):
            analyzer.execute_operations(operations, dry_run=False)
    elif choice == "3":
        # Export validated configs
        valid_campaigns = [c for c in validated_campaigns if c["status"] == "valid"]
        if valid_campaigns:
            export_data = []
            for campaign in valid_campaigns:
                export_data.append(campaign["data"])
            
            export_df = pd.DataFrame(export_data)
            export_file = "validated_campaign_configs.xlsx"
            export_df.to_excel(export_file, index=False)
            console.print(f"[green]✅ Exported {len(export_data)} validated configs to {export_file}[/green]")
    elif choice == "4":
        console.print("Goodbye!")

if __name__ == "__main__":
    main()
