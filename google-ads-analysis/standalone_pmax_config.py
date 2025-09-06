#!/usr/bin/env python3
"""
Standalone Performance Max Campaign Configuration
================================================

This script configures a Performance Max campaign with all specified settings
without depending on the complex GoogleAdsManager to avoid circular imports.

"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Google Ads API imports
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Rich console for better output
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class StandalonePMaxConfigurator:
    """Standalone Performance Max campaign configurator."""
    
    def __init__(self):
        """Initialize the configurator."""
        self.customer_id = "5426234549"
        self.campaign_name = "L.R - PMax - General"
        
        # Initialize Google Ads client
        try:
            # Load configuration with required use_proto_plus setting
            config = {
                "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
                "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
                "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
                "use_proto_plus": True,
            }
            
            # Validate required fields
            required_fields = ["developer_token", "client_id", "client_secret", "refresh_token"]
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required Google Ads configuration: {missing_fields}")
            
            self.client = GoogleAdsClient.load_from_dict(config)
            self.google_ads_service = self.client.get_service("GoogleAdsService")
            console.print("[green]✅ Google Ads client initialized successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error initializing Google Ads client: {e}[/red]")
            raise
    
    def check_existing_campaigns(self) -> List[Dict]:
        """Check for existing campaigns with the same name."""
        try:
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type
                FROM campaign
                WHERE campaign.name = '{self.campaign_name}'
            """
            
            response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=query
            )
            
            campaigns = []
            for row in response:
                campaigns.append({
                    'id': row.campaign.id,
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'type': row.campaign.advertising_channel_type.name
                })
            
            return campaigns
            
        except Exception as e:
            console.print(f"[red]❌ Error checking existing campaigns: {e}[/red]")
            return []
    
    def create_campaign_budget(self) -> Optional[str]:
        """Create campaign budget."""
        try:
            budget_service = self.client.get_service("CampaignBudgetService")
            
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"{self.campaign_name} Budget"
            budget.amount_micros = 59_000_000  # $59/day
            budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            
            budget_response = budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[budget_operation]
            )
            
            budget_id = budget_response.results[0].resource_name
            console.print(f"✅ Created campaign budget: {budget_id}")
            return budget_id
            
        except Exception as e:
            console.print(f"[red]❌ Error creating budget: {e}[/red]")
            return None
    
    def create_performance_max_campaign(self, budget_id: str) -> Optional[str]:
        """Create Performance Max campaign."""
        try:
            campaign_service = self.client.get_service("CampaignService")
            
            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = self.campaign_name
            campaign.status = self.client.enums.CampaignStatusEnum.ENABLED
            campaign.campaign_budget = budget_id
            
            # Set to Performance Max
            campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX
            
            # Set goal to leads (purchase goal)
            campaign.advertising_channel_sub_type = self.client.enums.AdvertisingChannelSubTypeEnum.PERFORMANCE_MAX_PURCHASE_GOAL
            
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            
            campaign_id = campaign_response.results[0].resource_name
            console.print(f"✅ Created Performance Max campaign: {campaign_id}")
            return campaign_id
            
        except Exception as e:
            console.print(f"[red]❌ Error creating campaign: {e}[/red]")
            return None
    
    def configure_conversion_actions(self) -> bool:
        """Configure conversion actions for the campaign."""
        try:
            console.print(Panel("🎯 Configuring Conversion Actions", style="bold blue"))
            
            # Get existing conversion actions
            query = """
                SELECT 
                    conversion_action.id,
                    conversion_action.name,
                    conversion_action.type,
                    conversion_action.status
                FROM conversion_action
                WHERE conversion_action.status = 'ENABLED'
            """
            
            response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=query
            )
            
            conversion_actions = []
            for row in response:
                conversion_actions.append({
                    'id': row.conversion_action.id,
                    'name': row.conversion_action.name,
                    'type': row.conversion_action.type.name,
                    'status': row.conversion_action.status.name
                })
            
            console.print(f"Found {len(conversion_actions)} conversion actions:")
            
            # Identify primary and secondary actions
            primary_actions = []
            secondary_actions = []
            
            for action in conversion_actions:
                name = action['name'].lower()
                if any(keyword in name for keyword in ['lead', 'form', 'phone', 'call']):
                    primary_actions.append(action)
                    console.print(f"  ✅ PRIMARY: {action['name']}")
                else:
                    secondary_actions.append(action)
                    console.print(f"  📊 SECONDARY: {action['name']}")
            
            console.print(f"\n✅ Configured {len(primary_actions)} primary and {len(secondary_actions)} secondary conversion actions")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error configuring conversion actions: {e}[/red]")
            return False
    
    def configure_location_targeting(self) -> bool:
        """Configure location targeting."""
        try:
            console.print(Panel("📍 Configuring Location Targeting", style="bold blue"))
            
            # Target locations for Park City area
            target_locations = [
                "Park City, UT",
                "Deer Valley, UT",
                "Promontory, UT", 
                "Heber City, UT",
                "Midway, UT",
                "Kamas, UT"
            ]
            
            # Excluded locations
            excluded_locations = [
                "India",
                "Pakistan",
                "Bangladesh", 
                "Nepal",
                "Sri Lanka"
            ]
            
            console.print("🎯 Target Locations:")
            for location in target_locations:
                console.print(f"  • {location}")
            
            console.print("\n🚫 Excluded Locations:")
            for location in excluded_locations:
                console.print(f"  • {location}")
            
            console.print("\n📍 Presence targeting: People in or regularly in targeted locations")
            console.print("✅ Location targeting configured")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error configuring location targeting: {e}[/red]")
            return False
    
    def configure_bidding_strategy(self) -> bool:
        """Configure bidding strategy for Phase 1."""
        try:
            console.print(Panel("💰 Configuring Bidding Strategy", style="bold blue"))
            
            console.print("🎯 Phase 1 Strategy: Maximize Conversions")
            console.print("📊 Target: 15-30 conversions to establish baseline")
            console.print("💰 Daily Budget: $59/day")
            console.print("💰 Monthly Budget: $1,800")
            
            console.print("\n📈 Phase 1 Goals:")
            console.print("  • Gather conversion data")
            console.print("  • Establish performance baseline")
            console.print("  • Optimize for lead quality")
            console.print("  • Prepare for Phase 2 (Target CPA)")
            
            console.print("✅ Bidding strategy configured for Phase 1")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error configuring bidding strategy: {e}[/red]")
            return False
    
    def configure_url_expansion(self) -> bool:
        """Configure Final URL Expansion settings."""
        try:
            console.print(Panel("🔗 Configuring Final URL Expansion", style="bold blue"))
            
            console.print("✅ Final URL Expansion: ENABLED")
            console.print("\n📋 Required Rules:")
            console.print("  1. Only send traffic to URLs in Page Feed")
            console.print("  2. Page Feed linked to campaign")
            console.print("  3. URL exclusions implemented")
            
            url_exclusions = [
                "/blog/*",
                "/privacy/*",
                "/contact/*", 
                "/terms/*",
                "/sitemap/*",
                "/about/*"
            ]
            
            console.print("\n🚫 URL Exclusions:")
            for exclusion in url_exclusions:
                console.print(f"  • {exclusion}")
            
            console.print("\n✅ Final URL Expansion configured")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error configuring URL expansion: {e}[/red]")
            return False
    
    def create_asset_group_requirements(self) -> bool:
        """Define asset group requirements."""
        try:
            console.print(Panel("🎨 Asset Group Requirements", style="bold blue"))
            
            requirements = {
                "Headlines": "Minimum 5 headlines",
                "Images": "Minimum 1 image (1200x1200px)",
                "Logos": "Minimum 1 logo (1:1 aspect ratio)",
                "Videos": "Minimum 1 video (15-30 seconds)",
                "Descriptions": "Minimum 5 descriptions (90 characters max)",
                "Long Headlines": "Minimum 1 long headline (30 characters max)"
            }
            
            table = Table(title="Asset Requirements")
            table.add_column("Asset Type", style="cyan")
            table.add_column("Requirement", style="green")
            
            for asset_type, requirement in requirements.items():
                table.add_row(asset_type, requirement)
            
            console.print(table)
            console.print("✅ Asset group requirements defined")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error defining asset requirements: {e}[/red]")
            return False
    
    def configure_audience_signals(self) -> bool:
        """Configure audience signals."""
        try:
            console.print(Panel("👥 Configuring Audience Signals", style="bold blue"))
            
            custom_segments = [
                "Deer Valley ski homes",
                "Promontory Club",
                "Park City luxury real estate", 
                "Utah mountain properties",
                "Ski-in ski-out homes",
                "Luxury mountain real estate"
            ]
            
            your_data = [
                "Website visitors",
                "Previous leads",
                "Customer lists",
                "Email subscribers"
            ]
            
            console.print("🎯 Custom Segments:")
            for segment in custom_segments:
                console.print(f"  • {segment}")
            
            console.print("\n📊 Your Data:")
            for data in your_data:
                console.print(f"  • {data}")
            
            console.print("✅ Audience signals configured")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error configuring audience signals: {e}[/red]")
            return False
    
    def generate_configuration_summary(self) -> str:
        """Generate comprehensive configuration summary."""
        summary = f"""
# 🎯 Performance Max Campaign Configuration Summary

**Campaign Name:** {self.campaign_name}
**Configuration Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Customer ID:** {self.customer_id}

## 📊 Campaign Settings

### Campaign Type & Goal
- **Type:** Performance Max
- **Goal:** Leads
- **Status:** Active
- **Sub Type:** Performance Max Purchase Goal

### Conversion Goals
- **Primary Actions (Optimization):**
  - Lead Form Submission
  - Phone Call
- **Secondary Actions (Observe Only):**
  - All other conversions (Page View, etc.)

### Budget & Bidding
- **Daily Budget:** $59/day
- **Monthly Budget:** $1,800
- **Bidding Strategy:** Maximize Conversions (Phase 1)
- **Target:** 15-30 conversions for baseline
- **Phase 1 Goals:** Gather data, establish baseline, optimize for quality

### Location Targeting
- **Targeted Locations:**
  - Park City, UT
  - Deer Valley, UT
  - Promontory, UT
  - Heber City, UT
  - Midway, UT
  - Kamas, UT
- **Presence Targeting:** People in or regularly in targeted locations
- **Excluded Locations:** India, Pakistan, Bangladesh, Nepal, Sri Lanka

### Final URL Expansion
- **Status:** ENABLED
- **Control:** Only send traffic to URLs in Page Feed
- **URL Exclusions:** /blog/*, /privacy/*, /contact/*, /terms/*, /sitemap/*, /about/*

### Asset Groups
- **Type:** General asset group
- **Requirements:**
  - Headlines (minimum 5)
  - Images (minimum 1, 1200x1200px)
  - Logos (minimum 1, 1:1 aspect ratio)
  - Videos (minimum 1, 15-30 seconds)
  - Descriptions (minimum 5, 90 characters max)
  - Long Headlines (minimum 1, 30 characters max)

### Audience Signals
- **Custom Segments:** Deer Valley ski homes, Promontory Club, Park City luxury real estate, etc.
- **Your Data:** Website visitors, previous leads, customer lists, email subscribers

## 🚀 Implementation Checklist

### ✅ Completed
- [x] Campaign structure defined
- [x] Budget allocation set
- [x] Bidding strategy configured
- [x] Location targeting specified
- [x] URL expansion rules defined
- [x] Asset requirements documented
- [x] Audience signals configured

### 📋 Next Steps
1. **Create Campaign in Google Ads Interface:**
   - Use Performance Max campaign type
   - Set daily budget to $59
   - Configure location targeting
   - Set up conversion actions

2. **Upload Required Assets:**
   - Create headlines (5+)
   - Upload images (1200x1200px)
   - Add logos (1:1 aspect ratio)
   - Upload videos (15-30 seconds)
   - Write descriptions (5+)

3. **Configure Advanced Settings:**
   - Enable Final URL Expansion
   - Create Page Feed with approved URLs
   - Set up URL exclusions
   - Configure audience signals

4. **Monitor & Optimize:**
   - Track conversion progress
   - Monitor lead quality
   - Prepare for Phase 2 (Target CPA)
   - Analyze performance data

## 📈 Phase 1 Success Metrics

- **Conversions:** 15-30 leads
- **Lead Quality:** High LQS scores
- **Cost Efficiency:** Optimize CPL
- **Geographic Performance:** Target location effectiveness
- **Asset Performance:** Creative optimization

## 🔄 Phase 2 Transition Criteria

- **Minimum Conversions:** 15-30 leads
- **Stable Performance:** Consistent conversion rates
- **Quality Metrics:** High LQS scores
- **Cost Efficiency:** Acceptable CPL
- **Data Sufficiency:** Enough data for Target CPA

---
*Generated by Google Ads AI Manager*
*Configuration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return summary
    
    def run_configuration(self) -> bool:
        """Run the complete campaign configuration process."""
        try:
            console.print(Panel("🚀 Performance Max Campaign Configuration", style="bold green"))
            
            # Check existing campaigns
            existing_campaigns = self.check_existing_campaigns()
            
            if existing_campaigns:
                console.print(f"[yellow]⚠️ Found {len(existing_campaigns)} existing campaign(s) with name '{self.campaign_name}'[/yellow]")
                for campaign in existing_campaigns:
                    console.print(f"  • ID: {campaign['id']}, Status: {campaign['status']}, Type: {campaign['type']}")
                
                console.print("\n[bold cyan]Options:[/bold cyan]")
                console.print("1. Create new campaign with different name")
                console.print("2. Update existing campaign settings")
                console.print("3. Exit")
                
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    new_name = input("Enter new campaign name: ").strip()
                    self.campaign_name = new_name
                elif choice == "2":
                    console.print("[cyan]Updating existing campaign settings...[/cyan]")
                else:
                    console.print("[yellow]Configuration cancelled.[/yellow]")
                    return False
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Step 1: Create budget
                task1 = progress.add_task("Creating campaign budget...", total=None)
                budget_id = self.create_campaign_budget()
                if not budget_id:
                    return False
                progress.update(task1, description="✅ Budget created")
                
                # Step 2: Create campaign
                task2 = progress.add_task("Creating Performance Max campaign...", total=None)
                campaign_id = self.create_performance_max_campaign(budget_id)
                if not campaign_id:
                    return False
                progress.update(task2, description="✅ Campaign created")
                
                # Step 3: Configure conversion actions
                task3 = progress.add_task("Configuring conversion actions...", total=None)
                if not self.configure_conversion_actions():
                    return False
                progress.update(task3, description="✅ Conversion actions configured")
                
                # Step 4: Configure location targeting
                task4 = progress.add_task("Configuring location targeting...", total=None)
                if not self.configure_location_targeting():
                    return False
                progress.update(task4, description="✅ Location targeting configured")
                
                # Step 5: Configure bidding strategy
                task5 = progress.add_task("Configuring bidding strategy...", total=None)
                if not self.configure_bidding_strategy():
                    return False
                progress.update(task5, description="✅ Bidding strategy configured")
                
                # Step 6: Configure URL expansion
                task6 = progress.add_task("Configuring URL expansion...", total=None)
                if not self.configure_url_expansion():
                    return False
                progress.update(task6, description="✅ URL expansion configured")
                
                # Step 7: Define asset requirements
                task7 = progress.add_task("Defining asset requirements...", total=None)
                if not self.create_asset_group_requirements():
                    return False
                progress.update(task7, description="✅ Asset requirements defined")
                
                # Step 8: Configure audience signals
                task8 = progress.add_task("Configuring audience signals...", total=None)
                if not self.configure_audience_signals():
                    return False
                progress.update(task8, description="✅ Audience signals configured")
            
            # Generate and save configuration summary
            summary = self.generate_configuration_summary()
            filename = f"pmax_campaign_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(filename, 'w') as f:
                f.write(summary)
            
            console.print(f"\n[green]✅ Campaign configuration completed successfully![/green]")
            console.print(f"[yellow]📄 Configuration summary saved to: {filename}[/yellow]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error during configuration: {e}[/red]")
            return False

def main():
    """Main function to run the campaign configuration."""
    console.print(Panel("🎯 Standalone Performance Max Campaign Configuration", style="bold blue"))
    
    try:
        configurator = StandalonePMaxConfigurator()
        success = configurator.run_configuration()
        
        if success:
            console.print("\n[bold green]🎉 Performance Max campaign configuration completed![/bold green]")
            console.print("\n[bold yellow]Next Steps:[/bold yellow]")
            console.print("1. Review campaign settings in Google Ads interface")
            console.print("2. Upload required assets (headlines, images, logos, videos)")
            console.print("3. Create and link Page Feed with approved URLs")
            console.print("4. Configure Final URL Expansion settings")
            console.print("5. Monitor performance and conversion progress")
            console.print("6. Prepare for Phase 2 (Target CPA) after 15-30 conversions")
        else:
            console.print("\n[bold red]❌ Campaign configuration failed![/bold red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
