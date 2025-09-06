#!/usr/bin/env python3
"""
Setup Daily Email for evan@levine.realestate
==========================================

Interactive setup script for configuring daily Google Ads email summaries.
"""

import os
import sys
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

def main():
    """Interactive setup for daily email configuration."""
    
    console.print(Panel("📧 Daily Email Setup for evan@levine.realestate", style="bold blue"))
    console.print("This will configure daily Google Ads summaries sent at 8 AM Mountain Time.\n")
    
    # Get Gmail credentials
    console.print("[bold cyan]Step 1: Gmail Configuration[/bold cyan]")
    console.print("You'll need a Gmail account and an app password (not your regular password).")
    console.print("To create an app password: https://support.google.com/accounts/answer/185833\n")
    
    gmail_address = Prompt.ask("Enter your Gmail address")
    
    # Validate email format
    if '@gmail.com' not in gmail_address:
        console.print("[red]❌ Please enter a valid Gmail address[/red]")
        return
    
    console.print("\n[yellow]Note: Use an app password, not your regular Gmail password[/yellow]")
    console.print("Create one at: https://myaccount.google.com/apppasswords\n")
    
    app_password = getpass.getpass("Enter your Gmail app password: ")
    
    if not app_password:
        console.print("[red]❌ App password is required[/red]")
        return
    
    # Update the configuration file
    console.print("\n[bold cyan]Step 2: Updating Configuration[/bold cyan]")
    
    config_file = 'daily_email_config.py'
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace the placeholder values
        content = content.replace(
            "'your-email@gmail.com'",
            f"'{gmail_address}'"
        )
        content = content.replace(
            "'your-app-password'",
            f"'{app_password}'"
        )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        console.print(f"[green]✅ Configuration updated in {config_file}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error updating configuration: {e}[/red]")
        return
    
    # Test the configuration
    console.print("\n[bold cyan]Step 3: Testing Configuration[/bold cyan]")
    
    test_confirm = Confirm.ask("Would you like to send a test email to evan@levine.realestate?")
    
    if test_confirm:
        try:
            # Import and test
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from daily_email_config import test_email
            
            success = test_email()
            
            if success:
                console.print("[green]✅ Test email sent successfully![/green]")
            else:
                console.print("[red]❌ Test email failed. Please check your credentials.[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Test failed: {e}[/red]")
    
    # Setup cron job
    console.print("\n[bold cyan]Step 4: Setting Up Automated Schedule[/bold cyan]")
    
    setup_confirm = Confirm.ask("Would you like to set up the daily 8 AM MT schedule?")
    
    if setup_confirm:
        try:
            # Get the current directory
            current_dir = os.path.abspath(os.path.dirname(__file__))
            python_path = os.path.join(current_dir, '.venv', 'bin', 'python')
            script_path = os.path.join(current_dir, 'daily_email_config.py')
            
            cron_command = f"0 8 * * * cd {current_dir} && {python_path} {script_path}"
            
            console.print(f"\n[bold yellow]Cron command to add:[/bold yellow]")
            console.print(f"{cron_command}")
            
            console.print("\n[bold cyan]To set up the cron job:[/bold cyan]")
            console.print("1. Open your crontab: crontab -e")
            console.print("2. Add the command above")
            console.print("3. Save and exit (Ctrl+X, then Y, then Enter)")
            console.print("4. Verify with: crontab -l")
            
            # Offer to create a script to add the cron job
            auto_setup = Confirm.ask("Would you like me to create a script to automatically add the cron job?")
            
            if auto_setup:
                cron_script = f"""#!/bin/bash
# Auto-generated cron setup script

# Add the cron job
(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -

echo "✅ Daily email cron job added successfully!"
echo "The email will be sent to evan@levine.realestate at 8 AM Mountain Time daily."
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -e (then delete the line)"
"""
                
                with open('setup_cron.sh', 'w') as f:
                    f.write(cron_script)
                
                os.chmod('setup_cron.sh', 0o755)
                
                console.print(f"[green]✅ Created setup_cron.sh[/green]")
                console.print("Run: ./setup_cron.sh to automatically add the cron job")
                
        except Exception as e:
            console.print(f"[red]❌ Error setting up cron: {e}[/red]")
    
    # Final instructions
    console.print("\n[bold green]🎉 Setup Complete![/bold green]")
    console.print("\n[bold cyan]Summary:[/bold cyan]")
    console.print(f"• Daily emails will be sent to: evan@levine.realestate")
    console.print(f"• Time: 8 AM Mountain Time")
    console.print(f"• Sender: {gmail_address}")
    console.print(f"• Configuration file: {config_file}")
    
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. If you chose to create setup_cron.sh, run: ./setup_cron.sh")
    console.print("2. Otherwise, manually add the cron job using crontab -e")
    console.print("3. Test the setup by running: python daily_email_config.py --test")
    
    console.print("\n[bold yellow]Important Notes:[/bold yellow]")
    console.print("• The system will only work once you get Basic/Standard API access")
    console.print("• Emails will contain real data once API access is granted")
    console.print("• Check daily_summary_errors.log for any issues")

if __name__ == "__main__":
    main()
