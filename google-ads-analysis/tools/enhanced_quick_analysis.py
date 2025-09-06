#!/usr/bin/env python3
"""
Enhanced Quick Analysis with Milestone Detection
===============================================

Monitors campaign performance and detects when campaigns exit Phase 1.
Sends milestone alerts for the Crawl/Walk strategy.
"""

import os
import sys
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

class EnhancedQuickAnalysis:
    """Enhanced analysis with milestone detection for Crawl/Walk strategy"""
    
    def __init__(self):
        self.customer_id = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '5426234549')
        
        # Initialize Google Ads client
        try:
            self.ads_client = GoogleAdsClient.load_from_storage()
            print("✅ Google Ads API client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google Ads client: {e}")
            self.ads_client = None
        
        # Email configuration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': os.environ.get('EMAIL_SENDER', 'evan@levine.realestate'),
            'sender_password': os.environ.get('EMAIL_PASSWORD'),
            'recipient_email': os.environ.get('EMAIL_RECIPIENT', 'evan@levine.realestate')
        }
    
    def analyze_campaigns(self):
        """Analyze all campaigns and detect milestones"""
        if not self.ads_client:
            return {"success": False, "error": "Google Ads client not initialized"}
        
        try:
            print("🔍 Analyzing campaigns for milestone detection...")
            
            # Get all Performance Max campaigns
            campaigns = self._get_performance_max_campaigns()
            
            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'campaigns': [],
                'milestones': [],
                'summary': {}
            }
            
            for campaign in campaigns:
                campaign_analysis = self._analyze_campaign(campaign)
                analysis_results['campaigns'].append(campaign_analysis)
                
                # Check for milestones
                milestone = self._check_milestone(campaign_analysis)
                if milestone:
                    analysis_results['milestones'].append(milestone)
            
            # Generate summary
            analysis_results['summary'] = self._generate_summary(analysis_results)
            
            # Send email if milestones detected
            if analysis_results['milestones']:
                self._send_milestone_email(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ Error analyzing campaigns: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_performance_max_campaigns(self):
        """Get all Performance Max campaigns"""
        try:
            gaql_query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method
                FROM campaign 
                WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'
                AND campaign.status IN ('ENABLED', 'PAUSED')
            """
            
            ga_service = self.ads_client.get_service("GoogleAdsService")
            response = ga_service.search(
                customer_id=self.customer_id,
                query=gaql_query
            )
            
            campaigns = []
            for row in response:
                campaigns.append({
                    'id': row.campaign.id,
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'budget_micros': row.campaign_budget.amount_micros,
                    'budget_amount': row.campaign_budget.amount_micros / 1000000
                })
            
            return campaigns
            
        except Exception as e:
            print(f"❌ Error fetching campaigns: {e}")
            return []
    
    def _analyze_campaign(self, campaign):
        """Analyze individual campaign performance"""
        try:
            campaign_id = campaign['id']
            
            # Get performance data for last 30 days
            gaql_query = f"""
                SELECT 
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.cost_per_conversion,
                    metrics.conversion_rate,
                    campaign.name
                FROM campaign 
                WHERE campaign.id = {campaign_id}
                AND segments.date BETWEEN '{self._get_date_range()[0]}' AND '{self._get_date_range()[1]}'
            """
            
            ga_service = self.ads_client.get_service("GoogleAdsService")
            response = ga_service.search(
                customer_id=self.customer_id,
                query=gaql_query
            )
            
            performance_data = {}
            for row in response:
                performance_data = {
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'ctr': row.metrics.ctr,
                    'cost_micros': row.metrics.cost_micros,
                    'cost_amount': row.metrics.cost_micros / 1000000,
                    'conversions': row.metrics.conversions,
                    'cost_per_conversion': row.metrics.cost_per_conversion,
                    'conversion_rate': row.metrics.conversion_rate
                }
                break
            
            # Determine campaign phase
            phase = self._determine_campaign_phase(performance_data)
            
            return {
                'campaign_info': campaign,
                'performance': performance_data,
                'phase': phase,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error analyzing campaign {campaign['name']}: {e}")
            return {
                'campaign_info': campaign,
                'performance': {},
                'phase': 'UNKNOWN',
                'error': str(e)
            }
    
    def _determine_campaign_phase(self, performance_data):
        """Determine campaign phase based on performance"""
        if not performance_data or not performance_data.get('conversions'):
            return 'PHASE_1'  # Learning phase
        
        conversions = performance_data['conversions']
        
        # Phase determination logic
        if conversions >= 30:
            return 'PHASE_3'  # Optimized
        elif conversions >= 15:
            return 'PHASE_2'  # Learning complete
        else:
            return 'PHASE_1'  # Learning phase
    
    def _check_milestone(self, campaign_analysis):
        """Check if campaign has reached a milestone"""
        campaign_name = campaign_analysis['campaign_info']['name']
        phase = campaign_analysis['phase']
        
        # Check for Local Presence campaign milestone
        if 'Local Presence' in campaign_name and phase in ['PHASE_2', 'PHASE_3']:
            return {
                'type': 'PHASE_EXIT',
                'campaign_name': campaign_name,
                'phase': phase,
                'message': f"Campaign '{campaign_name}' has exited Phase 1 and is now in {phase}",
                'action_required': 'Review scheduled document to launch Feeder Markets campaign',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _generate_summary(self, analysis_results):
        """Generate analysis summary"""
        total_campaigns = len(analysis_results['campaigns'])
        active_campaigns = len([c for c in analysis_results['campaigns'] if c['campaign_info']['status'] == 'ENABLED'])
        milestones_detected = len(analysis_results['milestones'])
        
        total_cost = sum(c['performance'].get('cost_amount', 0) for c in analysis_results['campaigns'])
        total_conversions = sum(c['performance'].get('conversions', 0) for c in analysis_results['campaigns'])
        
        return {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'milestones_detected': milestones_detected,
            'total_cost': total_cost,
            'total_conversions': total_conversions,
            'analysis_date': datetime.now().isoformat()
        }
    
    def _send_milestone_email(self, analysis_results):
        """Send milestone alert email"""
        try:
            if not self.email_config['sender_password']:
                print("⚠️ Email password not configured, skipping email")
                return
            
            # Create email content
            subject = "🚨 MILESTONE REACHED: Campaign Phase Exit Detected"
            
            # Build email body
            body = self._build_milestone_email_body(analysis_results)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['recipient_email'], text)
            server.quit()
            
            print("✅ Milestone email sent successfully")
            
        except Exception as e:
            print(f"❌ Error sending milestone email: {e}")
    
    def _build_milestone_email_body(self, analysis_results):
        """Build HTML email body for milestone alerts"""
        milestones = analysis_results['milestones']
        summary = analysis_results['summary']
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .milestone {{ background-color: #ff6b6b; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .campaign-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .action-required {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <h1>🚨 MILESTONE REACHED: Campaign Phase Exit Detected</h1>
            
            <div class="milestone">
                <h2>** MILESTONE REACHED: Campaign 'Local Presence' is now optimized. Please review the 'Scheduled Campaign Launch' Google Doc to launch the 'Feeder Markets' campaign. **</h2>
            </div>
            
            <h2>📊 Campaign Analysis Summary</h2>
            <div class="summary">
                <p><strong>Analysis Date:</strong> {summary['analysis_date']}</p>
                <p><strong>Total Campaigns:</strong> {summary['total_campaigns']}</p>
                <p><strong>Active Campaigns:</strong> {summary['active_campaigns']}</p>
                <p><strong>Total Cost:</strong> ${summary['total_cost']:.2f}</p>
                <p><strong>Total Conversions:</strong> {summary['total_conversions']}</p>
            </div>
            
            <h2>🎯 Milestone Details</h2>
        """
        
        for milestone in milestones:
            html_body += f"""
            <div class="campaign-info">
                <h3>{milestone['campaign_name']}</h3>
                <p><strong>Phase:</strong> {milestone['phase']}</p>
                <p><strong>Message:</strong> {milestone['message']}</p>
                <p><strong>Timestamp:</strong> {milestone['timestamp']}</p>
            </div>
            """
        
        html_body += f"""
            <div class="action-required">
                <h3>🎯 Action Required</h3>
                <p><strong>Next Steps:</strong></p>
                <ul>
                    <li>Review the 'Scheduled Campaign Launch - Feeder Markets' Google Doc</li>
                    <li>Verify campaign settings and budget allocation ($41/day)</li>
                    <li>Set up HNW zip code targeting for major metropolitan areas</li>
                    <li>Launch the 'L.R - PMax - Feeder Markets' campaign</li>
                    <li>Monitor both campaigns for optimal performance</li>
                </ul>
            </div>
            
            <h2>📈 Campaign Performance Details</h2>
        """
        
        for campaign in analysis_results['campaigns']:
            perf = campaign['performance']
            html_body += f"""
            <div class="campaign-info">
                <h3>{campaign['campaign_info']['name']}</h3>
                <p><strong>Status:</strong> {campaign['campaign_info']['status']}</p>
                <p><strong>Phase:</strong> {campaign['phase']}</p>
                <p><strong>Impressions:</strong> {perf.get('impressions', 0):,}</p>
                <p><strong>Clicks:</strong> {perf.get('clicks', 0):,}</p>
                <p><strong>CTR:</strong> {perf.get('ctr', 0):.2f}%</p>
                <p><strong>Cost:</strong> ${perf.get('cost_amount', 0):.2f}</p>
                <p><strong>Conversions:</strong> {perf.get('conversions', 0)}</p>
                <p><strong>Cost per Conversion:</strong> ${perf.get('cost_per_conversion', 0):.2f}</p>
            </div>
            """
        
        html_body += """
            <hr>
            <p><em>This email was automatically generated by the Enhanced Quick Analysis system.</em></p>
        </body>
        </html>
        """
        
        return html_body
    
    def _get_date_range(self):
        """Get date range for analysis (last 30 days)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def run_daily_analysis(self):
        """Run daily analysis and send summary"""
        print("🌅 Running daily campaign analysis...")
        
        analysis_results = self.analyze_campaigns()
        
        if analysis_results.get('success', True):  # Default to True if no success field
            print("✅ Daily analysis completed successfully")
            
            # Log results
            self._log_analysis_results(analysis_results)
            
            # Send summary email (even without milestones)
            self._send_daily_summary_email(analysis_results)
            
        else:
            print(f"❌ Daily analysis failed: {analysis_results.get('error', 'Unknown error')}")
        
        return analysis_results
    
    def _log_analysis_results(self, analysis_results):
        """Log analysis results to file"""
        try:
            log_file = 'data/daily_analysis_log.json'
            os.makedirs('data', exist_ok=True)
            
            # Load existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new log entry
            logs.append(analysis_results)
            
            # Keep only last 30 days
            if len(logs) > 30:
                logs = logs[-30:]
            
            # Save logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            print(f"✅ Analysis results logged to {log_file}")
            
        except Exception as e:
            print(f"❌ Error logging analysis results: {e}")
    
    def _send_daily_summary_email(self, analysis_results):
        """Send daily summary email"""
        try:
            if not self.email_config['sender_password']:
                print("⚠️ Email password not configured, skipping daily summary")
                return
            
            subject = f"📊 Daily Campaign Analysis - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Build email body
            body = self._build_daily_summary_email_body(analysis_results)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['recipient_email'], text)
            server.quit()
            
            print("✅ Daily summary email sent successfully")
            
        except Exception as e:
            print(f"❌ Error sending daily summary email: {e}")
    
    def _build_daily_summary_email_body(self, analysis_results):
        """Build HTML email body for daily summary"""
        summary = analysis_results['summary']
        campaigns = analysis_results['campaigns']
        milestones = analysis_results['milestones']
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #4a90e2; color: white; padding: 20px; border-radius: 10px; }}
                .milestone {{ background-color: #ff6b6b; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .campaign-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Daily Campaign Analysis Report</h1>
                <p>Analysis Date: {summary['analysis_date']}</p>
            </div>
        """
        
        # Add milestone alerts at the top if any
        if milestones:
            html_body += """
            <div class="milestone">
                <h2>🚨 MILESTONE ALERTS</h2>
            """
            for milestone in milestones:
                html_body += f"""
                <p><strong>{milestone['campaign_name']}:</strong> {milestone['message']}</p>
                """
            html_body += "</div>"
        
        html_body += f"""
            <div class="summary">
                <h2>📈 Summary</h2>
                <p><strong>Total Campaigns:</strong> {summary['total_campaigns']}</p>
                <p><strong>Active Campaigns:</strong> {summary['active_campaigns']}</p>
                <p><strong>Total Cost:</strong> ${summary['total_cost']:.2f}</p>
                <p><strong>Total Conversions:</strong> {summary['total_conversions']}</p>
                <p><strong>Milestones Detected:</strong> {summary['milestones_detected']}</p>
            </div>
            
            <h2>🎯 Campaign Details</h2>
        """
        
        for campaign in campaigns:
            perf = campaign['performance']
            html_body += f"""
            <div class="campaign-info">
                <h3>{campaign['campaign_info']['name']}</h3>
                <p><strong>Status:</strong> {campaign['campaign_info']['status']}</p>
                <p><strong>Phase:</strong> {campaign['phase']}</p>
                <p><strong>Budget:</strong> ${campaign['campaign_info']['budget_amount']:.2f}/day</p>
                <p><strong>Impressions:</strong> {perf.get('impressions', 0):,}</p>
                <p><strong>Clicks:</strong> {perf.get('clicks', 0):,}</p>
                <p><strong>CTR:</strong> {perf.get('ctr', 0):.2f}%</p>
                <p><strong>Cost:</strong> ${perf.get('cost_amount', 0):.2f}</p>
                <p><strong>Conversions:</strong> {perf.get('conversions', 0)}</p>
                <p><strong>Cost per Conversion:</strong> ${perf.get('cost_per_conversion', 0):.2f}</p>
            </div>
            """
        
        html_body += """
            <hr>
            <p><em>This report was automatically generated by the Enhanced Quick Analysis system.</em></p>
        </body>
        </html>
        """
        
        return html_body

def main():
    """Main execution function"""
    print("🔍 Starting Enhanced Quick Analysis")
    print("=" * 50)
    
    analyzer = EnhancedQuickAnalysis()
    
    # Run daily analysis
    results = analyzer.run_daily_analysis()
    
    if results.get('success', True):
        print("✅ Analysis completed successfully")
        
        # Print summary
        summary = results['summary']
        print(f"\n📊 Summary:")
        print(f"   Total Campaigns: {summary['total_campaigns']}")
        print(f"   Active Campaigns: {summary['active_campaigns']}")
        print(f"   Total Cost: ${summary['total_cost']:.2f}")
        print(f"   Total Conversions: {summary['total_conversions']}")
        print(f"   Milestones Detected: {summary['milestones_detected']}")
        
        # Print milestones
        if results['milestones']:
            print(f"\n🚨 Milestones Detected:")
            for milestone in results['milestones']:
                print(f"   {milestone['campaign_name']}: {milestone['message']}")
        
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
