from __future__ import annotations

from datetime import date
import calendar
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_command_center_view(
    ads_data: Mapping[str, Any],
    analytics_data: Mapping[str, Any],
    crm_data: Mapping[str, Any],
) -> None:
    """
    Render the AI Ads Command Center dashboard.

    Assumptions:
    - ads_data follows the structure described in DATA_SOURCES_REFERENCE.md and contains:
        - Optional top-level aggregates: 'daily' and 'cumulative'
        - Campaigns under 'campaigns' (list or dict), each with 'config' and 'cumulative'
    - analytics_data contains 'summary' with 'total_sessions' for the last 30 days.
    - crm_data contains 'leads' with:
        - 'records_by_source' (e.g., {'Google Ads': <int>})
        - 'records_by_status' (e.g., {'Qualify': <int>, 'Pending': <int>, 'Closed': <int>})
        - Optional daily breakdowns like 'daily_by_source' and 'daily_by_status'.
    - ROAS calculation uses an average home price of $1,500,000 and a 2.5% commission.

    The function defines a helper `calculate_performance_status(campaign)` and then renders:
    1) Executive KPI Header
    2) AI System Status
    3) Full Funnel Performance (Last 30 Days)
    4) Campaign Deep Dive Table
    """

    # -------------------------------
    # Helper: Determine performance status for a single campaign
    # -------------------------------
    def calculate_performance_status(campaign: Mapping[str, Any]) -> str:
        """
        Determine a simple performance status for a given campaign using pacing and efficiency.

        Pacing:
            Compare cumulative.total_conversions against config.goal_conversions
            relative to month elapsed fraction.

        Efficiency:
            Compare cumulative.avg_cpl against config.goal_cpl.

        Returns:
            One of: "🟢 Beating Expectations", "🔵 On Track", "🟡 Lagging", "🔴 Sucking"
        """
        config: Mapping[str, Any] = campaign.get("config", {}) or {}
        cumulative: Mapping[str, Any] = campaign.get("cumulative", {}) or {}

        goal_conversions: float = float(config.get("goal_conversions", 0) or 0)
        goal_cpl: float = float(config.get("goal_cpl", 0) or 0)
        actual_conversions: float = float(cumulative.get("total_conversions", 0) or 0)
        avg_cpl: float = float(cumulative.get("avg_cpl", 0) or 0)

        # Month elapsed ratio (e.g., on the 15th of a 30-day month -> 0.5)
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        month_elapsed_ratio = max(0.0, min(1.0, today.day / float(days_in_month)))

        # Expected conversions so far if pacing to goal across the month
        expected_conversions_so_far = goal_conversions * month_elapsed_ratio

        # Compute pacing and efficiency conditions with guards
        pacing_ratio = (
            (actual_conversions / expected_conversions_so_far)
            if expected_conversions_so_far > 0
            else None
        )

        # Efficiency comparisons (lower CPL is better).
        # We'll compare directly to goal_cpl with tolerances.
        has_efficiency_target = goal_cpl > 0 and avg_cpl > 0

        # Decision tree with practical thresholds:
        # - Beating: >= 110% pacing and <= 90% goal CPL
        # - On Track: >= 90% pacing and <= 110% goal CPL
        # - Lagging: >= 60% pacing OR <= 125% goal CPL
        # - Else: Sucking
        beating = (
            (pacing_ratio is not None and pacing_ratio >= 1.10)
            and (has_efficiency_target and avg_cpl <= goal_cpl * 0.90)
        )
        on_track = (
            (pacing_ratio is not None and pacing_ratio >= 0.90)
            and (has_efficiency_target and avg_cpl <= goal_cpl * 1.10)
        )
        lagging = (
            (pacing_ratio is not None and pacing_ratio >= 0.60)
            or (has_efficiency_target and avg_cpl <= goal_cpl * 1.25)
        )

        if beating:
            return "🟢 Beating Expectations"
        if on_track:
            return "🔵 On Track"
        if lagging:
            return "🟡 Lagging"
        return "🔴 Sucking"

    # -------------------------------
    # Internal helpers for safe extraction and aggregation
    # -------------------------------
    def _iter_campaigns(data: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        campaigns = data.get("campaigns")
        if campaigns is None:
            return []
        if isinstance(campaigns, dict):
            return campaigns.values()
        if isinstance(campaigns, list):
            return campaigns
        return []

    def _sum_campaign_metric(metric_key: str, scope: str = "cumulative") -> float:
        total_value: float = 0.0
        for c in _iter_campaigns(ads_data):
            scope_data = c.get(scope, {}) or {}
            total_value += float(scope_data.get(metric_key, 0) or 0)
        return total_value

    def _get_ads_topline_daily() -> Mapping[str, float]:
        daily = ads_data.get("daily", {}) or {}
        # Fallback to summing campaigns' daily metrics if needed
        cost = float(daily.get("cost", 0) or 0)
        conversions = float(daily.get("conversions", 0) or 0)
        if cost == 0 and conversions == 0:
            cost = _sum_campaign_metric("cost", scope="daily")
            conversions = _sum_campaign_metric("conversions", scope="daily")
        return {"cost": float(cost), "conversions": float(conversions)}

    def _get_ads_topline_cumulative() -> Mapping[str, float]:
        cumulative = ads_data.get("cumulative", {}) or {}
        total_cost = float(cumulative.get("total_cost", 0) or 0)
        total_conversions = float(cumulative.get("total_conversions", 0) or 0)
        impressions = float(cumulative.get("impressions", 0) or 0)
        clicks = float(cumulative.get("clicks", 0) or 0)

        # Fallback to summing campaigns if not present
        if total_cost == 0 and total_conversions == 0 and impressions == 0 and clicks == 0:
            total_cost = _sum_campaign_metric("total_cost", scope="cumulative")
            total_conversions = _sum_campaign_metric("total_conversions", scope="cumulative")
            impressions = _sum_campaign_metric("impressions", scope="cumulative")
            clicks = _sum_campaign_metric("clicks", scope="cumulative")

        # Compute MTD average CPL if not provided
        avg_cpl = float(cumulative.get("avg_cpl", 0) or 0)
        if avg_cpl == 0 and total_conversions > 0:
            avg_cpl = total_cost / total_conversions

        return {
            "total_cost": float(total_cost),
            "total_conversions": float(total_conversions),
            "impressions": float(impressions),
            "clicks": float(clicks),
            "avg_cpl": float(avg_cpl),
        }

    def _fmt_currency(value: Optional[float]) -> str:
        if value is None:
            return "—"
        return f"${value:,.0f}"

    def _fmt_currency_precise(value: Optional[float], decimals: int = 2) -> str:
        if value is None:
            return "—"
        return f"${value:,.{decimals}f}"

    def _fmt_int(value: Optional[Union[int, float]]) -> str:
        if value is None:
            return "—"
        try:
            return f"{int(round(float(value))):,}"
        except Exception:
            return "—"

    def _fmt_ratio(value: Optional[float]) -> str:
        if value is None:
            return "—"
        return f"{value:.2f}x"

    # -------------------------------
    # Pull top-line metrics
    # -------------------------------
    ads_daily = _get_ads_topline_daily()
    ads_cum = _get_ads_topline_cumulative()

    daily_spend = float(ads_daily["cost"])
    daily_conversions = float(ads_daily["conversions"])
    mtd_spend = float(ads_cum["total_cost"])
    mtd_conversions = float(ads_cum["total_conversions"])
    mtd_avg_cpl = float(ads_cum["avg_cpl"])
    daily_cpl = (daily_spend / daily_conversions) if daily_conversions > 0 else None

    leads_data = (crm_data.get("leads", {}) or {})
    mtd_crm_leads_ads = int((leads_data.get("records_by_source", {}) or {}).get("Google Ads", 0) or 0)
    daily_crm_leads_ads = int(
        ((leads_data.get("daily_by_source", {}) or {}).get("Google Ads", 0) or 0)
    )

    # ROAS calculation assumption
    avg_home_price = 1_500_000
    commission_rate = 0.025

    mtd_closed = int((leads_data.get("records_by_status", {}) or {}).get("Closed", 0) or 0)
    mtd_revenue = mtd_closed * avg_home_price * commission_rate
    mtd_roas = (mtd_revenue / mtd_spend) if mtd_spend > 0 else None

    daily_closed = int(((leads_data.get("daily_by_status", {}) or {}).get("Closed", 0) or 0))
    daily_revenue = daily_closed * avg_home_price * commission_rate
    daily_roas = (daily_revenue / daily_spend) if daily_spend > 0 and daily_revenue > 0 else None

    # -------------------------------
    # Dashboard Title
    # -------------------------------
    st.title("AI Ads Command Center")

    # -------------------------------
    # Module 1: Executive KPI Header
    # -------------------------------
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Ad Spend",
            value=_fmt_currency(daily_spend),
            delta=f"MTD: {_fmt_currency(mtd_spend)}",
        )
    with col2:
        st.metric(
            label="Primary Leads",
            value=_fmt_int(daily_conversions),
            delta=f"MTD: {_fmt_int(mtd_conversions)}",
        )
    with col3:
        st.metric(
            label="Cost Per Lead (CPL)",
            value=_fmt_currency(daily_cpl),
            delta=f"MTD: {_fmt_currency(mtd_avg_cpl)}",
        )
    with col4:
        st.metric(
            label="New CRM Leads (from Ads)",
            value=_fmt_int(daily_crm_leads_ads),
            delta=f"MTD: {_fmt_int(mtd_crm_leads_ads)}",
        )
    with col5:
        st.metric(
            label="Estimated ROAS",
            value=_fmt_ratio(daily_roas if daily_roas is not None else mtd_roas),
            delta=f"MTD: {_fmt_ratio(mtd_roas)}",
        )

    # -------------------------------
    # Module 2: AI System Status
    # -------------------------------
    with st.expander("AI System Status", expanded=True):
        # Compute campaign statuses
        campaign_statuses: List[Dict[str, str]] = []
        for campaign in _iter_campaigns(ads_data):
            cfg = campaign.get("config", {}) or {}
            name = str(cfg.get("name", "Unnamed Campaign"))
            status = calculate_performance_status(campaign)
            campaign_statuses.append({"name": name, "status": status})

        any_bad = any(s["status"].startswith("🔴") for s in campaign_statuses)
        if any_bad:
            st.error("INTERVENTION REQUIRED")
        else:
            st.success("NOMINAL")

        # Detail rows
        if campaign_statuses:
            status_df = pd.DataFrame(campaign_statuses)
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.info("No campaigns found.")

        # Placeholders for ops surface
        st.markdown("**Active Guardrails**")
        st.write("- Budget caps; Max CPL guardrail; Auto-pausing underperformers")
        st.markdown("**Planned Changes**")
        st.write("- Creative rotation; Bid strategy tests; Audience expansion")
        st.markdown("**Lag & Pacing Alerts**")
        st.write("- Alerts fire if pacing < 80% of expected or CPL > 125% of goal")

    # -------------------------------
    # Module 3: Full Funnel Performance (Last 30 Days)
    # -------------------------------
    st.subheader("Full Funnel Performance (Last 30 Days)")

    total_impressions = float(ads_cum.get("impressions", 0) or 0)
    total_clicks = float(ads_cum.get("clicks", 0) or 0)
    total_sessions = float((analytics_data.get("summary", {}) or {}).get("total_sessions", 0) or 0)
    total_primary_leads = float(mtd_conversions or 0)
    total_crm_leads_ads = float(mtd_crm_leads_ads or 0)
    total_appointments = float((leads_data.get("records_by_status", {}) or {}).get("Qualify", 0) or 0)
    total_under_contract = float((leads_data.get("records_by_status", {}) or {}).get("Pending", 0) or 0)
    total_closed = float((leads_data.get("records_by_status", {}) or {}).get("Closed", 0) or 0)

    funnel_labels = [
        "Ad Impressions",
        "Clicks",
        "Website Sessions",
        "Primary Leads (Ads)",
        "New CRM Leads (from Ads)",
        "Appointments Set",
        "Under Contract",
        "Closed Deals",
    ]
    funnel_values = [
        max(0, total_impressions),
        max(0, total_clicks),
        max(0, total_sessions),
        max(0, total_primary_leads),
        max(0, total_crm_leads_ads),
        max(0, total_appointments),
        max(0, total_under_contract),
        max(0, total_closed),
    ]

    funnel_fig = go.Figure(
        go.Funnel(
            y=funnel_labels,
            x=funnel_values,
            textinfo="value+percent initial",
            orientation="h",
        )
    )
    funnel_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380)
    st.plotly_chart(funnel_fig, use_container_width=True)

    # -------------------------------
    # Module 4: Campaign Deep Dive Table
    # -------------------------------
    st.subheader("Campaign Deep Dive")

    rows: List[Dict[str, Any]] = []
    for campaign in _iter_campaigns(ads_data):
        config = campaign.get("config", {}) or {}
        cumulative = campaign.get("cumulative", {}) or {}

        spend_mtd = float(cumulative.get("total_cost", 0) or 0)
        leads_mtd = float(cumulative.get("total_conversions", 0) or 0)
        cpl_mtd = float(cumulative.get("avg_cpl", 0) or 0)
        if cpl_mtd == 0 and leads_mtd > 0:
            cpl_mtd = spend_mtd / leads_mtd

        rows.append(
            {
                "Performance Status": calculate_performance_status(campaign),
                "Campaign Name": str(config.get("name", "Unnamed Campaign")),
                "Current Phase": str(config.get("phase", "Unknown")),
                "Spend (MTD)": spend_mtd,
                "Leads (MTD)": int(round(leads_mtd)),
                "CPL (MTD)": cpl_mtd,
                "Phase Goal": int(round(float(config.get("goal_conversions", 0) or 0))),
            }
        )

    if rows:
        df = pd.DataFrame(rows)
        # Sort by highest spend to float top-impact campaigns
        df = df.sort_values(by=["Spend (MTD)"], ascending=False)

        # Display with basic formatting
        st.dataframe(
            df.style.format(
                {
                    "Spend (MTD)": lambda v: _fmt_currency(float(v)),
                    "Leads (MTD)": lambda v: _fmt_int(int(v)),
                    "CPL (MTD)": lambda v: _fmt_currency_precise(float(v), decimals=2),
                    "Phase Goal": lambda v: _fmt_int(int(v)),
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No campaign data available for deep dive.")
