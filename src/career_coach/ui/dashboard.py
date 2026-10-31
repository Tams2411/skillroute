"""Dashboard tab UI - Overview and insights."""

import streamlit as st

from career_coach.services.tracker_service import get_tracker
from career_coach.ui.navigation import navigate_to
from career_coach.ui.theme import render_chip, render_empty_state, render_metric, render_section_header


def render_dashboard_tab():
    """Render the Dashboard tab."""
    results = st.session_state.get("analysis_results")
    tracker = get_tracker()
    
    # Overall stats
    apps = tracker.list_all()
    stats = tracker.get_stats()
    
    st.markdown(
        render_section_header("📊 Dashboard", "Your career pivot overview"),
        unsafe_allow_html=True,
    )
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric("Applications", stats["total"]), unsafe_allow_html=True)
    with col2:
        st.markdown(
            render_metric("Response Rate", f"{stats['response_rate']:.1f}%"),
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            render_metric("Interview Rate", f"{stats['interview_rate']:.1f}%"),
            unsafe_allow_html=True,
        )
    with col4:
        readiness = results.get("readiness_percentage", 0) if results else 0
        st.markdown(render_metric("Readiness", f"{readiness:.0f}%"), unsafe_allow_html=True)
    
    # Status chart
    if stats['by_status']:
        st.markdown("### Application Status")
        status_data = {k.replace('_', ' ').title(): v for k, v in stats['by_status'].items()}
        st.bar_chart(status_data, width="stretch")
    
    # Readiness breakdown
    if results:
        st.markdown("---")
        st.markdown(
            render_section_header(
                "🎯 Skill Readiness",
                f"Based on {results.get('total_jd_skills', 0)} JD skills analyzed",
            ),
            unsafe_allow_html=True,
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            matched = len(results.get("matched_skills", []))
            st.markdown(render_metric("Matched Skills", matched), unsafe_allow_html=True)
        with col2:
            missing = len(results.get("missing_skills", []))
            st.markdown(render_metric("Missing Skills", missing), unsafe_allow_html=True)
        with col3:
            partial = len(results.get("partial_skills", []))
            st.markdown(render_metric("Partial Matches", partial), unsafe_allow_html=True)
        
        # Top gaps
        gaps = results.get("gaps", [])
        if gaps:
            st.markdown("### Top Priority Gaps")
            for i, gap in enumerate(gaps[:5]):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(render_chip(gap["canonical_skill"], "teal"), unsafe_allow_html=True)
                    st.caption(gap.get('reason', ''))
                with col2:
                    priority = gap.get('priority', 0)
                    color = "error" if priority > 0.7 else "warning" if priority > 0.4 else "success"
                    st.markdown(
                        render_chip(f"Priority: {priority:.0%}", color),
                        unsafe_allow_html=True,
                    )
                with col3:
                    evidence = gap.get('evidence_strength', 0)
                    st.markdown(
                        render_chip(f"Evidence: {evidence:.0%}", "purple"),
                        unsafe_allow_html=True,
                    )
    
    # Recent activity
    st.markdown("---")
    st.markdown(
        render_section_header("📝 Recent Applications", "Latest activity"),
        unsafe_allow_html=True,
    )
    
    recent_apps = apps[:5]
    if recent_apps:
        for app in recent_apps:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{app.company}** — {app.role}")
                st.caption(f"Applied {app.applied_at.strftime('%Y-%m-%d')}")
            with col2:
                st.markdown(
                    render_chip(app.status.value.replace("_", " ").title(), "teal"),
                    unsafe_allow_html=True,
                )
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
    st.markdown(render_section_header("⚡ Quick Actions"), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "📄 Analyze New JD",
            width="stretch",
            key="goto_intake_dashboard",
            on_click=navigate_to,
            args=("Intake",),
        )
    with col2:
        st.button(
            "📅 Generate Plan",
            width="stretch",
            key="goto_plan_dashboard",
            on_click=navigate_to,
            args=("Plan",),
        )
    with col3:
        st.button(
            "🎤 Practice Interview",
            width="stretch",
            key="goto_interview_dashboard",
            on_click=navigate_to,
            args=("Interview",),
        )