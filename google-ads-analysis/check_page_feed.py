# check_page_feed.py
# Requirements:
#   pip install google-ads==22.1.0
#   google-ads.yaml configured OR env vars set (DEV_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
#
# Usage:
#   python check_page_feed.py --customer 8335511794 --login 5426234549 --campaign "L.R - PMax - General"

import argparse
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

def gaql(client, customer_id, query):
    svc = client.get_service("GoogleAdsService")
    resp = svc.search_stream(customer_id=customer_id, query=query)
    for batch in resp:
        for row in batch.results:
            yield row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--customer", required=True, help="Customer ID (no dashes)")
    parser.add_argument("--login", required=False, help="Login customer ID (MCC) (no dashes)")
    parser.add_argument("--campaign", default="L.R - PMax - General")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Load client with environment variables
    config = {
        "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }
    
    client = GoogleAdsClient.load_from_dict(config)
    
    # Set login customer ID for manager account access
    if args.login:
        client.login_customer_id = args.login

    cust = args.customer
    camp_name = args.campaign

    try:
        print(f"=== Campaign lookup: {camp_name} ===")
        # 1) Get campaign resource + final url expansion setting
        q1 = f"""
          SELECT
            campaign.resource_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            campaign.status,
            campaign.final_url_expansion_opt_out
          FROM campaign
          WHERE campaign.name = '{camp_name}'
        """
        camp = None
        for row in gaql(client, cust, q1):
            camp = row.campaign
            break
        if not camp:
            print("❌ Campaign not found.")
            return
        print(f"Campaign ID: {camp.id} | status: {camp.status.name}")
        fux = bool(camp.final_url_expansion_opt_out)
        print(f"Final URL Expansion Opt-Out = {fux} (should be False)")

        # 2) Find PAGE_FEED Asset Sets
        print("\n=== PAGE_FEED AssetSets ===")
        q2 = """
          SELECT
            asset_set.resource_name,
            asset_set.id,
            asset_set.name,
            asset_set.type
          FROM asset_set
          WHERE asset_set.type = 'PAGE_FEED'
        """
        page_feed_sets = list(gaql(client, cust, q2))
        if not page_feed_sets:
            print("❌ No PAGE_FEED asset sets found.")
        else:
            for r in page_feed_sets:
                aset = r.asset_set
                print(f"Found AssetSet: {aset.name} ({aset.resource_name})")

        # 3) Check which PAGE_FEED sets are linked to this campaign
        print("\n=== CampaignAssetSet links (campaign ↔ PAGE_FEED) ===")
        q3 = f"""
          SELECT
            campaign_asset_set.campaign,
            campaign_asset_set.asset_set,
            asset_set.name,
            asset_set.type
          FROM campaign_asset_set
          WHERE campaign_asset_set.campaign = '{camp.resource_name}'
        """
        linked_sets = []
        for row in gaql(client, cust, q3):
            if row.asset_set.type.name == "PAGE_FEED":
                linked_sets.append((row.asset_set.name, row.campaign_asset_set.asset_set))
                print(f"Linked PAGE_FEED: {row.asset_set.name} ({row.campaign_asset_set.asset_set})")
        if not linked_sets:
            print("❌ No PAGE_FEED AssetSet linked to campaign.")

        # 4) If we have a linked PAGE_FEED, list some URLs in it
        if linked_sets:
            print("\n=== First 25 PageFeed URLs in linked sets ===")
            for label, aset_res in linked_sets:
                q4 = f"""
                  SELECT
                    asset_set_asset.asset_set,
                    asset_set_asset.asset,
                    asset.resource_name,
                    asset.page_feed_asset.page_url,
                    asset.page_feed_asset.labels
                  FROM asset_set_asset
                  WHERE asset_set_asset.asset_set = '{aset_res}'
                  LIMIT 200
                """
                count = 0
                for row in gaql(client, cust, q4):
                    url = row.asset.page_feed_asset.page_url
                    labels = list(row.asset.page_feed_asset.labels) if row.asset.page_feed_asset.labels else []
                    if url:
                        print(f"- {url} | labels: {labels}")
                        count += 1
                        if count >= 25:
                            break
                if count == 0:
                    print("(No page URLs found in this asset set.)")

        # 5) Show URL Exclusions (if any stored at campaign criterion URLs)
        print("\n=== URL Exclusions (final URL expansion) ===")
        # For PMax, exclusions are not in campaign_criterion; they're campaign settings/UI.
        # We'll at least print brand exclusions or negative keywords if present.
        q5 = f"""
          SELECT
            campaign_criterion.campaign,
            campaign_criterion.type,
            campaign_criterion.negative,
            campaign_criterion.keyword.text,
            campaign_criterion.keyword.match_type,
            campaign_criterion.location.geo_target_constant
          FROM campaign_criterion
          WHERE campaign_criterion.campaign = '{camp.resource_name}'
        """
        neg_kw = 0
        neg_loc = 0
        for row in gaql(client, cust, q5):
            crit = row.campaign_criterion
            if crit.type.name == "KEYWORD" and crit.negative:
                neg_kw += 1
            if crit.type.name == "LOCATION" and crit.negative:
                neg_loc += 1
        print(f"Negative keywords found: {neg_kw}")
        print(f"Negative locations found: {neg_loc} (expect 4: India/Pakistan/Bangladesh/Philippines if you added them via API)")

        # Verdicts
        ok_fux = (fux is False)
        ok_feed = bool(linked_sets)
        print("\n=== Verdicts ===")
        print(f"Final URL expansion ON: {'✅' if ok_fux else '❌'}")
        print(f"PAGE_FEED linked to campaign: {'✅' if ok_feed else '❌'}")

    except GoogleAdsException as ex:
        print("GoogleAdsException:")
        for err in ex.failure.errors:
            print(f"- {err.error_code}: {err.message}")
        raise

if __name__ == "__main__":
    main()
