#!/usr/bin/env python3
"""
Campaign Auditor
================

Comprehensive campaign audit system that downloads all campaign data from Google Ads API
and provides detailed analysis and optimization recommendations.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class CampaignAuditor:
    """Comprehensive campaign audit and analysis system."""
    
    def __init__(self, customer_id: str, manager_customer_id: Optional[str] = None):
        self.customer_id = customer_id
        self.manager_customer_id = manager_customer_id or customer_id
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Google Ads client
        try:
            config = {
                "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"),
                "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
                "refresh_token": os.environ.get("GOOGLE_ADS_REFRESH_TOKEN"),
                "use_proto_plus": True,
            }
            
            self.client = GoogleAdsClient.load_from_dict(config)
            self.google_ads_service = self.client.get_service("GoogleAdsService")
            
            logger.info("✅ Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Ads client: {e}")
            raise
        
        # Audit results storage
        self.audit_results = {}
        self.audit_file = f"data/campaign_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def audit_campaign(self, campaign_name: str = "L.R - PMax - General") -> Dict:
        """Perform comprehensive campaign audit."""
        
        logger.info(f"🔍 Starting comprehensive audit for campaign: {campaign_name}")
        
        try:
            # Step 1: Download campaign data
            logger.info("📥 Step 1: Downloading campaign data...")
            campaign_data = self._download_campaign_data(campaign_name)
            
            if not campaign_data:
                return {
                    "success": False,
                    "error": f"Campaign '{campaign_name}' not found or no data available"
                }
            
            # Step 2: Analyze campaign structure
            logger.info("🏗️ Step 2: Analyzing campaign structure...")
            structure_analysis = self._analyze_campaign_structure(campaign_data)
            
            # Step 3: Analyze performance data
            logger.info("📊 Step 3: Analyzing performance data...")
            performance_analysis = self._analyze_performance_data(campaign_data)
            
            # Step 4: Analyze targeting and audience
            logger.info("🎯 Step 4: Analyzing targeting and audience...")
            targeting_analysis = self._analyze_targeting(campaign_data)
            
            # Step 5: Analyze assets and creatives
            logger.info("🖼️ Step 5: Analyzing assets and creatives...")
            asset_analysis = self._analyze_assets(campaign_data)
            
            # Step 6: Analyze budget and bidding
            logger.info("💰 Step 6: Analyzing budget and bidding...")
            budget_analysis = self._analyze_budget_bidding(campaign_data)
            
            # Step 7: Generate recommendations
            logger.info("💡 Step 7: Generating optimization recommendations...")
            recommendations = self._generate_recommendations(
                structure_analysis, performance_analysis, targeting_analysis, 
                asset_analysis, budget_analysis
            )
            
            # Step 8: Create comprehensive audit report
            audit_report = {
                "success": True,
                "campaign_name": campaign_name,
                "audit_timestamp": datetime.now().isoformat(),
                "campaign_data": campaign_data,
                "analysis": {
                    "structure": structure_analysis,
                    "performance": performance_analysis,
                    "targeting": targeting_analysis,
                    "assets": asset_analysis,
                    "budget": budget_analysis
                },
                "recommendations": recommendations,
                "summary": self._create_audit_summary(recommendations)
            }
            
            # Save audit results
            self._save_audit_results(audit_report)
            
            logger.info(f"✅ Campaign audit completed successfully!")
            logger.info(f"   Audit saved to: {self.audit_file}")
            
            return audit_report
            
        except Exception as e:
            logger.error(f"❌ Campaign audit failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_name": campaign_name
            }
    
    def _download_campaign_data(self, campaign_name: str) -> Optional[Dict]:
        """Download comprehensive campaign data from Google Ads API."""
        
        try:
            # Campaign basic info
            campaign_query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.campaign_budget,
                    campaign.advertising_channel_type,
                    campaign.advertising_channel_sub_type,
                    campaign.target_cpa.target_cpa_micros,
                    campaign.target_cpa.target_cpa_micros,
                    campaign.target_roas.target_roas,
                    campaign.bidding_strategy_type,
                    campaign.start_date,
                    campaign.end_date,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method,
                    campaign_budget.period,
                    campaign_budget.type
                FROM campaign
                WHERE campaign.name = '{campaign_name}'
            """
            
            campaign_response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=campaign_query
            )
            
            campaign_data = None
            for row in campaign_response:
                campaign_data = {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "budget_id": row.campaign.campaign_budget,
                    "channel_type": row.campaign.advertising_channel_type.name,
                    "channel_sub_type": row.campaign.advertising_channel_sub_type.name if row.campaign.advertising_channel_sub_type else None,
                    "target_cpa": row.campaign.target_cpa.target_cpa_micros / 1000000 if row.campaign.target_cpa else None,
                    "target_roas": row.campaign.target_roas.target_roas if row.campaign.target_roas else None,
                    "bidding_strategy": row.campaign.bidding_strategy_type.name,
                    "start_date": row.campaign.start_date,
                    "end_date": row.campaign.end_date,
                    "budget_amount": row.campaign_budget.amount_micros / 1000000 if row.campaign_budget.amount_micros else 0,
                    "budget_delivery": row.campaign_budget.delivery_method.name if row.campaign_budget.delivery_method else None,
                    "budget_period": row.campaign_budget.period.name if row.campaign_budget.period else None,
                    "budget_type": row.campaign_budget.type.name if row.campaign_budget.type else None
                }
                break
            
            if not campaign_data:
                return None
            
            # Performance metrics (last 30 days)
            performance_query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.cost_per_conversion,
                    metrics.value_per_conversion,
                    metrics.search_impression_share,
                    metrics.search_budget_lost_impression_share,
                    metrics.search_rank_lost_impression_share,
                    metrics.all_conversions,
                    metrics.all_conversions_value,
                    metrics.cost_per_all_conversions,
                    metrics.value_per_all_conversions
                FROM campaign
                WHERE campaign.name = '{campaign_name}'
                AND segments.date BETWEEN '{self._get_date_30_days_ago()}' AND '{datetime.now().strftime('%Y-%m-%d')}'
            """
            
            performance_response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=performance_query
            )
            
            performance_data = []
            for row in performance_response:
                performance_data.append({
                    "date": row.segments.date,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "ctr": row.metrics.ctr,
                    "average_cpc": row.metrics.average_cpc,
                    "cost": row.metrics.cost_micros / 1000000,
                    "conversions": row.metrics.conversions,
                    "conversions_value": row.metrics.conversions_value,
                    "cost_per_conversion": row.metrics.cost_per_conversion,
                    "value_per_conversion": row.metrics.value_per_conversion,
                    "search_impression_share": row.metrics.search_impression_share,
                    "search_budget_lost_impression_share": row.metrics.search_budget_lost_impression_share,
                    "search_rank_lost_impression_share": row.metrics.search_rank_lost_impression_share,
                    "all_conversions": row.metrics.all_conversions,
                    "all_conversions_value": row.metrics.all_conversions_value,
                    "cost_per_all_conversions": row.metrics.cost_per_all_conversions,
                    "value_per_all_conversions": row.metrics.value_per_all_conversions
                })
            
            campaign_data["performance"] = performance_data
            
            # Asset sets and assets
            asset_query = f"""
                SELECT 
                    campaign_asset_set.campaign,
                    campaign_asset_set.asset_set,
                    asset_set.name,
                    asset_set.type
                FROM campaign_asset_set
                WHERE campaign_asset_set.campaign = 'customers/{self.customer_id}/campaigns/{campaign_data["id"]}'
            """
            
            asset_response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=asset_query
            )
            
            asset_data = []
            for row in asset_response:
                asset_data.append({
                    "asset_set_name": row.asset_set.name,
                    "asset_set_type": row.asset_set.type.name
                })
            
            campaign_data["assets"] = asset_data
            
            # Keywords (if applicable)
            keyword_query = f"""
                SELECT 
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_micros,
                    metrics.conversions
                FROM keyword_view
                WHERE campaign.name = '{campaign_name}'
                AND segments.date BETWEEN '{self._get_date_30_days_ago()}' AND '{datetime.now().strftime('%Y-%m-%d')}'
            """
            
            keyword_response = self.google_ads_service.search(
                customer_id=self.customer_id,
                query=keyword_query
            )
            
            keyword_data = []
            for row in keyword_response:
                keyword_data.append({
                    "keyword_id": row.ad_group_criterion.criterion_id,
                    "keyword_text": row.ad_group_criterion.keyword.text,
                    "match_type": row.ad_group_criterion.keyword.match_type.name,
                    "status": row.ad_group_criterion.status.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "ctr": row.metrics.ctr,
                    "average_cpc": row.metrics.average_cpc,
                    "cost": row.metrics.cost_micros / 1000000,
                    "conversions": row.metrics.conversions
                })
            
            campaign_data["keywords"] = keyword_data
            
            return campaign_data
            
        except GoogleAdsException as e:
            logger.error(f"❌ Google Ads API error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error downloading campaign data: {e}")
            return None
    
    def _get_date_30_days_ago(self) -> str:
        """Get date string for 30 days ago."""
        date_30_days_ago = datetime.now() - timedelta(days=30)
        return date_30_days_ago.strftime('%Y-%m-%d')
    
    def _analyze_campaign_structure(self, campaign_data: Dict) -> Dict:
        """Analyze campaign structure and configuration."""
        
        analysis = {
            "campaign_type": campaign_data.get("channel_type"),
            "bidding_strategy": campaign_data.get("bidding_strategy"),
            "budget_amount": campaign_data.get("budget_amount"),
            "budget_delivery": campaign_data.get("budget_delivery"),
            "target_cpa": campaign_data.get("target_cpa"),
            "target_roas": campaign_data.get("target_roas"),
            "status": campaign_data.get("status"),
            "issues": [],
            "strengths": []
        }
        
        # Check campaign type
        if campaign_data.get("channel_type") == "PERFORMANCE_MAX":
            analysis["strengths"].append("Using Performance Max - good for automated optimization")
        else:
            analysis["issues"].append(f"Campaign type '{campaign_data.get('channel_type')}' may not be optimal for real estate")
        
        # Check bidding strategy
        bidding_strategy = campaign_data.get("bidding_strategy")
        if bidding_strategy in ["TARGET_CPA", "TARGET_ROAS"]:
            analysis["strengths"].append(f"Using {bidding_strategy} - good for conversion optimization")
        elif bidding_strategy == "MAXIMIZE_CONVERSIONS":
            analysis["strengths"].append("Using Maximize Conversions - good for new campaigns")
        else:
            analysis["issues"].append(f"Bidding strategy '{bidding_strategy}' may not be optimal")
        
        # Check budget
        budget = campaign_data.get("budget_amount", 0)
        if budget < 1000:
            analysis["issues"].append(f"Budget ${budget} may be too low for effective performance")
        elif budget > 10000:
            analysis["issues"].append(f"Budget ${budget} may be too high for initial testing")
        else:
            analysis["strengths"].append(f"Budget ${budget} is within reasonable range")
        
        # Check budget delivery
        if campaign_data.get("budget_delivery") == "STANDARD":
            analysis["strengths"].append("Using standard budget delivery - good for consistent spending")
        else:
            analysis["issues"].append("Consider using standard budget delivery for better control")
        
        return analysis
    
    def _analyze_performance_data(self, campaign_data: Dict) -> Dict:
        """Analyze campaign performance data."""
        
        performance_data = campaign_data.get("performance", [])
        
        if not performance_data:
            return {
                "status": "no_data",
                "message": "No performance data available (campaign may be too new)",
                "issues": ["Campaign is too new to analyze performance"],
                "recommendations": ["Wait for more data before making optimization decisions"]
            }
        
        # Calculate totals
        total_impressions = sum(day.get("impressions", 0) for day in performance_data)
        total_clicks = sum(day.get("clicks", 0) for day in performance_data)
        total_cost = sum(day.get("cost", 0) for day in performance_data)
        total_conversions = sum(day.get("conversions", 0) for day in performance_data)
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cost_per_conversion = (total_cost / total_conversions) if total_conversions > 0 else 0
        
        analysis = {
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_cost": total_cost,
            "total_conversions": total_conversions,
            "avg_ctr": avg_ctr,
            "avg_cpc": avg_cpc,
            "conversion_rate": conversion_rate,
            "cost_per_conversion": cost_per_conversion,
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Analyze CTR
        if avg_ctr < 1.0:
            analysis["issues"].append(f"CTR {avg_ctr:.2f}% is below industry average (1-3%)")
            analysis["recommendations"].append("Improve ad relevance and targeting to increase CTR")
        elif avg_ctr > 5.0:
            analysis["strengths"].append(f"CTR {avg_ctr:.2f}% is excellent")
        else:
            analysis["strengths"].append(f"CTR {avg_ctr:.2f}% is within good range")
        
        # Analyze CPC
        if avg_cpc > 5.0:
            analysis["issues"].append(f"CPC ${avg_cpc:.2f} is high for real estate")
            analysis["recommendations"].append("Consider adjusting bidding strategy or improving ad quality")
        elif avg_cpc < 1.0:
            analysis["strengths"].append(f"CPC ${avg_cpc:.2f} is very competitive")
        else:
            analysis["strengths"].append(f"CPC ${avg_cpc:.2f} is within reasonable range")
        
        # Analyze conversions
        if total_conversions == 0:
            analysis["issues"].append("No conversions yet - check conversion tracking")
            analysis["recommendations"].append("Verify conversion tracking is properly set up")
        elif conversion_rate < 2.0:
            analysis["issues"].append(f"Conversion rate {conversion_rate:.2f}% is low")
            analysis["recommendations"].append("Improve landing page experience and ad relevance")
        else:
            analysis["strengths"].append(f"Conversion rate {conversion_rate:.2f}% is good")
        
        # Analyze cost per conversion
        if cost_per_conversion > 200:
            analysis["issues"].append(f"Cost per conversion ${cost_per_conversion:.2f} is high")
            analysis["recommendations"].append("Optimize for lower cost conversions")
        elif cost_per_conversion < 50:
            analysis["strengths"].append(f"Cost per conversion ${cost_per_conversion:.2f} is excellent")
        else:
            analysis["strengths"].append(f"Cost per conversion ${cost_per_conversion:.2f} is reasonable")
        
        return analysis
    
    def _analyze_targeting(self, campaign_data: Dict) -> Dict:
        """Analyze targeting and audience configuration."""
        
        keyword_data = campaign_data.get("keywords", [])
        
        analysis = {
            "total_keywords": len(keyword_data),
            "match_types": {},
            "keyword_performance": {},
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        if not keyword_data:
            analysis["issues"].append("No keywords found - Performance Max campaigns use automated targeting")
            analysis["recommendations"].append("Consider adding negative keywords to exclude irrelevant traffic")
            analysis["keyword_performance"] = {
                "high_performing": 0,
                "low_performing": 0
            }
            return analysis
        
        # Analyze match types
        for keyword in keyword_data:
            match_type = keyword.get("match_type")
            if match_type not in analysis["match_types"]:
                analysis["match_types"][match_type] = 0
            analysis["match_types"][match_type] += 1
        
        # Analyze keyword performance
        high_performing_keywords = []
        low_performing_keywords = []
        
        for keyword in keyword_data:
            impressions = keyword.get("impressions", 0)
            ctr = keyword.get("ctr", 0)
            conversions = keyword.get("conversions", 0)
            
            if impressions > 100 and ctr > 2.0:
                high_performing_keywords.append(keyword)
            elif impressions > 50 and ctr < 1.0:
                low_performing_keywords.append(keyword)
        
        analysis["keyword_performance"] = {
            "high_performing": len(high_performing_keywords),
            "low_performing": len(low_performing_keywords)
        }
        
        # Generate recommendations
        if len(high_performing_keywords) > 0:
            analysis["strengths"].append(f"{len(high_performing_keywords)} high-performing keywords")
        
        if len(low_performing_keywords) > 0:
            analysis["issues"].append(f"{len(low_performing_keywords)} low-performing keywords")
            analysis["recommendations"].append("Consider pausing or modifying low-performing keywords")
        
        # Check for broad match keywords
        if "BROAD" in analysis["match_types"]:
            analysis["issues"].append("Broad match keywords may generate irrelevant traffic")
            analysis["recommendations"].append("Consider using phrase or exact match for better control")
        
        return analysis
    
    def _analyze_assets(self, campaign_data: Dict) -> Dict:
        """Analyze assets and creatives."""
        
        asset_data = campaign_data.get("assets", [])
        
        analysis = {
            "total_assets": len(asset_data),
            "asset_types": {},
            "asset_sets": {},
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        if not asset_data:
            analysis["issues"].append("No assets found - campaigns need assets for Performance Max")
            analysis["recommendations"].append("Add images, videos, and text assets to improve ad performance")
            return analysis
        
        # Analyze asset types
        for asset in asset_data:
            asset_type = asset.get("asset_type")
            if asset_type:
                if asset_type not in analysis["asset_types"]:
                    analysis["asset_types"][asset_type] = 0
                analysis["asset_types"][asset_type] += 1
            
            asset_set = asset.get("asset_set_name")
            if asset_set:
                if asset_set not in analysis["asset_sets"]:
                    analysis["asset_sets"][asset_set] = 0
                analysis["asset_sets"][asset_set] += 1
        
        # Check for required asset types
        required_types = ["IMAGE", "TEXT", "LOGO"]
        for required_type in required_types:
            if required_type not in analysis["asset_types"]:
                analysis["issues"].append(f"Missing {required_type} assets")
                analysis["recommendations"].append(f"Add {required_type} assets for better ad variety")
        
        # Check asset quantity
        if analysis["total_assets"] < 10:
            analysis["issues"].append(f"Only {analysis['total_assets']} assets - need more for optimal performance")
            analysis["recommendations"].append("Add more assets to improve ad variety and performance")
        else:
            analysis["strengths"].append(f"Good asset quantity: {analysis['total_assets']} assets")
        
        return analysis
    
    def _analyze_budget_bidding(self, campaign_data: Dict) -> Dict:
        """Analyze budget and bidding configuration."""
        
        analysis = {
            "budget_amount": campaign_data.get("budget_amount", 0),
            "bidding_strategy": campaign_data.get("bidding_strategy"),
            "target_cpa": campaign_data.get("target_cpa"),
            "target_roas": campaign_data.get("target_roas"),
            "issues": [],
            "strengths": [],
            "recommendations": []
        }
        
        # Analyze budget
        budget = analysis["budget_amount"]
        if budget < 500:
            analysis["issues"].append(f"Budget ${budget} is very low - may limit performance")
            analysis["recommendations"].append("Consider increasing budget to $1,000+ for better results")
        elif budget > 5000:
            analysis["issues"].append(f"Budget ${budget} is high for initial testing")
            analysis["recommendations"].append("Consider starting with lower budget and scaling up")
        else:
            analysis["strengths"].append(f"Budget ${budget} is appropriate for testing")
        
        # Analyze bidding strategy
        bidding_strategy = analysis["bidding_strategy"]
        if bidding_strategy == "TARGET_CPA":
            if analysis["target_cpa"] and analysis["target_cpa"] > 100:
                analysis["issues"].append(f"Target CPA ${analysis['target_cpa']} may be too high")
                analysis["recommendations"].append("Consider lowering target CPA to $50-100")
            else:
                analysis["strengths"].append("Using Target CPA bidding - good for conversion optimization")
        elif bidding_strategy == "MAXIMIZE_CONVERSIONS":
            analysis["strengths"].append("Using Maximize Conversions - good for new campaigns")
        elif bidding_strategy == "TARGET_ROAS":
            if analysis["target_roas"] and analysis["target_roas"] < 2.0:
                analysis["issues"].append(f"Target ROAS {analysis['target_roas']} may be too low")
                analysis["recommendations"].append("Consider setting target ROAS to 3.0+ for real estate")
            else:
                analysis["strengths"].append("Using Target ROAS bidding - good for revenue optimization")
        
        return analysis
    
    def _generate_recommendations(self, structure_analysis: Dict, performance_analysis: Dict,
                                targeting_analysis: Dict, asset_analysis: Dict, 
                                budget_analysis: Dict) -> List[Dict]:
        """Generate comprehensive optimization recommendations."""
        
        recommendations = []
        
        # High priority recommendations
        high_priority = []
        
        # Check for critical issues
        if performance_analysis.get("status") == "no_data":
            high_priority.append({
                "priority": "High",
                "category": "Data",
                "issue": "No performance data available",
                "recommendation": "Wait for more data before making optimization decisions",
                "impact": "Critical"
            })
        
        if asset_analysis.get("total_assets", 0) < 5:
            high_priority.append({
                "priority": "High",
                "category": "Assets",
                "issue": "Insufficient assets",
                "recommendation": "Add more images, videos, and text assets",
                "impact": "High"
            })
        
        if budget_analysis.get("budget_amount", 0) < 500:
            high_priority.append({
                "priority": "High",
                "category": "Budget",
                "issue": "Budget too low",
                "recommendation": "Increase budget to $1,000+ for better performance",
                "impact": "High"
            })
        
        # Medium priority recommendations
        medium_priority = []
        
        if performance_analysis.get("avg_ctr", 0) < 1.0:
            medium_priority.append({
                "priority": "Medium",
                "category": "Performance",
                "issue": f"Low CTR: {performance_analysis.get('avg_ctr', 0):.2f}%",
                "recommendation": "Improve ad relevance and targeting",
                "impact": "Medium"
            })
        
        if performance_analysis.get("avg_cpc", 0) > 5.0:
            medium_priority.append({
                "priority": "Medium",
                "category": "Performance",
                "issue": f"High CPC: ${performance_analysis.get('avg_cpc', 0):.2f}",
                "recommendation": "Adjust bidding strategy or improve ad quality",
                "impact": "Medium"
            })
        
        if targeting_analysis.get("total_keywords", 0) == 0:
            medium_priority.append({
                "priority": "Medium",
                "category": "Targeting",
                "issue": "No keyword targeting",
                "recommendation": "Add negative keywords to exclude irrelevant traffic",
                "impact": "Medium"
            })
        
        # Low priority recommendations
        low_priority = []
        
        if structure_analysis.get("budget_delivery") != "STANDARD":
            low_priority.append({
                "priority": "Low",
                "category": "Structure",
                "issue": "Non-standard budget delivery",
                "recommendation": "Consider using standard budget delivery",
                "impact": "Low"
            })
        
        if asset_analysis.get("total_assets", 0) < 20:
            low_priority.append({
                "priority": "Low",
                "category": "Assets",
                "issue": "Could use more assets",
                "recommendation": "Add more assets for better ad variety",
                "impact": "Low"
            })
        
        # Combine all recommendations
        recommendations.extend(high_priority)
        recommendations.extend(medium_priority)
        recommendations.extend(low_priority)
        
        return recommendations
    
    def _create_audit_summary(self, recommendations: List[Dict]) -> Dict:
        """Create audit summary."""
        
        high_priority_count = len([r for r in recommendations if r["priority"] == "High"])
        medium_priority_count = len([r for r in recommendations if r["priority"] == "Medium"])
        low_priority_count = len([r for r in recommendations if r["priority"] == "Low"])
        
        return {
            "total_recommendations": len(recommendations),
            "high_priority": high_priority_count,
            "medium_priority": medium_priority_count,
            "low_priority": low_priority_count,
            "overall_status": "Critical" if high_priority_count > 0 else "Good" if medium_priority_count == 0 else "Needs Attention"
        }
    
    def _save_audit_results(self, audit_report: Dict):
        """Save audit results to file."""
        os.makedirs('data', exist_ok=True)
        with open(self.audit_file, 'w') as f:
            json.dump(audit_report, f, indent=2)

def test_campaign_auditor():
    """Test the campaign auditor."""
    print("🔍 Testing Campaign Auditor")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        print("❌ GOOGLE_ADS_CUSTOMER_ID not found in environment")
        return
    
    try:
        auditor = CampaignAuditor(customer_id)
        
        # Test campaign audit
        print("🔍 Running campaign audit...")
        result = auditor.audit_campaign("L.R - PMax - General")
        
        if result["success"]:
            print(f"✅ Campaign audit completed successfully!")
            print(f"   Campaign: {result['campaign_name']}")
            print(f"   Audit File: {auditor.audit_file}")
            
            # Show summary
            summary = result["summary"]
            print(f"\n📊 Audit Summary:")
            print(f"   Overall Status: {summary['overall_status']}")
            print(f"   Total Recommendations: {summary['total_recommendations']}")
            print(f"   High Priority: {summary['high_priority']}")
            print(f"   Medium Priority: {summary['medium_priority']}")
            print(f"   Low Priority: {summary['low_priority']}")
            
            # Show top recommendations
            print(f"\n💡 Top Recommendations:")
            for rec in result["recommendations"][:5]:
                print(f"   {rec['priority']}: {rec['recommendation']}")
        else:
            print(f"❌ Campaign audit failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_campaign_auditor()
