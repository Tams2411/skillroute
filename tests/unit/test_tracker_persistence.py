"""Regression tests for tracker persistence safety.

Covers the failure modes that previously lost data silently: a truncated or
malformed store, an interrupted write, and an unwritable storage location.
"""

import json
import uuid
from datetime import datetime

import pytest

from career_coach.domain.schemas import ApplicationStatus
from career_coach.domain.timeutils import utcnow
from career_coach.services import tracker_service
from career_coach.services.tracker_service import ApplicationTracker


def _write_store(path, payload):
    path.write_text(payload)


def test_corrupted_store_is_quarantined_not_silently_dropped(tmp_path):
    store = tmp_path / "applications.json"
    _write_store(store, '[{"id": "broken"')

    tracker = ApplicationTracker(str(store))

    assert tracker.list_all() == []
    assert not store.exists(), "corrupt store should have been moved aside"
    assert list(tmp_path.glob("*.corrupt*")), "corrupt store should be preserved"


def test_partial_corruption_keeps_valid_records(tmp_path):
    store = tmp_path / "applications.json"
    valid = {
        "id": str(uuid.uuid4()),
        "company": "Acme",
        "role": "Engineer",
        "status": "applied",
        "applied_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    _write_store(store, json.dumps([valid, {"id": "not-a-record"}]))

    tracker = ApplicationTracker(str(store))

    assert [app.company for app in tracker.list_all()] == ["Acme"]
    assert list(tmp_path.glob("*.corrupt*")), "corrupt store should be preserved"


def test_failed_write_leaves_store_and_memory_consistent(tmp_path, monkeypatch):
    store = tmp_path / "applications.json"
    tracker = ApplicationTracker(str(store))
    tracker.create(company="Acme", role="Engineer")
    original = store.read_text()

    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(tracker_service.json, "dump", boom)

    with pytest.raises(OSError, match="disk full"):
        tracker.create(company="Other", role="Engineer")

    assert store.read_text() == original
    assert not list(tmp_path.glob("*.tmp"))
    assert [app.company for app in tracker.list_all()] == ["Acme"]


def test_missing_storage_directory_is_created(tmp_path):
    store = tmp_path / "nested" / "dir" / "applications.json"

    tracker = ApplicationTracker(str(store))
    tracker.create(company="Acme", role="Engineer")

    assert store.exists()


def test_unwritable_store_raises_instead_of_failing_silently(tmp_path, monkeypatch):
    """An unwritable storage location must surface, not silently drop, the write.

    The failure is injected at ``tempfile.mkstemp`` rather than with chmod: the
    store is written via a temp file plus ``os.replace``, so on POSIX a read-only
    *file* is still replaceable while its directory is writable, and chmod on a
    directory is not enforced on Windows.
    """
    store = tmp_path / "applications.json"
    tracker = ApplicationTracker(str(store))
    tracker.create(company="Acme", role="Engineer")
    original = store.read_text()

    def denied(*args, **kwargs):
        raise PermissionError("read-only filesystem")

    monkeypatch.setattr(tracker_service.tempfile, "mkstemp", denied)

    with pytest.raises(PermissionError):
        tracker.create(company="Other", role="Engineer")

    assert store.read_text() == original
    assert [app.company for app in tracker.list_all()] == ["Acme"]


def test_timestamps_are_timezone_aware(tmp_path):
    tracker = ApplicationTracker(str(tmp_path / "applications.json"))
    application = tracker.create(company="Acme", role="Engineer")

    assert application.applied_at.tzinfo is not None
    assert application.updated_at.tzinfo is not None


def test_naive_timestamps_from_older_stores_are_normalized(tmp_path):
    store = tmp_path / "applications.json"
    record = {
        "id": str(uuid.uuid4()),
        "company": "Acme",
        "role": "Engineer",
        "status": "applied",
        "applied_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    _write_store(store, json.dumps([record]))

    tracker = ApplicationTracker(str(store))
    application = tracker.list_all()[0]

    assert application.applied_at.tzinfo is not None
    assert application.updated_at.tzinfo is not None


def test_update_cannot_change_the_primary_key(tmp_path):
    tracker = ApplicationTracker(str(tmp_path / "applications.json"))
    application = tracker.create(company="Acme", role="Engineer")
    original_id = application.id

    tracker.update(application.id, id=uuid.uuid4())

    stored = tracker.get(original_id)
    assert stored is not None
    assert stored.company == "Acme"


def test_offer_rate_counts_offers(tmp_path):
    tracker = ApplicationTracker(str(tmp_path / "applications.json"))
    tracker.create(company="Acme", role="Engineer", status=ApplicationStatus.OFFER)

    assert tracker.get_stats()["offer_rate"] == 100.0


def test_round_trip_preserves_datetime_precision(tmp_path):
    store = tmp_path / "applications.json"
    tracker = ApplicationTracker(str(store))
    application = tracker.create(company="Acme", role="Engineer")
    application_id = application.id

    reloaded = ApplicationTracker(str(store))
    stored = reloaded.get(application_id)

    assert stored is not None
    assert stored.applied_at == application.applied_at


def test_list_all_sorts_mixed_naive_and_aware_stores(tmp_path):
    store = tmp_path / "applications.json"
    older = {
        "id": str(uuid.uuid4()),
        "company": "Older",
        "role": "Engineer",
        "status": "applied",
        "applied_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    _write_store(store, json.dumps([older]))

    tracker = ApplicationTracker(str(store))
    tracker.create(company="Newer", role="Engineer")

    assert [app.company for app in tracker.list_all()] == ["Newer", "Older"]


def test_create_uses_current_utc_time(tmp_path):
    tracker = ApplicationTracker(str(tmp_path / "applications.json"))
    before = datetime.now(utcnow().tzinfo)

    application = tracker.create(company="Acme", role="Engineer")

    assert application.applied_at >= before


def test_naive_applied_at_does_not_break_sorting(tmp_path):
    """A form-supplied naive applied_at must not crash list_all()."""
    store = tmp_path / "applications.json"
    store.write_text(
        json.dumps(
            [
                {
                    "id": str(uuid.uuid4()),
                    "company": "Old Corp",
                    "role": "Engineer",
                    "jd_text": "",
                    "status": "applied",
                    "applied_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "notes": "",
                }
            ]
        ),
        encoding="utf-8",
    )
    tracker = ApplicationTracker(str(store))

    tracker.create(company="New Corp", role="Engineer", applied_at=datetime(2026, 2, 1))

    listed = tracker.list_all()
    assert [app.company for app in listed] == ["New Corp", "Old Corp"]
    assert all(app.applied_at.tzinfo is not None for app in listed)
    assert json.loads(store.read_text(encoding="utf-8"))[1]["applied_at"].endswith("Z")
