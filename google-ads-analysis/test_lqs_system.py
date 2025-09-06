#!/usr/bin/env python3
"""
Test LQS System
==============

Test script to demonstrate the new Lead Quality Score based optimization system.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ads.lead_quality_engine import LeadQualityEngine, LeadQualityMetrics

console = Console()

def test_lqs_system():
    """Test the new LQS-based optimization system."""
    
    console.print(Panel("🎯 Testing Lead Quality Score System", style="bold blue"))
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize the LQS engine
        lqs_engine = LeadQualityEngine()
        console.print("✅ LQS Engine initialized")
        
        # Create sample lead data (simulating Sierra Interactive data)
        sample_leads = [
            {"id": "lead_001", "lqs": 8, "source": "google_ads", "date": "2024-01-01"},
            {"id": "lead_002", "lqs": 6, "source": "google_ads", "date": "2024-01-02"},
            {"id": "lead_003", "lqs": 9, "source": "google_ads", "date": "2024-01-03"},
            {"id": "lead_004", "lqs": 4, "source": "google_ads", "date": "2024-01-04"},
            {"id": "lead_005", "lqs": 7, "source": "google_ads", "date": "2024-01-05"},
            {"id": "lead_006", "lqs": 5, "source": "google_ads", "date": "2024-01-06"},
            {"id": "lead_007", "lqs": 8, "source": "google_ads", "date": "2024-01-07"},
            {"id": "lead_008", "lqs": 3, "source": "google_ads", "date": "2024-01-08"},
            {"id": "lead_009", "lqs": 6, "source": "google_ads", "date": "2024-01-09"},
            {"id": "lead_010", "lqs": 7, "source": "google_ads", "date": "2024-01-10"},
            {"id": "lead_011", "lqs": 9, "source": "google_ads", "date": "2024-01-11"},
            {"id": "lead_012", "lqs": 5, "source": "google_ads", "date": "2024-01-12"},
            {"id": "lead_013", "lqs": 8, "source": "google_ads", "date": "2024-01-13"},
            {"id": "lead_014", "lqs": 4, "source": "google_ads", "date": "2024-01-14"},
            {"id": "lead_015", "lqs": 7, "source": "google_ads", "date": "2024-01-15"},
        ]
        
        console.print(f"📊 Sample lead data: {len(sample_leads)} leads")
        
        # Calculate LQS metrics
        total_cost = 1500.0  # Simulated cost for the period
        lqs_metrics = lqs_engine.calculate_lead_quality_metrics(sample_leads, total_cost, 30)
        
        # Display LQS metrics
        lqs_table = Table(title="Lead Quality Score Metrics")
        lqs_table.add_column("Metric", style="cyan")
        lqs_table.add_column("Value", style="green")
        lqs_table.add_column("Status", style="yellow")
        
        lqs_table.add_row("Total Leads", str(lqs_metrics.total_leads), "✅")
        lqs_table.add_row("High Quality Leads (LQS ≥5)", str(lqs_metrics.high_quality_leads), "✅" if lqs_metrics.high_quality_leads >= 8 else "⚠️")
        lqs_table.add_row("Medium Quality Leads (LQS 3-4)", str(lqs_metrics.medium_quality_leads), "✅")
        lqs_table.add_row("Low Quality Leads (LQS 1-2)", str(lqs_metrics.low_quality_leads), "✅" if lqs_metrics.low_quality_leads <= 2 else "⚠️")
        lqs_table.add_row("Average LQS", f"{lqs_metrics.average_lqs:.1f}", "✅" if lqs_metrics.average_lqs >= 6.0 else "⚠️")
        lqs_table.add_row("High Quality Ratio", f"{lqs_metrics.high_quality_ratio:.1%}", "✅" if lqs_metrics.high_quality_ratio >= 0.4 else "⚠️")
        lqs_table.add_row("Cost per Lead", f"${lqs_metrics.cpl:.2f}", "✅" if lqs_metrics.cpl <= 100 else "⚠️")
        lqs_table.add_row("Cost per High-Quality Lead", f"${lqs_metrics.cphql:.2f}", "✅" if lqs_metrics.cphql <= 300 else "⚠️")
        
        console.print(lqs_table)
        
        # Generate optimization recommendation
        current_budget = 50.0
        current_tcpa = 100.0
        
        recommendation = lqs_engine.generate_optimization_recommendation(
            lqs_metrics, current_budget, current_tcpa
        )
        
        # Display recommendation
        if recommendation.action != "maintain":
            rec_table = Table(title="LQS Optimization Recommendation")
            rec_table.add_column("Action", style="cyan")
            rec_table.add_column("Confidence", style="green")
            rec_table.add_column("Reasoning", style="yellow")
            
            rec_table.add_row(
                recommendation.action.replace("_", " ").title(),
                f"{recommendation.confidence:.0%}",
                "; ".join(recommendation.reasoning[:2])
            )
            
            console.print(rec_table)
            
            # Display expected impact
            impact_table = Table(title="Expected Impact")
            impact_table.add_column("Metric", style="cyan")
            impact_table.add_column("Current", style="green")
            impact_table.add_column("Expected", style="yellow")
            
            impact = recommendation.expected_impact
            if "budget_adjustment" in impact:
                impact_table.add_row("Budget", f"${current_budget:.2f}/day", impact["budget_adjustment"])
            if "expected_high_quality_leads" in impact:
                impact_table.add_row("High-Quality Leads", str(lqs_metrics.high_quality_leads), str(impact["expected_high_quality_leads"]))
            if "expected_cphql" in impact:
                impact_table.add_row("CpHQL", f"${lqs_metrics.cphql:.2f}", f"${impact['expected_cphql']:.2f}")
            
            console.print(impact_table)
        
        # Get performance summary
        performance_summary = lqs_engine.get_performance_summary(lqs_metrics)
        
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
        
        # Test different scenarios
        console.print("\n🔍 Testing Different Scenarios:")
        
        scenarios = [
            {
                "name": "High Performance Scenario",
                "leads": [{"lqs": 8} for _ in range(10)] + [{"lqs": 9} for _ in range(5)],
                "cost": 1200.0
            },
            {
                "name": "Low Performance Scenario",
                "leads": [{"lqs": 3} for _ in range(8)] + [{"lqs": 4} for _ in range(7)],
                "cost": 1800.0
            },
            {
                "name": "Mixed Performance Scenario",
                "leads": [{"lqs": 7} for _ in range(6)] + [{"lqs": 4} for _ in range(6)] + [{"lqs": 2} for _ in range(3)],
                "cost": 1500.0
            }
        ]
        
        for scenario in scenarios:
            scenario_metrics = lqs_engine.calculate_lead_quality_metrics(scenario["leads"], scenario["cost"], 30)
            scenario_recommendation = lqs_engine.generate_optimization_recommendation(
                scenario_metrics, current_budget, current_tcpa
            )
            
            scenario_table = Table(title=f"Scenario: {scenario['name']}")
            scenario_table.add_column("Metric", style="cyan")
            scenario_table.add_column("Value", style="green")
            scenario_table.add_column("Recommendation", style="yellow")
            
            scenario_table.add_row("Average LQS", f"{scenario_metrics.average_lqs:.1f}", "")
            scenario_table.add_row("CpHQL", f"${scenario_metrics.cphql:.2f}", "")
            scenario_table.add_row("High Quality Ratio", f"{scenario_metrics.high_quality_ratio:.1%}", "")
            scenario_table.add_row("Action", "", scenario_recommendation.action.replace("_", " ").title())
            scenario_table.add_row("Confidence", "", f"{scenario_recommendation.confidence:.0%}")
            
            console.print(scenario_table)
        
        # Summary
        console.print(Panel("🎉 LQS System Test Complete!", style="bold green"))
        console.print("✅ LQS Engine: Working")
        console.print("✅ Metrics Calculation: Working")
        console.print("✅ Optimization Logic: Working")
        console.print("✅ Performance Summary: Working")
        console.print("\n🚀 Ready to integrate with Sierra Interactive!")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ LQS system test failed: {str(e)}[/red]")
        return False

def demonstrate_sierra_integration():
    """Demonstrate how Sierra Interactive integration would work."""
    
    console.print(Panel("🔗 Sierra Interactive Integration Demo", style="bold magenta"))
    
    # Simulate Sierra Interactive webhook data
    sierra_webhook_data = {
        "leads": [
            {
                "id": "sierra_lead_001",
                "lqs": 8.5,
                "source": "google_ads",
                "campaign": "L.R - PMax - General",
                "date": "2024-01-15",
                "contact_info": {
                    "email": "lead@example.com",
                    "phone": "+1234567890"
                },
                "property_interest": "luxury_homes",
                "budget_range": "1M-2M",
                "timeline": "3-6_months"
            },
            {
                "id": "sierra_lead_002",
                "lqs": 6.2,
                "source": "google_ads",
                "campaign": "L.R - PMax - General",
                "date": "2024-01-15",
                "contact_info": {
                    "email": "lead2@example.com",
                    "phone": "+1234567891"
                },
                "property_interest": "condos",
                "budget_range": "500K-1M",
                "timeline": "6-12_months"
            }
        ],
        "webhook_timestamp": "2024-01-15T10:30:00Z",
        "batch_size": 2
    }
    
    console.print("📥 Received webhook from Sierra Interactive:")
    console.print(f"   • {len(sierra_webhook_data['leads'])} new leads")
    console.print(f"   • Average LQS: {sum(lead['lqs'] for lead in sierra_webhook_data['leads']) / len(sierra_webhook_data['leads']):.1f}")
    console.print(f"   • Timestamp: {sierra_webhook_data['webhook_timestamp']}")
    
    # Process the leads
    lqs_engine = LeadQualityEngine()
    
    # Extract LQS data
    lqs_data = [{"lqs": lead["lqs"]} for lead in sierra_webhook_data["leads"]]
    
    # Calculate metrics for this batch
    batch_metrics = lqs_engine.calculate_lead_quality_metrics(lqs_data, 0, 1)  # No cost for batch
    
    console.print("\n📊 Batch Analysis:")
    console.print(f"   • High Quality Leads: {batch_metrics.high_quality_leads}")
    console.print(f"   • Average LQS: {batch_metrics.average_lqs:.1f}")
    console.print(f"   • High Quality Ratio: {batch_metrics.high_quality_ratio:.1%}")
    
    # Integration workflow
    integration_steps = [
        "1. Receive webhook from Sierra Interactive",
        "2. Extract LQS scores and lead metadata",
        "3. Update Google Ads conversion values based on LQS",
        "4. Trigger optimization if thresholds are met",
        "5. Send notification to team if high-value leads detected",
        "6. Update reporting dashboard with new metrics"
    ]
    
    console.print("\n🔄 Integration Workflow:")
    for step in integration_steps:
        console.print(f"   {step}")
    
    console.print("\n💡 Key Benefits:")
    benefits = [
        "• Real-time lead quality feedback",
        "• Automated conversion value optimization",
        "• Performance-based bid adjustments",
        "• Quality-focused audience targeting",
        "• ROI optimization based on lead value"
    ]
    
    for benefit in benefits:
        console.print(f"   {benefit}")

if __name__ == "__main__":
    test_lqs_system()
    console.print("\n" + "="*80 + "\n")
    demonstrate_sierra_integration()
