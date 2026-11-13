"""Tests for timezone-aware timestamp helpers."""

from datetime import UTC, datetime

from career_coach.domain.timeutils import utcnow


def test_utcnow_returns_timezone_aware_datetime():
    now = utcnow()

    assert now.tzinfo is not None
    assert now.utcoffset() == datetime.now(UTC).utcoffset()


def test_utcnow_is_comparable_with_other_aware_datetimes():
    """The tracker crash came from comparing a naive and an aware datetime."""
    assert utcnow() > datetime(2000, 1, 1, tzinfo=UTC)
