"""Streamlit UI - Intake tab for resume and JD input."""

import streamlit as st
from career_coach.ui.theme import (
    render_svg, render_chip, render_status, render_alert,
    render_empty_state, render_section_header, render_skill_card,
    render_metric
)


def render_intake_tab() -> dict | None:
    """
    Render the intake tab for resume and JD input.
    
    Returns:
        Dict with analysis results or None if not ready
    """
    st.markdown(render_section_header(
        "Input Your Profile",
        "Upload your resume and paste a job description to get started",
        icon="file-text"
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    # Resume Input
    with col1:
        st.markdown("### Resume")
        
        upload_col, text_col = st.columns([1, 1])
        
        with upload_col:
            resume_file = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx", "txt"],
                help="PDF, DOCX, or TXT (max 5MB, 10 pages)",
                key="resume_uploader"
            )
        
        with text_col:
            resume_text = st.text_area(
                "Or Paste Resume Text",
                height=200,
                placeholder="Paste your resume text here...",
                key="resume_text"
            )
        
        # Show extracted text preview if file uploaded
        if resume_file:
            st.markdown(render_status(
                f"File ready: {resume_file.name} ({resume_file.size / 1024:.1f} KB)",
                "success", "check-circle"
            ), unsafe_allow_html=True)
        
        if resume_text:
            st.caption(f"{len(resume_text)} characters")
    
    # Job Description Input
    with col2:
        st.markdown("### Job Description")
        
        jd_text = st.text_area(
            "Paste Job Description",
            height=320,
            placeholder="Paste the full job description here...",
            key="jd_text"
        )
        
        if jd_text:
            st.caption(f"{len(jd_text)} characters")
        
        # Sample JD button
        if st.button("Load Sample JD", key="sample_jd", use_container_width=True):
            st.session_state.jd_text = SAMPLE_JD
            st.rerun()
    
    # User confirmed skills
    st.markdown(render_section_header(
        "Confirmed Skills (Optional)",
        "Add skills you know you have but aren't captured in your resume",
        icon="check-circle"
    ), unsafe_allow_html=True)
    
    user_skills = st.text_input(
        "Comma-separated skills",
        placeholder="python, sql, docker, kubernetes",
        key="user_skills"
    )
    
    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    
    can_analyze = bool((resume_file or resume_text) and jd_text)
    
    if st.button(
        "Analyze Skill Gaps",
        type="primary",
        disabled=not can_analyze,
        use_container_width=True,
        key="analyze_btn"
    ):
        return {
            "resume_file": resume_file,
            "resume_text": resume_text,
            "jd_text": jd_text,
            "user_skills": [s.strip() for s in user_skills.split(",") if s.strip()] if user_skills else []
        }
    
    if not can_analyze:
        st.markdown(render_alert(
            "Upload a resume or paste resume text, and provide a job description to begin analysis.",
            "info", "info"
        ), unsafe_allow_html=True)
    
    return None


def render_results(results: dict) -> None:
    """Render the analysis results."""
    
    # Readiness Score
    readiness = results.get("readiness_score", 0)
    readiness_pct = results.get("readiness_percentage", 0)
    
    st.markdown(render_section_header(
        "Skill Gap Analysis",
        f"Overall Readiness: {readiness_pct}% | {results.get('total_jd_skills', 0)} skills in JD",
        icon="target"
    ), unsafe_allow_html=True)
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    matched = len(results.get("matched_skills", []))
    missing = len(results.get("missing_skills", []))
    actionable = len(results.get("actionable_gaps", []))
    top_gaps = len(results.get("top_gaps", []))
    
    with col1:
        st.markdown(render_metric("Matched", str(matched)), unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric("Missing", str(missing)), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric("Actionable", str(actionable)), unsafe_allow_html=True)
    with col4:
        st.markdown(render_metric("Top Gaps", str(top_gaps)), unsafe_allow_html=True)
    
    # Progress bar
    st.markdown(f'''
    <div class="progress-bar" style="margin: 1.5rem 0;">
        <div class="progress-fill" style="width: {readiness_pct}%"></div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Top Gaps", "All Gaps", "Matched Skills"])
    
    with tab1:
        top_gaps = results.get("top_gaps", [])
        if top_gaps:
            for gap in top_gaps:
                st.markdown(render_skill_card(gap, show_priority=True), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "No Critical Gaps Found",
                "Your profile aligns well with this role's requirements.",
                "check-circle"
            ), unsafe_allow_html=True)
    
    with tab2:
        all_gaps = results.get("all_gaps", [])
        if all_gaps:
            for gap in all_gaps:
                st.markdown(render_skill_card(gap, show_priority=True), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "No Gaps Identified",
                "All required skills are present in your resume.",
                "check-circle"
            ), unsafe_allow_html=True)
    
    with tab3:
        matched_skills = results.get("matched_skills", [])
        if matched_skills:
            for skill in matched_skills:
                st.markdown(render_skill_card(skill), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "No Matched Skills",
                "No skills from the job description were found in your resume.",
                "file-text"
            ), unsafe_allow_html=True)
    
    # JD Details
    with st.expander("Job Description Details"):
        jd_parsed = results.get("jd_parsed", {})
        st.write(f"**Target Experience:** {jd_parsed.get('target_experience_years', 0)} years")
        st.write(f"**Sections Found:** {', '.join(jd_parsed.get('sections_found', []))}")
        
        meta = results.get("extraction_metadata", {})
        jd_meta = meta.get("jd_extraction", {})
        if jd_meta:
            st.write(f"**Required Section:** {jd_meta.get('required_section_chars', 0)} chars")
            st.write(f"**Preferred Section:** {jd_meta.get('preferred_section_chars', 0)} chars")
            st.write(f"**Total Skills Found:** {jd_meta.get('total_skills_found', 0)}")
    
    # Resume Evidence Levels
    with st.expander("Resume Evidence Breakdown"):
        resume_meta = results.get("extraction_metadata", {}).get("resume_evidence_levels", {})
        if resume_meta:
            for level, count in resume_meta.items():
                if count > 0:
                    st.write(f"**{level.capitalize()}:** {count} skills")


# Sample Job Description for testing
SAMPLE_JD = """Senior Data Engineer

We're looking for a Senior Data Engineer to build and maintain our data platform.

Required Skills:
- 5+ years of experience with Python
- Expert level SQL and database design (PostgreSQL, MySQL)
- Strong experience with Apache Airflow for orchestration
- Hands-on experience with Apache Spark and PySpark
- Experience with AWS (S3, Redshift, Lambda, Glue)
- Docker and Kubernetes for container orchestration
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Data modeling and schema design

Preferred Skills:
- Experience with Kafka for event streaming
- Terraform for infrastructure as code
- Machine learning pipeline experience (MLflow, Kubeflow)
- GraphQL API development
- React/TypeScript for internal tools

Responsibilities:
- Design and build scalable data pipelines
- Optimize query performance and data storage costs
- Collaborate with ML engineers on feature stores
- Maintain data quality and observability
- Mentor junior engineers

Benefits:
- Competitive salary and equity
- Health, dental, vision
- 401k matching
- Flexible PTO
- Learning budget
"""