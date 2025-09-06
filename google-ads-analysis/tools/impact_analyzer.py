#!/usr/bin/env python3
"""
Impact Analyzer
==============

Analyzes the impact of lever pulls on key metrics over the following 1-2 weeks.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ImpactAnalyzer:
    """Analyzes the impact of lever pulls on performance metrics."""
    
    def __init__(self):
        self.lever_file = 'data/lever_history.json'
        self.change_file = 'data/change_history.json'
        self.impact_file = 'data/impact_analysis.json'
        self.load_data()
    
    def load_data(self):
        """Load lever and change history data."""
        self.levers = []
        self.changes = []
        
        if os.path.exists(self.lever_file):
            with open(self.lever_file, 'r') as f:
                self.levers = json.load(f)
        
        if os.path.exists(self.change_file):
            with open(self.change_file, 'r') as f:
                self.changes = json.load(f)
    
    def analyze_lever_impact(self, lever: Dict, days_after: int = 14) -> Dict:
        """Analyze the impact of a specific lever pull."""
        lever_date = datetime.fromisoformat(lever['timestamp'])
        impact_start = lever_date + timedelta(days=1)  # Start day after lever pull
        impact_end = lever_date + timedelta(days=days_after)
        
        # Get performance data before the lever pull
        before_start = lever_date - timedelta(days=7)
        before_end = lever_date - timedelta(days=1)
        
        # Find performance data in the relevant periods
        before_metrics = self._get_metrics_in_period(before_start, before_end)
        after_metrics = self._get_metrics_in_period(impact_start, impact_end)
        
        if not before_metrics or not after_metrics:
            return self._empty_impact_analysis(lever)
        
        # Calculate impact
        impact = self._calculate_impact(before_metrics, after_metrics)
        
        return {
            "lever": lever,
            "analysis_period": {
                "before": f"{before_start.strftime('%Y-%m-%d')} to {before_end.strftime('%Y-%m-%d')}",
                "after": f"{impact_start.strftime('%Y-%m-%d')} to {impact_end.strftime('%Y-%m-%d')}"
            },
            "impact": impact,
            "significance": self._assess_significance(impact),
            "recommendation": self._generate_recommendation(lever, impact)
        }
    
    def _get_metrics_in_period(self, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """Get average metrics for a specific period."""
        period_changes = []
        
        for change in self.changes:
            change_date = datetime.fromisoformat(change['timestamp'])
            if start_date <= change_date <= end_date:
                period_changes.append(change)
        
        if not period_changes:
            return None
        
        # Calculate average metrics for the period
        avg_metrics = {
            "sessions": sum(c['metrics']['sessions'] for c in period_changes) / len(period_changes),
            "users": sum(c['metrics']['users'] for c in period_changes) / len(period_changes),
            "bounce_rate": sum(c['metrics']['bounce_rate'] for c in period_changes) / len(period_changes),
            "session_duration": sum(c['metrics']['session_duration'] for c in period_changes) / len(period_changes),
            "roas": sum(c['metrics']['roas'] for c in period_changes) / len(period_changes),
            "conversion_rate": sum(c['metrics']['conversion_rate'] for c in period_changes) / len(period_changes)
        }
        
        return avg_metrics
    
    def _calculate_impact(self, before_metrics: Dict, after_metrics: Dict) -> Dict:
        """Calculate the percentage change in metrics."""
        impact = {}
        
        for metric in ['sessions', 'users', 'bounce_rate', 'session_duration', 'roas', 'conversion_rate']:
            before_val = before_metrics.get(metric, 0)
            after_val = after_metrics.get(metric, 0)
            
            if before_val == 0:
                impact[metric] = {
                    "change_pct": 0,
                    "change_abs": after_val - before_val,
                    "direction": "neutral"
                }
            else:
                change_pct = ((after_val - before_val) / before_val) * 100
                impact[metric] = {
                    "change_pct": change_pct,
                    "change_abs": after_val - before_val,
                    "direction": "positive" if change_pct > 5 else "negative" if change_pct < -5 else "neutral"
                }
        
        return impact
    
    def _assess_significance(self, impact: Dict) -> str:
        """Assess the overall significance of the impact."""
        significant_changes = 0
        positive_changes = 0
        negative_changes = 0
        
        for metric, data in impact.items():
            if abs(data['change_pct']) > 10:  # 10% threshold for significance
                significant_changes += 1
                if data['direction'] == 'positive':
                    positive_changes += 1
                elif data['direction'] == 'negative':
                    negative_changes += 1
        
        if significant_changes == 0:
            return "minimal"
        elif positive_changes > negative_changes:
            return "positive"
        elif negative_changes > positive_changes:
            return "negative"
        else:
            return "mixed"
    
    def _generate_recommendation(self, lever: Dict, impact: Dict) -> str:
        """Generate a recommendation based on the impact."""
        lever_type = lever['lever_type']
        significance = self._assess_significance(impact)
        
        if significance == "positive":
            return f"✅ {lever_type.replace('_', ' ').title()} change was successful. Consider similar adjustments."
        elif significance == "negative":
            return f"⚠️ {lever_type.replace('_', ' ').title()} change had negative impact. Consider reverting or adjusting."
        elif significance == "mixed":
            return f"🔄 {lever_type.replace('_', ' ').title()} change had mixed results. Monitor closely."
        else:
            return f"📊 {lever_type.replace('_', ' ').title()} change had minimal impact. May need time to see results."
    
    def _empty_impact_analysis(self, lever: Dict) -> Dict:
        """Return empty impact analysis when no data available."""
        return {
            "lever": lever,
            "analysis_period": {
                "before": "No data",
                "after": "No data"
            },
            "impact": {},
            "significance": "insufficient_data",
            "recommendation": "Insufficient data to analyze impact."
        }
    
    def analyze_all_levers(self) -> List[Dict]:
        """Analyze impact of all recent levers."""
        analyses = []
        
        for lever in self.levers:
            analysis = self.analyze_lever_impact(lever)
            analyses.append(analysis)
        
        # Save analyses
        os.makedirs('data', exist_ok=True)
        with open(self.impact_file, 'w') as f:
            json.dump(analyses, f, indent=2)
        
        return analyses
    
    def generate_impact_report(self) -> str:
        """Generate HTML report of lever impacts."""
        analyses = self.analyze_all_levers()
        
        if not analyses:
            return '''
            <div class="alert alert-info">
                <h6 class="text-primary mb-3">📊 Lever Impact Analysis</h6>
                <p>No lever pulls to analyze.</p>
            </div>
            '''
        
        html = '<div class="impact-report">'
        html += '<h6 class="text-primary mb-3">📊 Lever Impact Analysis (2 Weeks After Change)</h6>'
        
        for analysis in analyses:
            lever = analysis['lever']
            impact = analysis['impact']
            significance = analysis['significance']
            recommendation = analysis['recommendation']
            
            # Determine significance color
            significance_colors = {
                'positive': 'success',
                'negative': 'danger',
                'mixed': 'warning',
                'minimal': 'secondary',
                'insufficient_data': 'info'
            }
            color = significance_colors.get(significance, 'secondary')
            
            html += f'''
            <div class="card mb-3">
                <div class="card-header">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="mb-0">{lever['lever_type'].replace('_', ' ').title()}</h6>
                        </div>
                        <div class="col-md-6 text-end">
                            <span class="badge bg-{color}">{significance.title()}</span>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <strong>Change:</strong> {lever['old_value']} → {lever['new_value']}
                        </div>
                        <div class="col-md-6">
                            <strong>Date:</strong> {lever['date']}
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-12">
                            <strong>Reason:</strong> {lever['reason']}
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-12">
                            <h6 class="text-info">📈 Impact on Key Metrics (2 weeks after change):</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Change</th>
                                            <th>Direction</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            '''
            
            for metric, data in impact.items():
                if metric in ['sessions', 'users', 'bounce_rate', 'session_duration', 'roas', 'conversion_rate']:
                    direction_icon = "🟢" if data['direction'] == 'positive' else "🔴" if data['direction'] == 'negative' else "🟡"
                    html += f'''
                                        <tr>
                                            <td>{metric.replace('_', ' ').title()}</td>
                                            <td>{data['change_pct']:+.1f}%</td>
                                            <td>{direction_icon}</td>
                                        </tr>
                    '''
            
            html += f'''
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <div class="alert alert-{color}">
                                <strong>Recommendation:</strong> {recommendation}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        
        html += '</div>'
        return html

def get_impact_report():
    """Get the impact report HTML."""
    analyzer = ImpactAnalyzer()
    return analyzer.generate_impact_report()

def analyze_all_impacts():
    """Analyze all lever impacts."""
    analyzer = ImpactAnalyzer()
    return analyzer.analyze_all_levers()
