#!/usr/bin/env python3
"""
Change Management
================

Consolidated change management system that handles lever tracking,
performance monitoring, and intervention management for Google Ads campaigns.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ChangeManagement:
    """Consolidated change management for Google Ads campaigns."""
    
    def __init__(self):
        self.lever_data_file = 'data/lever_history.json'
        self.change_data_file = 'data/change_history.json'
        self.intervention_data_file = 'data/intervention_items.json'
        self.load_all_data()
    
    def load_all_data(self):
        """Load all change management data."""
        # Load lever history
        if os.path.exists(self.lever_data_file):
            with open(self.lever_data_file, 'r') as f:
                self.lever_history = json.load(f)
        else:
            self.lever_history = []
        
        # Load change history
        if os.path.exists(self.change_data_file):
            with open(self.change_data_file, 'r') as f:
                self.change_history = json.load(f)
        else:
            self.change_history = []
        
        # Load intervention items
        if os.path.exists(self.intervention_data_file):
            with open(self.intervention_data_file, 'r') as f:
                self.interventions = json.load(f)
        else:
            self.interventions = []
    
    def save_all_data(self):
        """Save all change management data."""
        os.makedirs('data', exist_ok=True)
        
        with open(self.lever_data_file, 'w') as f:
            json.dump(self.lever_history, f, indent=2)
        
        with open(self.change_data_file, 'w') as f:
            json.dump(self.change_history, f, indent=2)
        
        with open(self.intervention_data_file, 'w') as f:
            json.dump(self.interventions, f, indent=2)
    
    # Lever Tracking Methods
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
        
        self.lever_history.append(lever_record)
        
        # Keep only last 4 weeks
        cutoff_date = datetime.now() - timedelta(weeks=4)
        self.lever_history = [
            record for record in self.lever_history 
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
        
        self.save_all_data()
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
            record for record in self.lever_history 
            if datetime.fromisoformat(record['timestamp']) > cutoff_date
        ]
    
    def get_levers_by_type(self, lever_type: str) -> List[Dict]:
        """Get all levers of a specific type."""
        return [record for record in self.lever_history if record['lever_type'] == lever_type]
    
    def check_one_lever_per_week(self, campaign_name: str = "L.R - PMax - General") -> Dict:
        """Check if one lever per week rule is being followed."""
        recent_levers = self.get_recent_levers(7)  # Last 7 days
        campaign_levers = [lever for lever in recent_levers if lever['campaign'] == campaign_name]
        
        if len(campaign_levers) > 1:
            return {
                'rule_violated': True,
                'levers_in_week': len(campaign_levers),
                'levers': campaign_levers,
                'message': f"Multiple levers ({len(campaign_levers)}) pulled in last 7 days"
            }
        else:
            return {
                'rule_violated': False,
                'levers_in_week': len(campaign_levers),
                'levers': campaign_levers,
                'message': "One lever per week rule followed"
            }
    
    # Change Tracking Methods
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
        self.change_history.append(snapshot)
        if len(self.change_history) > 4:
            self.change_history = self.change_history[-4:]
        
        self.save_all_data()
        return snapshot
    
    def _detect_changes(self, sessions: int, users: int, bounce_rate: float, session_duration: float) -> List[str]:
        """Detect significant changes from previous week."""
        changes = []
        
        if len(self.change_history) > 0:
            last_week = self.change_history[-1]
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
        return self.change_history[-4:] if len(self.change_history) >= 4 else self.change_history
    
    # Intervention Management Methods
    def add_intervention_item(self, category: str, action: str, priority: str = "medium", 
                            due_date: str = None, notes: str = ""):
        """Add an item requiring manual intervention."""
        intervention = {
            "id": len(self.interventions) + 1,
            "category": category,
            "action": action,
            "priority": priority,
            "status": "pending",
            "created_date": datetime.now().isoformat(),
            "due_date": due_date,
            "notes": notes,
            "assigned_to": "user"
        }
        
        self.interventions.append(intervention)
        self.save_all_data()
        return intervention
    
    def mark_intervention_completed(self, intervention_id: int):
        """Mark an intervention item as completed."""
        for item in self.interventions:
            if item['id'] == intervention_id:
                item['status'] = 'completed'
                item['completed_date'] = datetime.now().isoformat()
                break
        self.save_all_data()
    
    def get_pending_interventions(self) -> List[Dict]:
        """Get all pending intervention items."""
        return [item for item in self.interventions if item['status'] == 'pending']
    
    def get_interventions_by_priority(self, priority: str) -> List[Dict]:
        """Get interventions by priority level."""
        return [item for item in self.interventions if item['priority'] == priority]
    
    # Reporting Methods
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
    
    def generate_intervention_report(self) -> str:
        """Generate HTML report of intervention items."""
        pending_items = self.get_pending_interventions()
        
        if not pending_items:
            return '''
            <div class="alert alert-success">
                <h6 class="text-success mb-2">✅ No Manual Interventions Required</h6>
                <p class="mb-0">All systems are running automatically. No user action needed.</p>
            </div>
            '''
        
        # Group by priority
        high_priority = [item for item in pending_items if item['priority'] == 'high']
        medium_priority = [item for item in pending_items if item['priority'] == 'medium']
        low_priority = [item for item in pending_items if item['priority'] == 'low']
        
        html = '<div class="intervention-report">'
        html += '<h6 class="text-danger mb-3">⚠️ Manual Interventions Required</h6>'
        
        # High Priority Items
        if high_priority:
            html += '''
            <div class="alert alert-danger mb-3">
                <h6 class="text-danger mb-2">🚨 High Priority - Immediate Action Required</h6>
            '''
            for item in high_priority:
                html += f'''
                <div class="row mb-2">
                    <div class="col-md-3">
                        <strong>{item['category']}</strong>
                    </div>
                    <div class="col-md-6">
                        {item['action']}
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">Due: {item['due_date'] or 'ASAP'}</small>
                    </div>
                </div>
                '''
                if item['notes']:
                    html += f'<div class="row mb-2"><div class="col-12"><small class="text-muted">Note: {item["notes"]}</small></div></div>'
            html += '</div>'
        
        # Medium Priority Items
        if medium_priority:
            html += '''
            <div class="alert alert-warning mb-3">
                <h6 class="text-warning mb-2">⚠️ Medium Priority - Action Required Soon</h6>
            '''
            for item in medium_priority:
                html += f'''
                <div class="row mb-2">
                    <div class="col-md-3">
                        <strong>{item['category']}</strong>
                    </div>
                    <div class="col-md-6">
                        {item['action']}
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">Due: {item['due_date'] or 'Soon'}</small>
                    </div>
                </div>
                '''
                if item['notes']:
                    html += f'<div class="row mb-2"><div class="col-12"><small class="text-muted">Note: {item["notes"]}</small></div></div>'
            html += '</div>'
        
        # Low Priority Items
        if low_priority:
            html += '''
            <div class="alert alert-info mb-3">
                <h6 class="text-info mb-2">ℹ️ Low Priority - When Convenient</h6>
            '''
            for item in low_priority:
                html += f'''
                <div class="row mb-2">
                    <div class="col-md-3">
                        <strong>{item['category']}</strong>
                    </div>
                    <div class="col-md-6">
                        {item['action']}
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">Due: {item['due_date'] or 'Flexible'}</small>
                    </div>
                </div>
                '''
                if item['notes']:
                    html += f'<div class="row mb-2"><div class="col-12"><small class="text-muted">Note: {item["notes"]}</small></div></div>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report combining all change management data."""
        html = '<div class="comprehensive-change-report">'
        html += '<h5 class="text-primary mb-4">📊 Comprehensive Change Management Report</h5>'
        
        # Lever tracking summary
        one_lever_check = self.check_one_lever_per_week()
        html += f'''
        <div class="card mb-3">
            <div class="card-header">
                <h6 class="mb-0">🔧 Lever Tracking Summary</h6>
            </div>
            <div class="card-body">
                <p><strong>One Lever Per Week Rule:</strong> {one_lever_check['message']}</p>
                <p><strong>Levers in Last 7 Days:</strong> {one_lever_check['levers_in_week']}</p>
            </div>
        </div>
        '''
        
        # Add lever report
        html += self.generate_lever_report()
        
        # Add change report
        html += self.generate_change_report()
        
        # Add intervention report
        html += self.generate_intervention_report()
        
        html += '</div>'
        return html

def get_lever_report():
    """Get the lever report HTML."""
    manager = ChangeManagement()
    return manager.generate_lever_report()

def get_change_report():
    """Get the change report HTML."""
    manager = ChangeManagement()
    return manager.generate_change_report()

def get_intervention_report():
    """Get the intervention report HTML."""
    manager = ChangeManagement()
    return manager.generate_intervention_report()

def get_comprehensive_report():
    """Get the comprehensive change management report HTML."""
    manager = ChangeManagement()
    return manager.generate_comprehensive_report()

def track_current_week(analytics_data: dict, ads_data: dict, unified_metrics: dict):
    """Track current week's performance."""
    manager = ChangeManagement()
    return manager.add_weekly_snapshot(analytics_data, ads_data, unified_metrics)

