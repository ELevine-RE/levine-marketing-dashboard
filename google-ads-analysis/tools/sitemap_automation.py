#!/usr/bin/env python3
"""
Sitemap Automation
==================

Complete automation system that fetches sitemap URLs and creates/updates
Google Ads page feeds automatically. Includes scheduling and monitoring.
"""

import os
import json
import sys
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sitemap_parser import SitemapParser
from tools.page_feed_creator import PageFeedCreator
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/sitemap_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SitemapAutomation:
    """Complete sitemap automation system."""
    
    def __init__(self, customer_id: str, manager_customer_id: Optional[str] = None):
        self.customer_id = customer_id
        self.manager_customer_id = manager_customer_id or customer_id
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.sitemap_parser = SitemapParser()
        self.page_feed_creator = PageFeedCreator(customer_id, manager_customer_id)
        
        # Configuration
        self.config_file = "data/sitemap_automation_config.json"
        self.load_config()
        
        logger.info("✅ Sitemap automation system initialized")
    
    def load_config(self):
        """Load automation configuration."""
        default_config = {
            "campaign_name": "L.R - PMax - General",
            "asset_set_name": "Levine Real Estate Page Feed",
            "max_urls": 1000,
            "update_frequency_hours": 24,
            "auto_create_page_feeds": True,
            "auto_link_to_campaigns": True,
            "notification_email": None,
            "last_run": None,
            "last_run_status": None,
            "total_runs": 0,
            "successful_runs": 0
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config, using defaults: {e}")
                self.config = default_config
        else:
            self.config = default_config
        
        self.save_config()
    
    def save_config(self):
        """Save automation configuration."""
        os.makedirs('data', exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def run_automation(self) -> Dict:
        """Run the complete sitemap automation process."""
        logger.info("🚀 Starting sitemap automation run")
        start_time = datetime.now()
        
        try:
            # Update run counter
            self.config["total_runs"] += 1
            
            # Step 1: Check if we need to run (based on frequency)
            if not self._should_run():
                logger.info("⏭️ Skipping run - not enough time has passed since last run")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "Frequency check"
                }
            
            # Step 2: Get URLs from sitemap
            logger.info("📋 Fetching URLs from sitemap...")
            urls = self.sitemap_parser.get_page_feed_urls(max_urls=self.config["max_urls"])
            
            if not urls:
                logger.warning("⚠️ No URLs found in sitemap")
                return {
                    "success": False,
                    "error": "No URLs found in sitemap",
                    "urls_processed": 0
                }
            
            logger.info(f"✅ Found {len(urls)} URLs from sitemap")
            
            # Step 3: Check for existing page feeds
            existing_feeds = self.page_feed_creator.get_existing_page_feeds()
            logger.info(f"📦 Found {len(existing_feeds)} existing page feeds")
            
            # Step 4: Create or update page feed
            if self.config["auto_create_page_feeds"]:
                logger.info("🔧 Creating/updating page feed...")
                
                result = self.page_feed_creator.create_page_feed_from_sitemap(
                    campaign_name=self.config["campaign_name"],
                    max_urls=self.config["max_urls"],
                    asset_set_name=self.config["asset_set_name"]
                )
                
                if result["success"]:
                    logger.info(f"✅ Page feed created/updated successfully")
                    logger.info(f"   Asset Set ID: {result['asset_set_id']}")
                    logger.info(f"   URLs Processed: {result['urls_processed']}")
                    logger.info(f"   Assets Created: {result['assets_created']}")
                    logger.info(f"   Campaign Linked: {result['campaign_linked']}")
                else:
                    logger.error(f"❌ Page feed creation failed: {result.get('error', 'Unknown error')}")
                    return result
            
            # Step 5: Update configuration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.config["last_run"] = start_time.isoformat()
            self.config["last_run_status"] = "success"
            self.config["successful_runs"] += 1
            self.save_config()
            
            # Step 6: Generate summary
            summary = {
                "success": True,
                "skipped": False,
                "urls_processed": len(urls),
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "config": {
                    "campaign_name": self.config["campaign_name"],
                    "asset_set_name": self.config["asset_set_name"],
                    "max_urls": self.config["max_urls"]
                }
            }
            
            logger.info(f"✅ Sitemap automation completed successfully in {duration:.1f} seconds")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Sitemap automation failed: {e}")
            
            # Update configuration with failure
            self.config["last_run"] = datetime.now().isoformat()
            self.config["last_run_status"] = "failed"
            self.save_config()
            
            return {
                "success": False,
                "error": str(e),
                "urls_processed": 0
            }
    
    def _should_run(self) -> bool:
        """Check if automation should run based on frequency."""
        if not self.config["last_run"]:
            return True
        
        try:
            last_run = datetime.fromisoformat(self.config["last_run"])
            hours_since_last_run = (datetime.now() - last_run).total_seconds() / 3600
            return hours_since_last_run >= self.config["update_frequency_hours"]
        except:
            return True
    
    def schedule_automation(self):
        """Schedule the automation to run at regular intervals."""
        frequency_hours = self.config["update_frequency_hours"]
        
        if frequency_hours == 24:
            schedule.every().day.at("08:00").do(self.run_automation)
            logger.info("📅 Scheduled daily automation at 8:00 AM")
        elif frequency_hours == 12:
            schedule.every().day.at("08:00").do(self.run_automation)
            schedule.every().day.at("20:00").do(self.run_automation)
            logger.info("📅 Scheduled twice-daily automation at 8:00 AM and 8:00 PM")
        elif frequency_hours == 6:
            schedule.every(6).hours.do(self.run_automation)
            logger.info("📅 Scheduled automation every 6 hours")
        else:
            schedule.every(frequency_hours).hours.do(self.run_automation)
            logger.info(f"📅 Scheduled automation every {frequency_hours} hours")
    
    def run_scheduler(self):
        """Run the scheduler (blocking)."""
        logger.info("🔄 Starting sitemap automation scheduler")
        self.schedule_automation()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def get_status(self) -> Dict:
        """Get current automation status."""
        return {
            "config": self.config,
            "last_run": self.config.get("last_run"),
            "last_run_status": self.config.get("last_run_status"),
            "total_runs": self.config.get("total_runs", 0),
            "successful_runs": self.config.get("successful_runs", 0),
            "success_rate": (
                self.config.get("successful_runs", 0) / max(self.config.get("total_runs", 1), 1) * 100
            ),
            "next_run_due": self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get the next scheduled run time."""
        if not self.config["last_run"]:
            return "Immediately"
        
        try:
            last_run = datetime.fromisoformat(self.config["last_run"])
            next_run = last_run + timedelta(hours=self.config["update_frequency_hours"])
            return next_run.isoformat()
        except:
            return "Unknown"
    
    def update_config(self, new_config: Dict):
        """Update automation configuration."""
        for key, value in new_config.items():
            if key in self.config:
                self.config[key] = value
        
        self.save_config()
        logger.info(f"✅ Configuration updated: {list(new_config.keys())}")
    
    def test_automation(self) -> Dict:
        """Test the automation with a small number of URLs."""
        logger.info("🧪 Running automation test")
        
        # Temporarily reduce max URLs for testing
        original_max_urls = self.config["max_urls"]
        self.config["max_urls"] = 10
        
        try:
            result = self.run_automation()
            return result
        finally:
            # Restore original setting
            self.config["max_urls"] = original_max_urls

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sitemap Automation System")
    parser.add_argument("--customer", required=True, help="Google Ads Customer ID")
    parser.add_argument("--manager", help="Google Ads Manager Customer ID")
    parser.add_argument("--run", action="store_true", help="Run automation once")
    parser.add_argument("--schedule", action="store_true", help="Run scheduler")
    parser.add_argument("--test", action="store_true", help="Run test with limited URLs")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    try:
        automation = SitemapAutomation(args.customer, args.manager)
        
        if args.status:
            status = automation.get_status()
            print("📊 Sitemap Automation Status")
            print("=" * 40)
            print(f"Last Run: {status['last_run']}")
            print(f"Last Status: {status['last_run_status']}")
            print(f"Total Runs: {status['total_runs']}")
            print(f"Successful Runs: {status['successful_runs']}")
            print(f"Success Rate: {status['success_rate']:.1f}%")
            print(f"Next Run Due: {status['next_run_due']}")
        
        elif args.test:
            result = automation.test_automation()
            print(f"🧪 Test Result: {'✅ Success' if result['success'] else '❌ Failed'}")
            if result.get('urls_processed'):
                print(f"URLs Processed: {result['urls_processed']}")
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        elif args.run:
            result = automation.run_automation()
            print(f"🚀 Automation Result: {'✅ Success' if result['success'] else '❌ Failed'}")
            if result.get('urls_processed'):
                print(f"URLs Processed: {result['urls_processed']}")
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        elif args.schedule:
            automation.run_scheduler()
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
