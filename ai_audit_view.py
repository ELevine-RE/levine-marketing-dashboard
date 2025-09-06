"""
AI Audit View - Comprehensive AI Logic and Decision Tracking

This module provides a comprehensive audit view of the AI system's:
- Decision-making processes and reasoning
- Action triggers and conditions
- Performance metrics and analysis
- Risk assessment and mitigation
- Learning patterns and optimization
- Performance impact analysis
- Risk assessment and mitigation
- Learning and optimization patterns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys
import logging
import traceback

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AIAuditView:
    """Renders a comprehensive AI Audit page."""

    def __init__(self):
        # Initialize with mock data for demonstration
        self.audit_data = self._generate_mock_audit_data()

    def _generate_mock_audit_data(self):
        """Generate comprehensive mock audit data"""
        return {
            "decision_logs": self._generate_mock_decision_logs(),
            "action_triggers": self._generate_mock_action_triggers(),
            "performance_analysis": self._generate_mock_performance_metrics(),
            "risk_assessments": self._generate_mock_risk_assessment(),
            "learning_patterns": self._generate_mock_learning_patterns(),
            "optimization_recommendations": self._generate_mock_optimization_recommendations()
        }

    def _generate_mock_decision_logs(self):
        """Generate mock decision logs"""
        return [
            {
                "timestamp": "2025-09-05 10:30:00",
                "decision_type": "Budget Adjustment",
                "campaign": "Levine Real Estate - Search",
                "ai_reasoning": "CTR dropped 15% over 3 days, CPC increased 8%. Budget reallocation needed to maintain ROAS target of 4.2x.",
                "decision": "APPROVED: Reduce daily budget by 20%",
                "confidence": 0.87,
                "risk_level": "Medium",
                "expected_impact": "Maintain ROAS while reducing spend",
                "data_points": {
                    "ctr_change": "-15%",
                    "cpc_change": "+8%",
                    "roas_target": "4.2x",
                    "current_roas": "3.8x"
                }
            },
            {
                "timestamp": "2025-09-05 09:15:00",
                "decision_type": "Keyword Optimization",
                "campaign": "Levine Real Estate - Display",
                "ai_reasoning": "Negative keywords 'apartment' and 'rental' showing high volume but low conversion. Removing to improve quality score.",
                "decision": "EXECUTED: Added negative keywords",
                "confidence": 0.92,
                "risk_level": "Low",
                "expected_impact": "Improve quality score and reduce irrelevant traffic",
                "data_points": {
                    "impressions": "12,450",
                    "conversions": "3",
                    "conversion_rate": "0.024%",
                    "quality_score": "6/10"
                }
            },
            {
                "timestamp": "2025-09-05 08:45:00",
                "decision_type": "Bid Adjustment",
                "campaign": "Levine Real Estate - Search",
                "ai_reasoning": "Mobile performance 40% better than desktop. Increase mobile bids by 25% to capture more high-value traffic.",
                "decision": "APPROVED: Mobile bid +25%",
                "confidence": 0.89,
                "risk_level": "Low",
                "expected_impact": "Increase mobile traffic and conversions",
                "data_points": {
                    "mobile_ctr": "4.2%",
                    "desktop_ctr": "3.0%",
                    "mobile_conversion_rate": "2.8%",
                    "desktop_conversion_rate": "2.1%"
                }
            }
        ]

    def _generate_mock_action_triggers(self):
        """Generate mock action triggers"""
        return [
            {
                "trigger_condition": "CTR drops below 2% for 3 consecutive days",
                "action": "Pause underperforming keywords",
                "success_rate": "78%",
                "frequency": "Weekly",
                "impact": "Medium"
            },
            {
                "trigger_condition": "CPC increases by 20% or more",
                "action": "Review and adjust bids",
                "success_rate": "85%",
                "frequency": "Daily",
                "impact": "High"
            },
            {
                "trigger_condition": "Quality Score drops below 5",
                "action": "Optimize ad relevance and landing page",
                "success_rate": "92%",
                "frequency": "As needed",
                "impact": "High"
            }
        ]

    def _generate_mock_performance_metrics(self):
        """Generate mock performance metrics"""
        return [
            {
                "metric": "Decision Accuracy",
                "current": 87.3,
                "target": 90.0,
                "trend": "+2.1%",
                "ai_insight": "Decision accuracy improving due to better data quality and enhanced ML models"
            },
            {
                "metric": "Action Success Rate",
                "current": 82.1,
                "target": 85.0,
                "trend": "+1.8%",
                "ai_insight": "Action success rate trending upward with improved trigger conditions"
            },
            {
                "metric": "ROI Impact",
                "current": 24.7,
                "target": 25.0,
                "trend": "+3.2%",
                "ai_insight": "ROI impact exceeding expectations due to optimized budget allocation"
            },
            {
                "metric": "Risk Mitigation",
                "current": 94.2,
                "target": 95.0,
                "trend": "+0.8%",
                "ai_insight": "Risk mitigation effectiveness high due to proactive monitoring"
            },
            {
                "metric": "Learning Efficiency",
                "current": 76.8,
                "target": 80.0,
                "trend": "+2.5%",
                "ai_insight": "Learning efficiency improving with more diverse training data"
            }
        ]

    def _generate_mock_risk_assessment(self):
        """Generate mock risk assessments"""
        return [
            {
                "risk_type": "Budget Overspend",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Daily budget monitoring and alerts",
                "status": "Monitored"
            },
            {
                "risk_type": "Quality Score Drop",
                "probability": "Low",
                "impact": "Medium",
                "mitigation": "Regular ad copy and landing page optimization",
                "status": "Controlled"
            },
            {
                "risk_type": "Competitor Activity",
                "probability": "High",
                "impact": "Medium",
                "mitigation": "Competitive analysis and bid adjustments",
                "status": "Active"
            }
        ]

    def _generate_mock_learning_patterns(self):
        """Generate mock learning patterns"""
        return [
            {
                "pattern": "Weekend Performance",
                "insight": "Mobile traffic increases 35% on weekends",
                "action": "Increase weekend mobile bids",
                "effectiveness": "High"
            },
            {
                "pattern": "Time of Day",
                "insight": "Peak conversion hours: 9-11 AM and 7-9 PM",
                "action": "Bid adjustments for peak hours",
                "effectiveness": "Medium"
            },
            {
                "pattern": "Seasonal Trends",
                "insight": "Real estate searches peak in spring months",
                "action": "Budget allocation for seasonal trends",
                "effectiveness": "High"
            }
        ]

    def _generate_mock_optimization_recommendations(self):
        """Generate mock optimization recommendations"""
        return [
            {
                "recommendation": "Expand high-performing keyword list",
                "priority": "High",
                "expected_impact": "Increase traffic by 25%",
                "implementation": "Add 15 new keywords with similar intent",
                "timeline": "1 week"
            },
            {
                "recommendation": "Optimize landing page for mobile",
                "priority": "Medium",
                "expected_impact": "Improve conversion rate by 15%",
                "implementation": "Mobile-first design updates",
                "timeline": "2 weeks"
            },
            {
                "recommendation": "Implement dynamic remarketing",
                "priority": "High",
                "expected_impact": "Increase ROAS by 30%",
                "implementation": "Set up remarketing audiences and campaigns",
                "timeline": "1 week"
            }
        ]

    def render_ai_audit_page(self):
        """Render the complete AI audit page with comprehensive error handling"""
        try:
            st.title("🤖 AI Audit Dashboard")
            st.markdown("**Comprehensive AI Logic, Decision Process, and Action Tracking**")
            
            # Create tabs for different audit views
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🧠 Decision Logs", "⚡ Action Triggers", "📊 Performance Analysis", 
                "🛡️ Risk Assessment", "🎓 Learning Patterns", "🎯 Recommendations"
            ])
            
            with tab1:
                self._render_decision_logs()
            
            with tab2:
                self._render_action_triggers()
            
            with tab3:
                self._render_performance_analysis()
            
            with tab4:
                self._render_risk_assessment()
            
            with tab5:
                self._render_learning_patterns()
            
            with tab6:
                self._render_optimization_recommendations()
                
        except Exception as e:
            # Log the error to app.log
            error_msg = f"AI Audit Page Error: {str(e)}\nTraceback: {traceback.format_exc()}"
            logging.error(error_msg)
            
            # Show user-friendly error message
            st.error("🚨 AI Audit page encountered an error. Check app.log for details.")
            st.code(f"Error: {str(e)}")
            
            # Show fallback content
            st.info("🔄 Loading simplified AI audit view...")
            self._render_fallback_audit()

    def _render_fallback_audit(self):
        """Render simplified fallback audit view when main view fails"""
        st.header("🤖 AI Audit - Simplified View")
        st.info("This is a simplified version of the AI audit. Full functionality will be restored after error resolution.")
        
        # Show basic metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Decision Accuracy", "87.3%", "+2.1%")
        with col2:
            st.metric("Action Success Rate", "82.1%", "+1.8%")
        with col3:
            st.metric("ROI Impact", "24.7%", "+3.2%")
        
        # Show recent decisions
        st.subheader("Recent AI Decisions")
        decisions = self.audit_data["decision_logs"][:3]  # Show only first 3
        for decision in decisions:
            with st.expander(f"{decision['decision_type']} - {decision['campaign']}"):
                st.write(f"**Reasoning:** {decision['ai_reasoning']}")
                st.write(f"**Decision:** {decision['decision']}")
                st.write(f"**Confidence:** {decision['confidence']:.1%}")

    def _render_decision_logs(self):
        """Render AI decision logs with reasoning"""
        try:
            st.header("🧠 AI Decision Logs")
            st.markdown("**Real-time AI thought processes and decision reasoning**")
            
            decisions_df = pd.DataFrame(self.audit_data["decision_logs"])
            
            # Decision overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Decisions", len(decisions_df))
            with col2:
                approved = len(decisions_df[decisions_df['decision'].str.contains('APPROVED')])
                st.metric("Approved", approved, f"{approved/len(decisions_df)*100:.1f}%")
            with col3:
                avg_confidence = decisions_df['confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            with col4:
                high_risk = len(decisions_df[decisions_df['risk_level'] == 'Critical'])
                st.metric("Critical Risks", high_risk)
            
            # Decision timeline
            decisions_df['timestamp_dt'] = pd.to_datetime(decisions_df['timestamp'])
            decisions_df['end_time'] = decisions_df['timestamp_dt'] + pd.Timedelta(hours=1)
            
            fig = px.timeline(
                decisions_df, 
                x_start="timestamp_dt", 
                x_end="end_time",
                y="decision_type",
                color="risk_level",
                title="AI Decision Timeline",
                color_discrete_map={
                    "Very Low": "green",
                    "Low": "lightgreen", 
                    "Medium": "orange",
                    "High": "red",
                    "Critical": "darkred"
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed decision log
            st.subheader("📋 Detailed Decision Log")
            for idx, decision in enumerate(decisions_df.to_dict('records')):
                with st.expander(f"Decision {idx+1}: {decision['decision_type']} - {decision['campaign']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🤖 AI Reasoning:**")
                        st.info(decision['ai_reasoning'])
                        
                        st.markdown("**📊 Data Points:**")
                        for key, value in decision['data_points'].items():
                            st.write(f"• {key.replace('_', ' ').title()}: {value}")
                    
                    with col2:
                        st.markdown("**🎯 Decision:**")
                        if "APPROVED" in decision['decision']:
                            st.success(decision['decision'])
                        elif "EXECUTED" in decision['decision']:
                            st.warning(decision['decision'])
                        else:
                            st.error(decision['decision'])
                        
                        st.markdown("**📈 Expected Impact:**")
                        st.info(decision['expected_impact'])
                        
                        # Confidence and risk indicators
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Confidence", f"{decision['confidence']:.1%}")
                        with col_b:
                            risk_color = {
                                "Very Low": "🟢", "Low": "🟡", "Medium": "🟠", 
                                "High": "🔴", "Critical": "🚨"
                            }
                            st.metric("Risk Level", f"{risk_color.get(decision['risk_level'], '⚪')} {decision['risk_level']}")
                        
        except Exception as e:
            logging.error(f"Decision Logs Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading decision logs: {str(e)}")
            st.info("🔄 Showing simplified decision view...")
            
            # Show simplified decision list
            decisions = self.audit_data["decision_logs"][:3]
            for decision in decisions:
                with st.expander(f"{decision['decision_type']} - {decision['campaign']}"):
                    st.write(f"**Reasoning:** {decision['ai_reasoning']}")
                    st.write(f"**Decision:** {decision['decision']}")
                    st.write(f"**Confidence:** {decision['confidence']:.1%}")

    def _render_action_triggers(self):
        """Render AI action triggers and conditions"""
        try:
            st.header("⚡ AI Action Triggers")
            st.markdown("**Conditions and logic that trigger AI actions**")
            
            triggers_df = pd.DataFrame(self.audit_data["action_triggers"])
            
            # Trigger overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Triggers", len(triggers_df))
            with col2:
                avg_success = triggers_df['success_rate'].str.rstrip('%').astype(float).mean()
                st.metric("Avg Success Rate", f"{avg_success:.1f}%")
            with col3:
                high_impact = len(triggers_df[triggers_df['impact'] == 'High'])
                st.metric("High Impact Triggers", high_impact)
            
            # Trigger details
            st.subheader("📋 Trigger Details")
            for idx, trigger in enumerate(triggers_df.to_dict('records')):
                with st.expander(f"Trigger {idx+1}: {trigger['trigger_condition']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎯 Action:**")
                        st.info(trigger['action'])
                        
                        st.markdown("**📅 Frequency:**")
                        st.write(trigger['frequency'])
                    
                    with col2:
                        st.markdown("**📊 Success Rate:**")
                        success_rate = float(trigger['success_rate'].rstrip('%'))
                        if success_rate >= 80:
                            st.success(f"{trigger['success_rate']}")
                        elif success_rate >= 60:
                            st.warning(f"{trigger['success_rate']}")
                        else:
                            st.error(f"{trigger['success_rate']}")
                        
                        st.markdown("**💥 Impact:**")
                        if trigger['impact'] == 'High':
                            st.error(trigger['impact'])
                        elif trigger['impact'] == 'Medium':
                            st.warning(trigger['impact'])
                        else:
                            st.success(trigger['impact'])
                            
        except Exception as e:
            logging.error(f"Action Triggers Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading action triggers: {str(e)}")

    def _render_performance_analysis(self):
        """Render AI performance analysis"""
        try:
            st.header("📊 AI Performance Analysis")
            st.markdown("**AI system performance metrics and insights**")
            
            perf_df = pd.DataFrame(self.audit_data["performance_analysis"])
            
            # Performance metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            metrics = ["Decision Accuracy", "Action Success Rate", "ROI Impact", "Risk Mitigation", "Learning Efficiency"]
            
            for i, metric in enumerate(metrics):
                with [col1, col2, col3, col4, col5][i]:
                    row = perf_df[perf_df['metric'] == metric].iloc[0]
                    st.metric(
                        metric, 
                        f"{row['current']:.1f}%",
                        delta=row['trend']
                    )
            
            # Performance trends - use simple bar chart instead of complex subplots
            metrics_data = perf_df.set_index('metric')
            
            # Create individual gauge charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Decision Accuracy Gauge
                fig1 = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics_data.loc["Decision Accuracy", "current"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Decision Accuracy"},
                    delta={'reference': metrics_data.loc["Decision Accuracy", "target"]},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, 85], 'color': "lightgray"},
                                    {'range': [85, 100], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 90}}
                ))
                fig1.update_layout(height=300)
                st.plotly_chart(fig1, use_container_width=True)
                
                # Action Success Rate Gauge
                fig2 = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics_data.loc["Action Success Rate", "current"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Action Success Rate"},
                    delta={'reference': metrics_data.loc["Action Success Rate", "target"]},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkgreen"},
                           'steps': [{'range': [0, 80], 'color': "lightgray"},
                                    {'range': [80, 100], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 90}}
                ))
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # ROI Impact Gauge
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics_data.loc["ROI Impact", "current"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "ROI Impact"},
                    delta={'reference': metrics_data.loc["ROI Impact", "target"]},
                    gauge={'axis': {'range': [None, 30]},
                           'bar': {'color': "darkorange"},
                           'steps': [{'range': [0, 20], 'color': "lightgray"},
                                    {'range': [20, 30], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 25}}
                ))
                fig3.update_layout(height=300)
                st.plotly_chart(fig3, use_container_width=True)
                
                # Risk Mitigation Gauge
                fig4 = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=metrics_data.loc["Risk Mitigation", "current"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Risk Mitigation"},
                    delta={'reference': metrics_data.loc["Risk Mitigation", "target"]},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkred"},
                           'steps': [{'range': [0, 90], 'color': "lightgray"},
                                    {'range': [90, 100], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 95}}
                ))
                fig4.update_layout(height=300)
                st.plotly_chart(fig4, use_container_width=True)
            
            # AI Insights
            st.subheader("🤖 AI Insights")
            for _, row in perf_df.iterrows():
                with st.expander(f"Insight: {row['metric']}"):
                    st.info(row['ai_insight'])
                    
        except Exception as e:
            logging.error(f"Performance Analysis Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading performance analysis: {str(e)}")
            st.info("🔄 Showing simplified performance metrics...")
            
            # Show simplified metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Decision Accuracy", "87.3%", "+2.1%")
            with col2:
                st.metric("Action Success Rate", "82.1%", "+1.8%")
            with col3:
                st.metric("ROI Impact", "24.7%", "+3.2%")

    def _render_risk_assessment(self):
        """Render AI risk assessment"""
        try:
            st.header("🛡️ AI Risk Assessment")
            st.markdown("**Risk analysis and mitigation strategies**")
            
            risks_df = pd.DataFrame(self.audit_data["risk_assessments"])
            
            # Risk overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Risks", len(risks_df))
            with col2:
                high_prob = len(risks_df[risks_df['probability'] == 'High'])
                st.metric("High Probability", high_prob)
            with col3:
                high_impact = len(risks_df[risks_df['impact'] == 'High'])
                st.metric("High Impact", high_impact)
            with col4:
                monitored = len(risks_df[risks_df['status'] == 'Monitored'])
                st.metric("Monitored", monitored)
            
            # Risk details
            st.subheader("📋 Risk Details")
            for idx, risk in enumerate(risks_df.to_dict('records')):
                with st.expander(f"Risk {idx+1}: {risk['risk_type']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📊 Risk Level:**")
                        prob_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                        impact_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                        
                        st.write(f"**Probability:** {prob_color.get(risk['probability'], '⚪')} {risk['probability']}")
                        st.write(f"**Impact:** {impact_color.get(risk['impact'], '⚪')} {risk['impact']}")
                    
                    with col2:
                        st.markdown("**🛡️ Mitigation:**")
                        st.info(risk['mitigation'])
                        
                        st.markdown("**📈 Status:**")
                        if risk['status'] == 'Controlled':
                            st.success(risk['status'])
                        elif risk['status'] == 'Monitored':
                            st.warning(risk['status'])
                        else:
                            st.info(risk['status'])
                            
        except Exception as e:
            logging.error(f"Risk Assessment Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading risk assessment: {str(e)}")

    def _render_learning_patterns(self):
        """Render AI learning patterns"""
        try:
            st.header("🎓 AI Learning Patterns")
            st.markdown("**Insights into how the AI system learns and adapts**")
            
            patterns_df = pd.DataFrame(self.audit_data["learning_patterns"])
            
            # Pattern overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Patterns", len(patterns_df))
            with col2:
                high_eff = len(patterns_df[patterns_df['effectiveness'] == 'High'])
                st.metric("High Effectiveness", high_eff)
            with col3:
                st.metric("Patterns Applied", len(patterns_df))
            
            # Pattern details
            st.subheader("📋 Learning Pattern Details")
            for idx, pattern in enumerate(patterns_df.to_dict('records')):
                with st.expander(f"Pattern {idx+1}: {pattern['pattern']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**💡 Insight:**")
                        st.info(pattern['insight'])
                    
                    with col2:
                        st.markdown("**🎯 Action:**")
                        st.success(pattern['action'])
                        
                        st.markdown("**📊 Effectiveness:**")
                        if pattern['effectiveness'] == 'High':
                            st.success(pattern['effectiveness'])
                        elif pattern['effectiveness'] == 'Medium':
                            st.warning(pattern['effectiveness'])
                        else:
                            st.info(pattern['effectiveness'])
                            
        except Exception as e:
            logging.error(f"Learning Patterns Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading learning patterns: {str(e)}")

    def _render_optimization_recommendations(self):
        """Render AI optimization recommendations"""
        try:
            st.header("🎯 AI Optimization Recommendations")
            st.markdown("**Current AI-driven recommendations for campaign optimization**")
            
            recs_df = pd.DataFrame(self.audit_data["optimization_recommendations"])
            
            # Recommendation overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Recommendations", len(recs_df))
            with col2:
                high_priority = len(recs_df[recs_df['priority'] == 'High'])
                st.metric("High Priority", high_priority)
            with col3:
                st.metric("Ready to Implement", len(recs_df))
            
            # Recommendation details
            st.subheader("📋 Recommendation Details")
            for idx, rec in enumerate(recs_df.to_dict('records')):
                with st.expander(f"Recommendation {idx+1}: {rec['recommendation']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎯 Priority:**")
                        if rec['priority'] == 'High':
                            st.error(rec['priority'])
                        elif rec['priority'] == 'Medium':
                            st.warning(rec['priority'])
                        else:
                            st.info(rec['priority'])
                        
                        st.markdown("**📈 Expected Impact:**")
                        st.success(rec['expected_impact'])
                    
                    with col2:
                        st.markdown("**🔧 Implementation:**")
                        st.info(rec['implementation'])
                        
                        st.markdown("**⏰ Timeline:**")
                        st.write(rec['timeline'])
                            
        except Exception as e:
            logging.error(f"Optimization Recommendations Error: {str(e)}\nTraceback: {traceback.format_exc()}")
            st.error(f"❌ Error loading optimization recommendations: {str(e)}")