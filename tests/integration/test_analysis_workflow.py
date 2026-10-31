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


def test_analysis_preserves_resume_source_and_extraction_confidence():
    results = SkillGapService().analyze(
        resume_text="Built production services using Python.",
        jd_text="Required Skills:\n- Python",
    )

    python_gap = next(gap for gap in results["gaps"] if gap["canonical_skill"] == "python")
    python_match = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "python"
    )

    assert python_gap["resume_evidence_source"] == "resume"
    assert 0.0 < python_gap["resume_extraction_confidence"] <= 1.0
    assert 0.0 < python_gap["extraction_confidence"] <= 1.0
    assert python_match["evidence_source"] == "resume"
    assert python_match["extraction_confidence"] == python_gap["resume_extraction_confidence"]


def test_legacy_gap_records_default_new_provenance_fields():
    legacy_gap = SkillGap.model_validate({
        "canonical_skill": "python",
        "role_relevance": 0.8,
        "evidence_strength": 0.0,
        "extraction_confidence": 0.9,
        "priority": 0.72,
        "reason": "Required for the role",
    })

    assert legacy_gap.resume_evidence_source == ""
    assert legacy_gap.resume_extraction_confidence == 0.0


def test_analysis_with_no_extracted_requirements_reports_insufficient_data(sample_resume_text):
    results = SkillGapService().analyze(
        resume_text=sample_resume_text,
        jd_text="A supportive team, flexible hours, and competitive benefits.",
    )

    assert results["total_jd_skills"] == 0
    assert results["readiness_state"] == "insufficient_data"
    assert results["readiness_score"] is None
    assert results["readiness_percentage"] is None


def test_confirming_demonstrated_skill_preserves_resume_evidence_level():
    results = SkillGapService().analyze(
        resume_text="Built production services with Python.",
        jd_text="Required Skills:\n- Python",
        user_confirmed_skills=["python"],
    )

    python = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "python"
    )

    assert python["evidence_level"] == "demonstrated"
    assert python["evidence_strength"] == 0.4
    assert python["user_confirmed"] is True


def test_alias_entered_by_user_becomes_canonical_self_reported_evidence(sample_jd_text):
    results = SkillGapService().analyze(
        resume_text="Career changer seeking a data engineering role.",
        jd_text=sample_jd_text,
        user_confirmed_skills=[" KAFKA ", "apache kafka", "unknown platform"],
    )

    kafka = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "kafka"
    )
    assert kafka["evidence_level"] == "self_reported"
    assert kafka["evidence_strength"] == 0.3
    assert kafka["user_confirmed"] is True
    assert results["unrecognized_user_skills"] == ["unknown platform"]


def test_unknown_user_skill_is_not_added_as_evidence():
    results = SkillGapService().analyze(
        resume_text="Career changer seeking a data engineering role.",
        jd_text="Required Skills:\n- Python",
        user_confirmed_skills=["unrecognized platform"],
    )

    python = next(
        skill for skill in results["matched_skills"] if skill["canonical_skill"] == "python"
    ) if results["matched_skills"] else None
    assert python is None
    assert results["unrecognized_user_skills"] == ["unrecognized platform"]
