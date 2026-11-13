"""Application tracker service."""

import json
import os
import tempfile
from uuid import UUID, uuid4

from pydantic import ValidationError

from career_coach.domain.schemas import Application, ApplicationStatus
from career_coach.domain.timeutils import utcnow


class ApplicationTracker:
    """Manage job applications with local JSON storage."""

    def __init__(self, storage_path: str = "data/applications.json"):
        self.storage_path = storage_path
        self._applications: list[Application] = []
        self._load()

    def _load(self):
        """Load applications, keeping valid records when the store is damaged."""
        try:
            with open(self.storage_path) as handle:
                data = json.load(handle)
        except FileNotFoundError:
            self._applications = []
            return
        except json.JSONDecodeError:
            self._quarantine()
            self._applications = []
            return

        if not isinstance(data, list):
            self._quarantine()
            self._applications = []
            return

        applications = []
        for record in data:
            try:
                applications.append(Application(**record))
            except (TypeError, ValidationError):
                self._quarantine()
        self._applications = applications

    def _quarantine(self) -> None:
        """Move an unreadable store aside instead of discarding it silently."""
        if not os.path.exists(self.storage_path):
            return
        stem, extension = os.path.splitext(self.storage_path)
        candidate = f"{stem}.corrupt{extension}"
        suffix = 1
        while os.path.exists(candidate):
            candidate = f"{stem}.corrupt.{suffix}{extension}"
            suffix += 1
        try:
            os.replace(self.storage_path, candidate)
        except OSError:
            pass

    def _save(self) -> None:
        """Write atomically so an interrupted write cannot truncate the store."""
        directory = os.path.dirname(self.storage_path) or "."
        temporary_path: str | None = None
        try:
            os.makedirs(directory, exist_ok=True)
            descriptor, temporary_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(descriptor, "w") as handle:
                json.dump(
                    [app.model_dump(mode="json") for app in self._applications],
                    handle,
                    indent=2,
                )
            os.replace(temporary_path, self.storage_path)
        except OSError:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass
            self._load()
            raise

    def create(self, **kwargs) -> Application:
        """Create a new application."""
        now = utcnow()
        kwargs.setdefault("applied_at", now)
        kwargs.setdefault("updated_at", now)
        app = Application(id=uuid4(), **kwargs)
        self._applications.append(app)
        self._save()
        return app

    def get(self, app_id: UUID) -> Application | None:
        """Get application by ID."""
        for app in self._applications:
            if app.id == app_id:
                return app
        return None

    def list_all(self) -> list[Application]:
        """List all applications, most recent first."""
        return sorted(self._applications, key=lambda a: a.applied_at, reverse=True)

    def update_status(self, app_id: UUID, status: ApplicationStatus) -> Application | None:
        """Update application status."""
        app = self.get(app_id)
        if app:
            app.status = status
            app.updated_at = utcnow()
            self._save()
            return app
        return None

    def update(self, app_id: UUID, **kwargs) -> Application | None:
        """Update application fields."""
        app = self.get(app_id)
        if app:
            kwargs.pop("id", None)
            for key, value in kwargs.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            app.updated_at = utcnow()
            self._save()
            return app
        return None

    def delete(self, app_id: UUID) -> bool:
        """Delete an application."""
        app = self.get(app_id)
        if app:
            self._applications.remove(app)
            self._save()
            return True
        return False

    def get_stats(self) -> dict:
        """Get application statistics."""
        total = len(self._applications)
        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "response_rate": 0,
                "interview_rate": 0,
                "offer_rate": 0,
            }

        by_status = {}
        for status in ApplicationStatus:
            count = len([a for a in self._applications if a.status == status])
            if count > 0:
                by_status[status.value] = count

        responded = (
            total
            - by_status.get(ApplicationStatus.APPLIED.value, 0)
            - by_status.get(ApplicationStatus.NO_RESPONSE.value, 0)
        )
        interviews = (
            by_status.get(ApplicationStatus.INTERVIEW_SCHEDULED.value, 0)
            + by_status.get(ApplicationStatus.INTERVIEW_COMPLETED.value, 0)
            + by_status.get(ApplicationStatus.OFFER.value, 0)
        )
        offers = by_status.get(ApplicationStatus.OFFER.value, 0)

        return {
            "total": total,
            "by_status": by_status,
            "response_rate": round(responded / total * 100, 1),
            "interview_rate": round(interviews / total * 100, 1),
            "offer_rate": round(offers / total * 100, 1),
        }


# Global tracker instance
_tracker: ApplicationTracker | None = None


def get_tracker() -> ApplicationTracker:
    """Get the global application tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ApplicationTracker()
    return _tracker
