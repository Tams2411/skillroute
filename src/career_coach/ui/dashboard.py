"""Dashboard tab UI - Overview and insights."""

import streamlit as st
from career_coach.services.tracker_service import get_tracker
from career_coach.ui.theme import (
    render_section_header, render_chip, render_empty_state,
    render_alert, render_metric
)
from career_coach.services.skill_gap_service import SkillGapService


def render_dashboard_tab():
    """Render the Dashboard tab."""
    results = st.session_state.get("analysis_results")
    tracker = get_tracker()
    
    # Overall stats
    apps = tracker.list_all()
    stats = tracker.get_stats()
    
    render_section_header("📊 Dashboard", "Your career pivot overview")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Applications", stats['total'])
    with col2:
        render_metric("Response Rate", f"{stats['response_rate']:.1f}%")
    with col3:
        render_metric("Interview Rate", f"{stats['interview_rate']:.1f}%")
    with col4:
        readiness = results.get("readiness_percentage", 0) if results else 0
        render_metric("Readiness", f"{readiness:.0f}%")
    
    # Status chart
    if stats['by_status']:
        st.markdown("### Application Status")
        status_data = {k.replace('_', ' ').title(): v for k, v in stats['by_status'].items()}
        st.bar_chart(status_data, use_container_width=True)
    
    # Readiness breakdown
    if results:
        st.markdown("---")
        render_section_header("🎯 Skill Readiness", f"Based on {results.get('total_jd_skills', 0)} JD skills analyzed")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            matched = len(results.get("matched_skills", []))
            render_metric("Matched Skills", matched)
        with col2:
            missing = len(results.get("missing_skills", []))
            render_metric("Missing Skills", missing)
        with col3:
            partial = len(results.get("partial_skills", []))
            render_metric("Partial Matches", partial)
        
        # Top gaps
        gaps = results.get("gaps", [])
        if gaps:
            st.markdown("### Top Priority Gaps")
            for i, gap in enumerate(gaps[:5]):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    render_chip(gap['canonical_skill'], "teal")
                    st.caption(gap.get('reason', ''))
                with col2:
                    priority = gap.get('priority', 0)
                    color = "error" if priority > 0.7 else "warning" if priority > 0.4 else "success"
                    render_chip(f"Priority: {priority:.0%}", color)
                with col3:
                    evidence = gap.get('evidence_strength', 0)
                    render_chip(f"Evidence: {evidence:.0%}", "purple")
    
    # Recent activity
    st.markdown("---")
    render_section_header("📝 Recent Applications", "Latest activity")
    
    recent_apps = apps[:5]
    if recent_apps:
        for app in recent_apps:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{app.company}** — {app.role}")
                st.caption(f"Applied {app.applied_at.strftime('%Y-%m-%d')}")
            with col2:
                render_chip(app.status.value.replace('_', ' ').title(), "teal")
            with col3:
                st.caption(f"Updated {app.updated_at.strftime('%Y-%m-%d')}")
    else:
        st.markdown(render_empty_state(
            title="No Applications Yet",
            description="Add applications in the Tracker tab to see activity here.",
            icon="file-text",
        ), unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("---")
    render_section_header("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Analyze New JD", use_container_width=True):
            st.session_state.active_tab = 0
            st.rerun()
    with col2:
        if st.button("📅 Generate Plan", use_container_width=True):
            st.session_state.active_tab = 2
            st.rerun()
    with col3:
        if st.button("🎤 Practice Interview", use_container_width=True):
            st.session_state.active_tab = 4
            st.rerun()