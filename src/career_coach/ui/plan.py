"""Plan tab UI - Learning plan and project recommendations."""

import streamlit as st

from career_coach.domain.schemas import LearningTask, ProjectRecommendation, SkillGap
from career_coach.services.plan_generator import (
    generate_learning_plan,
    generate_project_recommendations,
)
from career_coach.ui.theme import (
    render_alert,
    render_chip,
    render_empty_state,
    render_section_header,
)
from career_coach.ui.navigation import navigate_to


def render_plan_tab():
    """Render the Learning Plan tab."""
    results = st.session_state.get("analysis_results")
    
    if not results:
        st.markdown(render_empty_state(
            title="No Analysis Results",
            description="Complete the Intake tab first to generate your personalized learning plan.",
            icon="file-text",
        ), unsafe_allow_html=True)
        st.button(
            "Go to Intake",
            key="goto_intake_plan_btn",
            on_click=navigate_to,
            args=("Intake",),
        )
        return
    
    gaps = [SkillGap.model_validate(gap) for gap in results.get("gaps", [])]
    
    if not gaps:
        st.markdown(
            render_alert("🎉 No significant skill gaps found! You're well-prepared for this role.", "success"),
            unsafe_allow_html=True,
        )
        return

    plan: list[LearningTask] | None = None
    projects: list[ProjectRecommendation] | None = None
    
    # Plan configuration
    st.markdown(
        render_section_header(
            "📅 Learning Plan Configuration",
            "Configure your study plan parameters",
        ),
        unsafe_allow_html=True,
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        weeks = st.slider("Plan Duration (weeks)", 4, 16, 8, key="plan_weeks")
    with col2:
        hours_per_week = st.slider("Hours per Week", 5, 30, 15, key="plan_hours")
    with col3:
        max_projects = st.slider("Portfolio Projects", 1, 5, 3, key="plan_projects")
    
    if st.button(
        "Generate Plan",
        type="primary",
        key="generate_plan_btn",
        width="stretch",
    ):
        with st.spinner("Generating your personalized learning plan..."):
            plan = generate_learning_plan(gaps, weeks=weeks, hours_per_week=hours_per_week)
            projects = generate_project_recommendations(gaps, max_projects=max_projects)
            st.session_state.learning_plan = plan
            st.session_state.project_recommendations = projects
        st.success("Plan generated!")
        st.rerun()
    
    # Display learning plan
    plan = st.session_state.get("learning_plan")
    if plan:
        st.markdown("---")
        st.markdown(
            render_section_header(
                "📚 Weekly Learning Plan",
                f"{len(plan)} weeks · {sum(t.estimated_hours for t in plan):.0f} total hours",
            ),
            unsafe_allow_html=True,
        )
        
        # Group by week
        for task in plan:
            with st.expander(f"Week {task.week}: {task.skill.title()} — {task.focus}", expanded=(task.week <= 2)):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Learning:** {task.learning_task}")
                    st.markdown(f"**Practice:** {task.practice_task}")
                    st.markdown(f"**Deliverable:** {task.deliverable}")
                    st.markdown(f"**Acceptance:** {task.acceptance_criteria}")
                with col2:
                    st.metric("Hours", f"{task.estimated_hours:.0f}h")
                    if task.dependencies:
                        st.caption(f"Depends on: {', '.join(task.dependencies)}")
                    completed = st.checkbox("Completed", key=f"task_complete_{task.week}_{task.skill}", value=task.completed)
                    if completed != task.completed:
                        task.completed = completed
                        st.rerun()
    
    # Display project recommendations
    projects = st.session_state.get("project_recommendations")
    if projects:
        st.markdown("---")
        st.markdown(
            render_section_header(
                "🚀 Portfolio Project Recommendations",
                f"{len(projects)} projects to showcase your skills",
            ),
            unsafe_allow_html=True,
        )
        
        for i, proj in enumerate(projects):
            with st.expander(f"📦 {proj.title}", expanded=(i == 0)):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Scope:** {proj.scope}")
                    st.markdown(f"**Reasoning:** {proj.reasoning}")
                    st.markdown("**Deliverables:**")
                    for d in proj.deliverables:
                        st.markdown(f"  • {d}")
                    st.markdown("**Acceptance Criteria:**")
                    for a in proj.acceptance_criteria:
                        st.markdown(f"  ✓ {a}")
                    if proj.limitations:
                        st.caption(f"⚠️ {proj.limitations}")
                    if proj.stretch_goals:
                        st.markdown("**Stretch Goals:**")
                        for g in proj.stretch_goals:
                            st.markdown(f"  ★ {g}")
                with col2:
                    st.markdown(
                        render_chip(proj.difficulty.title(), "purple"),
                        unsafe_allow_html=True,
                    )
                    st.metric("Est. Hours", f"{proj.estimated_hours:.0f}h")
                    for skill in proj.targeted_skills:
                        st.markdown(render_chip(skill, "teal"), unsafe_allow_html=True)