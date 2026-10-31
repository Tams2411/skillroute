"""SkillRoute - Career Pivot Coach Main Application."""

import streamlit as st
import tempfile
import os

from career_coach.config import settings
from career_coach.services.skill_gap_service import SkillGapService
from career_coach.ui.intake import render_intake_tab, render_results, SAMPLE_JD
from career_coach.ui.theme import (
    render_section_header, render_alert, render_empty_state
)


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
        "user_skills": [],
        "current_step": "intake",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def process_resume_file(uploaded_file) -> str:
    """Save uploaded file to temp and extract text."""
    from career_coach.services.resume_parser import ResumeParser
    
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{uploaded_file.name.split('.')[-1]}"
    ) as tmp:
        tmp.write(uploaded_file.getvalue())
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


def render_sidebar() -> None:
    """Render sidebar with app info and settings."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0;">🎯 SkillRoute</h2>
            <p class="text-secondary" style="margin: 0.5rem 0;">Career Pivot Coach</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Status indicators
        st.markdown("### Status")
        
        # AI Provider status
        if settings.has_ai_provider:
            provider, _ = settings.get_primary_provider()
            st.markdown(f"""
            <div class="status-indicator status-success">
                {provider.title()} configured
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-indicator status-warning">
                No AI provider (deterministic mode)
            </div>
            """, unsafe_allow_html=True)
        
        # Database status
        st.markdown("""
        <div class="status-indicator status-info">
            SQLite (local)
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state.resume_text = SAMPLE_RESUME
            st.session_state.jd_text = SAMPLE_JD
            st.rerun()
        
        if st.button("Clear All", use_container_width=True):
            for key in ["analysis_results", "resume_text", "jd_text", "user_skills"]:
                st.session_state[key] = "" if key != "analysis_results" else None
            st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("Settings"):
            st.caption("Debug Info")
            st.code(f"""
Environment: {settings.app_env}
Debug: {settings.debug}
DB: {settings.database_url}
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


def main() -> None:
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    
    # Header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>SkillRoute</h1>
        <p class="text-secondary">Turn a target role and evidence of your current skills into a prioritized, explainable plan for becoming a stronger candidate.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tabs = st.tabs([
        "📥 Intake",
        "📊 Assessment",
        "📅 Plan",
        "🎤 Interview",
        "📋 Tracker",
        "📈 Dashboard",
    ])
    
    # Tab 1: Intake
    with tabs[0]:
        input_data = render_intake_tab()
        
        if input_data:
            try:
                results = run_analysis(input_data)
                st.session_state.analysis_results = results
                st.session_state.current_step = "assessment"
                st.rerun()
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.exception(e)
    
    # Tab 2: Assessment
    with tabs[1]:
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
    
    # Tab 3: Plan (placeholder)
    with tabs[2]:
        st.markdown(render_section_header(
            "Learning Plan",
            "Weekly learning tasks generated from your top skill gaps",
            icon="book-open"
        ), unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            st.markdown(render_alert(
                "Learning plan generation coming in next phase. Top gaps will be converted to weekly tasks with deliverables and acceptance criteria.",
                "info", "info"
            ), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "Complete Assessment First",
                "Run the skill gap analysis to generate a personalized learning plan.",
                "target"
            ), unsafe_allow_html=True)
    
    # Tab 4: Interview (placeholder)
    with tabs[3]:
        st.markdown(render_section_header(
            "Mock Interview",
            "Practice behavioral and technical questions with rubric-based feedback",
            icon="clipboard-list"
        ), unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            st.markdown(render_alert(
                "Mock interview coming in next phase. Questions will target your top skill gaps with a visible 1-5 rubric.",
                "info", "info"
            ), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "Complete Assessment First",
                "Run the skill gap analysis to enable targeted interview practice.",
                "target"
            ), unsafe_allow_html=True)
    
    # Tab 5: Tracker (placeholder)
    with tabs[4]:
        st.markdown(render_section_header(
            "Application Tracker",
            "Track applications, record status events, and capture feedback",
            icon="folder-open"
        ), unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            st.markdown(render_alert(
                "Application tracker coming in next phase. Append-only event log with guardrails against causal fallacy.",
                "info", "info"
            ), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "Complete Assessment First",
                "Run the skill gap analysis to start tracking applications for this role.",
                "target"
            ), unsafe_allow_html=True)
    
    # Tab 6: Dashboard (placeholder)
    with tabs[5]:
        st.markdown(render_section_header(
            "Progress Dashboard",
            "Overview of your pivot journey: gaps, plan progress, interview history, application funnel",
            icon="trending-up"
        ), unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            st.markdown(render_alert(
                "Dashboard coming in next phase. Will show readiness trend, plan completion, interview scores, and application funnel.",
                "info", "info"
            ), unsafe_allow_html=True)
        else:
            st.markdown(render_empty_state(
                "Complete Assessment First",
                "Run the skill gap analysis to see your progress dashboard.",
                "target"
            ), unsafe_allow_html=True)


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