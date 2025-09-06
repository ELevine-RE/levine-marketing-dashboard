import webbrowser
import time

def open_google_ads_for_customer_id():
    """Open Google Ads interface to help find customer ID."""
    print("Opening Google Ads interface to help find your customer ID...")
    print("\nSteps to find your Customer ID:")
    print("1. Look at the URL in your browser")
    print("2. It should look like: https://ads.google.com/um/Welcome/Home?ocid=1234567890")
    print("3. The number after 'ocid=' is your customer ID")
    print("4. Or go to Tools → Account access and look for 'Customer ID'")
    print("\nOpening Google Ads now...")
    
    webbrowser.open("https://ads.google.com/um/Welcome/Home")
    
    print("\nOnce you find your customer ID, tell me and I'll update the .env file.")
    print("Also, you'll need to get your developer token from:")
    print("https://ads.google.com/apis/credentials")

if __name__ == "__main__":
    open_google_ads_for_customer_id()
