"""End-to-end tests for the Streamlit app workflow."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from career_coach.domain.schemas import (
    InterviewCriterion,
    InterviewRubricScore,
    InterviewSession,
    SkillGap,
)
from career_coach.services.gemini_interview_service import (
    GeminiFeedbackError,
    GeminiInterviewFeedback,
)


@pytest.mark.parametrize("active_tab", ["Assessment", "Plan", "Interview", "Dashboard"])
def test_insufficient_requirements_are_not_presented_as_readiness(active_tab):
    app_path = Path(__file__).parents[2] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {
        "readiness_state": "insufficient_data",
        "readiness_score": None,
        "readiness_percentage": None,
        "total_jd_skills": 0,
        "gaps": [],
        "all_gaps": [],
        "top_gaps": [],
        "actionable_gaps": [],
        "matched_skills": [],
        "missing_skills": [],
    }
    app.session_state["active_tab"] = active_tab

    app.run()

    assert not app.exception
    messages = "\n".join(element.value for element in app.markdown)
    messages += "\n" + "\n".join(element.value for element in app.warning)
    assert "Insufficient data" in messages
    assert "well-prepared" not in messages
    assert "100%" not in messages


def test_sample_workflow_generates_assessment_plan_and_interview():
    app_path = Path(__file__).parents[2] / "app.py"

    intake_app = AppTest.from_file(str(app_path), default_timeout=15).run()
    assert not intake_app.exception

    intake_app.button(key="load_sample_data_btn").click().run()
    assert len(intake_app.session_state["resume_text"]) > 0
    assert len(intake_app.session_state["jd_text"]) > 0

    intake_app.button(key="analyze_btn").click().run()
    assert intake_app.session_state["analysis_results"]
    assert not intake_app.exception

    analysis_results = intake_app.session_state["analysis_results"]
    plan_app = AppTest.from_file(str(app_path), default_timeout=15)
    plan_app.session_state["analysis_results"] = analysis_results
    plan_app.session_state["active_tab"] = "Plan"
    plan_app.run()
    plan_app.button(key="generate_plan_btn").click().run()
    assert plan_app.session_state["learning_plan"]
    assert plan_app.session_state["project_recommendations"]
    assert not plan_app.exception

    interview_app = AppTest.from_file(str(app_path), default_timeout=15)
    interview_app.session_state["analysis_results"] = analysis_results
    interview_app.session_state["active_tab"] = "Interview"
    interview_app.run()
    interview_app.button(key="gen_interview_btn").click().run()
    assert interview_app.session_state["interview_sessions"]
    assert not interview_app.exception


def test_load_sample_jd_updates_widget_state_without_exception():
    app_path = Path(__file__).parents[2] / "app.py"

    app = AppTest.from_file(str(app_path), default_timeout=15).run()
    app.button(key="sample_jd").click().run()

    assert not app.exception
    assert len(app.session_state["jd_text"]) > 0


def test_loading_sample_data_clears_previous_analysis_and_confirmed_skills():
    app_path = Path(__file__).parents[2] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {"gaps": [{"canonical_skill": "old"}]}
    app.session_state["learning_plan"] = ["old plan"]
    app.session_state["project_recommendations"] = ["old project"]
    app.session_state["interview_sessions"] = ["old interview"]
    app.session_state["user_skills"] = "old skill"
    app.run()

    app.button(key="load_sample_data_btn").click().run()

    assert not app.exception
    assert app.session_state["analysis_results"] is None
    assert app.session_state["learning_plan"] is None
    assert app.session_state["project_recommendations"] is None
    assert app.session_state["interview_sessions"] is None
    assert app.session_state["user_skills"] == ""
    assert app.session_state["active_tab"] == "Intake"
    assert app.session_state["resume_text"]
    assert app.session_state["jd_text"]


def test_reset_inputs_and_results_keeps_tracker_storage_out_of_scope():
    app_path = Path(__file__).parents[2] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["resume_text"] = "resume"
    app.session_state["jd_text"] = "job description"
    app.session_state["user_skills"] = "python"
    app.session_state["analysis_results"] = {"gaps": []}
    app.session_state["learning_plan"] = ["old plan"]
    app.run()

    app.button(key="reset_workspace_btn").click().run()

    assert not app.exception
    assert app.session_state["resume_text"] == ""
    assert app.session_state["jd_text"] == ""
    assert app.session_state["user_skills"] == ""
    assert app.session_state["analysis_results"] is None
    assert app.session_state["learning_plan"] is None
    assert app.session_state["input_generation"] == 1
    assert app.session_state["active_tab"] == "Intake"


def test_changing_intake_input_invalidates_generated_results():
    app_path = Path(__file__).parents[2] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {"gaps": []}
    app.session_state["learning_plan"] = ["old plan"]
    app.run()

    app.text_area(key="_jd_text").set_value("Updated job description").run()

    assert not app.exception
    assert app.session_state["analysis_results"] is None
    assert app.session_state["learning_plan"] is None


def test_dashboard_quick_action_navigates_to_intake():
    app_path = Path(__file__).parents[2] / "app.py"

    app = AppTest.from_file(str(app_path), default_timeout=30).run()
    app.radio(key="active_tab").set_value("Dashboard").run()

    assert any("Dashboard" in element.value for element in app.markdown)
    app.button(key="goto_intake_dashboard").click().run()

    assert not app.exception
    assert app.session_state["active_tab"] == "Intake"


def test_intake_inputs_survive_navigation_away_and_back():
    app_path = Path(__file__).parents[2] / "app.py"

    app = AppTest.from_file(str(app_path), default_timeout=30).run()
    app.text_area(key="_resume_text").set_value("Python and SQL experience").run()
    app.text_area(key="_jd_text").set_value("Required Skills:\n- Terraform").run()
    app.radio(key="active_tab").set_value("Dashboard").run()

    assert app.session_state["resume_text"] == "Python and SQL experience"
    assert app.session_state["jd_text"] == "Required Skills:\n- Terraform"

    app.session_state["active_tab"] = "Intake"
    app.run()
    assert app.text_area(key="_resume_text").value == "Python and SQL experience"
    assert app.text_area(key="_jd_text").value == "Required Skills:\n- Terraform"


def test_interview_feedback_is_optional_and_defaults_to_deterministic():
    app_path = Path(__file__).parents[2] / "app.py"
    gap = SkillGap(
        canonical_skill="terraform",
        role_relevance=0.8,
        evidence_strength=0.0,
        extraction_confidence=1.0,
        priority=0.8,
        reason="Required for the role",
    )
    session = InterviewSession(
        target_role="Platform Engineer",
        category="terraform",
        question="How would you organize Terraform state?",
        answer="I would isolate state by environment.",
    )

    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {"gaps": [gap.model_dump()]}
    app.session_state["interview_sessions"] = [session]
    app.session_state["active_tab"] = "Interview"
    app.run()

    assert not app.exception
    assert app.session_state["gemini_api_key"] == ""
    assert app.session_state["gemini_interview_consent"] is False
    assert not any(button.label == "Get Gemini feedback" for button in app.button)


def test_gemini_credentials_can_be_cleared_from_session():
    app_path = Path(__file__).parents[2] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["gemini_api_key"] = "temporary-user-key"
    app.session_state["gemini_interview_consent"] = True
    app.run()

    app.button(key="clear_gemini_credentials").click().run()

    assert not app.exception
    assert app.session_state["gemini_api_key"] == ""
    assert app.session_state["gemini_interview_consent"] is False


def test_gemini_feedback_renders_as_advisory_without_replacing_self_scores(monkeypatch):
    app_path = Path(__file__).parents[2] / "app.py"
    gap = SkillGap(
        canonical_skill="terraform",
        role_relevance=0.8,
        evidence_strength=0.0,
        extraction_confidence=1.0,
        priority=0.8,
        reason="Required for the role",
    )
    session = InterviewSession(
        target_role="Platform Engineer",
        category="terraform",
        question="How would you organize Terraform state?",
        answer="I would isolate state by environment.",
    )
    feedback = GeminiInterviewFeedback(
        scores=[
            InterviewRubricScore(
                criterion=InterviewCriterion.STRUCTURE_CLARITY,
                score=4,
                evidence="The answer is concise.",
                improvement_action="Explain the environment boundary.",
            )
        ],
        overall_feedback="A useful starting point.",
        practice_task="Add one example of an environment boundary.",
    )
    monkeypatch.setattr(
        "career_coach.ui.interview.generate_gemini_interview_feedback",
        lambda *args: feedback,
    )

    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {"gaps": [gap.model_dump()]}
    app.session_state["interview_sessions"] = [session]
    app.session_state["gemini_api_key"] = "test-key"
    app.session_state["gemini_interview_consent"] = True
    app.session_state["active_tab"] = "Interview"
    app.run()
    app.button(key="gemini_feedback_0").click().run()

    assert not app.exception
    assert app.session_state["interview_ai_feedback"][str(session.id)]["feedback"] == feedback
    assert any("Gemini suggestions" in element.value for element in app.markdown)


def test_gemini_provider_error_keeps_deterministic_interview_available(monkeypatch):
    app_path = Path(__file__).parents[2] / "app.py"
    gap = SkillGap(
        canonical_skill="terraform",
        role_relevance=0.8,
        evidence_strength=0.0,
        extraction_confidence=1.0,
        priority=0.8,
        reason="Required for the role",
    )
    session = InterviewSession(
        target_role="Platform Engineer",
        category="terraform",
        question="How would you organize Terraform state?",
        answer="I would isolate state by environment.",
    )

    def fail_with_provider_error(*args):
        raise GeminiFeedbackError("rate_limited", "Gemini quota or rate limit reached.")

    monkeypatch.setattr(
        "career_coach.ui.interview.generate_gemini_interview_feedback",
        fail_with_provider_error,
    )

    app = AppTest.from_file(str(app_path), default_timeout=15)
    app.session_state["analysis_results"] = {"gaps": [gap.model_dump()]}
    app.session_state["interview_sessions"] = [session]
    app.session_state["gemini_api_key"] = "test-key"
    app.session_state["gemini_interview_consent"] = True
    app.session_state["active_tab"] = "Interview"
    app.run()
    app.button(key="gemini_feedback_0").click().run()

    assert not app.exception
    assert any(
        "deterministic self-evaluation remains available" in item.value
        for item in app.warning
    )
    assert any("not an automatic grade" in item.value for item in app.caption)
