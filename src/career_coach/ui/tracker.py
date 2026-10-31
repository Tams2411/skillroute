"""Tracker tab UI - Application tracking."""

import streamlit as st
from career_coach.services.tracker_service import get_tracker
from career_coach.domain.schemas import ApplicationStatus
from career_coach.ui.theme import (
    render_section_header, render_chip, render_empty_state,
    render_metric
)
from datetime import datetime


def render_tracker_tab():
    """Render the Application Tracker tab."""
    tracker = get_tracker()
    apps = tracker.list_all()
    
    # Stats
    stats = tracker.get_stats()
    
    st.markdown(
        render_section_header("📋 Application Tracker", f"{stats['total']} applications tracked"),
        unsafe_allow_html=True,
    )
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_metric("Total", stats["total"]), unsafe_allow_html=True)
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
        st.markdown(
            render_metric("Offer Rate", f"{stats['offer_rate']:.1f}%"),
            unsafe_allow_html=True,
        )
    
    # Status breakdown
    if stats['by_status']:
        st.markdown("**Status Breakdown:**")
        status_cols = st.columns(len(stats['by_status']))
        for i, (status, count) in enumerate(stats['by_status'].items()):
            with status_cols[i]:
                st.markdown(
                    render_chip(status.replace("_", " ").title(), "teal"),
                    unsafe_allow_html=True,
                )
                st.metric("Applications", count, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Add new application
    with st.expander("➕ Add New Application", expanded=False):
        with st.form("add_app_form"):
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("Company *", placeholder="Acme Corp")
                role = st.text_input("Role *", placeholder="Senior Data Engineer")
            with col2:
                status = st.selectbox("Status", [s.value for s in ApplicationStatus], index=0)
                applied_date = st.date_input("Applied Date", datetime.now())
            
            jd_text = st.text_area(
                "Job Description (optional)",
                height=100,
                max_chars=10_000,
                placeholder="Paste JD here for future reference...",
            )
            notes = st.text_area("Notes", height=80, placeholder="Referral? Recruiter contact? Salary range?")
            
            if st.form_submit_button("Add Application", type="primary", width="stretch"):
                if company and role:
                    tracker.create(
                        company=company,
                        role=role,
                        status=ApplicationStatus(status),
                        applied_at=datetime.combine(applied_date, datetime.min.time()),
                        jd_text=jd_text,
                        notes=notes,
                    )
                    st.success("Application added!")
                    st.rerun()
                else:
                    st.error("Company and Role are required")
    
    # Applications list
    if not apps:
        st.markdown(render_empty_state(
            title="No Applications Yet",
            description="Add your first application above to start tracking.",
            icon="file-text",
        ), unsafe_allow_html=True)
        return
    
    # Filter
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + [s.value for s in ApplicationStatus],
        key="tracker_filter"
    )
    
    filtered_apps = apps if status_filter == "All" else [a for a in apps if a.status.value == status_filter]
    
    # Display applications
    for app in filtered_apps:
        with st.expander(f"{app.company} — {app.role} [{app.status.value.replace('_', ' ').title()}]", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Applied:** {app.applied_at.strftime('%Y-%m-%d')}")
                st.markdown(f"**Updated:** {app.updated_at.strftime('%Y-%m-%d')}")
                if app.jd_text:
                    with st.expander("Job Description"):
                        st.text(app.jd_text[:500] + ("..." if len(app.jd_text) > 500 else ""))
                if app.notes:
                    st.markdown(f"**Notes:** {app.notes}")
            
            with col2:
                # Status update
                new_status = st.selectbox(
                    "Status",
                    [s.value for s in ApplicationStatus],
                    index=[s.value for s in ApplicationStatus].index(app.status.value),
                    key=f"status_{app.id}"
                )
                if new_status != app.status.value:
                    tracker.update_status(app.id, ApplicationStatus(new_status))
                    st.rerun()
                
                # Notes edit
                new_notes = st.text_area(
                    "Notes",
                    value=app.notes,
                    key=f"notes_{app.id}",
                    height=80
                )
                if new_notes != app.notes:
                    tracker.update(app.id, notes=new_notes)
                    st.rerun()
                
                # Delete
                if st.button("🗑️ Delete", key=f"del_{app.id}", type="secondary"):
                    tracker.delete(app.id)
                    st.rerun()