"""
Daily Email Summary System
Sends executive summary of status, goals, and planned changes
"""

import smtplib
import json
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import core systems
sys.path.append('google-ads-analysis')
from google_ads_integration import SimpleGoogleAdsManager
from google_analytics_simple import SimpleGoogleAnalyticsManager
from sierra_integration import SimpleSierraManager

class DailyEmailSystem:
    def __init__(self):
        self.ads_manager = SimpleGoogleAdsManager()
        self.analytics_manager = SimpleGoogleAnalyticsManager()
        self.sierra_manager = SimpleSierraManager()
        
        # Email configuration
        self.sender_email = os.getenv('EMAIL_SENDER', 'evan@levine.realestate')
        self.sender_password = os.getenv('EMAIL_PASSWORD', '')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT', 'evan@levine.realestate')
        
    def send_daily_summary(self):
        """Send daily executive summary email"""
        try:
            # Generate email content
            subject, html_content = self.generate_email_content()
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            if self.sender_password:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                print("✅ Daily summary email sent successfully")
            else:
                print("⚠️ Email password not configured - would send:")
                print(f"To: {self.recipient_email}")
                print(f"Subject: {subject}")
                print("Content preview:")
                print(html_content[:500] + "...")
                
        except Exception as e:
            print(f"❌ Error sending daily summary: {e}")
    
    def generate_email_content(self):
        """Generate email content with status, goals, and planned changes"""
        
        # Get data
        ads_data = self.get_ads_summary()
        goals_data = self.get_goals_summary()
        staged_changes = self.get_staged_changes_summary()
        
        # Email subject
        subject = f"🤖 AI Google Ads Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4fd; border-radius: 5px; }}
                .change {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .goal {{ background-color: #d1ecf1; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .status-good {{ color: #28a745; }}
                .status-warning {{ color: #ffc107; }}
                .status-error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI Google Ads Management System</h1>
                <p>Daily Executive Summary - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Campaign Status</h2>
                {ads_data}
            </div>
            
            <div class="section">
                <h2>🎯 Goals Progress</h2>
                {goals_data}
            </div>
            
            <div class="section">
                <h2>⏳ Staged Changes</h2>
                {staged_changes}
            </div>
            
            <div class="section">
                <h2>📋 Next Actions</h2>
                <ul>
                    <li>Review staged changes above</li>
                    <li>Check dashboard for detailed diagnostics</li>
                    <li>Intervene via Cursor chat if needed</li>
                </ul>
            </div>
            
            <div class="section">
                <p><em>This is an automated summary from your AI Google Ads Management System.</em></p>
                <p><em>Dashboard: <a href="https://levine-real-estate-website-4nxq5aaspozpfyed5gsxsk.streamlit.app/">View Dashboard</a></em></p>
            </div>
        </body>
        </html>
        """
        
        return subject, html_content
    
    def get_ads_summary(self):
        """Get Google Ads summary data"""
        try:
            ads_data = self.ads_manager.get_campaign_data()
            
            if ads_data and 'campaigns' in ads_data:
                campaigns = ads_data['campaigns']
                active_campaigns = [c for c in campaigns if c.get('status') == 'ENABLED']
                
                total_spend = sum(c.get('cost', 0) for c in campaigns)
                total_conversions = sum(c.get('conversions', 0) for c in campaigns)
                avg_cpl = total_spend / total_conversions if total_conversions > 0 else 0
                
                return f"""
                <div class="metric">
                    <strong>Active Campaigns:</strong> {len(active_campaigns)}
                </div>
                <div class="metric">
                    <strong>Total Spend (30d):</strong> ${total_spend:,.2f}
                </div>
                <div class="metric">
                    <strong>Total Conversions:</strong> {total_conversions}
                </div>
                <div class="metric">
                    <strong>Average CPL:</strong> ${avg_cpl:.2f}
                </div>
                """
            else:
                return "<p class='status-warning'>⚠️ Unable to fetch campaign data</p>"
                
        except Exception as e:
            return f"<p class='status-error'>❌ Error fetching ads data: {str(e)}</p>"
    
    def get_goals_summary(self):
        """Get goals progress summary"""
        goals = [
            {"name": "Crawl Campaign Conversions", "target": 30, "current": 0, "deadline": "2025-09-27"},
            {"name": "Monthly Budget Utilization", "target": 100, "current": 0, "deadline": "2025-09-30"},
            {"name": "CPL Target", "target": 150, "current": 0, "deadline": "Ongoing"},
        ]
        
        goals_html = ""
        for goal in goals:
            progress = min((goal['current'] / goal['target']) * 100, 100) if goal['target'] > 0 else 0
            status_class = "status-good" if progress >= 80 else "status-warning" if progress >= 50 else "status-error"
            
            goals_html += f"""
            <div class="goal">
                <strong>{goal['name']}</strong><br>
                Progress: {goal['current']}/{goal['target']} ({progress:.1f}%)<br>
                Deadline: {goal['deadline']}<br>
                <span class="{status_class}">Status: {'On Track' if progress >= 80 else 'Behind' if progress < 50 else 'Progressing'}</span>
            </div>
            """
        
        return goals_html
    
    def get_staged_changes_summary(self):
        """Get staged changes summary"""
        try:
            if os.path.exists('data/staged_changes.json'):
                with open('data/staged_changes.json', 'r') as f:
                    staged_changes = json.load(f)
                
                if not staged_changes:
                    return "<p>✅ No staged changes pending</p>"
                
                changes_html = ""
                for i, change in enumerate(staged_changes[:5]):  # Show max 5 changes
                    changes_html += f"""
                    <div class="change">
                        <strong>{change.get('type', 'Unknown')} - {change.get('campaign', 'Unknown Campaign')}</strong><br>
                        Current: {change.get('current', 'N/A')} → Proposed: {change.get('proposed', 'N/A')}<br>
                        Reason: {change.get('reason', 'N/A')}<br>
                        <em>Created: {change.get('created', 'N/A')}</em>
                    </div>
                    """
                
                if len(staged_changes) > 5:
                    changes_html += f"<p><em>... and {len(staged_changes) - 5} more changes</em></p>"
                
                return changes_html
            else:
                return "<p>✅ No staged changes file found</p>"
                
        except Exception as e:
            return f"<p class='status-error'>❌ Error loading staged changes: {str(e)}</p>"

def main():
    """Main function to send daily summary"""
    email_system = DailyEmailSystem()
    email_system.send_daily_summary()

if __name__ == "__main__":
    main()
