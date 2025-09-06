import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


def render_marketing_plan_view():
    """
    Renders a comprehensive Marketing Plan & Timeline dashboard with three main tabs:
    1. Marketing Timeline - High-level Gantt-chart style overview
    2. My Weekly Tasks - Weekly task breakdown with checkboxes
    3. Strategic Framework - Three-pillar marketing philosophy reference
    """
    
    # Dashboard Title
    st.title("🎯 My Marketing Plan & Timeline")
    st.markdown("*Strategic marketing initiatives with actionable weekly tasks and clear timelines.*")
    
    # Define marketing initiatives data
    initiatives = [
        {
            "name": "❄️ Winter 2026: Sundance & Lifestyle Campaign",
            "description": "A PPC and content campaign focused on capturing the luxury vacation buyer during peak season and the Sundance Film Festival.",
            "goals": {
                "Target Leads": 50,
                "Target CPL": "< $150",
                "Content Engagement": "Guide to Sundance Real Estate > 1,000 views"
            },
            "timeline": {
                "Strategy & Content (🔵)": ("2025-11-15", "2025-12-15"),
                "Production & Publishing (🟡)": ("2025-12-16", "2025-12-30"),
                "Campaign Build-Out (🟠)": ("2025-12-31", "2026-01-07"),
                "Launch & Monitor (🟢)": ("2026-01-08", "2026-02-28")
            }
        },
        {
            "name": "🌸 Spring 2026: Mountain Living & Investment Focus",
            "description": "Targeting spring buyers and investors with content about mountain living benefits and investment opportunities.",
            "goals": {
                "Target Leads": 75,
                "Target CPL": "< $120",
                "Content Engagement": "Mountain Investment Guide > 1,500 views"
            },
            "timeline": {
                "Strategy & Content (🔵)": ("2026-02-15", "2026-03-15"),
                "Production & Publishing (🟡)": ("2026-03-16", "2026-03-30"),
                "Campaign Build-Out (🟠)": ("2026-03-31", "2026-04-07"),
                "Launch & Monitor (🟢)": ("2026-04-08", "2026-05-31")
            }
        },
        {
            "name": "☀️ Summer 2026: Peak Season & Family Focus",
            "description": "Capitalizing on summer vacation season with family-oriented content and vacation rental opportunities.",
            "goals": {
                "Target Leads": 100,
                "Target CPL": "< $100",
                "Content Engagement": "Summer Family Guide > 2,000 views"
            },
            "timeline": {
                "Strategy & Content (🔵)": ("2026-05-15", "2026-06-15"),
                "Production & Publishing (🟡)": ("2026-06-16", "2026-06-30"),
                "Campaign Build-Out (🟠)": ("2026-07-01", "2026-07-07"),
                "Launch & Monitor (🟢)": ("2026-07-08", "2026-08-31")
            }
        },
        {
            "name": "🍂 Fall 2026: Back-to-School & Relocation",
            "description": "Targeting families relocating for school year and professionals seeking mountain lifestyle changes.",
            "goals": {
                "Target Leads": 60,
                "Target CPL": "< $130",
                "Content Engagement": "Relocation Guide > 1,200 views"
            },
            "timeline": {
                "Strategy & Content (🔵)": ("2026-08-15", "2026-09-15"),
                "Production & Publishing (🟡)": ("2026-09-16", "2026-09-30"),
                "Campaign Build-Out (🟠)": ("2026-10-01", "2026-10-07"),
                "Launch & Monitor (🟢)": ("2026-10-08", "2026-11-30")
            }
        }
    ]
    
    # Create main tabs
    tab1, tab2, tab3 = st.tabs(["📅 Marketing Timeline", "✅ My Weekly Tasks", "🎯 Strategic Framework"])
    
    with tab1:
        st.header("Marketing Timeline Overview")
        st.markdown("High-level view of all marketing initiatives with key metrics and timelines.")
        
        # Iterate through initiatives and create expanders
        for initiative in initiatives:
            with st.expander(f"**{initiative['name']}**", expanded=False):
                # Description
                st.markdown(f"**Description:** {initiative['description']}")
                
                # Goals in columns
                st.markdown("**Goals:**")
                col1, col2, col3 = st.columns(3)
                
                goals = initiative['goals']
                with col1:
                    st.metric("Target Leads", goals['Target Leads'])
                with col2:
                    st.metric("Target CPL", goals['Target CPL'])
                with col3:
                    st.metric("Content Engagement", goals['Content Engagement'])
                
                # Timeline visualization
                st.markdown("**Timeline:**")
                timeline = initiative['timeline']
                
                for stage, (start_date, end_date) in timeline.items():
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    duration = (end_dt - start_dt).days + 1
                    
                    st.markdown(f"**{stage}**")
                    st.markdown(f"📅 {start_date} → {end_date} ({duration} days)")
                    st.markdown("---")
    
    with tab2:
        st.header("My Weekly Tasks")
        st.markdown("Select any week to see your active marketing tasks and track progress.")
        
        # Date input for week selection
        selected_date = st.date_input(
            "Select Week",
            value=datetime.now().date(),
            help="Choose any week to see tasks for that period"
        )
        
        # Calculate week start and end
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        st.markdown(f"### ✅ My Tasks for: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
        
        # Find active tasks for the selected week
        active_tasks = []
        
        for initiative in initiatives:
            initiative_name = initiative['name']
            timeline = initiative['timeline']
            
            for stage, (start_date, end_date) in timeline.items():
                stage_start = datetime.strptime(start_date, "%Y-%m-%d").date()
                stage_end = datetime.strptime(end_date, "%Y-%m-%d").date()
                
                # Check if stage overlaps with selected week
                if (stage_start <= week_end and stage_end >= week_start):
                    # Determine task description based on stage
                    task_descriptions = {
                        "Strategy & Content (🔵)": "Develop strategy and create content assets",
                        "Production & Publishing (🟡)": "Finalize and publish content across channels",
                        "Campaign Build-Out (🟠)": "Set up and configure PPC campaigns",
                        "Launch & Monitor (🟢)": "Launch campaigns and monitor performance"
                    }
                    
                    task_desc = task_descriptions.get(stage, f"Work on {stage}")
                    active_tasks.append({
                        'initiative': initiative_name,
                        'stage': stage,
                        'description': task_desc,
                        'start_date': stage_start,
                        'end_date': stage_end
                    })
        
        # Display tasks as checkboxes
        if active_tasks:
            st.markdown("**Active Tasks This Week:**")
            for i, task in enumerate(active_tasks):
                # Create a unique key for each checkbox
                checkbox_key = f"task_{i}_{task['initiative']}_{task['stage']}"
                
                # Check if task is currently active (not just overlapping)
                is_currently_active = (task['start_date'] <= selected_date <= task['end_date'])
                
                checkbox_label = f"**{task['initiative']}**: {task['description']} ({task['stage']})"
                
                if is_currently_active:
                    checkbox_label = f"🔥 {checkbox_label}"
                
                st.checkbox(checkbox_label, key=checkbox_key)
        else:
            st.info("No active tasks for the selected week. Great time to focus on planning and strategy!")
    
    with tab3:
        st.header("Strategic Framework")
        st.markdown("The three-pillar approach to comprehensive marketing success.")
        
        # Three-column layout for strategic framework
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Demand Generation")
            st.markdown("**The 'Before' - Making the audience aware of you**")
            st.markdown("""
            **Key Activities:**
            - Content marketing
            - Social media presence
            - SEO optimization
            - Brand awareness campaigns
            - Thought leadership
            
            **Goal:** Build recognition and trust before prospects are actively searching.
            """)
        
        with col2:
            st.markdown("### 🎯 Demand Capture")
            st.markdown("**The 'During' - Capturing active searchers**")
            st.markdown("""
            **Key Activities:**
            - AI-powered PPC campaigns
            - Search engine marketing
            - Retargeting campaigns
            - Landing page optimization
            - Conversion tracking
            
            **Goal:** Capture prospects when they're actively looking for solutions.
            """)
        
        with col3:
            st.markdown("### 🎯 Lead Nurturing")
            st.markdown("**The 'After' - Converting leads into clients**")
            st.markdown("""
            **Key Activities:**
            - CRM management
            - Email sequences
            - Follow-up automation
            - Personalized outreach
            - Relationship building
            
            **Goal:** Convert qualified leads into paying clients through systematic nurturing.
            """)


if __name__ == "__main__":
    # This allows the file to be run directly for testing
    render_marketing_plan_view()
