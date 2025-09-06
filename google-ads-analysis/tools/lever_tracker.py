#!/usr/bin/env python3
"""
Lever Tracker
============

Tracks actual campaign levers/changes that were pulled over the last 4 weeks.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LeverTracker:
    """Tracks campaign levers/changes that were pulled."""
    
    def __init__(self):
        self.data_file = 'data/lever_history.json'
        self.load_history()
    
    def load_history(self):
        """Load existing lever history."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def save_history(self):
        """Save lever history to file."""
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_lever_pull(self, lever_type: str, old_value: any, new_value: any, 
                      campaign_name: str = "L.R - PMax - General", 
                      reason: str = "", impact: str = ""):
        """Record a lever that was pulled."""
        lever_record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime('%Y-%m-%d'),
            "campaign": campaign_name,
            "lever_type": lever_type,
            "old_value": old_value,
            "new_value": new_value,
            "change": self._calculate_change(old_value, new_value),
            "reason": reason,
            "impact": impact,
            "status": "completed"
        }
        
        self.history.append(lever_record)
        
        # Keep only last 4 weeks
        cutoff_date = datetime.now() - timedelta(weeks=4)
        self.history = [
            record for record in self.history 
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
        
        self.save_history()
        return lever_record
    
    def _calculate_change(self, old_value: any, new_value: any) -> str:
        """Calculate the change between old and new values."""
        try:
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                if old_value == 0:
                    return f"New: {new_value}"
                change_pct = ((new_value - old_value) / old_value) * 100
                return f"{change_pct:+.1f}%"
            else:
                return f"{old_value} → {new_value}"
        except:
            return f"{old_value} → {new_value}"
    
    def get_recent_levers(self, days: int = 28) -> List[Dict]:
        """Get levers pulled in the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            record for record in self.history 
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
    
    def get_levers_by_type(self, lever_type: str) -> List[Dict]:
        """Get all levers of a specific type."""
        return [record for record in self.history if record['lever_type'] == lever_type]
    
    def generate_lever_report(self) -> str:
        """Generate HTML report of recent lever pulls."""
        recent_levers = self.get_recent_levers(28)  # Last 4 weeks
        
        if not recent_levers:
            return '''
            <div class="alert alert-info">
                <h6 class="text-primary mb-3">🔧 Recent Lever Pulls</h6>
                <p>No levers pulled in the last 4 weeks.</p>
                <small class="text-muted">All campaigns are running on autopilot.</small>
            </div>
            '''
        
        html = '<div class="lever-report">'
        html += '<h6 class="text-primary mb-3">🔧 Recent Lever Pulls (Last 4 Weeks)</h6>'
        
        # Group by week
        weeks = {}
        for lever in recent_levers:
            lever_date = datetime.fromisoformat(lever['timestamp'])
            week_start = lever_date - timedelta(days=lever_date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(lever)
        
        # Sort weeks and display
        for week_start in sorted(weeks.keys(), reverse=True):
            week_levers = weeks[week_start]
            week_end = datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)
            
            html += f'''
            <div class="card mb-3">
                <div class="card-header">
                    <h6 class="mb-0">Week of {week_start} to {week_end.strftime('%Y-%m-%d')}</h6>
                </div>
                <div class="card-body">
            '''
            
            for lever in week_levers:
                lever_date = datetime.fromisoformat(lever['timestamp'])
                date_str = lever_date.strftime('%Y-%m-%d %H:%M')
                
                # Determine lever type color
                lever_colors = {
                    'budget': 'success',
                    'tCPA': 'warning', 
                    'geo_targeting': 'info',
                    'asset_group': 'secondary',
                    'keyword': 'primary',
                    'bid_adjustment': 'danger'
                }
                color = lever_colors.get(lever['lever_type'], 'primary')
                
                html += f'''
                <div class="row mb-2">
                    <div class="col-md-2">
                        <span class="badge bg-{color}">{lever['lever_type'].replace('_', ' ').title()}</span>
                    </div>
                    <div class="col-md-2">
                        <strong>{date_str}</strong>
                    </div>
                    <div class="col-md-3">
                        <code>{lever['old_value']} → {lever['new_value']}</code>
                    </div>
                    <div class="col-md-2">
                        <span class="badge bg-info">{lever['change']}</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">{lever['reason']}</small>
                    </div>
                </div>
                '''
            
            html += '</div></div>'
        
        html += '</div>'
        return html
    
    def add_sample_levers(self):
        """Add sample lever pulls for demonstration."""
        sample_levers = [
            {
                "lever_type": "budget",
                "old_value": "$40/day",
                "new_value": "$50/day",
                "reason": "Increased budget due to strong performance",
                "impact": "Expected 25% more impressions"
            },
            {
                "lever_type": "tCPA",
                "old_value": "None",
                "new_value": "$120",
                "reason": "Introduced tCPA after 30+ conversions",
                "impact": "Targeting cost per acquisition"
            },
            {
                "lever_type": "geo_targeting",
                "old_value": "Denver Metro",
                "new_value": "Denver Metro + Boulder",
                "reason": "Expanded to Boulder market",
                "impact": "Additional 15% reach"
            },
            {
                "lever_type": "asset_group",
                "old_value": "3 active groups",
                "new_value": "4 active groups",
                "reason": "Added new property type group",
                "impact": "Better ad relevance"
            }
        ]
        
        # Add levers with different dates (last 4 weeks)
        dates = [
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=8),
            datetime.now() - timedelta(days=15),
            datetime.now() - timedelta(days=22)
        ]
        
        for i, lever in enumerate(sample_levers):
            lever_record = lever.copy()
            lever_record['timestamp'] = dates[i].isoformat()
            lever_record['date'] = dates[i].strftime('%Y-%m-%d')
            lever_record['campaign'] = "L.R - PMax - General"
            lever_record['change'] = self._calculate_change(lever['old_value'], lever['new_value'])
            lever_record['status'] = "completed"
            
            self.history.append(lever_record)
        
        self.save_history()

def get_lever_report():
    """Get the lever report HTML."""
    tracker = LeverTracker()
    return tracker.generate_lever_report()

def add_sample_levers():
    """Add sample levers for demonstration."""
    tracker = LeverTracker()
    tracker.add_sample_levers()
