"""Regression tests for plan resource and project relevance."""

from career_coach.domain.schemas import SkillGap
from career_coach.services.plan_generator import (
    generate_project_recommendations,
    get_resources_for_skill,
)


def make_gap(skill: str) -> SkillGap:
    return SkillGap(
        canonical_skill=skill,
        role_relevance=0.8,
        evidence_strength=0.0,
        extraction_confidence=1.0,
        priority=0.8,
        reason="Required for the role",
    )


def test_devops_skills_receive_skill_specific_resources():
    docker = get_resources_for_skill("docker")
    terraform = get_resources_for_skill("terraform")

    assert docker != terraform
    assert all(resource["url"] for resource in docker + terraform)


def test_related_gaps_do_not_duplicate_the_same_project_recommendation():
    projects = generate_project_recommendations(
        [make_gap("sql"), make_gap("postgresql")],
        max_projects=2,
    )

    assert len(projects) == 1
    assert {"sql", "postgresql"} <= set(projects[0].targeted_skills)
