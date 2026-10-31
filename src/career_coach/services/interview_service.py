"""Interview preparation service - questions and rubric evaluation."""

from career_coach.domain.schemas import (
    InterviewSession, InterviewRubricScore, SkillGap,
    InterviewCriterion
)
from career_coach.domain.scoring import get_top_gaps
from career_coach.domain.skill_taxonomy import load_taxonomy
from datetime import datetime
from uuid import uuid4
from typing import Optional
import random


# Question templates by skill category
QUESTION_TEMPLATES = {
    "programming": {
        "technical": [
            "Explain the difference between *args and **kwargs in Python. When would you use each?",
            "How does Python's garbage collection work? What are reference cycles?",
            "Describe the GIL and its impact on multi-threaded Python programs.",
            "What are decorators in Python? Write a simple timer decorator.",
            "Explain the difference between list comprehension and generator expression.",
        ],
        "behavioral": [
            "Tell me about a time you optimized a slow piece of code. What was the bottleneck?",
            "Describe a situation where you had to refactor legacy code. How did you approach it?",
            "Have you ever introduced a bug in production? How did you handle it?",
        ],
    },
    "data": {
        "technical": [
            "Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN with examples.",
            "What are window functions in SQL? Give an example of ROW_NUMBER() vs RANK().",
            "How would you handle slowly changing dimensions (SCD Type 2) in a data warehouse?",
            "Describe the difference between OLTP and OLAP systems.",
            "What is the difference between a star schema and a snowflake schema?",
        ],
        "behavioral": [
            "Tell me about a data quality issue you discovered. How did you fix it?",
            "Describe a time you had to explain a complex data concept to a non-technical stakeholder.",
        ],
    },
    "ml": {
        "technical": [
            "Explain the bias-variance tradeoff. How do you diagnose which one is the problem?",
            "What is cross-validation? Why not just use a single train/test split?",
            "Describe how gradient descent works. What are common issues and solutions?",
            "Explain the difference between L1 and L2 regularization. When would you use each?",
            "How do you handle class imbalance in a classification problem?",
        ],
        "behavioral": [
            "Tell me about a model that didn't perform as expected. How did you debug it?",
            "Describe a time you had to choose between model accuracy and interpretability.",
        ],
    },
    "devops": {
        "technical": [
            "Explain the difference between Docker ADD and COPY instructions.",
            "What is a Kubernetes pod vs deployment vs service? How do they relate?",
            "Describe the difference between rolling update and blue-green deployment.",
            "What are Kubernetes probes (liveness, readiness, startup)? When to use each?",
            "How does Docker layer caching work? How do you optimize it?",
        ],
        "behavioral": [
            "Tell me about a production incident you helped resolve. What was the root cause?",
            "Describe a time you improved deployment reliability or speed.",
        ],
    },
    "cloud": {
        "technical": [
            "Explain the difference between S3 storage classes. When would you use each?",
            "What is the difference between a Load Balancer and an API Gateway?",
            "Describe how you would design a highly available architecture on AWS.",
            "What are the tradeoffs between Lambda and ECS/Fargate for containers?",
            "Explain VPC, subnets, and security groups.",
        ],
        "behavioral": [
            "Tell me about a cloud cost optimization you implemented.",
            "Describe a migration project you worked on. What were the challenges?",
        ],
    },
    "orchestration": {
        "technical": [
            "Explain the difference between a DAG run and a task instance in Airflow.",
            "What are XComs in Airflow? What are their limitations?",
            "How do you handle task dependencies that aren't purely sequential?",
            "Describe the difference between sensors and operators.",
            "What is dynamic task mapping in Airflow 2.3+?",
        ],
        "behavioral": [
            "Tell me about a pipeline failure that was hard to debug. How did you solve it?",
        ],
    },
    "backend": {
        "technical": [
            "Explain the difference between synchronous and asynchronous code in FastAPI.",
            "What is dependency injection in FastAPI? How does it help testing?",
            "Describe REST vs GraphQL tradeoffs.",
            "How do you handle database migrations in production?",
            "What are the principles of good API design?",
        ],
        "behavioral": [
            "Tell me about an API design decision you regret. What would you change?",
        ],
    },
    "frontend": {
        "technical": [
            "Explain the virtual DOM in React. How does reconciliation work?",
            "What are React hooks? Explain useEffect cleanup function.",
            "Describe the difference between controlled and uncontrolled components.",
            "What is TypeScript's type narrowing? Give examples.",
            "How do you optimize React rendering performance?",
        ],
        "behavioral": [
            "Describe a time you improved a web app's performance or accessibility.",
        ],
    },
    "tools": {
        "technical": [
            "Explain the difference between git merge and git rebase. When to use each?",
            "What is a git bisect? How does it help find bugs?",
            "Describe a branching strategy you've used (GitFlow, trunk-based, etc.).",
        ],
        "behavioral": [
            "Tell me about a merge conflict disaster. How did you resolve it?",
        ],
    },
    "process": {
        "technical": [
            "What is the difference between Scrum and Kanban?",
            "How do you handle scope creep in a sprint?",
            "Describe the purpose of a retrospective. What makes it effective?",
        ],
        "behavioral": [
            "Tell me about a time you disagreed with a team decision. How did you handle it?",
            "Describe how you estimate work. What techniques have you used?",
        ],
    },
    "data engineering": {
        "technical": [
            "Explain the difference between batch and stream processing. When to use each?",
            "What is the difference between Spark transformations and actions?",
            "Describe the Lambda architecture vs Kappa architecture.",
            "What is data partitioning? How do you choose a partition key?",
            "How do you handle late-arriving data in streaming?",
        ],
        "behavioral": [
            "Tell me about a data pipeline you built that scaled significantly.",
        ],
    },
}


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


def get_questions_for_skill(
    skill: str,
    count: int = 3,
    include_behavioral: bool = True,
) -> list[str]:
    """Get interview questions for a specific skill."""
    taxonomy = load_taxonomy()
    category = taxonomy.get_category(skill) or "programming"
    
    templates = QUESTION_TEMPLATES.get(category, QUESTION_TEMPLATES["programming"])
    
    technical_questions = templates.get("technical", [])
    behavioral_questions = templates.get("behavioral", [])
    
    selected = []
    
    tech_count = min(count, len(technical_questions))
    selected.extend(random.sample(technical_questions, tech_count))
    
    if include_behavioral:
        remaining = count - tech_count
        if remaining > 0:
            all_behavioral = behavioral_questions + DEFAULT_BEHAVIORAL
            beh_count = min(remaining, len(all_behavioral))
            selected.extend(random.sample(all_behavioral, beh_count))
    
    return selected[:count]


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
        questions = get_questions_for_skill(
            gap.canonical_skill,
            count=questions_per_skill,
            include_behavioral=True,
        )
        
        for q_text in questions:
            is_technical = q_text in QUESTION_TEMPLATES.get(
                load_taxonomy().get_category(gap.canonical_skill) or "programming", {}
            ).get("technical", [])
            
            session = InterviewSession(
                id=uuid4(),
                target_role=target_role,
                category=gap.canonical_skill,
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


def get_rubric_for_question(question: str, skill: str) -> dict:
    """Get the evaluation rubric for a question."""
    is_technical = skill != "general"
    
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
    Evaluate an answer against the rubric.
    Returns scores and feedback (deterministic template for self-evaluation).
    """
    rubric = get_rubric_for_question(session.question, session.category)
    
    return {
        "session_id": str(session.id),
        "question": session.question,
        "category": session.category,
        "scores": {criterion.value: 3 for criterion in rubric.keys()},  # Default mid-score for self-eval
        "weighted_score": 3.0,
        "feedback": "Use the rubric below to self-evaluate. Rate each criterion 1-5.",
        "rubric": rubric,
    }


def calculate_session_score(sessions: list[InterviewSession]) -> dict:
    """Calculate overall interview session score from completed sessions."""
    total_weighted = 0.0
    total_weight = 0.0
    criterion_scores = {c: [] for c in InterviewCriterion}
    completed = 0
    
    for session in sessions:
        if not session.completed or not session.scores:
            continue
        completed += 1
        for score_obj in session.scores:
            criterion = score_obj.criterion
            weight = get_rubric_for_question(session.question, session.category).get(criterion, {}).get("weight", 0)
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