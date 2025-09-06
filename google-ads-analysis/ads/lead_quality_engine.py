#!/usr/bin/env python3
"""
Lead Quality Score Engine
========================

Replaces ROAS-based optimization with Lead Quality Score (LQS) based optimization.
This engine focuses on acquiring high-value leads rather than just optimizing for volume.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only what we need to avoid circular imports

@dataclass
class LeadQualityMetrics:
    """Lead Quality Score metrics for a given period."""
    period_days: int
    total_leads: int
    high_quality_leads: int  # LQS >= 5
    medium_quality_leads: int  # LQS 3-4
    low_quality_leads: int  # LQS 1-2
    average_lqs: float
    total_cost: float
    cphql: float  # Cost per High-Quality Lead
    cpl: float  # Cost per Lead (overall)
    high_quality_ratio: float  # Percentage of high-quality leads
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "period_days": self.period_days,
            "total_leads": self.total_leads,
            "high_quality_leads": self.high_quality_leads,
            "medium_quality_leads": self.medium_quality_leads,
            "low_quality_leads": self.low_quality_leads,
            "average_lqs": self.average_lqs,
            "total_cost": self.total_cost,
            "cphql": self.cphql,
            "cpl": self.cpl,
            "high_quality_ratio": self.high_quality_ratio
        }

@dataclass
class LQSOptimizationRecommendation:
    """Recommendation based on Lead Quality Score analysis."""
    action: str  # 'budget_increase', 'budget_decrease', 'tcpa_increase', 'tcpa_decrease', 'maintain'
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    current_metrics: LeadQualityMetrics
    target_metrics: Dict[str, float]
    expected_impact: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "action": self.action,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "current_metrics": self.current_metrics.to_dict(),
            "target_metrics": self.target_metrics,
            "expected_impact": self.expected_impact
        }

class LeadQualityEngine:
    """
    Engine for Lead Quality Score based optimization.
    
    This engine replaces ROAS-based optimization with LQS-based optimization,
    focusing on acquiring high-value leads rather than just optimizing for volume.
    """
    
    def __init__(self):
        """Initialize the Lead Quality Engine."""
        # LQS thresholds
        self.LQS_THRESHOLDS = {
            'high_quality': 5,  # LQS >= 5
            'medium_quality': 3,  # LQS 3-4
            'low_quality': 1   # LQS 1-2
        }
        
        # Target metrics for optimization
        self.TARGET_METRICS = {
            'target_cphql': 300.0,  # Target cost per high-quality lead
            'target_average_lqs': 6.5,  # Target average LQS
            'target_high_quality_ratio': 0.4,  # Target 40% high-quality leads
            'max_cphql': 500.0,  # Maximum acceptable CpHQL
            'min_average_lqs': 5.0  # Minimum acceptable average LQS
        }
        
        # Optimization thresholds
        self.OPTIMIZATION_THRESHOLDS = {
            'budget_increase_cphql_ratio': 0.7,  # Increase budget if CpHQL < 70% of target
            'budget_decrease_cphql_ratio': 1.3,  # Decrease budget if CpHQL > 130% of target
            'tcpa_decrease_cphql_ratio': 0.8,  # Decrease tCPA if CpHQL < 80% of target
            'tcpa_increase_cphql_ratio': 1.2,  # Increase tCPA if CpHQL > 120% of target
            'excellent_performance_cphql': 250.0  # Excellent performance threshold
        }
    
    def calculate_lead_quality_metrics(self, leads_data: List[Dict], cost: float, period_days: int = 30) -> LeadQualityMetrics:
        """
        Calculate Lead Quality Score metrics from lead data.
        
        Args:
            leads_data: List of lead dictionaries with 'lqs' field
            cost: Total cost for the period
            period_days: Number of days in the period
            
        Returns:
            LeadQualityMetrics object
        """
        if not leads_data:
            return LeadQualityMetrics(
                period_days=period_days,
                total_leads=0,
                high_quality_leads=0,
                medium_quality_leads=0,
                low_quality_leads=0,
                average_lqs=0.0,
                total_cost=cost,
                cphql=0.0,
                cpl=0.0,
                high_quality_ratio=0.0
            )
        
        total_leads = len(leads_data)
        lqs_scores = [lead.get('lqs', 0) for lead in leads_data]
        
        # Categorize leads by quality
        high_quality_leads = sum(1 for lqs in lqs_scores if lqs >= self.LQS_THRESHOLDS['high_quality'])
        medium_quality_leads = sum(1 for lqs in lqs_scores if self.LQS_THRESHOLDS['medium_quality'] <= lqs < self.LQS_THRESHOLDS['high_quality'])
        low_quality_leads = sum(1 for lqs in lqs_scores if lqs < self.LQS_THRESHOLDS['medium_quality'])
        
        # Calculate metrics
        average_lqs = sum(lqs_scores) / total_leads if total_leads > 0 else 0.0
        cphql = cost / high_quality_leads if high_quality_leads > 0 else 0.0
        cpl = cost / total_leads if total_leads > 0 else 0.0
        high_quality_ratio = high_quality_leads / total_leads if total_leads > 0 else 0.0
        
        return LeadQualityMetrics(
            period_days=period_days,
            total_leads=total_leads,
            high_quality_leads=high_quality_leads,
            medium_quality_leads=medium_quality_leads,
            low_quality_leads=low_quality_leads,
            average_lqs=average_lqs,
            total_cost=cost,
            cphql=cphql,
            cpl=cpl,
            high_quality_ratio=high_quality_ratio
        )
    
    def generate_optimization_recommendation(self, current_metrics: LeadQualityMetrics, 
                                          current_budget: float, current_tcpa: float) -> LQSOptimizationRecommendation:
        """
        Generate optimization recommendations based on LQS metrics.
        
        Args:
            current_metrics: Current LeadQualityMetrics
            current_budget: Current daily budget
            current_tcpa: Current target CPA
            
        Returns:
            LQSOptimizationRecommendation object
        """
        reasoning = []
        action = "maintain"
        confidence = 0.5
        
        # Check if we have enough data
        if current_metrics.total_leads < 10:
            reasoning.append("Insufficient lead data for optimization (< 10 leads)")
            return LQSOptimizationRecommendation(
                action="maintain",
                confidence=0.3,
                reasoning=reasoning,
                current_metrics=current_metrics,
                target_metrics=self.TARGET_METRICS,
                expected_impact={"message": "Need more lead data for optimization"}
            )
        
        # Calculate performance ratios
        cphql_ratio = current_metrics.cphql / self.TARGET_METRICS['target_cphql'] if self.TARGET_METRICS['target_cphql'] > 0 else 1.0
        lqs_ratio = current_metrics.average_lqs / self.TARGET_METRICS['target_average_lqs'] if self.TARGET_METRICS['target_average_lqs'] > 0 else 1.0
        
        # Budget optimization logic
        if cphql_ratio < self.OPTIMIZATION_THRESHOLDS['budget_increase_cphql_ratio']:
            action = "budget_increase"
            confidence = 0.8
            reasoning.append(f"CpHQL (${current_metrics.cphql:.2f}) is {cphql_ratio:.1%} of target (${self.TARGET_METRICS['target_cphql']:.2f})")
            reasoning.append("Low CpHQL indicates efficient acquisition of high-quality leads")
            reasoning.append("Recommend increasing budget to scale successful performance")
            
        elif cphql_ratio > self.OPTIMIZATION_THRESHOLDS['budget_decrease_cphql_ratio']:
            action = "budget_decrease"
            confidence = 0.7
            reasoning.append(f"CpHQL (${current_metrics.cphql:.2f}) is {cphql_ratio:.1%} of target (${self.TARGET_METRICS['target_cphql']:.2f})")
            reasoning.append("High CpHQL indicates inefficient acquisition of high-quality leads")
            reasoning.append("Recommend decreasing budget to reduce inefficient spending")
        
        # tCPA optimization logic
        elif cphql_ratio < self.OPTIMIZATION_THRESHOLDS['tcpa_decrease_cphql_ratio']:
            action = "tcpa_decrease"
            confidence = 0.75
            reasoning.append(f"CpHQL (${current_metrics.cphql:.2f}) is {cphql_ratio:.1%} of target (${self.TARGET_METRICS['target_cphql']:.2f})")
            reasoning.append("Low CpHQL indicates we can afford to be more aggressive")
            reasoning.append("Recommend decreasing tCPA to acquire more leads at current efficiency")
            
        elif cphql_ratio > self.OPTIMIZATION_THRESHOLDS['tcpa_increase_cphql_ratio']:
            action = "tcpa_increase"
            confidence = 0.7
            reasoning.append(f"CpHQL (${current_metrics.cphql:.2f}) is {cphql_ratio:.1%} of target (${self.TARGET_METRICS['target_cphql']:.2f})")
            reasoning.append("High CpHQL indicates we need to be more selective")
            reasoning.append("Recommend increasing tCPA to focus on higher-quality leads")
        
        # Check for excellent performance
        if current_metrics.cphql < self.OPTIMIZATION_THRESHOLDS['excellent_performance_cphql']:
            reasoning.append(f"Excellent performance: CpHQL (${current_metrics.cphql:.2f}) below threshold (${self.OPTIMIZATION_THRESHOLDS['excellent_performance_cphql']:.2f})")
        
        # Calculate expected impact
        expected_impact = self._calculate_expected_impact(action, current_metrics, current_budget, current_tcpa)
        
        return LQSOptimizationRecommendation(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            current_metrics=current_metrics,
            target_metrics=self.TARGET_METRICS,
            expected_impact=expected_impact
        )
    
    def _calculate_expected_impact(self, action: str, current_metrics: LeadQualityMetrics, 
                                  current_budget: float, current_tcpa: float) -> Dict[str, Any]:
        """Calculate expected impact of the recommended action."""
        impact = {
            "action": action,
            "current_performance": "excellent" if current_metrics.cphql < self.OPTIMIZATION_THRESHOLDS['excellent_performance_cphql'] else "good" if current_metrics.cphql < self.TARGET_METRICS['target_cphql'] else "needs_improvement"
        }
        
        if action == "budget_increase":
            impact.update({
                "budget_adjustment": "+20%",
                "expected_high_quality_leads": int(current_metrics.high_quality_leads * 1.2),
                "expected_cost": current_metrics.total_cost * 1.2,
                "expected_cphql": current_metrics.cphql * 0.95  # Slight improvement due to scale
            })
        elif action == "budget_decrease":
            impact.update({
                "budget_adjustment": "-15%",
                "expected_high_quality_leads": int(current_metrics.high_quality_leads * 0.85),
                "expected_cost": current_metrics.total_cost * 0.85,
                "expected_cphql": current_metrics.cphql * 1.05  # Slight improvement due to focus
            })
        elif action == "tcpa_decrease":
            impact.update({
                "tcpa_adjustment": "-10%",
                "expected_leads": int(current_metrics.total_leads * 1.15),
                "expected_high_quality_leads": int(current_metrics.high_quality_leads * 1.1),
                "expected_cphql": current_metrics.cphql * 0.9
            })
        elif action == "tcpa_increase":
            impact.update({
                "tcpa_adjustment": "+10%",
                "expected_leads": int(current_metrics.total_leads * 0.9),
                "expected_high_quality_leads": int(current_metrics.high_quality_leads * 1.05),
                "expected_cphql": current_metrics.cphql * 0.95
            })
        else:
            impact.update({
                "message": "Maintain current settings - performance is within acceptable range"
            })
        
        return impact
    
    def get_performance_summary(self, metrics: LeadQualityMetrics) -> Dict[str, Any]:
        """Get a summary of performance based on LQS metrics."""
        performance_level = "excellent"
        if metrics.cphql > self.TARGET_METRICS['max_cphql']:
            performance_level = "poor"
        elif metrics.cphql > self.TARGET_METRICS['target_cphql']:
            performance_level = "needs_improvement"
        elif metrics.cphql < self.OPTIMIZATION_THRESHOLDS['excellent_performance_cphql']:
            performance_level = "excellent"
        else:
            performance_level = "good"
        
        return {
            "performance_level": performance_level,
            "primary_metric": "CpHQL",
            "primary_value": metrics.cphql,
            "primary_target": self.TARGET_METRICS['target_cphql'],
            "secondary_metrics": {
                "average_lqs": metrics.average_lqs,
                "high_quality_ratio": metrics.high_quality_ratio,
                "total_leads": metrics.total_leads
            },
            "recommendations": {
                "focus_area": "lead_quality" if metrics.average_lqs < self.TARGET_METRICS['target_average_lqs'] else "volume",
                "priority": "high" if performance_level in ["poor", "needs_improvement"] else "medium"
            }
        }
