"""Helpers for resetting analysis state shared across app pages."""

import streamlit as st


def clear_analysis_state() -> None:
    """Clear generated analysis and derived learning/interview results."""
    state_defaults: dict[str, object] = {
        "analysis_results": None,
        "learning_plan": None,
        "project_recommendations": None,
        "interview_sessions": None,
        "interview_current": 0,
        "interview_ai_feedback": {},
        "show_interview_results": False,
    }
    for key, value in state_defaults.items():
        st.session_state[key] = value

    for state_key in list(st.session_state):
        if isinstance(state_key, str) and state_key.startswith(("answer_", "score_")):
            del st.session_state[state_key]


def reset_workspace() -> None:
    """Clear intake inputs and derived results without deleting tracker records."""
    clear_analysis_state()
    for key in ("resume_text", "jd_text", "user_skills", "_resume_text", "_jd_text", "_user_skills"):
        st.session_state[key] = ""

    st.session_state["input_generation"] = st.session_state.get("input_generation", 0) + 1
    st.session_state["active_tab"] = "Intake"
    st.session_state["current_step"] = "intake"
    st.session_state.pop("pending_tab", None)
