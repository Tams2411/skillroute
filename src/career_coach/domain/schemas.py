"""Domain schemas and data contracts."""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime
from uuid import UUID, uuid4


class EvidenceLevel(str, Enum):
    """Strength of evidence for a skill."""
    NONE = "none"
    MENTIONED = "mentioned"
    SELF_REPORTED = "self_reported"
    DEMONSTRATED = "demonstrated"
    VERIFIED = "verified"


class ApplicationStatus(str, Enum):
    """Application status values."""
    APPLIED = "applied"
    ASSESSMENT_RECEIVED = "assessment_received"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    REJECTED = "rejected"
    OFFER = "offer"
    WITHDREW = "withdrew"
    NO_RESPONSE = "no_response"


class InterviewCriterion(str, Enum):
    """Interview rubric criteria."""
    TECHNICAL_CORRECTNESS = "technical_correctness"
    REASONING_TRADEOFFS = "reasoning_tradeoffs"
    SPECIFICITY_EVIDENCE = "specificity_evidence"
    STRUCTURE_CLARITY = "structure_clarity"
    FAILURE_AWARENESS = "failure_awareness"


class SkillEvidence(BaseModel):
    """Evidence for a skill from resume/profile."""
    model_config = ConfigDict(extra="forbid")

    canonical_skill: str = Field(min_length=1, max_length=80)
    evidence_level: EvidenceLevel
    source: str = Field(min_length=1, max_length=40)
    supporting_evidence: str = Field(default="", max_length=1200)
    user_confirmed: bool = False


class JobSkillRequirement(BaseModel):
    """A skill required by a job description."""
    model_config = ConfigDict(extra="forbid")

    canonical_skill: str = Field(min_length=1, max_length=80)
    importance: float = Field(ge=0.0, le=1.0)
    evidence_phrase: str = Field(default="", max_length=500)
    extraction_confidence: float = Field(ge=0.0, le=1.0)


class SkillGap(BaseModel):
    """A prioritized skill gap with rationale."""
    model_config = ConfigDict(extra="forbid")

    canonical_skill: str = Field(min_length=1, max_length=80)
    role_relevance: float = Field(ge=0.0, le=1.0)
    evidence_strength: float = Field(ge=0.0, le=1.0)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    priority: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=500)
    uncertainty: str = Field(default="", max_length=500)
    jd_evidence: str = Field(default="", max_length=500)
    resume_evidence: str = Field(default="", max_length=500)


class LearningTask(BaseModel):
    """A single learning task in the weekly plan."""
    model_config = ConfigDict(extra="forbid")

    week: int = Field(ge=1)
    skill: str = Field(min_length=1, max_length=80)
    focus: str = Field(min_length=1, max_length=200)
    learning_task: str = Field(min_length=1, max_length=500)
    practice_task: str = Field(min_length=1, max_length=500)
    deliverable: str = Field(min_length=1, max_length=300)
    acceptance_criteria: str = Field(min_length=1, max_length=500)
    estimated_hours: float = Field(ge=0.5, le=40.0)
    dependencies: list[str] = Field(default_factory=list)
    completed: bool = False


class ProjectRecommendation(BaseModel):
    """A portfolio project recommendation."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    targeted_skills: list[str] = Field(min_length=1)
    reasoning: str = Field(min_length=1, max_length=1000)
    scope: str = Field(min_length=1, max_length=500)
    deliverables: list[str] = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)
    estimated_hours: float = Field(ge=1.0, le=200.0)
    difficulty: str = Field(pattern="^(beginner|intermediate|advanced)$")
    limitations: str = Field(default="", max_length=500)
    stretch_goals: list[str] = Field(default_factory=list)


class InterviewRubricScore(BaseModel):
    """Score for a single interview criterion."""
    model_config = ConfigDict(extra="forbid")

    criterion: InterviewCriterion
    score: int = Field(ge=1, le=5)
    evidence: str = Field(min_length=1, max_length=1000)
    improvement_action: str = Field(min_length=1, max_length=500)


class InterviewSession(BaseModel):
    """A complete mock interview session."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    target_role: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    question_type: Literal["technical", "behavioral"] = "technical"
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(default="", max_length=5000)
    scores: list[InterviewRubricScore] = Field(default_factory=list)
    overall_feedback: str = Field(default="", max_length=2000)
    practice_task: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = False


class Application(BaseModel):
    """A job application record."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=100)
    jd_text: str = Field(default="", max_length=10000)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = Field(default="", max_length=2000)


class ApplicationEvent(BaseModel):
    """An append-only event for application status changes."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    application_id: UUID
    event_type: ApplicationStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    note: str = Field(default="", max_length=1000)
    source: str = Field(default="user_entered", max_length=30)
    explicit_feedback: str = Field(default="", max_length=2000)


class FeedbackHypothesis(BaseModel):
    """A hypothesis generated from outcome patterns."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    observation: str = Field(min_length=1, max_length=1000)
    sample_size: int = Field(ge=1)
    uncertainty: str = Field(min_length=1, max_length=500)
    suggested_experiment: str = Field(min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Profile(BaseModel):
    """User profile with target role and preferences."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    target_role: str = Field(min_length=1, max_length=100)
    seniority: str = Field(default="junior", max_length=30)
    timeline_weeks: int = Field(default=12, ge=1, le=52)
    available_hours_per_week: int = Field(default=10, ge=1, le=40)
    preferences: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobTarget(BaseModel):
    """Target job with JD text."""
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    profile_id: UUID
    role: str = Field(min_length=1, max_length=100)
    jd_text: str = Field(min_length=1, max_length=10000)
    source: str = Field(default="manual", max_length=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)