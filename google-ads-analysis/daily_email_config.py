#!/usr/bin/env python3
"""
Daily Email Configuration
========================

Configuration for daily Google Ads email summaries sent to evan@levine.realestate
at 8 AM Mountain Time.
"""

import os
import sys
from datetime import datetime
import pytz

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_summary_generator import EmailSummaryGenerator
from rich.console import Console
from rich.panel import Panel

console = Console()

# Email configuration for evan@levine.realestate
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # We'll use Gmail as relay
    'smtp_port': 587,
    'sender_email': 'elevine17@gmail.com',  # Use a Gmail account as sender
    'sender_password': 'fklk uwuh fakt tcio',  # Gmail app password
    'recipient_email': 'evan@levine.realestate',
    'reply_to': 'developer@levine.realestate'  # Set reply-to to your domain
}

def send_daily_summary():


    """Send daily Google Ads summary to evan@levine.realestate."""
    
    # Get current time in Mountain Time
    mt_tz = pytz.timezone('America/Denver')
    current_time = datetime.now(mt_tz)
    
    console.print(Panel(f"📧 Sending Daily Summary to evan@levine.realestate", style="bold blue"))
    console.print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    try:
        # Initialize email generator
        generator = EmailSummaryGenerator(EMAIL_CONFIG)
        
        # Generate and send email
        subject = f"Daily Google Ads Summary - {current_time.strftime('%Y-%m-%d')}"
        
        success = generator.send_email(
            subject=subject,
            recipient='evan@levine.realestate'
        )
        
        if success:
            console.print(f"[green]✅ Daily summary sent successfully to evan@levine.realestate[/green]")
            
            # Also save a local copy for backup
            backup_filename = f"daily_summary_backup_{current_time.strftime('%Y%m%d')}.html"
            generator.save_to_file(backup_filename)
            console.print(f"[blue]📁 Backup saved to: {backup_filename}[/blue]")
            
        else:
            console.print(f"[red]❌ Failed to send daily summary[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error sending daily summary: {e}[/red]")
        # Log error for debugging
        with open('daily_summary_errors.log', 'a') as f:
            f.write(f"{current_time}: {str(e)}\n")

def setup_cron_job():
    """Instructions for setting up the cron job."""
    
    console.print(Panel("🕗 Setting Up Daily Email at 8 AM MT", style="bold green"))
    
    console.print("""
To set up automated daily emails at 8 AM Mountain Time:

1. Open your crontab:
   crontab -e

2. Add this line:
   0 8 * * * cd /tmp/google-ads-setup && /tmp/google-ads-setup/.venv/bin/python daily_email_config.py

3. Save and exit (Ctrl+X, then Y, then Enter)

4. Verify the cron job is set:
   crontab -l

Note: Make sure to update the EMAIL_CONFIG in this file with your actual Gmail credentials.
    """)

def test_email():
    """Test the email configuration."""
    
    console.print(Panel("🧪 Testing Email Configuration", style="bold yellow"))
    
    # Check if email config is properly set
    if EMAIL_CONFIG['sender_email'] == 'your-email@gmail.com':
        console.print("[red]❌ Please update EMAIL_CONFIG with your actual Gmail credentials[/red]")
        console.print("""
Update these values in daily_email_config.py:
- sender_email: Your Gmail address
- sender_password: Your Gmail app password (not regular password)
        """)
        return False
    
    # Test sending
    try:
        generator = EmailSummaryGenerator(EMAIL_CONFIG)
        success = generator.send_email(
            subject="Test Email - Google Ads Daily Summary",
            recipient='evan@levine.realestate'
        )
        
        if success:
            console.print("[green]✅ Test email sent successfully![/green]")
            return True
        else:
            console.print("[red]❌ Test email failed[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Test email error: {e}[/red]")
        return False

if __name__ == "__main__":
    # Check if this is a test run or scheduled run
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_email()
    elif len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_cron_job()
    else:
        # Normal daily run
        send_daily_summary()

