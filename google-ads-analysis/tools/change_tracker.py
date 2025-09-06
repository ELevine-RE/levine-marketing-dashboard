#!/usr/bin/env python3
"""
Change Tracker
=============

Tracks rolling 4-week performance changes to help identify when things broke.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

class ChangeTracker:
    """Tracks performance changes over rolling 4-week periods."""
    
    def __init__(self):
        self.data_file = 'data/change_history.json'
        self.load_history()
    
    def load_history(self):
        """Load existing change history."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def save_history(self):
        """Save change history to file."""
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_weekly_snapshot(self, analytics_data: dict, ads_data: dict, unified_metrics: dict):
        """Add a weekly performance snapshot."""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        
        analytics_summary = analytics_data.get('summary', {})
        traffic_sources = analytics_data.get('traffic_sources', {})
        
        # Calculate key metrics
        total_sessions = analytics_summary.get('total_sessions', 0)
        total_users = analytics_summary.get('total_users', 0)
        bounce_rate = analytics_summary.get('avg_bounce_rate', 0) * 100
        session_duration = analytics_summary.get('avg_session_duration', 0) / 60
        
        # Get top traffic sources
        top_sources = sorted(traffic_sources.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get top pages
        top_pages = analytics_data.get('top_pages', {})
        top_pages_list = sorted(top_pages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        snapshot = {
            "week_start": week_start.strftime('%Y-%m-%d'),
            "week_end": week_end.strftime('%Y-%m-%d'),
            "timestamp": now.isoformat(),
            "metrics": {
                "sessions": total_sessions,
                "users": total_users,
                "bounce_rate": bounce_rate,
                "session_duration": session_duration,
                "roas": unified_metrics.get('roas', 0),
                "conversion_rate": unified_metrics.get('conversion_rate', 0),
                "cost_per_session": unified_metrics.get('cost_per_session', 0),
                "paid_traffic_ratio": unified_metrics.get('paid_traffic_ratio', 0)
            },
            "top_traffic_sources": dict(top_sources),
            "top_pages": dict(top_pages_list),
            "changes": self._detect_changes(total_sessions, total_users, bounce_rate, session_duration)
        }
        
        # Add to history (keep only last 4 weeks)
        self.history.append(snapshot)
        if len(self.history) > 4:
            self.history = self.history[-4:]
        
        self.save_history()
        return snapshot
    
    def _detect_changes(self, sessions: int, users: int, bounce_rate: float, session_duration: float) -> List[str]:
        """Detect significant changes from previous week."""
        changes = []
        
        if len(self.history) > 0:
            last_week = self.history[-1]
            last_sessions = last_week['metrics']['sessions']
            last_users = last_week['metrics']['users']
            last_bounce = last_week['metrics']['bounce_rate']
            last_duration = last_week['metrics']['session_duration']
            
            # Calculate percentage changes
            session_change = ((sessions - last_sessions) / last_sessions * 100) if last_sessions > 0 else 0
            user_change = ((users - last_users) / last_users * 100) if last_users > 0 else 0
            bounce_change = bounce_rate - last_bounce
            duration_change = session_duration - last_duration
            
            # Flag significant changes
            if abs(session_change) > 20:
                changes.append(f"Sessions {'increased' if session_change > 0 else 'decreased'} by {abs(session_change):.1f}%")
            
            if abs(user_change) > 20:
                changes.append(f"Users {'increased' if user_change > 0 else 'decreased'} by {abs(user_change):.1f}%")
            
            if abs(bounce_change) > 10:
                changes.append(f"Bounce rate {'increased' if bounce_change > 0 else 'decreased'} by {abs(bounce_change):.1f}%")
            
            if abs(duration_change) > 2:
                changes.append(f"Session duration {'increased' if duration_change > 0 else 'decreased'} by {abs(duration_change):.1f} minutes")
        
        return changes
    
    def get_rolling_4_weeks(self) -> List[Dict]:
        """Get the last 4 weeks of data."""
        return self.history[-4:] if len(self.history) >= 4 else self.history
    
    def generate_change_report(self) -> str:
        """Generate HTML report of rolling 4-week changes."""
        weeks = self.get_rolling_4_weeks()
        
        if not weeks:
            return '<div class="alert alert-info">No historical data available yet.</div>'
        
        html = '<div class="change-report">'
        html += '<h6 class="text-primary mb-3">📈 Rolling 4-Week Performance Changes</h6>'
        
        # Create week-by-week comparison
        for i, week in enumerate(weeks):
            is_current = i == len(weeks) - 1
            week_class = 'border-primary' if is_current else 'border-light'
            
            html += f'''
            <div class="card mb-3 border {week_class}">
                <div class="card-header">
                    <h6 class="mb-0">
                        Week of {week['week_start']} {'(Current)' if is_current else ''}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-success">📊 Key Metrics</h6>
                            <ul class="list-unstyled">
                                <li><strong>Sessions:</strong> {week['metrics']['sessions']}</li>
                                <li><strong>Users:</strong> {week['metrics']['users']}</li>
                                <li><strong>Bounce Rate:</strong> {week['metrics']['bounce_rate']:.1f}%</li>
                                <li><strong>Session Duration:</strong> {week['metrics']['session_duration']:.1f} min</li>
                                <li><strong>ROAS:</strong> ${week['metrics']['roas']:.2f}</li>
                                <li><strong>Conversion Rate:</strong> {week['metrics']['conversion_rate']:.1f}%</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-info">🚀 Top Traffic Sources</h6>
                            <ul class="list-unstyled">
            '''
            
            if 'top_traffic_sources' in week:
                for source, sessions in week['top_traffic_sources'].items():
                    html += f'<li><strong>{source}:</strong> {sessions} sessions</li>'
            else:
                html += '<li><em>No traffic source data</em></li>'
            
            html += '''
                            </ul>
                        </div>
                    </div>
            '''
            
            # Show changes if any
            if 'changes' in week and week['changes']:
                html += '''
                    <div class="mt-3">
                        <h6 class="text-warning">⚠️ Changes Detected</h6>
                        <ul class="list-unstyled">
                '''
                for change in week['changes']:
                    html += f'<li>• {change}</li>'
                html += '</ul></div>'
            
            html += '</div></div>'
        
        html += '</div>'
        return html

def track_current_week(analytics_data: dict, ads_data: dict, unified_metrics: dict):
    """Track current week's performance."""
    tracker = ChangeTracker()
    return tracker.add_weekly_snapshot(analytics_data, ads_data, unified_metrics)

def get_change_report():
    """Get the change report HTML."""
    tracker = ChangeTracker()
    return tracker.generate_change_report()
