"""Integration tests for the deterministic analysis workflow."""

from career_coach.domain.schemas import SkillGap
from career_coach.services.interview_service import generate_interview_session
from career_coach.services.plan_generator import generate_learning_plan
from career_coach.services.skill_gap_service import SkillGapService


def test_analysis_generates_role_specific_plan_and_interview(sample_resume_text, sample_jd_text):
    results = SkillGapService().analyze(
        resume_text=sample_resume_text,
        jd_text=sample_jd_text,
    )

    required_skills = {
        skill["canonical_skill"] for skill in results["all_gaps"] if skill["role_relevance"] >= 0.7
    }
    preferred_skills = {
        skill["canonical_skill"] for skill in results["all_gaps"] if skill["role_relevance"] < 0.7
    }

    assert results["total_jd_skills"] > 0
    assert results["readiness_state"] == "available"
    assert 0.0 <= results["readiness_score"] <= 1.0
    assert 0 <= results["readiness_percentage"] <= 100
    assert results["gaps"]
    assert "kafka" in preferred_skills
    assert "kafka" not in required_skills
    assert results["top_gaps"]

    gaps = [SkillGap.model_validate(gap) for gap in results["gaps"]]
    plan = generate_learning_plan(gaps, weeks=4, hours_per_week=10)
    sessions = generate_interview_session(
        gaps,
        target_role="Senior Data Engineer",
        max_skills=2,
        questions_per_skill=1,
    )

    assert plan
    assert all(task.week <= 4 for task in plan)
    assert sessions
    assert all(session.target_role == "Senior Data Engineer" for session in sessions)


def test_analysis_with_no_extracted_requirements_reports_insufficient_data(sample_resume_text):
    results = SkillGapService().analyze(
        resume_text=sample_resume_text,
        jd_text="A supportive team, flexible hours, and competitive benefits.",
    )

    assert results["total_jd_skills"] == 0
    assert results["readiness_state"] == "insufficient_data"
    assert results["readiness_score"] is None
    assert results["readiness_percentage"] is None


def test_confirmed_demonstrated_skill_is_verified_and_strength_is_numeric():
    results = SkillGapService().analyze(
        resume_text="Built production services with Python.",
        jd_text="Required Skills:\n- Python",
        user_confirmed_skills=["python"],
    )

    python = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "python"
    )

    assert python["evidence_level"] == "verified"
    assert python["evidence_strength"] == 0.9


def test_user_confirmed_skill_becomes_verified_evidence(sample_jd_text):
    results = SkillGapService().analyze(
        resume_text="Career changer seeking a data engineering role.",
        jd_text=sample_jd_text,
        user_confirmed_skills=["kafka"],
    )

    kafka = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "kafka"
    )
    assert kafka["evidence_level"] == "verified"
    assert kafka["user_confirmed"] is True
