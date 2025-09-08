#!/usr/bin/env python3
"""
Generate a Google Ads strategic brief from Google Trends CSVs in the project root.

This script constructs a master DataFrame for timelines and DMA geography across all
theme folders (excluding the Analysis folder), performs:
- Campaign & Ad Group Clustering (seasonality + geography overlap)
- Market Prioritization (avg monthly volume; YoY CAGR)
- Per-theme seasonal peaks and top DMA
- Geographic deep dive: Top 5 DMAs and top themes per DMA

Outputs a markdown report at Analysis/google_ads_strategy_report.md
"""

import os
import glob
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Tuple, Set

import numpy as np
import pandas as pd


PROJECT_ROOT = "/Users/evan/Downloads/Trends"
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "Analysis")
REPORT_PATH = os.path.join(ANALYSIS_DIR, "google_ads_strategy_report.md")


def find_latest_csv(folder_path: str, pattern: str) -> str:
    paths = glob.glob(os.path.join(folder_path, pattern))
    if not paths:
        return ""
    # Sort by modification time descending; pick most recent
    paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return paths[0]


def load_timeline(theme: str, folder_path: str) -> pd.DataFrame:
    csv_path = find_latest_csv(folder_path, "multiTimeline*.csv")
    if not csv_path:
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_path, skiprows=2)
        # Expect two columns: Week and the series
        if df.empty or "Week" not in df.columns:
            return pd.DataFrame()
        value_col = [c for c in df.columns if c != "Week"]
        if not value_col:
            return pd.DataFrame()
        value_col = value_col[0]
        out = pd.DataFrame({
            "theme": theme,
            "date": pd.to_datetime(df["Week"], errors="coerce"),
            "value": pd.to_numeric(df[value_col], errors="coerce").fillna(0)
        })
        out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
        return out
    except Exception:
        return pd.DataFrame()


def load_geo(theme: str, folder_path: str) -> pd.DataFrame:
    csv_path = find_latest_csv(folder_path, "geoMap*.csv")
    if not csv_path:
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_path, skiprows=2)
        # Expect: DMA,<series>
        if df.empty:
            return pd.DataFrame()
        first_col = df.columns[0]
        second_col = df.columns[1] if len(df.columns) > 1 else None
        if not second_col:
            return pd.DataFrame()
        out = pd.DataFrame({
            "theme": theme,
            "dma": df[first_col].astype(str).str.strip(),
            "score": pd.to_numeric(df[second_col], errors="coerce").fillna(0)
        })
        out = out[out["dma"].str.len() > 0].reset_index(drop=True)
        return out
    except Exception:
        return pd.DataFrame()


def build_master_frames() -> Tuple[pd.DataFrame, pd.DataFrame]:
    time_rows: List[pd.DataFrame] = []
    geo_rows: List[pd.DataFrame] = []

    for item in os.listdir(PROJECT_ROOT):
        dir_path = os.path.join(PROJECT_ROOT, item)
        if not os.path.isdir(dir_path):
            continue
        if item == "Analysis":
            continue
        theme = item.strip()

        tdf = load_timeline(theme, dir_path)
        if not tdf.empty:
            time_rows.append(tdf)

        gdf = load_geo(theme, dir_path)
        if not gdf.empty:
            geo_rows.append(gdf)

    master_time = pd.concat(time_rows, ignore_index=True) if time_rows else pd.DataFrame(columns=["theme", "date", "value"])
    master_geo = pd.concat(geo_rows, ignore_index=True) if geo_rows else pd.DataFrame(columns=["theme", "dma", "score"])

    return master_time, master_geo


def compute_avg_monthly_volume(master_time: pd.DataFrame) -> pd.DataFrame:
    if master_time.empty:
        return pd.DataFrame(columns=["theme", "avg_monthly_index"]).set_index("theme")
    df = master_time.copy()
    df["month"] = df["date"].dt.to_period("M")
    monthly = df.groupby(["theme", "month"], as_index=False)["value"].mean()
    ranking = monthly.groupby("theme", as_index=False)["value"].mean().rename(columns={"value": "avg_monthly_index"})
    return ranking.set_index("theme")


def compute_cagr(master_time: pd.DataFrame) -> pd.Series:
    if master_time.empty:
        return pd.Series(dtype=float)
    cagr_values: Dict[str, float] = {}
    for theme, g in master_time.groupby("theme"):
        g = g.sort_values("date")
        if g["value"].sum() == 0 or len(g) < 30:
            continue
        start_date = g["date"].min()
        end_date = g["date"].max()
        years = max((end_date - start_date).days / 365.25, 0.1)
        # First and last 52 weeks means
        first_window = g.head(min(52, len(g)))
        last_window = g.tail(min(52, len(g)))
        first_mean = first_window["value"].replace(0, np.nan).mean()
        last_mean = last_window["value"].replace(0, np.nan).mean()
        if pd.isna(first_mean) or first_mean == 0 or pd.isna(last_mean):
            continue
        cagr = (last_mean / first_mean) ** (1.0 / years) - 1.0
        cagr_values[theme] = float(cagr)
    return pd.Series(cagr_values)


def week_of_year(dt: pd.Timestamp) -> int:
    try:
        return int(dt.isocalendar().week)
    except Exception:
        return int(dt.weekofyear)


def build_seasonality_vectors(master_time: pd.DataFrame) -> Dict[str, np.ndarray]:
    vectors: Dict[str, np.ndarray] = {}
    if master_time.empty:
        return vectors
    tmp = master_time.copy()
    tmp["w"] = tmp["date"].apply(week_of_year)
    for theme, g in tmp.groupby("theme"):
        week_means = g.groupby("w")["value"].mean()
        # Build vector length 53 (ISO weeks up to 53)
        vec = np.zeros(53, dtype=float)
        for w in range(1, 54):
            vec[w - 1] = float(week_means.get(w, np.nan))
        # Fill NaNs with series mean
        mean_val = np.nanmean(vec) if np.isnan(vec).any() else vec.mean() if len(vec) else 0.0
        if np.isnan(vec).any():
            vec = np.where(np.isnan(vec), mean_val, vec)
        # Normalize to relative pattern (divide by mean) to compare shapes
        if mean_val > 0:
            vec = vec / mean_val
        vectors[theme] = vec
    return vectors


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def compute_geo_sets(master_geo: pd.DataFrame, top_n: int = 15) -> Dict[str, Set[str]]:
    if master_geo.empty:
        return {}
    geo_sets: Dict[str, Set[str]] = {}
    for theme, g in master_geo.groupby("theme"):
        gg = g.sort_values("score", ascending=False).head(top_n)
        geo_sets[theme] = set(gg["dma"].astype(str).str.strip().tolist())
    return geo_sets


def pairwise_correlations(vectors: Dict[str, np.ndarray]) -> Dict[Tuple[str, str], float]:
    themes = list(vectors.keys())
    corr: Dict[Tuple[str, str], float] = {}
    for i in range(len(themes)):
        for j in range(i + 1, len(themes)):
            a = vectors[themes[i]]
            b = vectors[themes[j]]
            if a.size == 0 or b.size == 0:
                c = 0.0
            else:
                # Handle constant vectors (std=0)
                if np.allclose(a, a.mean()) or np.allclose(b, b.mean()):
                    c = 0.0
                else:
                    c = float(np.corrcoef(a, b)[0, 1])
            corr[(themes[i], themes[j])] = c
    return corr


def build_clusters(vectors: Dict[str, np.ndarray], geo_sets: Dict[str, Set[str]], corr_thresh: float = 0.5, jacc_thresh: float = 0.15) -> List[List[str]]:
    themes = list(vectors.keys())
    if not themes:
        return []
    # Build adjacency by dual thresholds on seasonality correlation and geo Jaccard
    corr = pairwise_correlations(vectors)
    adj: Dict[str, Set[str]] = {t: set() for t in themes}
    for (a, b), c in corr.items():
        jac = jaccard(geo_sets.get(a, set()), geo_sets.get(b, set()))
        if c >= corr_thresh and jac >= jacc_thresh:
            adj[a].add(b)
            adj[b].add(a)

    # Connected components
    visited: Set[str] = set()
    clusters: List[List[str]] = []
    for t in themes:
        if t in visited:
            continue
        comp: List[str] = []
        q: deque[str] = deque([t])
        visited.add(t)
        while q:
            cur = q.popleft()
            comp.append(cur)
            for nei in adj.get(cur, set()):
                if nei not in visited:
                    visited.add(nei)
                    q.append(nei)
        clusters.append(sorted(comp))

    # Sort clusters by size descending, then lexicographically
    clusters.sort(key=lambda lst: (-len(lst), [s.lower() for s in lst]))
    return clusters


def label_cluster(themes: List[str]) -> str:
    text = " ".join(themes).lower()
    luxury_terms = ["deer", "promontory", "red ledges", "glenwild", "victory", "ski"]
    general_terms = ["real estate", "park city", "heber", "kamas"]
    golf_terms = ["golf", "ranch", "glenwild", "promontory", "red ledges"]
    ski_terms = ["ski", "deer", "slope"]

    if any(term in text for term in ski_terms) and len(themes) <= 4:
        return "Campaign: Ski-In/Ski-Out & Mountain Resorts"
    if any(term in text for term in golf_terms) and len(themes) <= 5:
        return "Campaign: Golf & Gated Luxury Communities"
    if any(term in text for term in luxury_terms):
        return "Campaign: Luxury Developments"
    if any(term in text for term in general_terms):
        return "Campaign: General Real Estate"
    return "Campaign: Thematic Group"


def month_name(m: int) -> str:
    return datetime(2000, m, 1).strftime("%B")


def compute_peak_months(master_time: pd.DataFrame) -> Dict[str, List[str]]:
    peaks: Dict[str, List[str]] = {}
    if master_time.empty:
        return peaks
    df = master_time.copy()
    df["month"] = df["date"].dt.month
    monthly = df.groupby(["theme", "month"], as_index=False)["value"].mean()
    for theme, g in monthly.groupby("theme"):
        g2 = g.sort_values("value", ascending=False)
        top = g2.head(2)["month"].astype(int).tolist()
        peaks[theme] = [month_name(m) for m in top]
    return peaks


def top_dma_per_theme(master_geo: pd.DataFrame) -> Dict[str, Tuple[str, float]]:
    best: Dict[str, Tuple[str, float]] = {}
    if master_geo.empty:
        return best
    for theme, g in master_geo.groupby("theme"):
        g2 = g.sort_values("score", ascending=False)
        if not g2.empty:
            row = g2.iloc[0]
            best[theme] = (str(row["dma"]), float(row["score"]))
    return best


def top5_dmas_and_top3_themes(master_geo: pd.DataFrame) -> Tuple[List[Tuple[str, float]], Dict[str, List[Tuple[str, float]]]]:
    if master_geo.empty:
        return [], {}
    # Aggregate scores across themes per DMA
    agg = master_geo.groupby("dma", as_index=False)["score"].sum().sort_values("score", ascending=False)
    top5 = agg.head(5).reset_index(drop=True)
    top5_list = [(str(row["dma"]), float(row["score"])) for _, row in top5.iterrows()]
    # For each top DMA, select top 3 themes by that DMA's score
    result: Dict[str, List[Tuple[str, float]]] = {}
    for dma_name, _ in top5_list:
        sub = master_geo[master_geo["dma"] == dma_name]
        top_themes = sub.sort_values("score", ascending=False).groupby("theme", as_index=False).first()
        top_themes = top_themes.sort_values("score", ascending=False).head(3)
        result[dma_name] = [(str(r["theme"]), float(r["score"])) for _, r in top_themes.iterrows()]
    return top5_list, result


def format_percentage(x: float) -> str:
    try:
        return f"{x*100:.1f}%"
    except Exception:
        return "—"


def write_report(master_time: pd.DataFrame, master_geo: pd.DataFrame) -> None:
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # Section 2: Market Prioritization
    avg_monthly = compute_avg_monthly_volume(master_time)
    cagr = compute_cagr(master_time)

    top5_avg = []
    if not avg_monthly.empty:
        top5_avg = avg_monthly.sort_values("avg_monthly_index", ascending=False).head(5).reset_index().values.tolist()

    top5_cagr = []
    if not cagr.empty:
        top5_cagr = cagr.sort_values(ascending=False).head(5).reset_index().values.tolist()

    # Section 1: Clustering
    season_vectors = build_seasonality_vectors(master_time)
    geo_sets = compute_geo_sets(master_geo)
    clusters = build_clusters(season_vectors, geo_sets, corr_thresh=0.5, jacc_thresh=0.15)

    cluster_blocks: List[str] = []
    for idx, members in enumerate(clusters, 1):
        label = label_cluster(members)
        bullets = "\n".join([f"- {m}" for m in members])
        cluster_blocks.append(f"**{label}**\n{bullets}")

    # Section 3: Thematic cards
    peaks = compute_peak_months(master_time)
    top_dma = top_dma_per_theme(master_geo)
    all_themes_sorted = sorted(set(master_time["theme"].unique()) | set(master_geo["theme"].unique()))

    thematic_blocks: List[str] = []
    for theme in all_themes_sorted:
        peak_list = peaks.get(theme, [])
        peak_str = ", ".join(peak_list) if peak_list else "—"
        dma_name, dma_score = top_dma.get(theme, ("—", 0.0))
        thematic_blocks.append(
            f"- **Theme**: {theme}\n"
            f"  - **Peak Seasonality**: {peak_str}\n"
            f"  - **Top Metro Area**: {dma_name}\n"
            f"  - **Strategic Recommendation**: Prioritize ad scheduling in {peak_str or 'peak months'}; target {dma_name} with tailored copy and bid adjustments."
        )

    # Section 4: Geographic deep dive
    top5_dmas, dma_to_themes = top5_dmas_and_top3_themes(master_geo)
    dma_blocks: List[str] = []
    for dma_name, total_score in top5_dmas:
        inner = dma_to_themes.get(dma_name, [])
        inner_lines = "\n".join([f"  - {t} (score {s:.0f})" for t, s in inner])
        dma_blocks.append(f"- **{dma_name}**\n{inner_lines if inner_lines else '  - —'}")

    # Compose report
    lines: List[str] = []
    lines.append("## Google Ads Strategic Brief: Park City Launch")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    # 1. Clustering
    lines.append("### 1) Campaign & Ad Group Clustering")
    lines.append("**Analysis**: We clustered themes using seasonal search patterns (week-of-year profiles) and overlap of top DMAs. Themes within a cluster share timing and audience geography, making them efficient to manage under one campaign with segmented ad groups.")
    lines.append("")
    for block in cluster_blocks:
        lines.append(block)
        lines.append("")
    lines.append("**Strategic Recommendation**: Use the cluster labels as campaign shells. Keep shared budgets at the campaign level; create ad groups per theme within each cluster, inheriting location targets from the overlapping DMAs.")
    lines.append("")

    # 2. Market Prioritization
    lines.append("### 2) Market Prioritization")
    lines.append("**Analysis**:")
    lines.append("- **Top 5 by Avg Monthly Index**:")
    if top5_avg:
        for theme, val in top5_avg:
            lines.append(f"  - {theme}: {val:.1f}")
    else:
        lines.append("  - —")
    lines.append("- **Top 5 by YoY Growth (CAGR)**:")
    if top5_cagr:
        for theme, val in top5_cagr:
            lines.append(f"  - {theme}: {format_percentage(val)}")
    else:
        lines.append("  - —")
    lines.append("")
    lines.append("**Strategic Recommendation**: Allocate the initial budget with a 70/30 split: 70% to high-volume themes to drive immediate lead flow, 30% to the fastest-growing themes to capture emerging demand early. Rebalance monthly using actual CPA and lead quality.")
    lines.append("")

    # 3. Detailed Thematic Analysis
    lines.append("### 3) Detailed Thematic Analysis")
    lines.append("**Analysis**: Peak months indicate when to increase bids and expand match types; the top DMA highlights where out-of-area interest concentrates.")
    lines.append("")
    lines.extend(thematic_blocks)
    lines.append("")
    lines.append("**Strategic Recommendation**: For each theme, schedule bid modifiers (+15–30%) in peak months and create DMA-specific ad variants for the top metro.")
    lines.append("")

    # 4. Geographic Deep Dive
    lines.append("### 4) Geographic Deep Dive: Top Metro Areas")
    lines.append("**Analysis**:")
    lines.append("- **Top 5 DMAs by Aggregated Interest**:")
    if top5_dmas:
        for dma_name, total in top5_dmas:
            lines.append(f"  - {dma_name}")
    else:
        lines.append("  - —")
    lines.append("- **Top 3 Themes per DMA**:")
    if dma_blocks:
        lines.extend(dma_blocks)
    else:
        lines.append("  - —")
    lines.append("")
    lines.append("**Strategic Recommendation**: Build geo-targeted copy and RSAs referencing the DMA (e.g., ‘Park City Homes for Bay Area Buyers’). Layer DMA bid adjustments (+10–20%) and test sitelinks aligned to the top themes for each DMA.")
    lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    master_time, master_geo = build_master_frames()
    write_report(master_time, master_geo)
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()


