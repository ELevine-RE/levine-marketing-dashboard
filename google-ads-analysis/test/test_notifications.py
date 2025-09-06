#!/usr/bin/env python3
"""
Unit Tests for Notification System
==================================

Comprehensive test suite for the NotificationManager class.
Tests all notification types and formatting.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ads.notifications import NotificationManager, NotificationConfig, NotificationType

class TestNotificationManager(unittest.TestCase):
    """Test cases for NotificationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test configuration with notifications disabled
        self.test_config = NotificationConfig(
            email_enabled=False,
            slack_enabled=False,
            email_recipients=["test@example.com"]
        )
        self.notification_manager = NotificationManager(self.test_config)
    
    def test_phase_advance_notification_formatting(self):
        """Test phase advancement message formatting."""
        next_phase = "phase_2"
        details = {
            'current_phase': 'phase_1',
            'recommended_action': 'Safe to introduce tCPA at $100-$150',
            'readiness_score': 0.95,
            'blocking_factors': []
        }
        
        message = self.notification_manager._format_phase_advance_message(next_phase, details)
        
        self.assertIn("PHASE ADVANCEMENT ALERT", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("PHASE_1 → PHASE_2", message)
        self.assertIn("Safe to introduce tCPA at $100-$150", message)
        self.assertIn("0.95", message)
    
    def test_phase_lag_notification_formatting(self):
        """Test phase lag message formatting."""
        days_in_phase = 30
        expected_days = 21
        reason = "Insufficient conversions"
        
        message = self.notification_manager._format_phase_lag_message(days_in_phase, expected_days, reason)
        
        self.assertIn("PHASE LAG ALERT", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("30", message)
        self.assertIn("21", message)
        self.assertIn("9", message)  # days behind
        self.assertIn("Insufficient conversions", message)
    
    def test_critical_lag_notification_formatting(self):
        """Test critical lag message formatting."""
        days_in_phase = 40
        max_days = 35
        reason = "Multiple blocking factors preventing advancement"
        
        message = self.notification_manager._format_critical_lag_message(days_in_phase, max_days, reason)
        
        self.assertIn("CRITICAL LAG ALERT", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("40", message)
        self.assertIn("35", message)
        self.assertIn("5", message)  # days over limit
        self.assertIn("Multiple blocking factors preventing advancement", message)
        self.assertIn("IMMEDIATE ACTIONS REQUIRED", message)
    
    def test_planned_change_notification_formatting(self):
        """Test planned change message formatting."""
        change = {
            'type': 'budget_adjustment',
            'new_daily_budget': 60.0
        }
        execute_after = (datetime.now() + timedelta(hours=2)).isoformat()
        
        message = self.notification_manager._format_planned_change_message(change, execute_after)
        
        self.assertIn("PLANNED CHANGE ALERT", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("budget_adjustment", message)
        self.assertIn("New Daily Budget: $60.0", message)
        self.assertIn("To Cancel This Change", message)
        self.assertIn("CANCEL", message)
    
    def test_stop_loss_notification_formatting(self):
        """Test stop-loss message formatting."""
        reason = "Spend $120.00 exceeds 2.0x budget with 0 conversions"
        
        message = self.notification_manager._format_stop_loss_message(reason)
        
        self.assertIn("STOP-LOSS ALERT", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("STOP-LOSS TRIGGERED", message)
        self.assertIn("Spend $120.00 exceeds 2.0x budget with 0 conversions", message)
        self.assertIn("IMMEDIATE ACTIONS REQUIRED", message)
    
    def test_daily_recap_notification_formatting(self):
        """Test daily recap message formatting."""
        phase_status = {
            'current_phase': 'phase_1',
            'message': 'Phase progressing normally'
        }
        lag_alerts = ["Phase lagging - 5 days behind expected"]
        planned_changes = [
            {'type': 'budget_adjustment', 'execute_after': '2024-01-01T10:00:00'}
        ]
        stop_loss_alerts = ["STOP-LOSS: No conversions in 15 days"]
        
        message = self.notification_manager._format_daily_recap_message(
            phase_status, lag_alerts, planned_changes, stop_loss_alerts
        )
        
        self.assertIn("DAILY CAMPAIGN RECAP", message)
        self.assertIn("L.R - PMax - General", message)
        self.assertIn("PHASE_1", message)
        self.assertIn("Phase progressing normally", message)
        self.assertIn("Lag Alerts (1)", message)
        self.assertIn("Stop-Loss Alerts (1)", message)
        self.assertIn("Planned Changes (1)", message)
    
    def test_daily_recap_no_alerts(self):
        """Test daily recap with no alerts."""
        phase_status = {
            'current_phase': 'phase_1',
            'message': 'Phase progressing normally'
        }
        lag_alerts = []
        planned_changes = []
        stop_loss_alerts = []
        
        message = self.notification_manager._format_daily_recap_message(
            phase_status, lag_alerts, planned_changes, stop_loss_alerts
        )
        
        self.assertIn("DAILY CAMPAIGN RECAP", message)
        self.assertIn("No alerts to report - campaign performing normally", message)
    
    def test_change_details_formatting(self):
        """Test change details formatting for different change types."""
        # Budget adjustment
        budget_change = {'type': 'budget_adjustment', 'new_daily_budget': 60.0}
        details = self.notification_manager._format_change_details(budget_change)
        self.assertIn("New Daily Budget: $60.0", details)
        
        # Target CPA adjustment
        tcpa_change = {'type': 'target_cpa_adjustment', 'new_target_cpa': 120.0}
        details = self.notification_manager._format_change_details(tcpa_change)
        self.assertIn("New Target CPA: $120.0", details)
        
        # Asset group modification
        asset_change = {'type': 'asset_group_modification', 'action': 'add_assets'}
        details = self.notification_manager._format_change_details(asset_change)
        self.assertIn("Action: add_assets", details)
        
        # Geo targeting modification
        geo_change = {'type': 'geo_targeting_modification', 'action': 'add_location'}
        details = self.notification_manager._format_change_details(geo_change)
        self.assertIn("Action: add_location", details)
        
        # Unknown change type
        unknown_change = {'type': 'unknown_type'}
        details = self.notification_manager._format_change_details(unknown_change)
        self.assertIn("Change Type: unknown_type", details)
    
    def test_time_remaining_formatting(self):
        """Test time remaining formatting."""
        # Future time
        future_time = datetime.now() + timedelta(hours=3, minutes=30)
        remaining = self.notification_manager._format_time_remaining(future_time)
        self.assertIn("3h", remaining)
        
        # Future time less than 1 hour
        future_time = datetime.now() + timedelta(minutes=45)
        remaining = self.notification_manager._format_time_remaining(future_time)
        self.assertIn("45m", remaining)
        
        # Past time
        past_time = datetime.now() - timedelta(hours=1)
        remaining = self.notification_manager._format_time_remaining(past_time)
        self.assertEqual(remaining, "Executing now")
    
    def test_html_conversion(self):
        """Test markdown to HTML conversion."""
        markdown_message = "**Bold text**\n\nRegular text"
        html = self.notification_manager._convert_to_html(markdown_message)
        
        self.assertIn("<strong>Bold text</strong>", html)
        self.assertIn("Regular text", html)
        self.assertIn("<html>", html)
        self.assertIn("<body>", html)
    
    def test_slack_format_conversion(self):
        """Test markdown to Slack format conversion."""
        markdown_message = "**Bold text**\n\nRegular text"
        slack_message = self.notification_manager._convert_to_slack_format(markdown_message)
        
        self.assertIn("*Bold text*", slack_message)
        self.assertIn("Regular text", slack_message)
        self.assertNotIn("**Bold text**", slack_message)
    
    @patch('ads.notifications.smtplib.SMTP')
    def test_email_sending_disabled(self, mock_smtp):
        """Test email sending when disabled."""
        config = NotificationConfig(email_enabled=False)
        manager = NotificationManager(config)
        
        success = manager._send_email("Test Subject", "Test Message")
        self.assertFalse(success)
        mock_smtp.assert_not_called()
    
    @patch('ads.notifications.requests.post')
    def test_slack_sending_disabled(self, mock_post):
        """Test Slack sending when disabled."""
        config = NotificationConfig(slack_enabled=False)
        manager = NotificationManager(config)
        
        success = manager._send_slack("Test Message")
        self.assertFalse(success)
        mock_post.assert_not_called()
    
    @patch('ads.notifications.smtplib.SMTP')
    def test_email_sending_no_password(self, mock_smtp):
        """Test email sending without password configured."""
        config = NotificationConfig(email_enabled=True)
        manager = NotificationManager(config)
        manager.email_password = ""  # No password
        
        success = manager._send_email("Test Subject", "Test Message")
        self.assertFalse(success)
        mock_smtp.assert_not_called()
    
    @patch('ads.notifications.requests.post')
    def test_slack_sending_no_webhook(self, mock_post):
        """Test Slack sending without webhook configured."""
        config = NotificationConfig(slack_enabled=True)
        manager = NotificationManager(config)
        manager.slack_webhook_url = ""  # No webhook
        
        success = manager._send_slack("Test Message")
        self.assertFalse(success)
        mock_post.assert_not_called()
    
    def test_notification_config_defaults(self):
        """Test notification config default values."""
        config = NotificationConfig()
        
        self.assertTrue(config.email_enabled)
        self.assertTrue(config.slack_enabled)
        self.assertEqual(config.sender_email, "noreply@levine.realestate")
        self.assertEqual(config.sender_name, "Google Ads AI Manager")
        self.assertEqual(config.email_recipients, ["evan@levine.realestate"])
    
    def test_notification_config_custom_values(self):
        """Test notification config with custom values."""
        config = NotificationConfig(
            email_enabled=False,
            slack_enabled=True,
            email_recipients=["custom@example.com"],
            sender_email="custom@example.com",
            sender_name="Custom Manager"
        )
        
        self.assertFalse(config.email_enabled)
        self.assertTrue(config.slack_enabled)
        self.assertEqual(config.email_recipients, ["custom@example.com"])
        self.assertEqual(config.sender_email, "custom@example.com")
        self.assertEqual(config.sender_name, "Custom Manager")
    
    def test_send_phase_advance_with_disabled_notifications(self):
        """Test phase advance notification with notifications disabled."""
        next_phase = "phase_2"
        details = {'current_phase': 'phase_1', 'recommended_action': 'Test action'}
        
        success = self.notification_manager.send_phase_advance(next_phase, details)
        self.assertTrue(success)  # Should succeed even with notifications disabled
    
    def test_send_phase_lag_with_disabled_notifications(self):
        """Test phase lag notification with notifications disabled."""
        success = self.notification_manager.send_phase_lag(30, 21, "Test reason")
        self.assertTrue(success)  # Should succeed even with notifications disabled
    
    def test_send_critical_lag_with_disabled_notifications(self):
        """Test critical lag notification with notifications disabled."""
        success = self.notification_manager.send_critical_lag(40, 35, "Test reason")
        self.assertTrue(success)  # Should succeed even with notifications disabled
    
    def test_announce_planned_change_with_disabled_notifications(self):
        """Test planned change notification with notifications disabled."""
        change = {'type': 'budget_adjustment', 'new_daily_budget': 60.0}
        execute_after = (datetime.now() + timedelta(hours=2)).isoformat()
        
        success = self.notification_manager.announce_planned_change(change, execute_after)
        self.assertTrue(success)  # Should succeed even with notifications disabled
    
    def test_send_stop_loss_with_disabled_notifications(self):
        """Test stop-loss notification with notifications disabled."""
        success = self.notification_manager.send_stop_loss("Test reason")
        self.assertTrue(success)  # Should succeed even with notifications disabled
    
    def test_send_daily_recap_with_disabled_notifications(self):
        """Test daily recap notification with notifications disabled."""
        phase_status = {'current_phase': 'phase_1', 'message': 'Test message'}
        lag_alerts = []
        planned_changes = []
        stop_loss_alerts = []
        
        success = self.notification_manager.send_daily_recap(
            phase_status, lag_alerts, planned_changes, stop_loss_alerts
        )
        self.assertTrue(success)  # Should succeed even with notifications disabled

if __name__ == '__main__':
    unittest.main()
