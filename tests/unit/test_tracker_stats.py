"""Regression tests for tracker statistics and stored JD bounds."""

import pytest
from pydantic import ValidationError

from career_coach.domain.schemas import Application, ApplicationStatus
from career_coach.services.tracker_service import ApplicationTracker


def test_response_rate_excludes_pending_and_no_response_and_offers_count_as_interviews(tmp_path):
    tracker = ApplicationTracker(str(tmp_path / "applications.json"))
    for status in (
        ApplicationStatus.APPLIED,
        ApplicationStatus.NO_RESPONSE,
        ApplicationStatus.REJECTED,
        ApplicationStatus.INTERVIEW_SCHEDULED,
        ApplicationStatus.OFFER,
    ):
        tracker.create(company=status.value, role="Engineer", status=status)

    stats = tracker.get_stats()

    assert stats["response_rate"] == 60.0
    assert stats["interview_rate"] == 40.0


def test_application_accepts_job_descriptions_up_to_parser_limit():
    app = Application(company="Example", role="Engineer", jd_text="x" * 10_000)

    assert len(app.jd_text) == 10_000
    with pytest.raises(ValidationError):
        Application(company="Example", role="Engineer", jd_text="x" * 10_001)
