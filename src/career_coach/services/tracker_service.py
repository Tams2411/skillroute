"""Application tracker service."""

from career_coach.domain.schemas import Application, ApplicationStatus
from datetime import datetime
from uuid import uuid4
from typing import Optional
import json


class ApplicationTracker:
    """Manage job applications with local JSON storage."""
    
    def __init__(self, storage_path: str = "data/applications.json"):
        self.storage_path = storage_path
        self._applications: list[Application] = []
        self._load()
    
    def _load(self):
        """Load applications from JSON file."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self._applications = [Application(**app) for app in data]
        except FileNotFoundError:
            self._applications = []
        except json.JSONDecodeError:
            self._applications = []
    
    def _save(self):
        """Save applications to JSON file."""
        data = [app.model_dump() for app in self._applications]
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create(self, **kwargs) -> Application:
        """Create a new application."""
        app = Application(
            id=uuid4(),
            applied_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **kwargs
        )
        self._applications.append(app)
        self._save()
        return app
    
    def get(self, app_id: uuid4) -> Optional[Application]:
        """Get application by ID."""
        for app in self._applications:
            if app.id == app_id:
                return app
        return None
    
    def list_all(self) -> list[Application]:
        """List all applications, most recent first."""
        return sorted(self._applications, key=lambda a: a.applied_at, reverse=True)
    
    def list_by_status(self, status: ApplicationStatus) -> list[Application]:
        """List applications by status."""
        return [a for a in self._applications if a.status == status]
    
    def update_status(self, app_id: uuid4, status: ApplicationStatus) -> Optional[Application]:
        """Update application status."""
        app = self.get(app_id)
        if app:
            app.status = status
            app.updated_at = datetime.utcnow()
            self._save()
            return app
        return None
    
    def update(self, app_id: uuid4, **kwargs) -> Optional[Application]:
        """Update application fields."""
        app = self.get(app_id)
        if app:
            for key, value in kwargs.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            app.updated_at = datetime.utcnow()
            self._save()
            return app
        return None
    
    def delete(self, app_id: uuid4) -> bool:
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
        
        responded = total - by_status.get("no_response", 0)
        interviews = by_status.get("interview_scheduled", 0) + by_status.get("interview_completed", 0)
        offers = by_status.get("offer", 0)
        
        return {
            "total": total,
            "by_status": by_status,
            "response_rate": round(responded / total * 100, 1),
            "interview_rate": round(interviews / total * 100, 1),
            "offer_rate": round(offers / total * 100, 1),
        }


# Global tracker instance
_tracker: Optional[ApplicationTracker] = None


def get_tracker() -> ApplicationTracker:
    """Get the global application tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ApplicationTracker()
    return _tracker