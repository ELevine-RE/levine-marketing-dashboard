import os
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv

def discover_account_info():
    """Try to discover account information using the API."""
    load_dotenv()
    
    # Try with minimal config first
    config = {
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }
    
    print("Attempting to discover account information...")
    print("This will help us find your customer ID and check if developer token is needed.")
    
    try:
        client = GoogleAdsClient.load_from_dict(config)
        
        # Try to get accessible customers
        customer_service = client.get_service("CustomerService")
        
        # This might work without developer token for basic account discovery
        accessible_customers = customer_service.list_accessible_customers()
        
        print("\n✅ Successfully connected!")
        print("Accessible customer IDs:")
        for customer_id in accessible_customers.resource_names:
            print(f"  - {customer_id}")
            
        # Try to get details for the first customer
        if accessible_customers.resource_names:
            first_customer = accessible_customers.resource_names[0]
            customer_id = first_customer.split('/')[-1]
            print(f"\nFirst customer ID: {customer_id}")
            
            # Try to get customer details
            try:
                customer = customer_service.get_customer(resource_name=first_customer)
                print(f"Account name: {customer.descriptive_name}")
                print(f"Currency: {customer.currency_code}")
                print(f"Time zone: {customer.time_zone}")
                return customer_id
            except Exception as e:
                print(f"Could not get customer details: {e}")
                return customer_id
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nThis might be because:")
        print("1. Developer token is required")
        print("2. API access not enabled")
        print("3. OAuth scope issues")
        return None

if __name__ == "__main__":
    discover_account_info()
