"""
Google Ads Manager - AI-Powered Campaign Management
==================================================

This module provides a comprehensive interface for managing Google Ads campaigns
using AI assistance. It includes methods for analyzing performance, making
bulk changes, and troubleshooting common issues.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from ads.lead_quality_engine import LeadQualityEngine, LeadQualityMetrics, LQSOptimizationRecommendation

console = Console()

class GoogleAdsManager:
    """AI-Powered Google Ads Campaign Manager"""
    
    def __init__(self, customer_id: Optional[str] = None):
        """Initialize the Google Ads Manager."""
        load_dotenv()
        
        self.customer_id = customer_id or os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
        if not self.customer_id:
            raise ValueError("Customer ID is required")
            
        self.client = self._build_client()
        self._initialize_services()
        self.lqs_engine = LeadQualityEngine()
        
    def _build_client(self) -> GoogleAdsClient:
        """Build the Google Ads client using environment variables."""
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
        
        client = GoogleAdsClient.load_from_dict(config)
        return client
    
    def _initialize_services(self):
        """Initialize Google Ads services."""
        self.customer_service = self.client.get_service("CustomerService")
        self.campaign_service = self.client.get_service("CampaignService")
        self.ad_group_service = self.client.get_service("AdGroupService")
        self.ad_service = self.client.get_service("AdService")
        self.ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
        self.google_ads_service = self.client.get_service("GoogleAdsService")
        
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information and display it."""
        try:
            # Use GoogleAdsService to get customer info
            query = f"""
                SELECT 
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.manager,
                    customer.test_account
                FROM customer 
                WHERE customer.id = {self.customer_id}
            """
            
            response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=query
            )
            
            customer = next(response)
            
            info = {
                "customer_id": self.customer_id,
                "descriptive_name": customer.descriptive_name,
                "currency_code": customer.currency_code,
                "time_zone": customer.time_zone,
                "manager": customer.manager,
                "test_account": customer.test_account,
            }
            
            # Display account info
            table = Table(title="Account Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in info.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            return info
            
        except GoogleAdsException as ex:
            console.print(f"[red]Error getting account info: {ex}[/red]")
            return {}
    
    def get_campaigns(self, status: Optional[str] = None) -> pd.DataFrame:
        """Get all campaigns and return as DataFrame."""
        query = """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.start_date,
                campaign.end_date,
                campaign.budget_amount_micros,
                campaign.optimization_score,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.average_cpc
            FROM campaign
        """
        
        if status:
            query += f" WHERE campaign.status = '{status}'"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Fetching campaigns...", total=None)
                
                response = self.google_ads_service.search(
                    customer_id=self.customer_id,
                    query=query
                )
                
                progress.update(task, completed=True)
            
            # Convert to DataFrame
            data = []
            for row in response:
                campaign_data = {
                    "campaign_id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "channel_type": row.campaign.advertising_channel_type.name,
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date,
                    "budget": row.campaign.budget_amount_micros / 1_000_000 if row.campaign.budget_amount_micros else 0,
                    "optimization_score": row.campaign.optimization_score,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "cost": row.metrics.cost_micros / 1_000_000 if row.metrics.cost_micros else 0,
                    "conversions": row.metrics.conversions,
                    "avg_cpc": row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                }
                data.append(campaign_data)
            
            df = pd.DataFrame(data)
            
            # Display summary
            if not df.empty:
                console.print(Panel(f"Found {len(df)} campaigns", title="Campaign Summary"))
                
                # Show performance summary
                summary_table = Table(title="Performance Summary")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="green")
                
                summary_table.add_row("Total Campaigns", str(len(df)))
                summary_table.add_row("Active Campaigns", str(len(df[df['status'] == 'ENABLED'])))
                summary_table.add_row("Total Impressions", f"{df['impressions'].sum():,}")
                summary_table.add_row("Total Clicks", f"{df['clicks'].sum():,}")
                summary_table.add_row("Total Cost", f"${df['cost'].sum():.2f}")
                summary_table.add_row("Total Conversions", f"{df['conversions'].sum():.2f}")
                summary_table.add_row("Avg CPC", f"${df['avg_cpc'].mean():.2f}")
                
                console.print(summary_table)
            
            return df
            
        except GoogleAdsException as ex:
            console.print(f"[red]Error fetching campaigns: {ex}[/red]")
            return pd.DataFrame()
    
    def analyze_performance(self, days: int = 30) -> Dict[str, Any]:
        """Analyze campaign performance and provide insights."""
        console.print(Panel("Analyzing Campaign Performance", title="AI Analysis"))
        
        # Get campaigns with performance data
        df = self.get_campaigns()
        if df.empty:
            return {}
        
        # Filter for recent data
        recent_df = df.copy()
        
        # Calculate key metrics
        total_cost = recent_df['cost'].sum()
        total_clicks = recent_df['clicks'].sum()
        total_impressions = recent_df['impressions'].sum()
        total_conversions = recent_df['conversions'].sum()
        
        # Calculate rates
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpa = (total_cost / total_conversions) if total_conversions > 0 else 0
        
        # Performance insights
        insights = {
            "total_campaigns": len(recent_df),
            "active_campaigns": len(recent_df[recent_df['status'] == 'ENABLED']),
            "total_cost": total_cost,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_conversions": total_conversions,
            "ctr": ctr,
            "cpc": cpc,
            "conversion_rate": conversion_rate,
            "cpa": cpa,
            "recommendations": []
        }
        
        # Generate AI recommendations
        recommendations = []
        
        # Low CTR campaigns
        if 'ctr' in recent_df.columns:
            low_ctr_campaigns = recent_df[recent_df['ctr'] < 1.0]
            if not low_ctr_campaigns.empty:
                recommendations.append({
                    "type": "Low CTR",
                    "message": f"{len(low_ctr_campaigns)} campaigns have CTR below 1%. Consider improving ad copy and targeting.",
                    "priority": "high"
                })
        
        # High CPC campaigns
        if 'avg_cpc' in recent_df.columns:
            high_cpc_campaigns = recent_df[recent_df['avg_cpc'] > 2.0]
            if not high_cpc_campaigns.empty:
                recommendations.append({
                    "type": "High CPC",
                    "message": f"{len(high_cpc_campaigns)} campaigns have high CPC. Review keyword bids and quality scores.",
                    "priority": "medium"
                })
        
        # Zero conversion campaigns
        zero_conv_campaigns = recent_df[recent_df['conversions'] == 0]
        if not zero_conv_campaigns.empty:
            recommendations.append({
                "type": "No Conversions",
                "message": f"{len(zero_conv_campaigns)} campaigns have no conversions. Review landing pages and conversion tracking.",
                "priority": "high"
            })
        
        insights["recommendations"] = recommendations
        
        # Display analysis
        analysis_table = Table(title="Performance Analysis")
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Value", style="green")
        analysis_table.add_column("Status", style="yellow")
        
        analysis_table.add_row("CTR", f"{ctr:.2f}%", "⚠️ Low" if ctr < 1.0 else "✅ Good")
        analysis_table.add_row("CPC", f"${cpc:.2f}", "⚠️ High" if cpc > 2.0 else "✅ Good")
        analysis_table.add_row("Conversion Rate", f"{conversion_rate:.2f}%", "⚠️ Low" if conversion_rate < 1.0 else "✅ Good")
        analysis_table.add_row("CPA", f"${cpa:.2f}", "⚠️ High" if cpa > 50.0 else "✅ Good")
        
        console.print(analysis_table)
        
        # Display recommendations
        if recommendations:
            rec_table = Table(title="AI Recommendations")
            rec_table.add_column("Type", style="cyan")
            rec_table.add_column("Message", style="green")
            rec_table.add_column("Priority", style="yellow")
            
            for rec in recommendations:
                priority_icon = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                rec_table.add_row(rec["type"], rec["message"], f"{priority_icon} {rec['priority']}")
            
            console.print(rec_table)
        
        return insights
    
    def troubleshoot_issues(self) -> Dict[str, Any]:
        """Troubleshoot common Google Ads issues."""
        console.print(Panel("Troubleshooting Google Ads Issues", title="AI Troubleshooting"))
        
        issues = {
            "account_issues": [],
            "campaign_issues": [],
            "billing_issues": [],
            "recommendations": []
        }
        
        # Check account status
        try:
            account_info = self.get_account_info()
            if account_info.get("test_account"):
                issues["account_issues"].append("Account is a test account - limited functionality")
        except Exception as e:
            issues["account_issues"].append(f"Account access issue: {str(e)}")
        
        # Check campaign performance
        campaigns_df = self.get_campaigns()
        if not campaigns_df.empty:
            # Check for paused campaigns
            paused_campaigns = campaigns_df[campaigns_df['status'] == 'PAUSED']
            if not paused_campaigns.empty:
                issues["campaign_issues"].append(f"{len(paused_campaigns)} campaigns are paused")
            
            # Check for campaigns with no impressions
            no_impressions = campaigns_df[campaigns_df['impressions'] == 0]
            if not no_impressions.empty:
                issues["campaign_issues"].append(f"{len(no_impressions)} campaigns have no impressions")
            
            # Check for campaigns with high cost but no conversions
            high_cost_no_conv = campaigns_df[
                (campaigns_df['cost'] > 100) & 
                (campaigns_df['conversions'] == 0)
            ]
            if not high_cost_no_conv.empty:
                issues["campaign_issues"].append(f"{len(high_cost_no_conv)} campaigns have high cost but no conversions")
        
        # Generate recommendations
        if issues["account_issues"]:
            issues["recommendations"].append("Review account settings and permissions")
        
        if issues["campaign_issues"]:
            issues["recommendations"].append("Review campaign settings and performance")
        
        if not issues["account_issues"] and not issues["campaign_issues"]:
            issues["recommendations"].append("Account appears healthy - focus on optimization")
        
        # Display issues
        for category, category_issues in issues.items():
            if category_issues:
                console.print(f"\n[bold cyan]{category.replace('_', ' ').title()}:[/bold cyan]")
                for issue in category_issues:
                    console.print(f"  • {issue}")
        
        return issues
    
    def analyze_lead_quality_performance(self, leads_data: List[Dict], period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze campaign performance using Lead Quality Score metrics.
        
        Args:
            leads_data: List of lead dictionaries with 'lqs' field
            period_days: Number of days in the analysis period
            
        Returns:
            Dictionary containing LQS-based performance analysis
        """
        console.print(Panel("🎯 Lead Quality Score Analysis", title="LQS Performance Analysis"))
        
        # Get campaign cost for the period
        campaign_cost = self._get_campaign_cost_for_period(period_days)
        
        # Calculate LQS metrics
        lqs_metrics = self.lqs_engine.calculate_lead_quality_metrics(leads_data, campaign_cost, period_days)
        
        # Get current campaign settings
        current_budget = self._get_current_daily_budget()
        current_tcpa = self._get_current_tcpa()
        
        # Generate optimization recommendation
        recommendation = self.lqs_engine.generate_optimization_recommendation(
            lqs_metrics, current_budget, current_tcpa
        )
        
        # Get performance summary
        performance_summary = self.lqs_engine.get_performance_summary(lqs_metrics)
        
        # Display LQS metrics
        lqs_table = Table(title="Lead Quality Score Metrics")
        lqs_table.add_column("Metric", style="cyan")
        lqs_table.add_column("Value", style="green")
        lqs_table.add_column("Status", style="yellow")
        
        lqs_table.add_row("Total Leads", str(lqs_metrics.total_leads), "✅" if lqs_metrics.total_leads > 0 else "⚠️")
        lqs_table.add_row("High Quality Leads", str(lqs_metrics.high_quality_leads), "✅" if lqs_metrics.high_quality_leads > 0 else "⚠️")
        lqs_table.add_row("Average LQS", f"{lqs_metrics.average_lqs:.1f}", "✅" if lqs_metrics.average_lqs >= 6.0 else "⚠️")
        lqs_table.add_row("High Quality Ratio", f"{lqs_metrics.high_quality_ratio:.1%}", "✅" if lqs_metrics.high_quality_ratio >= 0.4 else "⚠️")
        lqs_table.add_row("Cost per Lead", f"${lqs_metrics.cpl:.2f}", "✅" if lqs_metrics.cpl <= 100 else "⚠️")
        lqs_table.add_row("Cost per High-Quality Lead", f"${lqs_metrics.cphql:.2f}", "✅" if lqs_metrics.cphql <= 300 else "⚠️")
        
        console.print(lqs_table)
        
        # Display recommendation
        if recommendation.action != "maintain":
            rec_table = Table(title="LQS Optimization Recommendation")
            rec_table.add_column("Action", style="cyan")
            rec_table.add_column("Confidence", style="green")
            rec_table.add_column("Reasoning", style="yellow")
            
            rec_table.add_row(
                recommendation.action.replace("_", " ").title(),
                f"{recommendation.confidence:.0%}",
                "; ".join(recommendation.reasoning[:2])  # Show first 2 reasons
            )
            
            console.print(rec_table)
        
        # Display performance summary
        summary_table = Table(title="Performance Summary")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Performance Level", performance_summary["performance_level"].title())
        summary_table.add_row("Primary Metric", performance_summary["primary_metric"])
        summary_table.add_row("Primary Value", f"${performance_summary['primary_value']:.2f}")
        summary_table.add_row("Primary Target", f"${performance_summary['primary_target']:.2f}")
        summary_table.add_row("Focus Area", performance_summary["recommendations"]["focus_area"].replace("_", " ").title())
        summary_table.add_row("Priority", performance_summary["recommendations"]["priority"].title())
        
        console.print(summary_table)
        
        return {
            "lqs_metrics": lqs_metrics.to_dict(),
            "recommendation": recommendation.to_dict(),
            "performance_summary": performance_summary
        }
    
    def _get_campaign_cost_for_period(self, period_days: int) -> float:
        """Get campaign cost for the specified period."""
        try:
            query = f"""
            SELECT metrics.cost_micros
            FROM campaign 
            WHERE campaign.name = "L.R - PMax - General"
            AND segments.date DURING LAST_{period_days}_DAYS
            """
            
            response = self.google_ads_service.search(customer_id=self.customer_id, query=query)
            data = list(response)
            
            if data:
                return data[0].metrics.cost_micros / 1000000  # Convert from micros
            else:
                return 0.0
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not get campaign cost: {str(e)}[/yellow]")
            return 0.0
    
    def _get_current_daily_budget(self) -> float:
        """Get current daily budget."""
        try:
            query = """
            SELECT campaign_budget.amount_micros
            FROM campaign 
            WHERE campaign.name = "L.R - PMax - General"
            """
            
            response = self.google_ads_service.search(customer_id=self.customer_id, query=query)
            data = list(response)
            
            if data:
                return data[0].campaign_budget.amount_micros / 1000000  # Convert from micros
            else:
                return 50.0  # Default budget
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not get daily budget: {str(e)}[/yellow]")
            return 50.0
    
    def _get_current_tcpa(self) -> float:
        """Get current target CPA."""
        try:
            query = """
            SELECT campaign.target_cpa_micros
            FROM campaign 
            WHERE campaign.name = "L.R - PMax - General"
            """
            
            response = self.google_ads_service.search(customer_id=self.customer_id, query=query)
            data = list(response)
            
            if data and hasattr(data[0].campaign, 'target_cpa_micros'):
                return data[0].campaign.target_cpa_micros / 1000000  # Convert from micros
            else:
                return 100.0  # Default tCPA
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not get target CPA: {str(e)}[/yellow]")
            return 100.0

def main():
    """Main function for testing the Google Ads Manager."""
    try:
        manager = GoogleAdsManager()
        
        # Get account info
        manager.get_account_info()
        
        # Analyze performance
        manager.analyze_performance()
        
        # Troubleshoot issues
        manager.troubleshoot_issues()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
