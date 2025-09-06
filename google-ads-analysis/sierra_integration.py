import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleSierraManager:
    """Simplified Sierra Interactive Manager for Dashboard Integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Sierra Interactive Manager."""
        load_dotenv()
        
        self.api_key = api_key or os.environ.get("SIERRA_API_KEY")
        if not self.api_key:
            raise ValueError("Sierra Interactive API Key is required")
            
        self.base_url = "https://api.sierrainteractivedev.com"
        self.headers = {
            "Content-Type": "application/json",
            "Sierra-ApiKey": self.api_key,
            "Sierra-OriginatingSystemName": "MarketingDashboard"
        }
        
        logger.info("✅ Sierra Interactive Manager initialized successfully")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make a request to the Sierra Interactive API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"📡 Sierra API Response Status: {response.status_code}")
            logger.info(f"📡 Sierra API Response Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                json_response = response.json()
                logger.info(f"📡 Sierra API JSON Response: {json_response}")
                return json_response
            except json.JSONDecodeError:
                # If not JSON, return the text content
                text_response = response.text
                logger.info(f"📡 Sierra API Text Response: {text_response}")
                return {"error": f"Non-JSON response: {text_response}"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Sierra API request failed: {e}")
            return {"error": f"Sierra API request failed: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Sierra API response parsing failed: {e}")
            return {"error": f"Sierra API response parsing failed: {e}"}
    
    def get_leads_data(self, days: int = 30) -> Dict:
        """Fetch leads data from Sierra Interactive."""
        logger.info(f"📋 Fetching Sierra leads data for last {days} days")
        
        try:
            # Try different endpoints to find the right one for listing leads
            # Based on the API docs, let's try the users endpoint first to see the structure
            response = self._make_request("/users?pageSize=10")
            
            if "error" in response:
                return response
            
            if not response.get("success", False):
                return {"error": "Sierra API returned unsuccessful response"}
            
            # The response structure is different - it's users data, not leads
            users_data = response.get("data", {})
            records = users_data.get("records", [])
            
            # Process users data (since we're testing with users endpoint)
            processed_data = {
                "total_records": len(records),
                "records_by_status": {},
                "records_by_role": {},
                "recent_records": [],
                "summary": {
                    "total_records": len(records),
                    "active_records": 0,
                    "new_records": 0,
                    "converted_records": 0
                }
            }
            
            # Process each record
            for record in records:
                # Count by status
                status = record.get("status", "Unknown")
                processed_data["records_by_status"][status] = processed_data["records_by_status"].get(status, 0) + 1
                
                # Count by role
                role = record.get("role", "Unknown")
                processed_data["records_by_role"][role] = processed_data["records_by_role"].get(role, 0) + 1
                
                # Track recent records (last 30 days)
                created_date = record.get("created", "")
                if created_date:
                    try:
                        record_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        # Make datetime.now() timezone-aware for comparison
                        from datetime import timezone
                        now_aware = datetime.now(timezone.utc)
                        if record_date >= now_aware - timedelta(days=days):
                            processed_data["recent_records"].append({
                                "id": record.get("id"),
                                "name": record.get("name", ""),
                                "email": record.get("email", ""),
                                "status": status,
                                "role": role,
                                "created": created_date
                            })
                    except ValueError:
                        logger.warning(f"⚠️ Invalid date format for record {record.get('id')}: {created_date}")
                
                # Update summary counts
                if status == "Active":
                    processed_data["summary"]["active_records"] += 1
                elif status == "Inactive":
                    processed_data["summary"]["new_records"] += 1
            
            logger.info(f"✅ Successfully processed {len(records)} records from Sierra Interactive")
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching Sierra leads data: {e}")
            return {"error": f"Sierra leads data error: {e}"}
    
    def get_users_data(self) -> Dict:
        """Fetch users/agents data from Sierra Interactive."""
        logger.info("👥 Fetching Sierra users data")
        
        try:
            response = self._make_request("/users")
            
            if "error" in response:
                return response
            
            if not response.get("success", False):
                return {"error": "Sierra API returned unsuccessful response"}
            
            users_data = response.get("data", {})
            records = users_data.get("records", [])
            
            # Process users data
            processed_users = {
                "total_users": len(records),
                "users_by_role": {},
                "users_by_status": {},
                "active_users": [],
                "summary": {
                    "total_users": len(records),
                    "active_users": 0,
                    "agents": 0,
                    "managers": 0
                }
            }
            
            # Process each user
            for user in records:
                role = user.get("role", "Unknown")
                status = user.get("status", "Unknown")
                
                # Count by role
                processed_users["users_by_role"][role] = processed_users["users_by_role"].get(role, 0) + 1
                
                # Count by status
                processed_users["users_by_status"][status] = processed_users["users_by_status"].get(status, 0) + 1
                
                # Track active users
                if status == "Active":
                    processed_users["active_users"].append({
                        "id": user.get("id"),
                        "name": user.get("name", ""),
                        "email": user.get("email", ""),
                        "role": role,
                        "phone": user.get("phone", "")
                    })
                
                # Update summary counts
                if status == "Active":
                    processed_users["summary"]["active_users"] += 1
                if "Agent" in role:
                    processed_users["summary"]["agents"] += 1
                if "Manager" in role:
                    processed_users["summary"]["managers"] += 1
            
            logger.info(f"✅ Successfully processed {len(records)} users from Sierra Interactive")
            return processed_users
            
        except Exception as e:
            logger.error(f"❌ Error fetching Sierra users data: {e}")
            return {"error": f"Sierra users data error: {e}"}
    
    def get_comprehensive_data(self, days: int = 30) -> Dict:
        """Fetch comprehensive Sierra Interactive data."""
        logger.info(f"📊 Fetching comprehensive Sierra Interactive data for last {days} days")
        
        try:
            # Fetch leads data
            leads_data = self.get_leads_data(days)
            if "error" in leads_data:
                return leads_data
            
            # Fetch users data
            users_data = self.get_users_data()
            if "error" in users_data:
                return users_data
            
            # Combine data
            comprehensive_data = {
                "leads": leads_data,
                "users": users_data,
                "summary": {
                    "total_records": leads_data["summary"]["total_records"],
                    "active_records": leads_data["summary"]["active_records"],
                    "total_users": users_data["summary"]["total_users"],
                    "active_users": users_data["summary"]["active_users"],
                    "conversion_rate": 0  # Will calculate based on closed records
                }
            }
            
            # Calculate conversion rate
            if leads_data["summary"]["total_records"] > 0:
                comprehensive_data["summary"]["conversion_rate"] = (
                    leads_data["summary"]["converted_records"] / leads_data["summary"]["total_records"]
                ) * 100
            
            logger.info("✅ Successfully fetched comprehensive Sierra Interactive data")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching comprehensive Sierra data: {e}")
            return {"error": f"Comprehensive Sierra data error: {e}"}

def test_sierra_integration():
    """Test the Sierra Interactive integration."""
    try:
        print("🔧 Testing Sierra Interactive integration...")
        manager = SimpleSierraManager()
        
        # Test leads data
        print("📋 Testing leads data...")
        leads_data = manager.get_leads_data(days=7)
        if "error" in leads_data:
            print(f"❌ Leads data error: {leads_data['error']}")
            return
        print(f"✅ Successfully fetched {leads_data['total_records']} records")
        
        # Test users data
        print("👥 Testing users data...")
        users_data = manager.get_users_data()
        if "error" in users_data:
            print(f"❌ Users data error: {users_data['error']}")
            return
        print(f"✅ Successfully fetched {users_data['total_users']} users")
        
        # Test comprehensive data
        print("📊 Testing comprehensive data...")
        comprehensive_data = manager.get_comprehensive_data(days=7)
        if "error" in comprehensive_data:
            print(f"❌ Comprehensive data error: {comprehensive_data['error']}")
            return
        print("🎉 All Sierra Interactive tests passed!")
        
        print(f"\n📋 Records Summary:")
        print(f"   Total Records: {leads_data['summary']['total_records']}")
        print(f"   Active Records: {leads_data['summary']['active_records']}")
        print(f"   New Records: {leads_data['summary']['new_records']}")
        
        print(f"\n👥 Users Summary:")
        print(f"   Total Users: {users_data['summary']['total_users']}")
        print(f"   Active Users: {users_data['summary']['active_users']}")
        print(f"   Agents: {users_data['summary']['agents']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sierra_integration()
