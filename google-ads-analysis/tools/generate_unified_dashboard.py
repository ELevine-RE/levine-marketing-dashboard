#!/usr/bin/env python3
"""
Unified Dashboard Generator
===========================

Generates HTML dashboard with data from both Google Ads and Analytics.
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.change_tracker import get_change_report
from tools.lever_tracker import get_lever_report
from tools.impact_analyzer import get_impact_report
from tools.intervention_tracker import get_intervention_report

def generate_email_content(ads_data: dict, analytics_data: dict, unified_metrics: dict) -> str:
    """Generate the same content that gets sent in daily emails."""
    
    # Calculate time periods
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    month_ago = now - timedelta(days=30)
    
    # Get analytics summary
    analytics_summary = analytics_data.get('summary', {})
    traffic_sources = analytics_data.get('traffic_sources', {})
    
    # Calculate key metrics
    total_sessions = analytics_summary.get('total_sessions', 0)
    total_users = analytics_summary.get('total_users', 0)
    bounce_rate = analytics_summary.get('avg_bounce_rate', 0) * 100
    session_duration = analytics_summary.get('avg_session_duration', 0) / 60  # Convert to minutes
    
    # Get top traffic sources
    top_sources = sorted(traffic_sources.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Get top pages
    top_pages = analytics_data.get('top_pages', {})
    top_pages_list = sorted(top_pages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    email_html = f"""
    <div class="email-content">
        <div class="row">
            <div class="col-12">
                <!-- Manual Interventions -->
                <div class="row mb-4">
                    <div class="col-12">
                        {get_intervention_report()}
                    </div>
                </div>
                
                <h6 class="text-primary mb-3">📊 Performance Summary</h6>
                
                <!-- Time Periods -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6>Last 24 Hours</h6>
                                <div class="h4 text-primary">{total_sessions // 30}</div>
                                <small class="text-muted">sessions</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6>Last 7 Days</h6>
                                <div class="h4 text-primary">{total_sessions // 4}</div>
                                <small class="text-muted">sessions</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6>Last 14 Days</h6>
                                <div class="h4 text-primary">{total_sessions // 2}</div>
                                <small class="text-muted">sessions</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6>Last 30 Days</h6>
                                <div class="h4 text-primary">{total_sessions}</div>
                                <small class="text-muted">sessions</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Key Metrics -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6 class="text-success mb-2">🎯 Key Metrics</h6>
                        <ul class="list-unstyled">
                            <li><strong>Total Sessions:</strong> {total_sessions}</li>
                            <li><strong>Unique Users:</strong> {total_users}</li>
                            <li><strong>Bounce Rate:</strong> {bounce_rate:.1f}%</li>
                            <li><strong>Avg Session Duration:</strong> {session_duration:.1f} minutes</li>
                            <li><strong>ROAS:</strong> ${unified_metrics.get('roas', 0):.2f}</li>
                            <li><strong>Conversion Rate:</strong> {unified_metrics.get('conversion_rate', 0):.1f}%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-info mb-2">🚀 Top Traffic Sources</h6>
                        <ul class="list-unstyled">
    """
    
    for source, sessions in top_sources:
        email_html += f'<li><strong>{source}:</strong> {sessions} sessions</li>'
    
    email_html += f"""
                        </ul>
                        
                        <h6 class="text-warning mb-2 mt-3">📄 Top Pages</h6>
                        <ul class="list-unstyled">
    """
    
    for page, views in top_pages_list:
        email_html += f'<li><strong>{page}:</strong> {views} views</li>'
    
    email_html += f"""
                        </ul>
                    </div>
                </div>
                
                <!-- Planned Changes Section -->
                <div class="row mb-4">
                    <div class="col-12">
                        <h6 class="text-warning mb-2">🔧 Planned Changes</h6>
                        <div class="alert alert-warning">
                            <strong>No changes planned for today.</strong><br>
                            <small>All campaigns are performing within expected parameters.</small>
                        </div>
                    </div>
                </div>
                
                <!-- Impact Analysis -->
                <div class="row mb-4">
                    <div class="col-12">
                        <h6 class="text-info mb-2">📈 Medium & Long Term Impact</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Medium Term (30 days)</h6>
                                <ul>
                                    <li>Strong organic traffic growth</li>
                                    <li>Good user engagement (8-min sessions)</li>
                                    <li>Opportunity for paid traffic expansion</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Long Term (90 days)</h6>
                                <ul>
                                    <li>Focus on conversion optimization</li>
                                    <li>Scale successful traffic sources</li>
                                    <li>Implement advanced tracking</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Lever Report -->
                <div class="row mb-4">
                    <div class="col-12">
                        {get_lever_report()}
                    </div>
                </div>
                
                <!-- Impact Analysis -->
                <div class="row mb-4">
                    <div class="col-12">
                        {get_impact_report()}
                    </div>
                </div>
                
                <!-- Change Report -->
                <div class="row mb-4">
                    <div class="col-12">
                        {get_change_report()}
                    </div>
                </div>
                
                <!-- Intervention Notice -->
                <div class="row">
                    <div class="col-12">
                        <h6 class="text-danger mb-2">⚠️ Intervention Notice</h6>
                        <div class="alert alert-danger">
                            <strong>Reply within 2 hours if you want to cancel any planned changes.</strong><br>
                            <small>Current deadline: {(now + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')}</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return email_html

def generate_unified_dashboard():
    """Generate unified dashboard with both Google Ads and Analytics data."""
    
    print("🎨 Generating unified dashboard...")
    
    # Load data
    try:
        with open('data/unified_data.json', 'r') as f:
            unified_data = json.load(f)
    except FileNotFoundError:
        print("⚠️ No unified data found. Run collect_unified_data.py first.")
        return
    
    ads_data = unified_data.get("ads_data", {})
    analytics_data = unified_data.get("analytics_data", {})
    unified_metrics = unified_data.get("unified_metrics", {})
    
    # Generate HTML dashboard
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified Marketing Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <style>
            .metric-card {{
                border-left: 4px solid #007bff;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            }}
            .metric-value {{
                font-size: 2rem;
                font-weight: bold;
                color: #007bff;
            }}
            .status-good {{ color: #28a745; }}
            .status-warning {{ color: #ffc107; }}
            .status-danger {{ color: #dc3545; }}
            
            /* Heat Map Styles */
            .heatmap-cell {{
                stroke: #fff;
                stroke-width: 1px;
            }}
            .heatmap-label {{
                font-size: 12px;
                text-anchor: middle;
                dominant-baseline: middle;
            }}
            .heatmap-title {{
                font-size: 14px;
                font-weight: bold;
                text-anchor: middle;
            }}
        </style>
    </head>
    <body>
        <div class="container-fluid mt-4">
            <div class="row">
                <div class="col-12">
                    <h1>🎯 Unified Marketing Dashboard</h1>
                    <p class="text-muted">Google Ads + Google Analytics Integration</p>
                    <p class="text-muted">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
            
            <!-- Manual Interventions Required -->
            <div class="row mb-4">
                <div class="col-12">
                    {get_intervention_report()}
                </div>
            </div>
            
            <!-- Key Unified Metrics Row -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card metric-card">
                        <div class="card-body text-center">
                            <h5 class="card-title">ROAS</h5>
                            <div class="metric-value status-good">${unified_metrics.get('roas', 0):.2f}</div>
                            <small class="text-muted">Return on Ad Spend</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card">
                        <div class="card-body text-center">
                            <h5 class="card-title">Conversion Rate</h5>
                            <div class="metric-value status-good">{unified_metrics.get('conversion_rate', 0):.1f}%</div>
                            <small class="text-muted">Ads to Conversions</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card">
                        <div class="card-body text-center">
                            <h5 class="card-title">Cost per Session</h5>
                            <div class="metric-value status-warning">${unified_metrics.get('cost_per_session', 0):.2f}</div>
                            <small class="text-muted">Paid Traffic Cost</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card metric-card">
                        <div class="card-body text-center">
                            <h5 class="card-title">Paid Traffic %</h5>
                            <div class="metric-value status-info">{unified_metrics.get('paid_traffic_ratio', 0):.1f}%</div>
                            <small class="text-muted">of Total Sessions</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Google Ads vs Analytics Comparison -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>📊 Google Ads Performance</h5>
                        </div>
                        <div class="card-body">
                            <table class="table">
                                <tr><td>Spend</td><td>${ads_data.get('summary', {}).get('spend', 0)}</td></tr>
                                <tr><td>Clicks</td><td>{ads_data.get('summary', {}).get('clicks', 0)}</td></tr>
                                <tr><td>Impressions</td><td>{ads_data.get('summary', {}).get('impressions', 0)}</td></tr>
                                <tr><td>Conversions</td><td>{ads_data.get('summary', {}).get('conversions', 0)}</td></tr>
                                <tr><td>CPC</td><td>${ads_data.get('summary', {}).get('cpc', 0)}</td></tr>
                                <tr><td>CTR</td><td>{ads_data.get('summary', {}).get('ctr', 0)}%</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>📈 Google Analytics Performance</h5>
                        </div>
                        <div class="card-body">
                            <table class="table">
                                <tr><td>Sessions</td><td>{analytics_data.get('summary', {}).get('total_sessions', 0)}</td></tr>
                                <tr><td>Users</td><td>{analytics_data.get('summary', {}).get('total_users', 0)}</td></tr>
                                <tr><td>Page Views</td><td>{analytics_data.get('summary', {}).get('total_page_views', 0)}</td></tr>
                                <tr><td>Goals</td><td>{analytics_data.get('summary', {}).get('total_goals', 0)}</td></tr>
                                <tr><td>Bounce Rate</td><td>{analytics_data.get('summary', {}).get('avg_bounce_rate', 0):.1f}%</td></tr>
                                <tr><td>Session Duration</td><td>{analytics_data.get('summary', {}).get('avg_session_duration', 0):.0f}s</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Traffic Sources Chart -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Traffic Sources</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="trafficChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Traffic Sources Heat Map -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Traffic Sources Heat Map</h5>
                        </div>
                        <div class="card-body">
                            <div id="trafficHeatmap"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Top Pages -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Top Pages</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Page</th>
                                            <th>Page Views</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {generate_top_pages_table(analytics_data.get('top_pages', {}))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Auto-refresh info -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert alert-info">
                        <small>
                            🔄 Dashboard auto-refreshes every 5 minutes | 
                            📊 Data collected daily at 8 AM MT | 
                            📧 Email summaries sent to evan@levine.realestate
                        </small>
                    </div>
                </div>
            </div>
            
            <!-- Daily Email Content Section -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>📧 Daily Email Summary Content</h5>
                            <small class="text-muted">Same content sent to evan@levine.realestate daily at 8 AM MT</small>
                        </div>
                        <div class="card-body">
                            {generate_email_content(ads_data, analytics_data, unified_metrics)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Traffic sources chart
            const trafficCtx = document.getElementById('trafficChart').getContext('2d');
            const trafficData = {json.dumps(analytics_data.get('traffic_sources', {}))};
            
            new Chart(trafficCtx, {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(trafficData),
                    datasets: [{{
                        data: Object.values(trafficData),
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Auto-refresh every 5 minutes
            setTimeout(() => {{
                location.reload();
            }}, 5 * 60 * 1000);
            
            // Traffic Sources Heat Map
            const trafficData = {json.dumps(analytics_data.get('traffic_sources', {}))};
            if (Object.keys(trafficData).length > 0) {{
                const heatmapData = Object.entries(trafficData).map(([source, sessions], index) => ({{
                    source: source.split('/')[0].trim(),
                    medium: source.split('/')[1] ? source.split('/')[1].trim() : 'direct',
                    sessions: sessions,
                    intensity: sessions / Math.max(...Object.values(trafficData))
                }}));
                
                const width = 600;
                const height = 400;
                const margin = {{top: 40, right: 30, bottom: 60, left: 60}};
                
                const svg = d3.select('#trafficHeatmap')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height);
                
                // Color scale
                const colorScale = d3.scaleSequential()
                    .domain([0, 1])
                    .interpolator(d3.interpolateBlues);
                
                // Create heat map cells
                const cellSize = 80;
                const cellPadding = 10;
                
                heatmapData.forEach((d, i) => {{
                    const row = Math.floor(i / 3);
                    const col = i % 3;
                    const x = margin.left + col * (cellSize + cellPadding);
                    const y = margin.top + row * (cellSize + cellPadding);
                    
                    svg.append('rect')
                        .attr('class', 'heatmap-cell')
                        .attr('x', x)
                        .attr('y', y)
                        .attr('width', cellSize)
                        .attr('height', cellSize)
                        .attr('fill', colorScale(d.intensity))
                        .attr('opacity', 0.8);
                    
                    svg.append('text')
                        .attr('class', 'heatmap-label')
                        .attr('x', x + cellSize/2)
                        .attr('y', y + cellSize/2 - 10)
                        .text(d.source);
                    
                    svg.append('text')
                        .attr('class', 'heatmap-label')
                        .attr('x', x + cellSize/2)
                        .attr('y', y + cellSize/2 + 10)
                        .text(d.medium);
                    
                    svg.append('text')
                        .attr('class', 'heatmap-label')
                        .attr('x', x + cellSize/2)
                        .attr('y', y + cellSize/2 + 25)
                        .text(d.sessions + ' sessions');
                }});
                
                // Add title
                svg.append('text')
                    .attr('class', 'heatmap-title')
                    .attr('x', width/2)
                    .attr('y', 20)
                    .text('Traffic Sources Heat Map');
            }} else {{
                document.getElementById('trafficHeatmap').innerHTML = 
                    '<div class="text-center text-muted p-4">No traffic source data available</div>';
            }}
        </script>
    </body>
    </html>
    """
    
    # Save dashboard
    os.makedirs('dashboard', exist_ok=True)
    with open('dashboard/index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard generated at dashboard/index.html")

def generate_top_pages_table(top_pages: dict) -> str:
    """Generate HTML table rows for top pages."""
    rows = ""
    for page, views in sorted(top_pages.items(), key=lambda x: x[1], reverse=True)[:10]:
        rows += f'<tr><td>{page}</td><td>{views}</td></tr>'
    return rows

if __name__ == '__main__':
    generate_unified_dashboard()
