#!/usr/bin/env python3
"""
Test Phase Progression Logic
============================

Test script to verify the updated Phase 1 to Phase 2 progression logic
with both standard and time-based conditions for lean budget campaigns.
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ads.phase_manager import CampaignPhaseManager, CampaignPhase
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def test_phase_1_to_2_progression():
    """Test the updated Phase 1 to Phase 2 progression logic."""
    
    console.print(Panel("🔄 Testing Phase 1 → Phase 2 Progression Logic", style="bold blue"))
    
    try:
        # Initialize phase manager
        phase_manager = CampaignPhaseManager()
        console.print("✅ Phase manager initialized successfully")
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Standard Progression - All Requirements Met",
                "metrics": {
                    "primary_conversions_count": 35,
                    "campaign_age_days": 20,
                    "cpl_7d": 120.0,
                    "cpl_30d": 125.0,
                    "days_since_last_change": 10,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "standard",
                "description": "Should progress via standard path (≥30 conversions, ≥14 days, stable CPL)"
            },
            {
                "name": "Time-Based Progression - Lean Budget Campaign",
                "metrics": {
                    "primary_conversions_count": 18,
                    "campaign_age_days": 65,
                    "cpl_7d": 110.0,
                    "cpl_30d": 100.0,
                    "days_since_last_change": 5,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "time_based",
                "description": "Should progress via time-based path (≥60 days, ≥15 conversions, stable performance)"
            },
            {
                "name": "Blocked - Insufficient Conversions & Too New",
                "metrics": {
                    "primary_conversions_count": 10,
                    "campaign_age_days": 10,
                    "cpl_7d": 120.0,
                    "cpl_30d": 125.0,
                    "days_since_last_change": 10,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "blocked",
                "description": "Should be blocked (insufficient conversions and too new for both paths)"
            },
            {
                "name": "Blocked - Unstable Performance",
                "metrics": {
                    "primary_conversions_count": 20,
                    "campaign_age_days": 70,
                    "cpl_7d": 150.0,
                    "cpl_30d": 100.0,
                    "days_since_last_change": 10,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "blocked",
                "description": "Should be blocked (unstable performance - CPL increased by 50%)"
            },
            {
                "name": "Standard Progression - Edge Case",
                "metrics": {
                    "primary_conversions_count": 30,
                    "campaign_age_days": 14,
                    "cpl_7d": 120.0,
                    "cpl_30d": 125.0,
                    "days_since_last_change": 7,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "standard",
                "description": "Should progress via standard path (exactly at minimums)"
            },
            {
                "name": "Time-Based Progression - Edge Case",
                "metrics": {
                    "primary_conversions_count": 15,
                    "campaign_age_days": 60,
                    "cpl_7d": 110.0,
                    "cpl_30d": 100.0,
                    "days_since_last_change": 5,
                    "primary_conversions": ["Lead Form Submission"],
                    "secondary_conversions": ["Page View", "Click"]
                },
                "expected": "time_based",
                "description": "Should progress via time-based path (exactly at minimums)"
            }
        ]
        
        # Create results table
        results_table = Table(title="Phase 1 → Phase 2 Progression Test Results")
        results_table.add_column("Scenario", style="cyan")
        results_table.add_column("Expected", style="blue")
        results_table.add_column("Actual", style="green")
        results_table.add_column("Eligible", style="yellow")
        results_table.add_column("Path", style="magenta")
        results_table.add_column("Status", style="red")
        
        all_passed = True
        
        for scenario in test_scenarios:
            # Run eligibility check
            result = phase_manager.check_phase_eligibility(scenario["metrics"], CampaignPhase.PHASE_1.value)
            
            # Determine actual path
            actual_path = "blocked"
            if result.eligible_for_next:
                progression_path = result.details.get("progression_path", "standard")
                if progression_path == "time_based":
                    actual_path = "time_based"
                else:
                    actual_path = "standard"
            
            # Check if test passed
            passed = (
                (scenario["expected"] == "blocked" and not result.eligible_for_next) or
                (scenario["expected"] == "standard" and result.eligible_for_next and result.details.get("progression_path") == "standard") or
                (scenario["expected"] == "time_based" and result.eligible_for_next and result.details.get("progression_path") == "time_based")
            )
            
            if not passed:
                all_passed = False
            
            status = "✅ PASS" if passed else "❌ FAIL"
            
            results_table.add_row(
                scenario["name"],
                scenario["expected"].title(),
                actual_path.title(),
                "Yes" if result.eligible_for_next else "No",
                result.details.get("progression_path", "N/A"),
                status
            )
        
        console.print(results_table)
        
        # Display detailed results for each scenario
        console.print("\n[bold cyan]📋 Detailed Results[/bold cyan]")
        
        for i, scenario in enumerate(test_scenarios, 1):
            result = phase_manager.check_phase_eligibility(scenario["metrics"], CampaignPhase.PHASE_1.value)
            
            console.print(f"\n[bold]{i}. {scenario['name']}[/bold]")
            console.print(f"   Description: {scenario['description']}")
            console.print(f"   Expected: {scenario['expected'].title()}")
            console.print(f"   Actual: {'Eligible' if result.eligible_for_next else 'Blocked'}")
            
            if result.eligible_for_next:
                console.print(f"   Path: {result.details.get('progression_path', 'standard').title()}")
                console.print(f"   Recommendation: {result.recommended_action}")
            else:
                console.print(f"   Blocking Factors: {', '.join(result.details.get('blocking_factors', []))}")
            
            # Show requirements breakdown
            requirements = result.details.get('requirements_met', {})
            console.print("   Requirements Met:")
            for req, met in requirements.items():
                status = "✅" if met else "❌"
                console.print(f"     {status} {req.replace('_', ' ').title()}")
        
        # Summary
        if all_passed:
            console.print(Panel("🎉 All Phase Progression Tests Passed!", style="bold green"))
        else:
            console.print(Panel("⚠️ Some Phase Progression Tests Failed", style="bold red"))
        
        console.print("\n💡 Key Benefits of New Logic:")
        benefits = [
            "• Lean budget campaigns can progress after 60 days with 15+ conversions",
            "• Standard progression still available for campaigns meeting all criteria",
            "• Performance stability check prevents progression of unstable campaigns",
            "• Clear blocking factors help identify what needs to be addressed",
            "• Flexible progression paths reduce campaign stagnation"
        ]
        
        for benefit in benefits:
            console.print(f"   {benefit}")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Phase progression test failed: {str(e)}[/red]")
        return False

def demonstrate_lean_budget_scenarios():
    """Demonstrate how the new logic helps lean budget campaigns."""
    
    console.print(Panel("💰 Lean Budget Campaign Scenarios", style="bold magenta"))
    
    scenarios = [
        {
            "name": "New Campaign - $30/day Budget",
            "age_days": 10,
            "conversions": 5,
            "cpl_trend": "Stable",
            "old_logic": "❌ Blocked (need 30 conversions)",
            "new_logic": "❌ Still blocked (too new)",
            "next_milestone": "Day 14 + 30 conversions OR Day 60 + 15 conversions"
        },
        {
            "name": "Growing Campaign - $50/day Budget",
            "age_days": 30,
            "conversions": 12,
            "cpl_trend": "Stable",
            "old_logic": "❌ Blocked (need 30 conversions)",
            "new_logic": "❌ Still blocked (need 15 conversions)",
            "next_milestone": "Day 60 + 15 conversions"
        },
        {
            "name": "Mature Lean Campaign - $40/day Budget",
            "age_days": 65,
            "conversions": 18,
            "cpl_trend": "Stable",
            "old_logic": "❌ Blocked (need 30 conversions)",
            "new_logic": "✅ Eligible (time-based progression)",
            "next_milestone": "Introduce tCPA"
        },
        {
            "name": "Stable Campaign - $80/day Budget",
            "age_days": 25,
            "conversions": 35,
            "cpl_trend": "Stable",
            "old_logic": "✅ Eligible (standard progression)",
            "new_logic": "✅ Eligible (standard progression)",
            "next_milestone": "Introduce tCPA"
        }
    ]
    
    scenario_table = Table(title="Lean Budget Campaign Progression")
    scenario_table.add_column("Scenario", style="cyan")
    scenario_table.add_column("Age", style="green")
    scenario_table.add_column("Conversions", style="yellow")
    scenario_table.add_column("CPL Trend", style="blue")
    scenario_table.add_column("Old Logic", style="red")
    scenario_table.add_column("New Logic", style="green")
    scenario_table.add_column("Next Milestone", style="magenta")
    
    for scenario in scenarios:
        scenario_table.add_row(
            scenario["name"],
            f"{scenario['age_days']} days",
            str(scenario["conversions"]),
            scenario["cpl_trend"],
            scenario["old_logic"],
            scenario["new_logic"],
            scenario["next_milestone"]
        )
    
    console.print(scenario_table)
    
    console.print("\n🎯 Key Improvements:")
    improvements = [
        "• Campaigns with lean budgets can now progress after 60 days",
        "• Reduced conversion requirement (30 → 15) for time-based path",
        "• Performance stability check ensures quality progression",
        "• No more indefinite stagnation in Phase 1",
        "• Maintains quality standards while providing flexibility"
    ]
    
    for improvement in improvements:
        console.print(f"   {improvement}")

if __name__ == "__main__":
    test_phase_1_to_2_progression()
    console.print("\n" + "="*80 + "\n")
    demonstrate_lean_budget_scenarios()

