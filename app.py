"""SkillRoute - Career Pivot Coach Main Application."""

import logging
import os
import tempfile
from pathlib import Path

import streamlit as st

from career_coach.config import settings
from career_coach.services.skill_gap_service import SkillGapService
from career_coach.ui.dashboard import render_dashboard_tab
from career_coach.ui.intake import SAMPLE_JD, render_intake_tab, render_results
from career_coach.ui.interview import render_interview_tab
from career_coach.ui.navigation import NAVIGATION_ITEMS
from career_coach.ui.plan import render_plan_tab
from career_coach.ui.session_state import clear_analysis_state, reset_workspace
from career_coach.ui.tracker import render_tracker_tab
from career_coach.ui.theme import apply_theme

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="SkillRoute — Career Pivot Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state() -> None:
    """Initialize session state variables."""
    defaults = {
        "analysis_results": None,
        "resume_text": "",
        "jd_text": "",
        "user_skills": "",
        "active_tab": "Intake",
        "current_step": "intake",
        "input_generation": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "pending_tab" in st.session_state:
        st.session_state["active_tab"] = st.session_state.pop("pending_tab")


def process_resume_file(uploaded_file) -> str:
    """Save uploaded file to temp and extract text."""
    from career_coach.services.resume_parser import ResumeParser

    max_size_bytes = settings.max_pdf_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        raise ValueError(f"Resume file exceeds the {settings.max_pdf_size_mb}MB size limit.")

    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in ResumeParser.SUPPORTED_FORMATS:
        raise ValueError("Unsupported resume format. Upload a PDF, DOCX, or TXT file.")

    file_bytes = uploaded_file.getvalue()
    if len(file_bytes) > max_size_bytes:
        raise ValueError(f"Resume file exceeds the {settings.max_pdf_size_mb}MB size limit.")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    try:
        parser = ResumeParser()
        text = parser.extract_text(tmp_path)
        return text
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def run_analysis(input_data: dict) -> dict:
    """Run the skill gap analysis pipeline."""
    with st.spinner("Analyzing your profile against the job description..."):
        # Get resume text
        resume_text = input_data.get("resume_text", "")
        if input_data.get("resume_file") and not resume_text:
            resume_text = process_resume_file(input_data["resume_file"])
        
        jd_text = input_data["jd_text"]
        user_skills = input_data.get("user_skills", [])
        
        # Run analysis
        service = SkillGapService()
        results = service.analyze(
            resume_text=resume_text,
            jd_text=jd_text,
            user_confirmed_skills=user_skills,
        )
        
        return results


def render_sidebar() -> str:
    """Render sidebar with app info and settings."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0;">🎯 SkillRoute</h2>
            <p class="text-secondary" style="margin: 0.5rem 0;">Career Pivot Coach</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        st.markdown("### Navigate")
        st.radio(
            "Navigate",
            NAVIGATION_ITEMS,
            key="active_tab",
            label_visibility="collapsed",
        )

        st.divider()

        # Status indicators
        st.markdown("### Status")
        
        st.markdown("""
        <div class="status-indicator status-info">
            Deterministic analysis — no AI requests
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="status-indicator status-info">
            Tracker records are plaintext JSON
        </div>
        """, unsafe_allow_html=True)
        st.caption(
            "Single-user demo. Tracker records are plain text and shared by this app instance."
        )
        
        st.divider()
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        def load_sample_data() -> None:
            reset_workspace()
            st.session_state["resume_text"] = SAMPLE_RESUME
            st.session_state["jd_text"] = SAMPLE_JD
            st.session_state["_resume_text"] = SAMPLE_RESUME
            st.session_state["_jd_text"] = SAMPLE_JD

        st.button(
            "Load sample data",
            key="load_sample_data_btn",
            width="stretch",
            on_click=load_sample_data,
        )
        st.button(
            "Reset inputs & results",
            key="reset_workspace_btn",
            width="stretch",
            help="Clears intake text and generated results. Saved tracker applications are kept.",
            on_click=reset_workspace,
        )
        
        st.divider()
        
        # Settings
        with st.expander("Settings"):
            st.caption("Debug Info")
            st.code(f"""
Environment: {settings.app_env}
Debug: {settings.debug}
Max PDF: {settings.max_pdf_size_mb}MB
Max Pages: {settings.max_pdf_pages}
            """)
        
        st.divider()
        
        # Footer
        st.markdown("""
        <div class="text-center text-muted" style="font-size: 0.75rem;">
            SkillRoute v0.1.0<br>
            MIT License
        </div>
        """, unsafe_allow_html=True)

    return st.session_state["active_tab"]


def main() -> None:
    """Main application entry point."""
    apply_theme()
    init_session_state()
    active_tab = render_sidebar()
    
    # Header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>SkillRoute</h1>
        <p class="text-secondary">Turn a target role and evidence of your current skills into a prioritized, explainable plan for becoming a stronger candidate.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if active_tab == "Intake":
        input_data = render_intake_tab()
        
        if input_data:
            try:
                results = run_analysis(input_data)
                st.session_state.analysis_results = results
                st.session_state.current_step = "assessment"
                st.session_state.pending_tab = "Assessment"
                st.rerun()
            except ValueError as exc:
                st.error(f"Unable to analyze these inputs: {exc}")
            except Exception as exc:
                logger.error("Analysis failed (%s)", type(exc).__name__)
                st.error("Analysis failed unexpectedly. Please check your inputs and try again.")
    
    elif active_tab == "Assessment":
        if st.session_state.analysis_results:
            render_results(st.session_state.analysis_results)
        else:
            st.markdown("""
            <div class="skill-card text-center" style="padding: 3rem 2rem;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" style="margin-bottom: 1rem;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                <h3 style="margin-bottom: 0.5rem;">No Analysis Yet</h3>
                <p class="text-secondary">Complete the Intake tab to see your skill gap assessment.</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif active_tab == "Plan":
        render_plan_tab()
    
    elif active_tab == "Interview":
        render_interview_tab()
    
    elif active_tab == "Tracker":
        render_tracker_tab()
    
    elif active_tab == "Dashboard":
        render_dashboard_tab()


# Sample Resume for testing
SAMPLE_RESUME = """Alex Chen
Data Engineer | alex.chen@email.com | github.com/alexchen | linkedin.com/in/alexchen

SUMMARY
Data Engineer with 3 years building scalable data pipelines and platforms. Experience with Python, SQL, Airflow, and AWS. Passionate about data quality, observability, and enabling ML workflows.

TECHNICAL SKILLS
- Languages: Python, SQL, Bash
- Data: Pandas, NumPy, PySpark, PostgreSQL, MySQL
- Orchestration: Apache Airflow (2 years), dbt
- Cloud: AWS (S3, EC2, RDS, Lambda), Docker
- CI/CD: GitHub Actions, GitLab CI
- Tools: Git, Jira, Confluence

EXPERIENCE

Data Engineer | TechCorp Inc. | 2022-Present
- Built and maintain 50+ Airflow DAGs processing 10TB+ daily
- Migrated legacy ETL to PySpark, reducing runtime by 60%
- Implemented data quality checks with Great Expectations
- Designed star schema for analytics warehouse (PostgreSQL)
- Containerized pipelines with Docker, deployed on ECS
- Set up CI/CD with GitHub Actions for automated testing

Junior Data Analyst | StartupXYZ | 2021-2022
- Wrote complex SQL for business intelligence dashboards
- Automated weekly reporting with Python and Pandas
- Collaborated with product team on A/B test analysis
- Built internal tools with Flask and React

EDUCATION
BS Computer Science | State University | 2021
- Relevant coursework: Database Systems, Distributed Systems, Algorithms

PROJECTS
- Real-time Analytics Pipeline: Kafka → Spark Streaming → Cassandra → Grafana
- ML Feature Store: Airflow → Feast → Redis for low-latency serving
"""


if __name__ == "__main__":
    main()