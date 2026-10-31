"""Integration tests for application tracker persistence."""

from career_coach.domain.schemas import ApplicationStatus
from career_coach.services.tracker_service import ApplicationTracker


def test_application_status_and_notes_survive_reload(tmp_path):
    storage_path = tmp_path / "applications.json"
    tracker = ApplicationTracker(str(storage_path))

    application = tracker.create(
        company="Example Corp",
        role="Data Engineer",
        notes="Applied through a referral",
    )
    tracker.update_status(application.id, ApplicationStatus.INTERVIEW_SCHEDULED)

    reloaded = ApplicationTracker(str(storage_path))
    saved_application = reloaded.get(application.id)

    assert saved_application is not None
    assert saved_application.status is ApplicationStatus.INTERVIEW_SCHEDULED
    assert saved_application.notes == "Applied through a referral"
    assert reloaded.get_stats()["total"] == 1
