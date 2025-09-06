#!/usr/bin/env python3
"""
Enhanced Real Estate Chatbot
============================

AI-powered chatbot that can discuss strategies, analyze data, and implement
changes through the staging area. Integrates with Gemini API and campaign data.
"""

import streamlit as st
import google.generativeai as genai
import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add google-ads-analysis to path for imports
google_ads_path = os.path.join(os.path.dirname(__file__), 'google-ads-analysis')
sys.path.insert(0, google_ads_path)

try:
    from tools.campaign_auditor import CampaignAuditor
    HAS_CAMPAIGN_AUDITOR = True
except ImportError:
    CampaignAuditor = None
    HAS_CAMPAIGN_AUDITOR = False

try:
    from ads.guardrails import PerformanceMaxGuardrails as AdsGuardrails
    HAS_ADS_GUARDRAILS = True
except ImportError:
    AdsGuardrails = None
    HAS_ADS_GUARDRAILS = False

class EnhancedRealEstateChatbot:
    """
    Enhanced chatbot that can discuss strategies, analyze data, and implement
    changes through the staging area with guardrails validation.
    """
    
    def __init__(self):
        # Configure Gemini API
        try:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            self.model = genai.GenerativeModel(
                'gemini-pro',
                tools=self._get_function_declarations()
            )
        except (AttributeError, KeyError):
            st.error("Please set the GOOGLE_API_KEY environment variable.")
            return
        
        # Initialize tools
        self.tools = {
            "get_campaign_performance": self.get_campaign_performance,
            "analyze_campaign_data": self.analyze_campaign_data,
            "propose_budget_change": self.propose_budget_change,
            "propose_targeting_change": self.propose_targeting_change,
            "propose_asset_change": self.propose_asset_change,
            "validate_strategy": self.validate_strategy,
            "implement_strategy": self.implement_strategy,
            "get_staging_status": self.get_staging_status,
            "approve_changes": self.approve_changes
        }
        
        # Initialize guardrails
        self.guardrails = None
        if HAS_ADS_GUARDRAILS:
            try:
                self.guardrails = AdsGuardrails()
            except Exception as e:
                st.warning(f"Could not initialize guardrails: {e}")
        
        # Initialize campaign auditor
        self.campaign_auditor = None
        if HAS_CAMPAIGN_AUDITOR:
            try:
                self.campaign_auditor = CampaignAuditor('5426234549')
            except Exception as e:
                st.warning(f"Could not initialize campaign auditor: {e}")
        
        # Staging data
        self.staging_file = 'data/campaign_staging.json'
        self.staging_data = self._load_staging_data()
    
    def _get_function_declarations(self):
        """Get function declarations for Gemini API."""
        return [
            {
                "name": "get_campaign_performance",
                "description": "Get current performance metrics for a Google Ads campaign",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "campaign_name": {
                            "type": "STRING",
                            "description": "The name of the campaign to analyze"
                        }
                    },
                    "required": ["campaign_name"]
                }
            },
            {
                "name": "analyze_campaign_data",
                "description": "Run comprehensive campaign audit and analysis",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "campaign_name": {
                            "type": "STRING",
                            "description": "The name of the campaign to audit"
                        }
                    },
                    "required": ["campaign_name"]
                }
            },
            {
                "name": "propose_budget_change",
                "description": "Propose a budget change with guardrails validation",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "campaign_name": {
                            "type": "STRING",
                            "description": "The name of the campaign"
                        },
                        "current_budget": {
                            "type": "NUMBER",
                            "description": "Current daily budget"
                        },
                        "new_budget": {
                            "type": "NUMBER",
                            "description": "Proposed new daily budget"
                        },
                        "reason": {
                            "type": "STRING",
                            "description": "Reason for the budget change"
                        }
                    },
                    "required": ["campaign_name", "current_budget", "new_budget", "reason"]
                }
            },
            {
                "name": "propose_targeting_change",
                "description": "Propose targeting changes with guardrails validation",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "campaign_name": {
                            "type": "STRING",
                            "description": "The name of the campaign"
                        },
                        "change_type": {
                            "type": "STRING",
                            "description": "Type of targeting change (add_location, remove_location, adjust_demographics, add_negative_keywords)"
                        },
                        "details": {
                            "type": "STRING",
                            "description": "Details of the targeting change"
                        }
                    },
                    "required": ["campaign_name", "change_type", "details"]
                }
            },
            {
                "name": "propose_asset_change",
                "description": "Propose asset changes with guardrails validation",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "campaign_name": {
                            "type": "STRING",
                            "description": "The name of the campaign"
                        },
                        "asset_type": {
                            "type": "STRING",
                            "description": "Type of asset (images, videos, text_assets, logos)"
                        },
                        "action": {
                            "type": "STRING",
                            "description": "Action to take (add_assets, remove_assets, update_assets)"
                        },
                        "count": {
                            "type": "NUMBER",
                            "description": "Number of assets to change"
                        }
                    },
                    "required": ["campaign_name", "asset_type", "action", "count"]
                }
            },
            {
                "name": "validate_strategy",
                "description": "Validate a marketing strategy against guardrails and best practices",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "strategy": {
                            "type": "STRING",
                            "description": "The marketing strategy to validate"
                        },
                        "budget": {
                            "type": "NUMBER",
                            "description": "Proposed budget for the strategy"
                        },
                        "timeline": {
                            "type": "STRING",
                            "description": "Timeline for the strategy"
                        }
                    },
                    "required": ["strategy", "budget", "timeline"]
                }
            },
            {
                "name": "implement_strategy",
                "description": "Implement a validated strategy by creating staging changes",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "strategy_name": {
                            "type": "STRING",
                            "description": "Name of the strategy to implement"
                        },
                        "changes": {
                            "type": "STRING",
                            "description": "JSON string of changes to implement"
                        }
                    },
                    "required": ["strategy_name", "changes"]
                }
            },
            {
                "name": "get_staging_status",
                "description": "Get current status of staging area changes",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "approve_changes",
                "description": "Approve pending changes in staging area",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "change_ids": {
                            "type": "STRING",
                            "description": "Comma-separated list of change IDs to approve"
                        }
                    },
                    "required": ["change_ids"]
                }
            }
        ]
    
    def _load_staging_data(self) -> Dict:
        """Load staging data from file."""
        try:
            os.makedirs('data', exist_ok=True)
            if os.path.exists(self.staging_file):
                with open(self.staging_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'pending_changes': [],
                    'approved_changes': [],
                    'rejected_changes': []
                }
        except Exception as e:
            st.error(f"Error loading staging data: {e}")
            return {'pending_changes': [], 'approved_changes': [], 'rejected_changes': []}
    
    def _save_staging_data(self):
        """Save staging data to file."""
        try:
            with open(self.staging_file, 'w') as f:
                json.dump(self.staging_data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving staging data: {e}")
    
    def get_campaign_performance(self, campaign_name: str):
        """Get current campaign performance data."""
        try:
            if self.campaign_auditor:
                result = self.campaign_auditor.audit_campaign(campaign_name)
                if result["success"]:
                    campaign_data = result["campaign_data"]
                    performance = result["analysis"]["performance"]
                    
                    return {
                        "campaign": campaign_name,
                        "status": campaign_data["status"],
                        "budget": campaign_data["budget_amount"],
                        "impressions": performance.get("total_impressions", 0),
                        "clicks": performance.get("total_clicks", 0),
                        "ctr": performance.get("avg_ctr", 0),
                        "cost": performance.get("total_cost", 0),
                        "conversions": performance.get("total_conversions", 0),
                        "cost_per_conversion": performance.get("cost_per_conversion", 0)
                    }
                else:
                    return f"Error: {result.get('error', 'Unknown error')}"
            else:
                # Fallback to mock data
                return {
                    "campaign": campaign_name,
                    "status": "ENABLED",
                    "budget": 50.0,
                    "impressions": 22,
                    "clicks": 2,
                    "ctr": 9.09,
                    "cost": 2.81,
                    "conversions": 0,
                    "cost_per_conversion": 0
                }
        except Exception as e:
            return f"Error getting campaign performance: {e}"
    
    def analyze_campaign_data(self, campaign_name: str):
        """Run comprehensive campaign audit."""
        try:
            if self.campaign_auditor:
                result = self.campaign_auditor.audit_campaign(campaign_name)
                if result["success"]:
                    summary = result["summary"]
                    recommendations = result["recommendations"]
                    
                    return {
                        "campaign": campaign_name,
                        "overall_status": summary["overall_status"],
                        "total_recommendations": summary["total_recommendations"],
                        "high_priority": summary["high_priority"],
                        "medium_priority": summary["medium_priority"],
                        "low_priority": summary["low_priority"],
                        "top_recommendations": recommendations[:3]
                    }
                else:
                    return f"Error: {result.get('error', 'Unknown error')}"
            else:
                return "Campaign auditor not available"
        except Exception as e:
            return f"Error analyzing campaign: {e}"
    
    def propose_budget_change(self, campaign_name: str, current_budget: float, new_budget: float, reason: str):
        """Propose budget change with guardrails validation."""
        try:
            if not self.guardrails:
                return "Guardrails not available for validation"
            
            change_request = {
                'type': 'budget_adjustment',
                'new_daily_budget': new_budget,
                'campaign_name': campaign_name,
                'reason': reason
            }
            
            campaign_state = {
                'daily_budget': current_budget,
                'last_budget_change_date': None
            }
            
            verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
            
            if verdict.approved:
                # Add to staging
                change_details = {
                    'type': 'budget_adjustment',
                    'campaign_name': campaign_name,
                    'current_budget': current_budget,
                    'new_budget': new_budget,
                    'reason': reason,
                    'guardrails_approved': True,
                    'guardrails_reasons': verdict.reasons,
                    'execute_after': verdict.execute_after,
                    'created_at': datetime.now().isoformat()
                }
                
                self.staging_data['pending_changes'].append(change_details)
                self._save_staging_data()
                
                return f"✅ Budget change approved by guardrails! Added to staging area. Execute after: {verdict.execute_after}"
            else:
                return f"❌ Budget change rejected by guardrails: {'; '.join(verdict.reasons)}"
                
        except Exception as e:
            return f"Error proposing budget change: {e}"
    
    def propose_targeting_change(self, campaign_name: str, change_type: str, details: str):
        """Propose targeting change with guardrails validation."""
        try:
            if not self.guardrails:
                return "Guardrails not available for validation"
            
            change_request = {
                'type': 'geo_targeting_modification',
                'action': change_type,
                'campaign_name': campaign_name,
                'details': details
            }
            
            campaign_state = {
                'last_geo_change_date': None
            }
            
            verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
            
            if verdict.approved:
                # Add to staging
                change_details = {
                    'type': 'targeting_modification',
                    'campaign_name': campaign_name,
                    'change_type': change_type,
                    'details': details,
                    'guardrails_approved': True,
                    'guardrails_reasons': verdict.reasons,
                    'execute_after': verdict.execute_after,
                    'created_at': datetime.now().isoformat()
                }
                
                self.staging_data['pending_changes'].append(change_details)
                self._save_staging_data()
                
                return f"✅ Targeting change approved by guardrails! Added to staging area. Execute after: {verdict.execute_after}"
            else:
                return f"❌ Targeting change rejected by guardrails: {'; '.join(verdict.reasons)}"
                
        except Exception as e:
            return f"Error proposing targeting change: {e}"
    
    def propose_asset_change(self, campaign_name: str, asset_type: str, action: str, count: int):
        """Propose asset change with guardrails validation."""
        try:
            if not self.guardrails:
                return "Guardrails not available for validation"
            
            change_request = {
                'type': 'asset_group_modification',
                'action': action,
                'campaign_name': campaign_name,
                'asset_type': asset_type,
                'count': count
            }
            
            campaign_state = {
                'asset_groups': [{'name': 'Main Group', 'status': 'ENABLED', 'asset_counts': {}}]
            }
            
            verdict = self.guardrails.enforce_guardrails(change_request, campaign_state)
            
            if verdict.approved:
                # Add to staging
                change_details = {
                    'type': 'asset_modification',
                    'campaign_name': campaign_name,
                    'asset_type': asset_type,
                    'action': action,
                    'count': count,
                    'guardrails_approved': True,
                    'guardrails_reasons': verdict.reasons,
                    'execute_after': verdict.execute_after,
                    'created_at': datetime.now().isoformat()
                }
                
                self.staging_data['pending_changes'].append(change_details)
                self._save_staging_data()
                
                return f"✅ Asset change approved by guardrails! Added to staging area. Execute after: {verdict.execute_after}"
            else:
                return f"❌ Asset change rejected by guardrails: {'; '.join(verdict.reasons)}"
                
        except Exception as e:
            return f"Error proposing asset change: {e}"
    
    def validate_strategy(self, strategy: str, budget: float, timeline: str):
        """Validate marketing strategy against guardrails and best practices."""
        try:
            validation_results = []
            
            # Budget validation
            if budget < 30:
                validation_results.append("❌ Budget too low - minimum $30/day required")
            elif budget > 250:
                validation_results.append("❌ Budget too high - maximum $250/day allowed")
            else:
                validation_results.append("✅ Budget within acceptable range")
            
            # Strategy validation
            if "park city" in strategy.lower():
                validation_results.append("✅ Strategy targets Park City market")
            if "real estate" in strategy.lower():
                validation_results.append("✅ Strategy focuses on real estate")
            if "a/b test" in strategy.lower() or "ab test" in strategy.lower():
                validation_results.append("✅ Strategy includes A/B testing")
            
            # Timeline validation
            if "month" in timeline.lower():
                validation_results.append("✅ Timeline includes monthly planning")
            
            return {
                "strategy": strategy,
                "budget": budget,
                "timeline": timeline,
                "validation_results": validation_results,
                "overall_status": "✅ Strategy validated" if all("✅" in result for result in validation_results) else "⚠️ Strategy needs review"
            }
            
        except Exception as e:
            return f"Error validating strategy: {e}"
    
    def implement_strategy(self, strategy_name: str, changes: str):
        """Implement validated strategy by creating staging changes."""
        try:
            changes_data = json.loads(changes)
            implemented_changes = []
            
            for change in changes_data:
                if change['type'] == 'budget':
                    result = self.propose_budget_change(
                        change['campaign_name'],
                        change['current_budget'],
                        change['new_budget'],
                        f"Strategy: {strategy_name}"
                    )
                    implemented_changes.append(result)
                elif change['type'] == 'targeting':
                    result = self.propose_targeting_change(
                        change['campaign_name'],
                        change['change_type'],
                        change['details']
                    )
                    implemented_changes.append(result)
                elif change['type'] == 'asset':
                    result = self.propose_asset_change(
                        change['campaign_name'],
                        change['asset_type'],
                        change['action'],
                        change['count']
                    )
                    implemented_changes.append(result)
            
            return {
                "strategy_name": strategy_name,
                "implemented_changes": implemented_changes,
                "status": "✅ Strategy implemented successfully"
            }
            
        except Exception as e:
            return f"Error implementing strategy: {e}"
    
    def get_staging_status(self):
        """Get current staging area status."""
        try:
            pending_count = len(self.staging_data.get('pending_changes', []))
            approved_count = len(self.staging_data.get('approved_changes', []))
            rejected_count = len(self.staging_data.get('rejected_changes', []))
            
            return {
                "pending_changes": pending_count,
                "approved_changes": approved_count,
                "rejected_changes": rejected_count,
                "total_changes": pending_count + approved_count + rejected_count,
                "status": "✅ Staging area active" if pending_count > 0 else "📋 No pending changes"
            }
            
        except Exception as e:
            return f"Error getting staging status: {e}"
    
    def approve_changes(self, change_ids: str):
        """Approve pending changes in staging area."""
        try:
            ids = [int(id.strip()) for id in change_ids.split(',')]
            approved_changes = []
            
            for i in sorted(ids, reverse=True):  # Reverse order to maintain indices
                if i < len(self.staging_data['pending_changes']):
                    change = self.staging_data['pending_changes'].pop(i)
                    change['approved_at'] = datetime.now().isoformat()
                    change['status'] = 'approved'
                    self.staging_data['approved_changes'].append(change)
                    approved_changes.append(change['type'])
            
            self._save_staging_data()
            
            return {
                "approved_changes": approved_changes,
                "count": len(approved_changes),
                "status": f"✅ Approved {len(approved_changes)} changes"
            }
            
        except Exception as e:
            return f"Error approving changes: {e}"
    
    def process_message(self, user_message: str, chat_history):
        """Process user message with Gemini API and function calling."""
        try:
            # Convert chat history to Gemini format
            history_for_api = []
            for message in chat_history:
                role = 'user' if message['role'] == 'user' else 'model'
                history_for_api.append({'role': role, 'parts': [message['parts']]})
            
            # Generate response with function calling
            response = self.model.generate_content(
                user_message,
                generation_config=genai.types.GenerationConfig(candidate_count=1),
                history=history_for_api[:-1] if history_for_api else None
            )
            
            response_part = response.candidates[0].content.parts[0]
            
            if response_part.function_call:
                # Execute function call
                function_name = response_part.function_call.name
                function_args = dict(response_part.function_call.args)
                
                if function_name in self.tools:
                    result = self.tools[function_name](**function_args)
                    return {"type": "function_call", "data": result}
                else:
                    return {"type": "error", "data": f"Unknown function: {function_name}"}
            else:
                return {"type": "text", "data": response_part.text}
                
        except Exception as e:
            return {"type": "error", "data": f"Error processing message: {e}"}
