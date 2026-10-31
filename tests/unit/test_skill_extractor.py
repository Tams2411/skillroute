"""Regression tests for taxonomy aliases and evidence assessment."""

from career_coach.domain.skill_taxonomy import DEFAULT_TAXONOMY
from career_coach.services.skill_extractor import SkillExtractor


def test_aliases_resolve_to_canonical_skills():
    matches = SkillExtractor().extract_from_resume(
        "Deployed workloads with k8s and trained models with sklearn."
    )

    skills = {match.canonical_skill for match in matches}
    assert "kubernetes" in skills
    assert "scikit-learn" in skills
    assert "k8s" not in skills
    assert "sklearn" not in skills


def test_short_ambiguous_aliases_are_not_used_for_matching():
    short_aliases = {"rest", "es", "ts", "tf", "py", "stats"}
    aliases = {alias for alias, _ in DEFAULT_TAXONOMY.all_aliases()}

    assert short_aliases.isdisjoint(aliases)


def test_unrelated_demonstration_language_does_not_inflate_evidence():
    resume = "Built a garden project.\n" + (" " * 200) + "Python"

    python = next(
        match
        for match in SkillExtractor().extract_from_resume(resume)
        if match.canonical_skill == "python"
    )

    assert python.evidence_level == "mentioned"


def test_user_confirmation_upgrades_demonstrated_evidence():
    extractor = SkillExtractor()
    matches = extractor.extract_from_resume("Built a service with Python.")

    extractor.add_user_confirmation(matches, "python", confirmed=True)

    python = next(match for match in matches if match.canonical_skill == "python")
    assert python.evidence_level == "verified"
    assert python.user_confirmed is True
