import os
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv

def check_manager_account():
    """Check manager account structure and identify customer IDs."""
    load_dotenv()
    
    config = {
        "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }
    
    print("Checking manager account structure...")
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        customer_service = client.get_service("CustomerService")
        
        # Get accessible customers
        accessible_customers = customer_service.list_accessible_customers()
        
        print(f"\n✅ Found {len(accessible_customers.resource_names)} accessible customers:")
        
        for i, customer in enumerate(accessible_customers.resource_names):
            customer_id = customer.split('/')[-1]
            print(f"  {i+1}. Customer ID: {customer_id}")
            
            # Try to get customer details
            try:
                customer_details = customer_service.get_customer(resource_name=customer)
                print(f"     Name: {customer_details.descriptive_name}")
                print(f"     Manager: {customer_details.manager}")
                print(f"     Test Account: {customer_details.test_account}")
                print()
            except Exception as e:
                print(f"     Could not get details: {e}")
                print()
        
        # Determine which is the manager account
        print("Manager Account Setup:")
        print("1. LOGIN_CUSTOMER_ID should be your manager account ID")
        print("2. CUSTOMER_ID should be the specific account you want to access")
        print("3. If you only have one account, use the same ID for both")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_manager_account()
