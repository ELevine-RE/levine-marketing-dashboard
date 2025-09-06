import os
from google.ads.googleads.client import GoogleAdsClient
from dotenv import load_dotenv


def build_client_from_env() -> GoogleAdsClient:
	load_dotenv()
	config = {
		"developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
		"client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
		"client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
		"refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
		"login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
		"use_proto_plus": True,
	}
	return GoogleAdsClient.load_from_dict(config)


def main() -> None:
	client = build_client_from_env()
	customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
	if not customer_id:
		raise RuntimeError("GOOGLE_ADS_CUSTOMER_ID is required")

	customer_service = client.get_service("CustomerService")
	
	# Try to get accessible customers first
	try:
		accessible_customers = customer_service.list_accessible_customers()
		print(f"✅ Successfully connected to Google Ads API!")
		print(f"Accessible customers: {len(accessible_customers.resource_names)}")
		for customer in accessible_customers.resource_names:
			print(f"  - {customer}")
	except Exception as e:
		print(f"❌ Error accessing customers: {e}")
		print("This might be due to missing developer token or permissions.")


if __name__ == "__main__":
	main()

