#!/usr/bin/env python3
"""
Notification System for Google Ads Management
============================================

Provides Slack and email notifications for phase advancement, lag alerts,
planned changes, and stop-loss conditions.

This module integrates with the guardrails and phase management systems
to provide timely, actionable notifications.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class NotificationType(Enum):
    """Types of notifications that can be sent."""
    PHASE_ADVANCE = "phase_advance"
    PHASE_LAG = "phase_lag"
    CRITICAL_LAG = "critical_lag"
    PLANNED_CHANGE = "planned_change"
    STOP_LOSS = "stop_loss"
    DAILY_RECAP = "daily_recap"

@dataclass
class NotificationConfig:
    """Configuration for notification channels."""
    email_enabled: bool = True
    slack_enabled: bool = True
    email_recipients: List[str] = None
    slack_webhook_url: Optional[str] = None
    sender_email: str = "noreply@levine.realestate"
    sender_name: str = "Google Ads AI Manager"
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = ["evan@levine.realestate"]

class NotificationManager:
    """
    Manages notifications for the Google Ads management system.
    
    Provides Slack and email notifications for various system events
    including phase advancement, lag alerts, planned changes, and stop-loss.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """Initialize the notification manager."""
        self.config = config or NotificationConfig()
        self.campaign_name = "L.R - PMax - General"
        
        # Load environment variables for email
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Load environment variables for Slack
        self.slack_webhook_url = self.config.slack_webhook_url or os.getenv('SLACK_WEBHOOK_URL', '')
    
    def send_phase_advance(self, next_phase: str, details: Dict) -> bool:
        """
        Send notification for phase advancement.
        
        Args:
            next_phase: The phase being advanced to
            details: Additional details about the advancement
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_phase_advance_message(next_phase, details)
            subject = f"🎯 Phase Advancement: {self.campaign_name} → {next_phase.upper()}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "success")
            
            return success
            
        except Exception as e:
            print(f"Error sending phase advance notification: {str(e)}")
            return False
    
    def send_phase_lag(self, days_in_phase: int, expected_days: int, reason: str) -> bool:
        """
        Send notification for phase lagging behind schedule.
        
        Args:
            days_in_phase: Current days in phase
            expected_days: Expected days for phase completion
            reason: Reason for lagging
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_phase_lag_message(days_in_phase, expected_days, reason)
            subject = f"⚠️ Phase Lag Alert: {self.campaign_name}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "warning")
            
            return success
            
        except Exception as e:
            print(f"Error sending phase lag notification: {str(e)}")
            return False
    
    def send_critical_lag(self, days_in_phase: int, max_days: int, reason: str) -> bool:
        """
        Send notification for critical phase lag (exceeded max days).
        
        Args:
            days_in_phase: Current days in phase
            max_days: Maximum allowed days for phase
            reason: Reason for critical lag
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_critical_lag_message(days_in_phase, max_days, reason)
            subject = f"🚨 CRITICAL LAG ALERT: {self.campaign_name}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "danger")
            
            return success
            
        except Exception as e:
            print(f"Error sending critical lag notification: {str(e)}")
            return False
    
    def announce_planned_change(self, change: Dict, execute_after: str) -> bool:
        """
        Announce a planned change with 2-hour intervention window.
        
        Args:
            change: Details of the planned change
            execute_after: ISO timestamp when change will execute
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_planned_change_message(change, execute_after)
            subject = f"⏰ Planned Change Alert: {self.campaign_name}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "info")
            
            return success
            
        except Exception as e:
            print(f"Error sending planned change notification: {str(e)}")
            return False
    
    def send_stop_loss(self, reason: str) -> bool:
        """
        Send notification for stop-loss conditions.
        
        Args:
            reason: Reason for stop-loss trigger
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_stop_loss_message(reason)
            subject = f"🛑 STOP-LOSS ALERT: {self.campaign_name}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "danger")
            
            return success
            
        except Exception as e:
            print(f"Error sending stop-loss notification: {str(e)}")
            return False
    
    def send_daily_recap(self, phase_status: Dict, lag_alerts: List[str], 
                        planned_changes: List[Dict], stop_loss_alerts: List[str]) -> bool:
        """
        Send daily recap with phase status and alerts.
        
        Args:
            phase_status: Current phase status information
            lag_alerts: List of lag alert messages
            planned_changes: List of planned changes
            stop_loss_alerts: List of stop-loss alerts
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            message = self._format_daily_recap_message(
                phase_status, lag_alerts, planned_changes, stop_loss_alerts
            )
            subject = f"📊 Daily Recap: {self.campaign_name}"
            
            success = True
            
            if self.config.email_enabled:
                success &= self._send_email(subject, message)
            
            if self.config.slack_enabled:
                success &= self._send_slack(message, "info")
            
            return success
            
        except Exception as e:
            print(f"Error sending daily recap notification: {str(e)}")
            return False
    
    def _format_phase_advance_message(self, next_phase: str, details: Dict) -> str:
        """Format phase advancement message."""
        current_phase = details.get('current_phase', 'Unknown')
        recommended_action = details.get('recommended_action', 'No action required')
        
        message = f"""
🎯 **PHASE ADVANCEMENT ALERT**

**Campaign:** {self.campaign_name}
**Advancing:** {current_phase.upper()} → {next_phase.upper()}

**Recommended Action:**
{recommended_action}

**Details:**
- Current Phase: {current_phase.upper()}
- Next Phase: {next_phase.upper()}
- Eligibility Score: {details.get('readiness_score', 'N/A')}
- Blocking Factors: {', '.join(details.get('blocking_factors', [])) if details.get('blocking_factors') else 'None'}

**Next Steps:**
1. Review the recommended action above
2. Consider implementing the suggested changes
3. Monitor performance closely during transition

---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_phase_lag_message(self, days_in_phase: int, expected_days: int, reason: str) -> str:
        """Format phase lag message."""
        days_behind = days_in_phase - expected_days
        
        message = f"""
⚠️ **PHASE LAG ALERT**

**Campaign:** {self.campaign_name}
**Status:** Lagging behind schedule

**Timeline:**
- Days in Phase: {days_in_phase}
- Expected Completion: {expected_days} days
- Days Behind: {days_behind}

**Reason for Lag:**
{reason}

**Recommended Actions:**
1. Review blocking factors
2. Consider optimization strategies
3. Adjust timeline expectations if needed
4. Monitor performance closely

---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_critical_lag_message(self, days_in_phase: int, max_days: int, reason: str) -> str:
        """Format critical lag message."""
        days_over = days_in_phase - max_days
        
        message = f"""
🚨 **CRITICAL LAG ALERT**

**Campaign:** {self.campaign_name}
**Status:** CRITICAL - Exceeded maximum timeline

**Timeline:**
- Days in Phase: {days_in_phase}
- Maximum Allowed: {max_days} days
- Days Over Limit: {days_over}

**Critical Issues:**
{reason}

**IMMEDIATE ACTIONS REQUIRED:**
1. **URGENT:** Review and address blocking factors
2. Consider campaign pause if necessary
3. Implement emergency optimization strategies
4. Contact account manager for guidance
5. Reassess campaign strategy

**This requires immediate attention to prevent campaign failure.**

---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_planned_change_message(self, change: Dict, execute_after: str) -> str:
        """Format planned change message."""
        change_type = change.get('type', 'Unknown')
        execute_time = datetime.fromisoformat(execute_after.replace('Z', '+00:00'))
        intervention_deadline = execute_time - timedelta(minutes=30)  # 30 min before execution
        
        message = f"""
⏰ **PLANNED CHANGE ALERT**

**Campaign:** {self.campaign_name}
**Change Type:** {change_type}

**Change Details:**
{self._format_change_details(change)}

**Timeline:**
- Planned Execution: {execute_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Intervention Deadline: {intervention_deadline.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Time Remaining: {self._format_time_remaining(execute_time)}

**To Cancel This Change:**
Reply to this notification with "CANCEL" before the intervention deadline.

**Change will execute automatically unless cancelled.**

---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_stop_loss_message(self, reason: str) -> str:
        """Format stop-loss message."""
        message = f"""
🛑 **STOP-LOSS ALERT**

**Campaign:** {self.campaign_name}
**Status:** STOP-LOSS TRIGGERED

**Trigger Reason:**
{reason}

**IMMEDIATE ACTIONS REQUIRED:**
1. **URGENT:** Review campaign performance
2. Consider pausing campaign if necessary
3. Investigate root cause of performance issues
4. Implement corrective measures
5. Contact account manager for guidance

**This is a critical alert requiring immediate attention.**

---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_daily_recap_message(self, phase_status: Dict, lag_alerts: List[str], 
                                  planned_changes: List[Dict], stop_loss_alerts: List[str]) -> str:
        """Format daily recap message."""
        current_phase = phase_status.get('current_phase', 'Unknown')
        phase_message = phase_status.get('message', 'No status available')
        
        message = f"""
📊 **DAILY CAMPAIGN RECAP**

**Campaign:** {self.campaign_name}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

**Phase Status:**
- Current Phase: {current_phase.upper()}
- Status: {phase_message}

**Alerts Summary:**
"""
        
        if lag_alerts:
            message += f"\n**Lag Alerts ({len(lag_alerts)}):**\n"
            for alert in lag_alerts:
                message += f"- {alert}\n"
        
        if stop_loss_alerts:
            message += f"\n**Stop-Loss Alerts ({len(stop_loss_alerts)}):**\n"
            for alert in stop_loss_alerts:
                message += f"- {alert}\n"
        
        if planned_changes:
            message += f"\n**Planned Changes ({len(planned_changes)}):**\n"
            for change in planned_changes:
                change_type = change.get('type', 'Unknown')
                execute_after = change.get('execute_after', 'Unknown')
                message += f"- {change_type}: {execute_after}\n"
        
        if not lag_alerts and not stop_loss_alerts and not planned_changes:
            message += "\n✅ No alerts to report - campaign performing normally.\n"
        
        message += """
---
*Sent by Google Ads AI Manager*
        """
        return message.strip()
    
    def _format_change_details(self, change: Dict) -> str:
        """Format change details for display."""
        change_type = change.get('type', 'Unknown')
        
        if change_type == 'budget_adjustment':
            new_budget = change.get('new_daily_budget', 'Unknown')
            return f"- New Daily Budget: ${new_budget}"
        elif change_type == 'target_cpa_adjustment':
            new_tcpa = change.get('new_target_cpa', 'Unknown')
            return f"- New Target CPA: ${new_tcpa}"
        elif change_type == 'asset_group_modification':
            action = change.get('action', 'Unknown')
            return f"- Action: {action}"
        elif change_type == 'geo_targeting_modification':
            action = change.get('action', 'Unknown')
            return f"- Action: {action}"
        else:
            return f"- Change Type: {change_type}"
    
    def _format_time_remaining(self, execute_time: datetime) -> str:
        """Format time remaining until execution."""
        now = datetime.now()
        time_diff = execute_time - now
        
        if time_diff.total_seconds() <= 0:
            return "Executing now"
        
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        # Round up minutes to avoid showing 44m when it's actually 45m
        if minutes > 0 and (time_diff.total_seconds() % 3600) % 60 > 30:
            minutes += 1
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _send_email(self, subject: str, message: str) -> bool:
        """Send email notification."""
        try:
            if not self.email_password:
                print("Email password not configured - skipping email notification")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = subject
            
            # Convert markdown-style formatting to HTML
            html_message = self._convert_to_html(message)
            msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.config.sender_email, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending email notification: {str(e)}")
            return False
    
    def _send_slack(self, message: str, color: str = "info") -> bool:
        """Send Slack notification."""
        try:
            if not self.slack_webhook_url:
                print("Slack webhook URL not configured - skipping Slack notification")
                return False
            
            # Convert markdown-style formatting to Slack format
            slack_message = self._convert_to_slack_format(message)
            
            payload = {
                "text": slack_message,
                "username": self.config.sender_name,
                "icon_emoji": ":robot_face:"
            }
            
            response = requests.post(self.slack_webhook_url, json=payload)
            
            if response.status_code == 200:
                print(f"Slack notification sent successfully")
                return True
            else:
                print(f"Error sending Slack notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending Slack notification: {str(e)}")
            return False
    
    def _convert_to_html(self, message: str) -> str:
        """Convert markdown-style message to HTML."""
        # Replace ** with <strong> tags properly
        html = message
        html = html.replace('**', '<strong>', 1)
        html = html.replace('**', '</strong>', 1)
        html = html.replace('\n\n', '</p><p>')
        html = f"<p>{html}</p>"
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                p {{ margin: 10px 0; }}
                strong {{ color: #333; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
    
    def _convert_to_slack_format(self, message: str) -> str:
        """Convert markdown-style message to Slack format."""
        # Slack uses * for bold instead of **
        slack_message = message.replace('**', '*')
        return slack_message
