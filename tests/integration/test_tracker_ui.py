"""UI tests for the Application Tracker tab.

The tracker tab renders through ``render_tracker_tab``; the module-level
``get_tracker`` singleton is replaced with a store backed by ``tmp_path`` so
each test starts from known state.
"""

import pytest
from streamlit.testing.v1 import AppTest

import career_coach.ui.tracker as tracker_ui
from career_coach.services.tracker_service import ApplicationTracker


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    store = ApplicationTracker(str(tmp_path / "applications.json"))
    monkeypatch.setattr(tracker_ui, "get_tracker", lambda: store)
    return store


def _launch(tmp_path):
    script = tmp_path / "tracker_app.py"
    script.write_text(
        "from career_coach.ui.tracker import render_tracker_tab\nrender_tracker_tab()\n",
        encoding="utf-8",
    )
    app = AppTest.from_file(str(script), default_timeout=30)
    app.run()
    return app


def test_empty_state_renders_without_error(tmp_path, tracker):
    app = _launch(tmp_path)

    assert not app.exception
    assert tracker.list_all() == []


def test_add_application_persists(tmp_path, tracker):
    app = _launch(tmp_path)

    app.text_input(key="_tracker_company").set_value("Acme Corp")
    app.text_input(key="_tracker_role").set_value("Data Engineer")
    app.text_area(key="_tracker_notes").set_value("Referred by Sam")
    app.form_submit_button(key="_tracker_add").click()
    app.run()

    assert not app.exception
    apps = tracker.list_all()
    assert len(apps) == 1
    assert apps[0].company == "Acme Corp"
    assert apps[0].role == "Data Engineer"
    assert apps[0].notes == "Referred by Sam"


def test_add_application_requires_company_and_role(tmp_path, tracker):
    app = _launch(tmp_path)

    app.form_submit_button(key="_tracker_add").click()
    app.run()

    assert not app.exception
    assert tracker.list_all() == []
    assert app.error


def test_status_change_persists(tmp_path, tracker):
    created = tracker.create(company="Acme Corp", role="Data Engineer")
    app = _launch(tmp_path)

    app.selectbox(key=f"status_{created.id}").set_value("interview_scheduled")
    app.run()

    assert not app.exception
    assert tracker.get(created.id).status.value == "interview_scheduled"


def test_notes_edit_persists(tmp_path, tracker):
    created = tracker.create(company="Acme Corp", role="Data Engineer")
    app = _launch(tmp_path)

    app.text_area(key=f"notes_{created.id}").set_value("Recruiter called on Monday")
    app.run()

    assert not app.exception
    assert tracker.get(created.id).notes == "Recruiter called on Monday"


def test_delete_removes_application(tmp_path, tracker):
    created = tracker.create(company="Acme Corp", role="Data Engineer")
    app = _launch(tmp_path)

    app.button(key=f"del_{created.id}").click()
    app.run()

    assert not app.exception
    assert tracker.list_all() == []


def test_filter_selectbox_renders_with_applications(tmp_path, tracker):
    tracker.create(company="Acme Corp", role="Data Engineer")
    app = _launch(tmp_path)

    assert not app.exception
    assert app.selectbox(key="tracker_filter").value == "All"
