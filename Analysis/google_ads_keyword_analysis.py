import argparse
import sys
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

# --- Instructions for Docker Setup ---
# This script is designed to be run in a Docker container to ensure a clean environment.
# 1. Create a .env file in the same directory as this script with your Google Ads credentials:
#    GOOGLE_ADS_DEVELOPER_TOKEN=...
#    GOOGLE_ADS_CLIENT_ID=...
#    GOOGLE_ADS_CLIENT_SECRET=...
#    GOOGLE_ADS_REFRESH_TOKEN=...
#    GOOGLE_ADS_LOGIN_CUSTOMER_ID=...
#    GOOGLE_ADS_CUSTOMER_ID=...
#
# 2. Build the Docker image:
#    docker build -t google-ads-analyzer .
#
# 3. Run the Docker container:
#    docker run --env-file .env google-ads-analyzer
# -----------------------------------------

# --- Configuration ---
# Keywords to analyze.
KEYWORD_THEMES = [
    "Deer Valley East Real Estate",
    "Heber Utah Real Estate",
    "Ski in Ski Out Home for Sale",
    "Victory Ranch",
    "Red Ledges",
    "Promontory Park City",
]

# Geographic targeting: Park City, Utah, United States.
GEO_TARGET_ID = "1026481"  # Park City, UT, US
LANGUAGE_ID = "1000" # English

# --- Main Script ---

def main(client, customer_id):
    """
    Main function to execute the keyword analysis process.

    Args:
        client: An authenticated Google Ads API client.
        customer_id: The Google Ads customer ID.
    """
    results = get_keyword_metrics(client, customer_id, KEYWORD_THEMES, GEO_TARGET_ID, LANGUAGE_ID)
    process_and_display_results(results)


def get_keyword_metrics(client, customer_id, keywords, location_id, language_id):
    """Fetches historical metrics for a list of keywords.

    Args:
        client: An authenticated Google Ads API client.
        customer_id: The Google Ads customer ID.
        keywords: A list of keyword strings to analyze.
        location_id: The geo target constant ID for the location.
        language_id: The language constant ID.

    Returns:
        The response from the API containing the keyword ideas.
    """
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    googleads_service = client.get_service("GoogleAdsService")

    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = googleads_service.language_constant_path(language_id)
    request.geo_target_constants.append(
        googleads_service.geo_target_constant_path(location_id)
    )
    request.keyword_seed.keywords.extend(keywords)
    request.include_adult_keywords = False
    request.historical_metrics_options.year_month_range.start.year = 2023
    request.historical_metrics_options.year_month_range.start.month = client.enums.MonthOfYearEnum.JANUARY
    request.historical_metrics_options.year_month_range.end.year = 2023
    request.historical_metrics_options.year_month_range.end.month = client.enums.MonthOfYearEnum.DECEMBER


    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(
            request=request
        )
        return response
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)


def process_and_display_results(results):
    """Processes the API response and displays results in a DataFrame.

    Args:
        results: The keyword ideas response from the API.
    """
    data = []

    for result in results:
        metrics = result.keyword_idea_metrics
        competition_level = metrics.competition.name if metrics.competition else "UNSPECIFIED"
        
        data.append(
            {
                "Keyword": result.text,
                "Avg Monthly Searches": metrics.avg_monthly_searches if metrics.avg_monthly_searches else 0,
                "Competition": competition_level,
                "Low Bid ($)": metrics.low_top_of_page_bid_micros / 1_000_000 if metrics.low_top_of_page_bid_micros else 0,
                "High Bid ($)": metrics.high_top_of_page_bid_micros / 1_000_000 if metrics.high_top_of_page_bid_micros else 0,
            }
        )

    if not data:
        print("No metrics returned for the given keywords.")
        return
        
    df = pd.DataFrame(data)
    
    # Format the currency columns
    df["Low Bid ($)"] = df["Low Bid ($)"].map("${:,.2f}".format)
    df["High Bid ($)"] = df["High Bid ($)"].map("${:,.2f}".format)
    
    print("\n--- Keyword Performance Analysis ---")
    print(df.to_string(index=False))
    print("------------------------------------\n")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv is not installed. Credentials must be set as environment variables.")

    # Create a dictionary with your Google Ads API credentials.
    google_ads_config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    if not all(google_ads_config.values()) or not customer_id:
        print(
            "One or more required Google Ads environment variables are not set. "
            "Please check your .env file or environment variables."
        )
        sys.exit(1)


    try:
        # Initialize the Google Ads client from the dictionary.
        googleads_client = GoogleAdsClient.load_from_dict(google_ads_config)
        main(googleads_client, customer_id)
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
