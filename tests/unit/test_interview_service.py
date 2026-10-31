"""Regression tests for skill-focused interview generation."""

from career_coach.domain.schemas import InterviewCriterion, InterviewSession, SkillGap
from career_coach.services.interview_service import (
    evaluate_answer,
    generate_interview_session,
    get_questions_for_skill,
    get_rubric_for_question,
)


def test_terraform_questions_are_skill_specific_and_include_behavioral_questions():
    gap = SkillGap(
        canonical_skill="terraform",
        role_relevance=0.8,
        evidence_strength=0.0,
        extraction_confidence=1.0,
        priority=0.8,
        reason="Required for the role",
    )

    sessions = generate_interview_session(
        [gap],
        target_role="Platform Engineer",
        max_skills=1,
        questions_per_skill=2,
    )
    terraform_sessions = [session for session in sessions if session.category == "terraform"]

    assert len(terraform_sessions) == 2
    assert all("terraform" in session.question.lower() for session in terraform_sessions)
    assert {session.question_type for session in terraform_sessions} == {
        "technical",
        "behavioral",
    }

    behavioral = next(
        session for session in terraform_sessions if session.question_type == "behavioral"
    )
    assert set(
        get_rubric_for_question(
            behavioral.question,
            behavioral.category,
            behavioral.question_type,
        )
    ) == {
        InterviewCriterion.SPECIFICITY_EVIDENCE,
        InterviewCriterion.STRUCTURE_CLARITY,
        InterviewCriterion.FAILURE_AWARENESS,
    }


def test_unmapped_skill_uses_skill_specific_questions_instead_of_category_questions():
    questions = get_questions_for_skill("pandas", count=2)

    assert all("pandas" in question.lower() for question in questions)
    assert all("sql" not in question.lower() for question in questions)


def test_answer_evaluation_identifies_neutral_self_rating_as_not_automatic():
    session = InterviewSession(
        target_role="Engineer",
        category="terraform",
        question="How would you organize Terraform state?",
    )

    result = evaluate_answer(session, "I would isolate state by environment.")

    assert result["answer_word_count"] == 6
    assert set(result["scores"].values()) == {3}
    assert "not an automatic grade" in result["feedback"]
