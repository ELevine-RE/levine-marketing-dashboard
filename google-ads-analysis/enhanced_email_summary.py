#!/usr/bin/env python3
"""
Enhanced Email Summary Generator
===============================

Generates comprehensive, actionable email summaries for Google Ads campaigns
with dynamic subject lines and structured content including:

- Dynamic subject lines based on planned changes
- Top-line summary (last 24 hours)
- Lead quality analysis
- Phase progression status
- Planned actions & intervention window
- Key insights

"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_ads_manager import GoogleAdsManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class EnhancedEmailSummaryGenerator:
    """Generates enhanced email summaries for Google Ads campaigns."""
    
    def __init__(self, email_config: Dict = None):
        """
        Initialize the enhanced email summary generator.
        
        Args:
            email_config: Dictionary containing email settings
                - smtp_server: SMTP server (e.g., 'smtp.gmail.com')
                - smtp_port: SMTP port (e.g., 587)
                - sender_email: Email address to send from
                - sender_password: Email password or app password
                - recipient_email: Email address to send to
        """
        self.manager = GoogleAdsManager()
        self.email_config = email_config or {}
        self.campaign_name = "L.R - PMax - General"
        self.intervention_deadline = datetime.now() + timedelta(hours=2)
        
        # Set manager account access for proper API calls
        if hasattr(self.manager, 'client') and self.manager.client:
            self.manager.client.login_customer_id = "5426234549"
    
    def get_last_24_hours_data(self) -> Dict:
        """Get performance data for the last 24 hours."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.average_cpc
                FROM campaign
                WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}'
                AND '{end_date.strftime('%Y-%m-%d')}'
                AND campaign.status = 'ENABLED'
            """
            
            response = self.manager.google_ads_service.search(
                customer_id="5426234549",
                query=query
            )
            
            total_impressions = 0
            total_clicks = 0
            total_cost = 0
            total_conversions = 0
            
            for row in response:
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
            
            cost_usd = total_cost / 1_000_000
            cpl = cost_usd / total_conversions if total_conversions > 0 else 0
            
            return {
                'spend': cost_usd,
                'conversions': total_conversions,
                'cpl': cpl,
                'impressions': total_impressions,
                'clicks': total_clicks
            }
        except Exception as e:
            console.print(f"[red]Error getting 24h data: {e}[/red]")
            return {'spend': 0, 'conversions': 0, 'cpl': 0, 'impressions': 0, 'clicks': 0}
    
    def get_lead_quality_data(self) -> Dict:
        """Get lead quality analysis data."""
        try:
            # Query for lead quality data
            query = """
                SELECT 
                    metrics.lead_quality_score,
                    metrics.cost_per_high_quality_lead,
                    metrics.high_quality_leads,
                    metrics.total_leads
                FROM customer
                WHERE segments.date DURING LAST_7_DAYS
            """
            
            response = self.manager.google_ads_service.search(
                customer_id="5426234549",
                query=query
            )
            
            total_leads = 0
            high_quality_leads = 0
            total_lqs = 0
            total_cphql = 0
            lead_count = 0
            
            for row in response:
                total_leads += row.metrics.total_leads
                high_quality_leads += row.metrics.high_quality_leads
                if row.metrics.lead_quality_score > 0:
                    total_lqs += row.metrics.lead_quality_score
                    lead_count += 1
                if row.metrics.cost_per_high_quality_lead > 0:
                    total_cphql += row.metrics.cost_per_high_quality_lead
            
            avg_lqs = total_lqs / lead_count if lead_count > 0 else 0
            avg_cphql = total_cphql / lead_count if lead_count > 0 else 0
            
            return {
                'new_leads_scored': total_leads,
                'lqs_new_leads': avg_lqs,
                'cphql': avg_cphql,
                'avg_lqs_7d': avg_lqs,
                'high_quality_leads': high_quality_leads
            }
        except Exception as e:
            console.print(f"[red]Error getting lead quality data: {e}[/red]")
            return {
                'new_leads_scored': 0,
                'lqs_new_leads': 0,
                'cphql': 0,
                'avg_lqs_7d': 0,
                'high_quality_leads': 0
            }
    
    def get_phase_progression_data(self) -> Dict:
        """Get phase progression status."""
        try:
            # This would integrate with your phase management system
            # For now, returning mock data based on typical phase progression
            current_phase = "PHASE_1"
            target_conversions = 30
            current_conversions = 18
            progress_percentage = (current_conversions / target_conversions) * 100
            
            if progress_percentage >= 80:
                status = "On Track"
            elif progress_percentage >= 60:
                status = "Slightly Behind"
            else:
                status = "Lagging"
            
            return {
                'current_phase': current_phase,
                'progress': f"{current_conversions} / {target_conversions} conversions",
                'status': status,
                'progress_percentage': progress_percentage
            }
        except Exception as e:
            console.print(f"[red]Error getting phase progression: {e}[/red]")
            return {
                'current_phase': "PHASE_1",
                'progress': "0 / 30 conversions",
                'status': "Unknown",
                'progress_percentage': 0
            }
    
    def get_planned_changes(self) -> List[Dict]:
        """Get planned changes and their details."""
        try:
            # This would integrate with your change management system
            # For now, returning mock data
            planned_changes = []
            
            # Example: Check if CpHQL is below target
            lead_quality_data = self.get_lead_quality_data()
            if lead_quality_data['cphql'] > 300:  # Assuming $300 target
                planned_changes.append({
                    'type': 'budget_increase',
                    'description': 'Increase daily budget by 20%',
                    'reason': f"CpHQL is ${lead_quality_data['cphql']:.2f} (above $300 target)",
                    'impact': 'Moderate'
                })
            
            # Example: Check if conversions are low
            last_24h = self.get_last_24_hours_data()
            if last_24h['conversions'] == 0:
                planned_changes.append({
                    'type': 'bid_adjustment',
                    'description': 'Increase bids by 15%',
                    'reason': 'No conversions in last 24 hours',
                    'impact': 'High'
                })
            
            return planned_changes
        except Exception as e:
            console.print(f"[red]Error getting planned changes: {e}[/red]")
            return []
    
    def generate_key_insight(self, last_24h: Dict, lead_quality: Dict, phase_data: Dict) -> str:
        """Generate a key insight based on the data."""
        try:
            insights = []
            
            # Check for zero conversions
            if last_24h['conversions'] == 0:
                insights.append("No conversions in the last 24 hours - immediate attention needed")
            
            # Check CpHQL performance
            if lead_quality['cphql'] > 300:
                insights.append(f"Cost per high-quality lead (${lead_quality['cphql']:.2f}) exceeds target")
            
            # Check phase progress
            if phase_data['progress_percentage'] < 60:
                insights.append(f"Phase {phase_data['current_phase']} is lagging behind schedule")
            
            # Check LQS performance
            if lead_quality['avg_lqs_7d'] < 5:
                insights.append(f"Average LQS ({lead_quality['avg_lqs_7d']:.1f}) is below optimal range")
            
            # Default positive insight if no issues
            if not insights:
                insights.append("Campaign performing within expected parameters")
            
            return insights[0] if insights else "Campaign status normal"
        except Exception as e:
            return "Unable to generate insight due to data error"
    
    def generate_dynamic_subject_line(self, planned_changes: List[Dict]) -> str:
        """Generate dynamic subject line based on planned changes."""
        if planned_changes:
            return "⚠️ ACTION REQUIRED: Daily Google Ads Report (Change Planned)"
        else:
            return "Daily Google Ads Report: L.R - PMax - General"
    
    def generate_email_content(self) -> str:
        """Generate the complete enhanced email content."""
        try:
            # Get all required data
            last_24h = self.get_last_24_hours_data()
            lead_quality = self.get_lead_quality_data()
            phase_data = self.get_phase_progression_data()
            planned_changes = self.get_planned_changes()
            key_insight = self.generate_key_insight(last_24h, lead_quality, phase_data)
            
            # Generate dynamic subject line
            subject_line = self.generate_dynamic_subject_line(planned_changes)
            
            # Format intervention deadline
            mdt_tz = pytz.timezone('America/Denver')
            deadline_mdt = self.intervention_deadline.astimezone(mdt_tz)
            deadline_str = deadline_mdt.strftime('%I:%M %p MDT')
            
            # Generate email content
            email_content = f"""
# {subject_line}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Top-Line Summary (Last 24 Hours)

- **Spend:** ${last_24h['spend']:.2f}
- **Conversions (Leads):** {last_24h['conversions']}
- **Cost Per Lead (CPL):** ${last_24h['cpl']:.2f}

---

## 🎯 Lead Quality Analysis

- **New Leads Scored:** {lead_quality['new_leads_scored']}
- **Lead Quality Score (LQS) of New Leads:** {lead_quality['lqs_new_leads']:.1f}
- **Cost per High-Quality Lead (CpHQL):** ${lead_quality['cphql']:.2f}
- **7-Day Average LQS:** {lead_quality['avg_lqs_7d']:.1f}

---

## 🚀 Phase Progression Status

- **Current Phase:** {phase_data['current_phase']}
- **Progress:** {phase_data['progress']}
- **Status:** {phase_data['status']}

---

## ⚡ Planned Actions & Intervention Window

"""
            
            if planned_changes:
                email_content += f"""
**⚠️ AUTOMATED CHANGES PLANNED**

"""
                for i, change in enumerate(planned_changes, 1):
                    email_content += f"""
**Change {i}: {change['description']}**
- **Reason:** {change['reason']}
- **Impact:** {change['impact']}

"""
                
                email_content += f"""
**You have 2 hours to cancel this change.**
If no action is taken, the change will be executed automatically at **{deadline_str}**.

**To Cancel:** Reply to this email with the word 'CANCEL' in the subject line or body.

---
"""
            else:
                email_content += """
**No automated changes planned for today.**

---
"""
            
            email_content += f"""
## 💡 Key Insight

{key_insight}

---

*Generated by Google Ads AI Manager*
*Campaign: {self.campaign_name}*
"""
            
            return email_content
            
        except Exception as e:
            console.print(f"[red]Error generating email content: {e}[/red]")
            return f"""
# Daily Google Ads Report: L.R - PMax - General

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Error:** Unable to generate complete report due to data access issues.

Please check the GitHub Actions logs for more details.

---

*Generated by Google Ads AI Manager*
*Campaign: {self.campaign_name}*
"""
    
    def send_email(self, subject: str = None, recipient: str = None) -> bool:
        """Send the enhanced email summary."""
        if not self.email_config:
            console.print("[yellow]Email configuration not provided. Email not sent.[/yellow]")
            return False
        
        try:
            # Generate email content
            email_content = self.generate_email_content()
            
            # Convert markdown to proper HTML
            html_content = self._convert_to_html(email_content)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('sender_email', '')
            msg['To'] = recipient or self.email_config.get('recipient_email', '')
            msg['Subject'] = subject or self.generate_dynamic_subject_line(self.get_planned_changes())
            
            # Set reply-to if configured
            if self.email_config.get('reply_to'):
                msg['Reply-To'] = self.email_config.get('reply_to')
            
            # Add body
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            server = smtplib.SMTP(
                self.email_config.get('smtp_server', 'smtp.gmail.com'),
                self.email_config.get('smtp_port', 587)
            )
            server.starttls()
            server.login(
                self.email_config.get('sender_email', ''),
                self.email_config.get('sender_password', '')
            )
            
            text = msg.as_string()
            server.sendmail(
                self.email_config.get('sender_email', ''),
                msg['To'],
                text
            )
            server.quit()
            
            console.print(f"[green]✅ Enhanced email summary sent successfully to {msg['To']}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error sending email: {e}[/red]")
            return False
    
    def _convert_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to proper HTML for email."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Google Ads Summary</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                .metric { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }
                .alert { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }
                .warning { background-color: #f8d7da; padding: 10px; margin: 10px 0; border-left: 4px solid #dc3545; }
                .success { background-color: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }
                ul { margin: 10px 0; }
                li { margin: 5px 0; }
                hr { border: none; border-top: 1px solid #eee; margin: 20px 0; }
                .footer { font-size: 12px; color: #666; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        # Convert markdown to HTML
        html_content = markdown_content
        
        # Convert headers
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n')
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n')
        
        # Convert bold text
        html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
        
        # Convert lists
        html_content = html_content.replace('- ', '<li>').replace('\n', '</li>\n')
        
        # Add list tags
        lines = html_content.split('\n')
        in_list = False
        formatted_lines = []
        
        for line in lines:
            if line.strip().startswith('<li>'):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(line)
            elif line.strip() == '</li>':
                formatted_lines.append(line)
            else:
                if in_list:
                    formatted_lines.append('</ul>')
                    in_list = False
                formatted_lines.append(line)
        
        if in_list:
            formatted_lines.append('</ul>')
        
        html_content = '\n'.join(formatted_lines)
        
        # Add special styling for alerts and warnings
        html_content = html_content.replace(
            '⚠️ ACTION REQUIRED:',
            '<div class="warning"><strong>⚠️ ACTION REQUIRED:</strong>'
        ).replace(
            '**⚠️ AUTOMATED CHANGES PLANNED**',
            '<div class="alert"><strong>⚠️ AUTOMATED CHANGES PLANNED</strong>'
        )
        
        # Insert into template
        return html_template.format(content=html_content)
    
    def save_to_file(self, filename: str = None) -> str:
        """Save the email content to a file."""
        if not filename:
            filename = f"enhanced_google_ads_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        email_content = self.generate_email_content()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        console.print(f"[green]✅ Enhanced email summary saved to {filename}[/green]")
        return filename

def main():
    """Main function to generate and send enhanced email summary."""
    console.print(Panel("📧 Enhanced Google Ads Email Summary Generator", style="bold blue"))
    
    # Example email configuration
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your-email@gmail.com',
        'sender_password': 'your-app-password',
        'recipient_email': 'recipient@example.com'
    }
    
    # Initialize generator
    generator = EnhancedEmailSummaryGenerator(email_config)
    
    # Generate and display summary
    console.print("\n[bold cyan]Generating enhanced email summary...[/bold cyan]")
    
    # Save to file first
    filename = generator.save_to_file()
    
    # Ask if user wants to send email
    console.print(f"\n[bold yellow]Email content saved to: {filename}[/bold yellow]")
    console.print("\nTo send via email, update the email_config in the script and run:")
    console.print("generator.send_email()")
    
    # Display preview
    console.print("\n[bold cyan]Email Preview:[/bold cyan]")
    email_content = generator.generate_email_content()
    console.print(email_content[:500] + "..." if len(email_content) > 500 else email_content)

if __name__ == "__main__":
    main()
