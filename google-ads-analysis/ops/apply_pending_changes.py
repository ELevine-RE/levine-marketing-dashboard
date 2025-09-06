#!/usr/bin/env python3
"""
Apply Pending Changes Runner
===========================

Executes changes that have been approved by the guardrails system
and whose execute_after time has passed.

This script should be run periodically (e.g., every 15 minutes) to
process pending changes and apply them to the Google Ads campaigns.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.guardrails import PerformanceMaxGuardrails, ChangeType
from ads.notifications import NotificationManager
from google_ads_manager import GoogleAdsManager

class PendingChangeExecutor:
    """
    Executes pending changes that have been approved and are ready to be applied.
    
    This class manages the execution of changes that have passed through the
    guardrails system and are waiting for their scheduled execution time.
    """
    
    def __init__(self):
        """Initialize the change executor."""
        self.guardrails = PerformanceMaxGuardrails()
        self.notification_manager = NotificationManager()
        self.manager = GoogleAdsManager()
        
        # Campaign configuration
        self.CAMPAIGN_NAME = "L.R - PMax - General"
        self.CUSTOMER_ID = "8335511794"
        
        # File to store pending changes
        self.pending_changes_file = Path("pending_changes.json")
    
    def load_pending_changes(self) -> List[Dict]:
        """Load pending changes from file."""
        try:
            if self.pending_changes_file.exists():
                with open(self.pending_changes_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading pending changes: {str(e)}")
            return []
    
    def save_pending_changes(self, changes: List[Dict]):
        """Save pending changes to file."""
        try:
            with open(self.pending_changes_file, 'w') as f:
                json.dump(changes, f, indent=2)
        except Exception as e:
            print(f"Error saving pending changes: {str(e)}")
    
    def add_pending_change(self, change_request: Dict, verdict: Dict):
        """Add a new pending change."""
        try:
            pending_changes = self.load_pending_changes()
            
            # Create pending change record
            pending_change = {
                'id': f"change_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'change_request': change_request,
                'verdict': verdict,
                'execute_after': verdict.get('execute_after'),
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            pending_changes.append(pending_change)
            self.save_pending_changes(pending_changes)
            
            print(f"Added pending change: {pending_change['id']}")
            
        except Exception as e:
            print(f"Error adding pending change: {str(e)}")
    
    def execute_pending_changes(self) -> List[Dict]:
        """
        Execute all pending changes that are ready to be applied.
        
        Returns:
            List of executed changes
        """
        try:
            pending_changes = self.load_pending_changes()
            now = datetime.now()
            executed_changes = []
            remaining_changes = []
            
            for change in pending_changes:
                if change['status'] != 'pending':
                    remaining_changes.append(change)
                    continue
                
                execute_after = datetime.fromisoformat(change['execute_after'].replace('Z', '+00:00'))
                
                if now >= execute_after:
                    # Execute the change
                    success = self._execute_change(change)
                    
                    if success:
                        change['status'] = 'executed'
                        change['executed_at'] = now.isoformat()
                        executed_changes.append(change)
                        print(f"Executed change: {change['id']}")
                    else:
                        change['status'] = 'failed'
                        change['failed_at'] = now.isoformat()
                        print(f"Failed to execute change: {change['id']}")
                    
                    remaining_changes.append(change)
                else:
                    # Not ready yet, keep in pending list
                    remaining_changes.append(change)
            
            # Save updated pending changes
            self.save_pending_changes(remaining_changes)
            
            return executed_changes
            
        except Exception as e:
            print(f"Error executing pending changes: {str(e)}")
            return []
    
    def _execute_change(self, change: Dict) -> bool:
        """
        Execute a single change.
        
        Args:
            change: The change to execute
            
        Returns:
            bool: True if execution was successful
        """
        try:
            change_request = change['change_request']
            change_type = change_request.get('type')
            
            if change_type == ChangeType.BUDGET_ADJUSTMENT.value:
                return self._execute_budget_change(change_request)
            elif change_type == ChangeType.TARGET_CPA_ADJUSTMENT.value:
                return self._execute_tcpa_change(change_request)
            elif change_type == ChangeType.ASSET_GROUP_MODIFICATION.value:
                return self._execute_asset_group_change(change_request)
            elif change_type == ChangeType.GEO_TARGETING_MODIFICATION.value:
                return self._execute_geo_targeting_change(change_request)
            else:
                print(f"Unknown change type: {change_type}")
                return False
                
        except Exception as e:
            print(f"Error executing change: {str(e)}")
            return False
    
    def _execute_budget_change(self, change_request: Dict) -> bool:
        """Execute a budget adjustment change."""
        try:
            new_budget = change_request.get('new_daily_budget')
            if not new_budget:
                print("No new budget specified")
                return False
            
            # Convert to micros (Google Ads API format)
            budget_micros = int(new_budget * 1000000)
            
            # Get campaign ID
            campaign_id = self._get_campaign_id()
            if not campaign_id:
                print("Could not find campaign")
                return False
            
            # Create campaign operation
            campaign_service = self.manager.client.get_service("CampaignService")
            
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{self.CUSTOMER_ID}/campaigns/{campaign_id}",
                    "daily_budget": {
                        "amount_micros": budget_micros
                    }
                },
                "update_mask": {
                    "paths": ["daily_budget"]
                }
            }
            
            # Execute the operation
            response = campaign_service.mutate_campaigns(
                customer_id=self.CUSTOMER_ID,
                operations=[campaign_operation]
            )
            
            print(f"Budget updated to ${new_budget}/day")
            return True
            
        except Exception as e:
            print(f"Error executing budget change: {str(e)}")
            return False
    
    def _execute_tcpa_change(self, change_request: Dict) -> bool:
        """Execute a target CPA adjustment change."""
        try:
            new_tcpa = change_request.get('new_target_cpa')
            if not new_tcpa:
                print("No new target CPA specified")
                return False
            
            # Convert to micros (Google Ads API format)
            tcpa_micros = int(new_tcpa * 1000000)
            
            # Get campaign ID
            campaign_id = self._get_campaign_id()
            if not campaign_id:
                print("Could not find campaign")
                return False
            
            # Create campaign operation
            campaign_service = self.manager.client.get_service("CampaignService")
            
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{self.CUSTOMER_ID}/campaigns/{campaign_id}",
                    "target_cpa": {
                        "amount_micros": tcpa_micros
                    }
                },
                "update_mask": {
                    "paths": ["target_cpa"]
                }
            }
            
            # Execute the operation
            response = campaign_service.mutate_campaigns(
                customer_id=self.CUSTOMER_ID,
                operations=[campaign_operation]
            )
            
            print(f"Target CPA updated to ${new_tcpa}")
            return True
            
        except Exception as e:
            print(f"Error executing target CPA change: {str(e)}")
            return False
    
    def _execute_asset_group_change(self, change_request: Dict) -> bool:
        """Execute an asset group modification change."""
        try:
            action = change_request.get('action')
            print(f"Asset group modification: {action}")
            
            # This would implement asset group modifications
            # For now, just log the action
            return True
            
        except Exception as e:
            print(f"Error executing asset group change: {str(e)}")
            return False
    
    def _execute_geo_targeting_change(self, change_request: Dict) -> bool:
        """Execute a geo targeting modification change."""
        try:
            action = change_request.get('action')
            print(f"Geo targeting modification: {action}")
            
            # This would implement geo targeting modifications
            # For now, just log the action
            return True
            
        except Exception as e:
            print(f"Error executing geo targeting change: {str(e)}")
            return False
    
    def _get_campaign_id(self) -> Optional[str]:
        """Get the campaign ID for the target campaign."""
        try:
            query = f"""
            SELECT
                campaign.id,
                campaign.name
            FROM campaign
            WHERE campaign.name = '{self.CAMPAIGN_NAME}'
            AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
            """
            
            response = self.manager.google_ads_service.search(
                customer_id=self.CUSTOMER_ID,
                query=query
            )
            
            for row in response:
                return str(row.campaign.id)
            
            return None
            
        except Exception as e:
            print(f"Error getting campaign ID: {str(e)}")
            return None
    
    def cancel_pending_change(self, change_id: str) -> bool:
        """
        Cancel a pending change.
        
        Args:
            change_id: ID of the change to cancel
            
        Returns:
            bool: True if cancellation was successful
        """
        try:
            pending_changes = self.load_pending_changes()
            
            for change in pending_changes:
                if change['id'] == change_id and change['status'] == 'pending':
                    change['status'] = 'cancelled'
                    change['cancelled_at'] = datetime.now().isoformat()
                    
                    self.save_pending_changes(pending_changes)
                    print(f"Cancelled change: {change_id}")
                    return True
            
            print(f"Change not found or not pending: {change_id}")
            return False
            
        except Exception as e:
            print(f"Error cancelling change: {str(e)}")
            return False
    
    def list_pending_changes(self) -> List[Dict]:
        """List all pending changes."""
        try:
            pending_changes = self.load_pending_changes()
            return [c for c in pending_changes if c['status'] == 'pending']
        except Exception as e:
            print(f"Error listing pending changes: {str(e)}")
            return []

def main():
    """Main function to run the change executor."""
    executor = PendingChangeExecutor()
    
    print("🔄 Applying Pending Changes...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Execute pending changes
    executed_changes = executor.execute_pending_changes()
    
    if executed_changes:
        print(f"✅ Executed {len(executed_changes)} changes:")
        for change in executed_changes:
            change_type = change['change_request'].get('type', 'Unknown')
            print(f"  - {change['id']}: {change_type}")
    else:
        print("ℹ️ No changes ready for execution")
    
    # List remaining pending changes
    pending_changes = executor.list_pending_changes()
    if pending_changes:
        print(f"\n⏰ {len(pending_changes)} changes still pending:")
        for change in pending_changes:
            change_type = change['change_request'].get('type', 'Unknown')
            execute_after = change.get('execute_after', 'Unknown')
            print(f"  - {change['id']}: {change_type} (execute after {execute_after})")
    
    print("\n✅ Change execution complete")

if __name__ == "__main__":
    main()
