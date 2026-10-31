"""Interview preparation service - questions and rubric evaluation."""

import random
from datetime import datetime
from typing import Literal
from uuid import uuid4

from career_coach.domain.schemas import InterviewCriterion, InterviewSession, SkillGap
from career_coach.domain.scoring import get_top_gaps


# Default behavioral questions
DEFAULT_BEHAVIORAL = [
    "Tell me about a challenging technical project you worked on. What was your role?",
    "Describe a time you had to learn a new technology quickly. How did you approach it?",
    "Tell me about a time you disagreed with a colleague on a technical approach. How did you resolve it?",
    "Describe a situation where you had to balance technical debt with feature delivery.",
    "Tell me about a time you mentored someone or helped a teammate grow.",
    "Describe a project that failed or was cancelled. What did you learn?",
    "Tell me about a time you had to communicate a complex technical issue to non-technical stakeholders.",
]


SKILL_QUESTION_TEMPLATES = {
    "terraform": {
        "technical": [
            "How would you organize Terraform state and manage changes safely across environments?",
            "How do Terraform modules improve reuse, and what trade-offs do they introduce?",
            "How would you troubleshoot an unexpected Terraform plan before applying it?",
        ],
        "behavioral": [
            "Tell me about a time you used Terraform to provision infrastructure. What trade-offs did you make?",
            "Describe a Terraform change that was difficult to review or roll back. How did you handle it?",
        ],
    },
    "testing": {
        "technical": [
            "How would you choose unit, integration, and end-to-end tests for a new service?",
            "How do you diagnose and reduce flaky tests in a CI pipeline?",
            "What makes a test valuable, and how do you avoid testing implementation details?",
        ],
        "behavioral": [
            "Tell me about a time a test caught a regression before release. What did you change afterward?",
            "Describe a testing gap you discovered and how you improved coverage without slowing delivery.",
        ],
    },
    "docker": {
        "technical": [
            "How would you reduce a Docker image's size while keeping builds reproducible?",
            "When would you use a multi-stage Docker build, and what belongs in each stage?",
        ],
        "behavioral": [
            "Tell me about a time Docker improved consistency between development and production.",
        ],
    },
    "kubernetes": {
        "technical": [
            "How would you investigate a Kubernetes pod that is repeatedly restarting?",
            "When would you use a Deployment, StatefulSet, or Job in Kubernetes?",
        ],
        "behavioral": [
            "Tell me about a time you operated or debugged a Kubernetes workload.",
        ],
    },
}


def _get_typed_questions_for_skill(
    skill: str,
    count: int = 3,
    include_behavioral: bool = True,
) -> list[tuple[str, Literal["technical", "behavioral"]]]:
    """Return skill-focused questions annotated with their rubric type."""
    if count <= 0:
        return []

    skill_label = skill.strip()
    templates = SKILL_QUESTION_TEMPLATES.get(skill_label.lower())
    if templates is None:
        templates = {
            "technical": [
                f"What problems does {skill_label} solve, and how would you decide when to use it?",
                f"How would you validate and troubleshoot a system that depends on {skill_label}?",
                f"What trade-offs would you consider when applying {skill_label} in production?",
            ],
            "behavioral": [
                f"Tell me about a time you used {skill_label} to solve a problem. What did you learn?",
            ],
        }
    technical_questions = templates.get("technical", [])
    behavioral_questions = templates.get("behavioral", []) or DEFAULT_BEHAVIORAL
    selected: list[tuple[str, Literal["technical", "behavioral"]]] = []

    if include_behavioral and count >= 2 and technical_questions and behavioral_questions:
        technical_count = min(count - 1, len(technical_questions))
        selected.extend(
            (question, "technical")
            for question in random.sample(technical_questions, technical_count)
        )
        selected.append((random.choice(behavioral_questions), "behavioral"))

    remaining = count - len(selected)
    if remaining > 0:
        available_technical = [q for q in technical_questions if (q, "technical") not in selected]
        technical_count = min(remaining, len(available_technical))
        selected.extend(
            (question, "technical")
            for question in random.sample(available_technical, technical_count)
        )
        remaining = count - len(selected)

    if remaining > 0 and include_behavioral:
        available_behavioral = [q for q in behavioral_questions if (q, "behavioral") not in selected]
        selected.extend(
            (question, "behavioral")
            for question in random.sample(available_behavioral, min(remaining, len(available_behavioral)))
        )

    return selected[:count]


def get_questions_for_skill(
    skill: str,
    count: int = 3,
    include_behavioral: bool = True,
) -> list[str]:
    """Get interview question text for a specific skill."""
    return [
        question
        for question, _ in _get_typed_questions_for_skill(skill, count, include_behavioral)
    ]


def generate_interview_session(
    gaps: list[SkillGap],
    target_role: str = "Target Role",
    max_skills: int = 5,
    questions_per_skill: int = 2,
) -> list[InterviewSession]:
    """Generate mock interview sessions targeting top skill gaps.
    
    Returns list of InterviewSession objects (one per question).
    """
    actionable = [g for g in gaps if g.priority >= 0.15]
    top_gaps = get_top_gaps(actionable, n=max_skills)
    
    sessions = []
    
    for gap in top_gaps:
        questions = _get_typed_questions_for_skill(
            gap.canonical_skill,
            count=questions_per_skill,
            include_behavioral=True,
        )
        
        for q_text, question_type in questions:
            session = InterviewSession(
                id=uuid4(),
                target_role=target_role,
                category=gap.canonical_skill,
                question_type=question_type,
                question=q_text,
                answer="",
                scores=[],
                overall_feedback="",
                practice_task="",
                created_at=datetime.utcnow(),
                completed=False,
            )
            sessions.append(session)
    
    # Add general behavioral questions
    for q_text in random.sample(DEFAULT_BEHAVIORAL, 2):
        session = InterviewSession(
            id=uuid4(),
            target_role=target_role,
            category="general",
            question_type="behavioral",
            question=q_text,
            answer="",
            scores=[],
            overall_feedback="",
            practice_task="",
            created_at=datetime.utcnow(),
            completed=False,
        )
        sessions.append(session)
    
    return sessions


def get_rubric_for_question(
    question: str,
    skill: str,
    question_type: str | None = None,
) -> dict:
    """Get the evaluation rubric for a question."""
    is_technical = question_type != "behavioral" if question_type else skill != "general"
    
    if is_technical:
        return {
            InterviewCriterion.TECHNICAL_CORRECTNESS: {
                "description": "Correctness of technical answer",
                "weight": 0.35,
            },
            InterviewCriterion.REASONING_TRADEOFFS: {
                "description": "Shows reasoning and discusses tradeoffs",
                "weight": 0.25,
            },
            InterviewCriterion.SPECIFICITY_EVIDENCE: {
                "description": "Provides specific examples/evidence",
                "weight": 0.20,
            },
            InterviewCriterion.STRUCTURE_CLARITY: {
                "description": "Clear, structured communication",
                "weight": 0.15,
            },
            InterviewCriterion.FAILURE_AWARENESS: {
                "description": "Acknowledges limitations/failure modes",
                "weight": 0.05,
            },
        }
    else:
        return {
            InterviewCriterion.SPECIFICITY_EVIDENCE: {
                "description": "Provides specific STAR-format examples",
                "weight": 0.4,
            },
            InterviewCriterion.STRUCTURE_CLARITY: {
                "description": "Clear, structured communication",
                "weight": 0.3,
            },
            InterviewCriterion.FAILURE_AWARENESS: {
                "description": "Shows self-awareness and learning",
                "weight": 0.3,
            },
        }


def evaluate_answer(
    session: InterviewSession,
    answer: str,
) -> dict:
    """
    Prepare neutral starting scores for a self-evaluation.

    The application does not automatically grade answer correctness.
    """
    rubric = get_rubric_for_question(
        session.question,
        session.category,
        session.question_type,
    )
    
    return {
        "session_id": str(session.id),
        "question": session.question,
        "category": session.category,
        "scores": {criterion.value: 3 for criterion in rubric.keys()},  # Default mid-score for self-eval
        "weighted_score": 3.0,
        "answer_word_count": len(answer.split()),
        "feedback": (
            f"Neutral starting scores, not an automatic grade. Your answer has "
            f"{len(answer.split())} words; use the rubric below to self-evaluate."
        ),
        "rubric": rubric,
    }


def calculate_session_score(sessions: list[InterviewSession]) -> dict:
    """Calculate overall interview session score from completed sessions."""
    total_weighted = 0.0
    total_weight = 0.0
    criterion_scores: dict[InterviewCriterion, list[int]] = {
        criterion: [] for criterion in InterviewCriterion
    }
    completed = 0
    
    for session in sessions:
        if not session.completed or not session.scores:
            continue
        completed += 1
        for score_obj in session.scores:
            criterion = score_obj.criterion
            weight = get_rubric_for_question(
                session.question,
                session.category,
                session.question_type,
            ).get(criterion, {}).get("weight", 0)
            total_weighted += score_obj.score * weight
            total_weight += weight
            criterion_scores[criterion].append(score_obj.score)
    
    overall = total_weighted / total_weight if total_weight > 0 else 0
    
    avg_by_criterion = {}
    for criterion, scores in criterion_scores.items():
        if scores:
            avg_by_criterion[criterion.value] = round(sum(scores) / len(scores), 2)
    
    return {
        "overall_score": round(overall, 2),
        "max_score": 5.0,
        "percentage": round(overall / 5.0 * 100),
        "by_criterion": avg_by_criterion,
        "total_questions": len(sessions),
        "completed": completed,
    }