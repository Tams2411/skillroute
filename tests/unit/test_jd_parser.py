"""Regression tests for job-description section parsing."""

from career_coach.services.jd_parser import JDParser
from career_coach.services.skill_gap_service import SkillGapService


def test_parser_preserves_requirements_and_preferred_sections():
    parsed = JDParser().parse(
        "Data Engineer\n\n"
        "Required Skills:\n- Python\n\n"
        "Preferred Skills:\n- Terraform\n\n"
        "Responsibilities:\n- Use Spark for daily processing\n\n"
        "Benefits:\n- Python training budget"
    )

    assert {"requirements", "preferred", "responsibilities", "benefits"} <= set(parsed["sections"])
    assert {skill["canonical_skill"] for skill in parsed["required_skills"]} == {"python"}
    assert {skill["canonical_skill"] for skill in parsed["preferred_skills"]} == {"terraform"}


def test_skill_list_deduplicates_skills_repeated_as_required_and_preferred():
    results = SkillGapService().analyze(
        resume_text="Python",
        jd_text="Required Skills:\n- Python\n\nPreferred Skills:\n- Python",
    )

    python_gaps = [gap for gap in results["gaps"] if gap["canonical_skill"] == "python"]

    assert len(python_gaps) == 1
    assert python_gaps[0]["role_relevance"] > 0.5
    assert results["total_jd_skills"] == len({gap["canonical_skill"] for gap in results["gaps"]})


def test_sample_job_description_extracts_preferred_skills_and_not_benefits():
    from career_coach.ui.intake import SAMPLE_JD

    parsed = JDParser().parse(SAMPLE_JD + "\nBenefits:\n- Training for TensorFlow and Kubernetes")

    assert parsed["preferred_skills"]
    assert "kafka" in {skill["canonical_skill"] for skill in parsed["preferred_skills"]}
    extracted = {
        skill["canonical_skill"] for skill in parsed["required_skills"] + parsed["preferred_skills"]
    }
    assert "tensorflow" not in extracted


def test_parser_extracts_contextual_skills_with_explicit_section_types():
    parsed = JDParser().parse(
        "Data Engineer\n"
        "Required Skills:\n- Python\n"
        "Preferred Skills:\n- Terraform\n"
        "Responsibilities:\n- Build pipelines using Docker\n"
        "Experience:\n- Five years working with Apache Spark\n"
        "Education:\n- Computer science degree and SQL\n"
        "Benefits:\n- Python learning budget"
    )

    required = {skill["canonical_skill"]: skill for skill in parsed["required_skills"]}
    preferred = {skill["canonical_skill"]: skill for skill in parsed["preferred_skills"]}
    contextual = {skill["canonical_skill"]: skill for skill in parsed["contextual_skills"]}

    assert required["python"]["requirement_type"] == "required"
    assert preferred["terraform"]["requirement_type"] == "preferred"
    assert contextual["docker"]["requirement_type"] == "responsibility"
    assert contextual["spark"]["requirement_type"] == "experience"
    assert contextual["sql"]["requirement_type"] == "education"
    assert contextual["docker"]["importance"] > preferred["terraform"]["importance"]
    assert contextual["docker"]["importance"] < required["python"]["importance"]
    assert "python" not in {
        skill["canonical_skill"] for skill in parsed["contextual_skills"]
    }


def test_required_mention_wins_when_skill_repeats_in_contextual_section():
    parsed = JDParser().parse(
        "Required Skills:\n- Python\n"
        "Responsibilities:\n- Build data tools using Python"
    )

    python = [
        skill for collection in (
            parsed["required_skills"],
            parsed["preferred_skills"],
            parsed["contextual_skills"],
        )
        for skill in collection
        if skill["canonical_skill"] == "python"
    ]

    assert len(python) == 1
    assert python[0]["requirement_type"] == "required"
