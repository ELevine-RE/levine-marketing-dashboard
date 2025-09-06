#!/usr/bin/env python3
"""
Intervention Tracker
===================

Tracks items requiring manual user intervention that can't be automated.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class InterventionTracker:
    """Tracks items requiring manual user intervention."""
    
    def __init__(self):
        self.data_file = 'data/intervention_items.json'
        self.load_interventions()
    
    def load_interventions(self):
        """Load existing intervention items."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.interventions = json.load(f)
        else:
            self.interventions = []
    
    def save_interventions(self):
        """Save intervention items to file."""
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.interventions, f, indent=2)
    
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
        self.save_interventions()
        return intervention
    
    def mark_completed(self, intervention_id: int):
        """Mark an intervention item as completed."""
        for item in self.interventions:
            if item['id'] == intervention_id:
                item['status'] = 'completed'
                item['completed_date'] = datetime.now().isoformat()
                break
        self.save_interventions()
    
    def get_pending_interventions(self) -> List[Dict]:
        """Get all pending intervention items."""
        return [item for item in self.interventions if item['status'] == 'pending']
    
    def get_interventions_by_priority(self, priority: str) -> List[Dict]:
        """Get interventions by priority level."""
        return [item for item in self.interventions if item['priority'] == priority]
    
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
    
    def add_sample_interventions(self):
        """Add sample intervention items for demonstration."""
        sample_items = [
            {
                "category": "Content Creation",
                "action": "Create new video ad for luxury properties",
                "priority": "medium",
                "due_date": "2025-09-10",
                "notes": "Video ads perform 3x better than static images for luxury segment."
            },
            {
                "category": "Content Creation",
                "action": "Create new video ad for luxury properties",
                "priority": "medium",
                "due_date": "2025-09-10",
                "notes": "Video ads perform 3x better than static images for luxury segment."
            },
            {
                "category": "Website Updates",
                "action": "Update property search filters",
                "priority": "medium",
                "due_date": "2025-09-08",
                "notes": "Users requesting more granular search options."
            },
            {
                "category": "Creative Assets",
                "action": "Design new logo variations for different property types",
                "priority": "low",
                "due_date": "2025-09-15",
                "notes": "Different logos for luxury vs standard properties."
            },
            {
                "category": "Campaign Setup",
                "action": "Set up new campaign for Boulder market expansion",
                "priority": "high",
                "due_date": "2025-09-03",
                "notes": "Geo targeting expanded but need new campaign structure."
            }
        ]
        
        for item in sample_items:
            self.add_intervention_item(
                category=item['category'],
                action=item['action'],
                priority=item['priority'],
                due_date=item['due_date'],
                notes=item['notes']
            )

def get_intervention_report():
    """Get the intervention report HTML."""
    tracker = InterventionTracker()
    return tracker.generate_intervention_report()

def add_sample_interventions():
    """Add sample interventions for demonstration."""
    tracker = InterventionTracker()
    tracker.add_sample_interventions()
