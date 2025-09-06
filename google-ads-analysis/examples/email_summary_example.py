#!/usr/bin/env python3
"""
Email Summary Example
====================

Example usage of the EmailSummaryGenerator for Google Ads campaign summaries.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_summary_generator import EmailSummaryGenerator
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Example of generating and sending email summaries."""
    console.print(Panel("📧 Email Summary Example", style="bold blue"))
    
    # Example 1: Generate summary and save to file
    console.print("\n[bold cyan]Example 1: Generate and save summary[/bold cyan]")
    
    generator = EmailSummaryGenerator()
    filename = generator.save_to_file()
    console.print(f"✅ Summary saved to: {filename}")
    
    # Example 2: Configure email settings and send
    console.print("\n[bold cyan]Example 2: Configure email settings[/bold cyan]")
    
    # Email configuration (update with your actual settings)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your-email@gmail.com',
        'sender_password': 'your-app-password',  # Use app password for Gmail
        'recipient_email': 'recipient@example.com'
    }
    
    # Create generator with email config
    email_generator = EmailSummaryGenerator(email_config)
    
    # Example 3: Send email summary
    console.print("\n[bold cyan]Example 3: Send email summary[/bold cyan]")
    console.print("[yellow]Note: Update email_config with your actual settings first[/yellow]")
    
    # Uncomment the line below to actually send the email
    # success = email_generator.send_email(
    #     subject="Your Google Ads Summary Report",
    #     recipient="your-email@example.com"
    # )
    
    # Example 4: Custom intervention deadline
    console.print("\n[bold cyan]Example 4: Custom intervention deadline[/bold cyan]")
    
    from datetime import datetime, timedelta
    
    # Set custom deadline (e.g., 4 hours instead of 2)
    custom_generator = EmailSummaryGenerator(email_config)
    custom_generator.intervention_deadline = datetime.now() + timedelta(hours=4)
    
    # Example 5: Preview email content
    console.print("\n[bold cyan]Example 5: Preview email content[/bold cyan]")
    
    email_content = generator.generate_email_content()
    console.print("\n[bold]Email Preview:[/bold]")
    console.print("=" * 50)
    console.print(email_content[:1000] + "..." if len(email_content) > 1000 else email_content)
    console.print("=" * 50)
    
    # Example 6: Scheduled summary (for cron jobs)
    console.print("\n[bold cyan]Example 6: Scheduled summary setup[/bold cyan]")
    
    console.print("""
To set up automated daily summaries, add this to your crontab:

# Daily summary at 9 AM
0 9 * * * cd /path/to/google-ads-setup && python examples/email_summary_example.py

# Weekly summary every Monday at 8 AM
0 8 * * 1 cd /path/to/google-ads-setup && python examples/email_summary_example.py
    """)

if __name__ == "__main__":
    main()
