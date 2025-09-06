#!/usr/bin/env python3
"""
Email Summary Generator
======================

Generates comprehensive email summaries for Google Ads campaigns including:
- Performance summaries for different time periods
- Planned changes and their impact
- Intervention options with time limits
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_ads_manager import GoogleAdsManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class EmailSummaryGenerator:
    """Generates and sends email summaries for Google Ads campaigns."""
    
    def __init__(self, email_config: Dict = None):
        """
        Initialize the email summary generator.
        
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
        self.intervention_deadline = datetime.now() + timedelta(hours=2)
        
        # Set manager account access for proper API calls
        if hasattr(self.manager, 'client') and self.manager.client:
            self.manager.client.login_customer_id = "5426234549"
        
    def generate_performance_summary(self, days: int) -> Dict:
        """
        Generate performance summary for specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # Get campaigns for the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Query for campaign performance data
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.average_cpc,
                    metrics.ctr,
                    metrics.average_cpm
                FROM campaign
                WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' 
                AND '{end_date.strftime('%Y-%m-%d')}'
            """
            
            response = self.manager.google_ads_service.search(
                customer_id="5426234549",  # Use manager account
                query=query
            )
            
            campaigns = []
            total_impressions = 0
            total_clicks = 0
            total_cost = 0
            total_conversions = 0
            
            for row in response:
                campaign_data = {
                    'id': row.campaign.id,
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'cost_micros': row.metrics.cost_micros,
                    'conversions': row.metrics.conversions,
                    'ctr': row.metrics.ctr,
                    'avg_cpc': row.metrics.average_cpc
                }
                
                campaigns.append(campaign_data)
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_cost += row.metrics.cost_micros
                total_conversions += row.metrics.conversions
            
            # Calculate summary metrics
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            total_cost_usd = total_cost / 1000000  # Convert from micros to USD
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            return {
                'period_days': days,
                'campaigns': campaigns,
                'summary': {
                    'total_campaigns': len(campaigns),
                    'total_impressions': total_impressions,
                    'total_clicks': total_clicks,
                    'total_cost_usd': total_cost_usd,
                    'total_conversions': total_conversions,
                    'avg_ctr': avg_ctr,
                    'conversion_rate': conversion_rate
                }
            }
            
        except Exception as e:
            console.print(f"[red]Error generating performance summary: {e}[/red]")
            return {
                'period_days': days,
                'campaigns': [],
                'summary': {
                    'total_campaigns': 0,
                    'total_impressions': 0,
                    'total_clicks': 0,
                    'total_cost_usd': 0,
                    'total_conversions': 0,
                    'avg_ctr': 0,
                    'conversion_rate': 0
                }
            }
    
    def analyze_planned_changes(self) -> Dict:
        """
        Analyze and identify planned changes based on performance data.
        
        Returns:
            Dictionary containing planned changes and their impact
        """
        try:
            # Get underperforming campaigns
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr
                FROM campaign
                WHERE segments.date >= '2024-01-01'
                ORDER BY metrics.cost_micros DESC
            """
            
            response = self.manager.google_ads_service.search(
                customer_id="5426234549",  # Use manager account
                query=query
            )
            
            planned_changes = []
            
            for row in response:
                campaign = {
                    'id': row.campaign.id,
                    'name': row.campaign.name,
                    'status': row.campaign.status.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'cost_micros': row.metrics.cost_micros,
                    'conversions': row.metrics.conversions,
                    'ctr': row.metrics.ctr
                }
                
                # AI-driven recommendations
                changes = self._generate_ai_recommendations(campaign)
                if changes:
                    planned_changes.append({
                        'campaign': campaign,
                        'changes': changes,
                        'impact': self._assess_impact(changes)
                    })
            
            return {
                'planned_changes': planned_changes,
                'total_changes': len(planned_changes),
                'estimated_impact': self._calculate_overall_impact(planned_changes)
            }
            
        except Exception as e:
            console.print(f"[red]Error analyzing planned changes: {e}[/red]")
            return {
                'planned_changes': [],
                'total_changes': 0,
                'estimated_impact': 'Unable to assess'
            }
    
    def _generate_ai_recommendations(self, campaign: Dict) -> List[Dict]:
        """Generate AI-driven recommendations for a campaign."""
        changes = []
        
        # Low CTR campaigns
        if campaign['ctr'] < 1.0 and campaign['impressions'] > 1000:
            changes.append({
                'type': 'pause_campaign',
                'reason': f'Low CTR ({campaign["ctr"]:.2f}%) - below industry average',
                'priority': 'high'
            })
        
        # High cost, low conversion campaigns
        if (campaign['cost_micros'] > 50000000 and  # $50+
            campaign['conversions'] < 1 and 
            campaign['clicks'] > 10):
            changes.append({
                'type': 'reduce_budget',
                'reason': f'High cost (${campaign["cost_micros"]/1000000:.2f}) with no conversions',
                'priority': 'high'
            })
        
        # Inactive campaigns
        if campaign['impressions'] == 0 and campaign['status'] == 'ENABLED':
            changes.append({
                'type': 'pause_campaign',
                'reason': 'No impressions in recent period',
                'priority': 'medium'
            })
        
        return changes
    
    def _assess_impact(self, changes: List[Dict]) -> str:
        """Assess the impact of planned changes."""
        high_priority = sum(1 for change in changes if change['priority'] == 'high')
        
        if high_priority > 0:
            return 'High - Significant performance improvements expected'
        elif len(changes) > 0:
            return 'Medium - Moderate optimizations planned'
        else:
            return 'Low - Minor adjustments only'
    
    def _calculate_overall_impact(self, planned_changes: List[Dict]) -> str:
        """Calculate overall impact of all planned changes."""
        total_changes = len(planned_changes)
        
        if total_changes == 0:
            return 'No changes planned'
        elif total_changes <= 2:
            return 'Minimal impact expected'
        elif total_changes <= 5:
            return 'Moderate impact expected'
        else:
            return 'Significant impact expected'
    
    def generate_email_content(self) -> str:
        """Generate the complete email content."""
        
        # Generate performance summaries
        last_24h = self.generate_performance_summary(1)
        last_7d = self.generate_performance_summary(7)
        last_14d = self.generate_performance_summary(14)
        last_30d = self.generate_performance_summary(30)
        
        # Analyze planned changes
        planned_changes = self.analyze_planned_changes()
        
        # Generate email content
        email_content = f"""
# Google Ads Campaign Summary Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Here's What Has Happened

### Last 24 Hours
- **Campaigns Active:** {last_24h['summary']['total_campaigns']}
- **Impressions:** {last_24h['summary']['total_impressions']:,}
- **Clicks:** {last_24h['summary']['total_clicks']:,}
- **Cost:** ${last_24h['summary']['total_cost_usd']:.2f}
- **Conversions:** {last_24h['summary']['total_conversions']}
- **Avg CTR:** {last_24h['summary']['avg_ctr']:.2f}%
- **Conversion Rate:** {last_24h['summary']['conversion_rate']:.2f}%

### Last 7 Days
- **Campaigns Active:** {last_7d['summary']['total_campaigns']}
- **Impressions:** {last_7d['summary']['total_impressions']:,}
- **Clicks:** {last_7d['summary']['total_clicks']:,}
- **Cost:** ${last_7d['summary']['total_cost_usd']:.2f}
- **Conversions:** {last_7d['summary']['total_conversions']}
- **Avg CTR:** {last_7d['summary']['avg_ctr']:.2f}%
- **Conversion Rate:** {last_7d['summary']['conversion_rate']:.2f}%

### Last 14 Days
- **Campaigns Active:** {last_14d['summary']['total_campaigns']}
- **Impressions:** {last_14d['summary']['total_impressions']:,}
- **Clicks:** {last_14d['summary']['total_clicks']:,}
- **Cost:** ${last_14d['summary']['total_cost_usd']:.2f}
- **Conversions:** {last_14d['summary']['total_conversions']}
- **Avg CTR:** {last_14d['summary']['avg_ctr']:.2f}%
- **Conversion Rate:** {last_14d['summary']['conversion_rate']:.2f}%

### Last 30 Days
- **Campaigns Active:** {last_30d['summary']['total_campaigns']}
- **Impressions:** {last_30d['summary']['total_impressions']:,}
- **Clicks:** {last_30d['summary']['total_clicks']:,}
- **Cost:** ${last_30d['summary']['total_cost_usd']:.2f}
- **Conversions:** {last_30d['summary']['total_conversions']}
- **Avg CTR:** {last_30d['summary']['avg_ctr']:.2f}%
- **Conversion Rate:** {last_30d['summary']['conversion_rate']:.2f}%

## 🔧 Here Are the Changes We Plan to Make

**Total Changes Planned:** {planned_changes['total_changes']}
**Overall Impact:** {planned_changes['estimated_impact']}

### Planned Actions:
"""
        
        for change in planned_changes['planned_changes']:
            campaign = change['campaign']
            email_content += f"""
**Campaign:** {campaign['name']} (ID: {campaign['id']})
"""
            for action in change['changes']:
                email_content += f"- **{action['type'].replace('_', ' ').title()}**: {action['reason']} (Priority: {action['priority']})\n"
        
        email_content += f"""
## 📈 How Your Medium Term and Long Term Plans Are Impacted

### Medium Term (Next 30 Days)
- **Expected Cost Savings:** Based on planned optimizations
- **Performance Improvements:** Higher CTR and conversion rates expected
- **Campaign Efficiency:** Better resource allocation

### Long Term (Next 90 Days)
- **Scalability:** Improved campaign structure for growth
- **ROI Optimization:** Better return on ad spend
- **Automation Benefits:** Reduced manual management time

## ⚠️ Intervention Required?

**Reply now if you want to cancel these changes and intervene**
**Deadline:** {self.intervention_deadline.strftime('%Y-%m-%d %H:%M:%S')} (2 hour limit)

### How to Intervene:
1. **Reply to this email** with "STOP" to cancel all changes
2. **Reply with specific campaign IDs** to modify only those campaigns
3. **Call or text** for immediate intervention

### What Happens If You Don't Respond:
- Changes will be automatically implemented at the deadline
- You'll receive a confirmation email with results
- Performance will be monitored and reported in the next summary

---
*This is an automated report from your AI-Powered Google Ads Management System*
*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
        
        return email_content
    
    def send_email(self, subject: str = None, recipient: str = None) -> bool:
        """
        Send the email summary.
        
        Args:
            subject: Email subject line
            recipient: Recipient email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
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
            msg['Subject'] = subject or f"Google Ads Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
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
            
            console.print(f"[green]✅ Email summary sent successfully to {msg['To']}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error sending email: {e}[/red]")
            return False
    
    def _convert_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to proper HTML for email."""
        
        # Simple HTML template without complex CSS
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Google Ads Summary</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
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
        
        # Add metric styling
        html_content = html_content.replace(
            '**Campaigns Active:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Impressions:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Clicks:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Cost:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Conversions:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Avg CTR:**',
            '<div class="metric-card"><div class="metric-value">'
        ).replace(
            '**Conversion Rate:**',
            '<div class="metric-card"><div class="metric-value">'
        )
        
        # Insert into template
        return html_template.format(content=html_content)

    def save_to_file(self, filename: str = None) -> str:
        """
        Save the email content to a file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved file
        """
        if not filename:
            filename = f"google_ads_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        email_content = self.generate_email_content()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        console.print(f"[green]✅ Email summary saved to {filename}[/green]")
        return filename

def main():
    """Main function to generate and send email summary."""
    console.print(Panel("📧 Google Ads Email Summary Generator", style="bold blue"))
    
    # Example email configuration
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your-email@gmail.com',
        'sender_password': 'your-app-password',
        'recipient_email': 'recipient@example.com'
    }
    
    # Initialize generator
    generator = EmailSummaryGenerator(email_config)
    
    # Generate and display summary
    console.print("\n[bold cyan]Generating email summary...[/bold cyan]")
    
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
