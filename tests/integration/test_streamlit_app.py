"""End-to-end tests for the Streamlit app workflow."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_sample_workflow_generates_assessment_plan_and_interview():
    app_path = Path(__file__).parents[2] / "app.py"

    intake_app = AppTest.from_file(str(app_path), default_timeout=15).run()
    assert not intake_app.exception

    intake_app.sidebar.button[0].click().run()
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
