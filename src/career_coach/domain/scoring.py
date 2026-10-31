"""Scoring and priority calculation for skill gaps."""

from career_coach.domain.schemas import SkillEvidence, JobSkillRequirement, SkillGap, EvidenceLevel
from career_coach.config import settings


def evidence_level_to_weight(level: EvidenceLevel) -> float:
    """Convert evidence level to numeric weight."""
    return settings.evidence_weights.get(level, 0.0)


def calculate_priority(
    role_relevance: float,
    evidence_level: EvidenceLevel,
    extraction_confidence: float = 1.0,
) -> float:
    """
    Calculate skill gap priority.

    Formula: R × (1 - E) × C
    where:
    - R = role_relevance (0-1): how important skill is in JD
    - E = evidence_strength (0-1): user's evidence level weight
    - C = extraction_confidence (0-1): confidence in extraction

    Priority is higher when:
    - Skill is highly relevant to role (R high)
    - User has weak/no evidence (E low, so 1-E high)
    - Extraction is confident (C high)
    """
    evidence_strength = evidence_level_to_weight(evidence_level)
    priority = role_relevance * (1.0 - evidence_strength) * extraction_confidence
    return max(0.0, min(1.0, priority))


def calculate_evidence_strength(evidence_level: EvidenceLevel) -> float:
    """Get evidence strength (0-1) from evidence level."""
    return evidence_level_to_weight(evidence_level)


def compute_skill_gap(
    jd_skill: JobSkillRequirement,
    resume_evidence: SkillEvidence | None,
) -> SkillGap:
    """
    Compute a skill gap from JD requirement and resume evidence.

    Args:
        jd_skill: Skill requirement from job description
        resume_evidence: User's evidence for this skill (or None)

    Returns:
        SkillGap with priority and rationale
    """
    # Determine evidence level
    if resume_evidence is None:
        evidence_level = EvidenceLevel.NONE
        evidence_strength = 0.0
        resume_evidence_str = "No evidence found in resume"
        resume_evidence_source = ""
        resume_extraction_confidence = 0.0
    else:
        evidence_level = resume_evidence.evidence_level
        evidence_strength = evidence_level_to_weight(evidence_level)
        resume_evidence_str = resume_evidence.supporting_evidence or f"Evidence level: {evidence_level.value}"
        resume_evidence_source = resume_evidence.source
        resume_extraction_confidence = resume_evidence.extraction_confidence

    # Role relevance from JD importance
    role_relevance = jd_skill.importance

    # Extraction confidence
    extraction_confidence = jd_skill.extraction_confidence

    # Calculate priority
    priority = calculate_priority(role_relevance, evidence_level, extraction_confidence)

    # Build rationale
    if evidence_level == EvidenceLevel.NONE:
        reason = f"Skill required for role (importance: {role_relevance:.0%}) but not found in resume"
    elif evidence_level == EvidenceLevel.MENTIONED:
        reason = f"Skill mentioned in resume but not demonstrated; role requires it (importance: {role_relevance:.0%})"
    elif evidence_level == EvidenceLevel.SELF_REPORTED:
        reason = (
            f"Skill self-reported by user but not independently verified; "
            f"role requires it (importance: {role_relevance:.0%})"
        )
    elif evidence_level == EvidenceLevel.DEMONSTRATED:
        reason = f"Skill demonstrated in resume; role requires it (importance: {role_relevance:.0%})"
    else:  # VERIFIED
        reason = f"Skill verified in resume; role requires it (importance: {role_relevance:.0%})"

    # Build uncertainty
    uncertainty_parts = []
    if extraction_confidence < 0.7:
        uncertainty_parts.append(f"JD extraction confidence low ({extraction_confidence:.0%})")
    # Note: SkillEvidence doesn't have extraction_confidence field
    if evidence_level == EvidenceLevel.NONE:
        uncertainty_parts.append("Skill may exist but not captured in provided resume text")

    uncertainty = "; ".join(uncertainty_parts) if uncertainty_parts else ""

    return SkillGap(
        canonical_skill=jd_skill.canonical_skill,
        role_relevance=role_relevance,
        evidence_strength=evidence_strength,
        extraction_confidence=extraction_confidence,
        priority=priority,
        reason=reason,
        uncertainty=uncertainty,
        jd_evidence=jd_skill.evidence_phrase or "",
        resume_evidence=resume_evidence_str,
        resume_evidence_source=resume_evidence_source,
        resume_extraction_confidence=resume_extraction_confidence,
    )


def rank_gaps(gaps: list[SkillGap]) -> list[SkillGap]:
    """Rank gaps by priority (highest first)."""
    return sorted(gaps, key=lambda g: g.priority, reverse=True)


def calculate_readiness_score(gaps: list[SkillGap]) -> float | None:
    """
    Calculate weighted evidence coverage (0-1).

    Returns None when there are no assessable requirements.
    """
    if not gaps:
        return None

    total_weight = sum(g.role_relevance for g in gaps)
    if total_weight == 0:
        return None

    covered_weight = sum(
        g.role_relevance * g.evidence_strength
        for g in gaps
    )

    return min(1.0, covered_weight / total_weight)


def get_top_gaps(gaps: list[SkillGap], n: int = 5) -> list[SkillGap]:
    """Get top N priority gaps."""
    ranked = rank_gaps(gaps)
    return ranked[:n]


def filter_actionable_gaps(gaps: list[SkillGap], min_priority: float = 0.15) -> list[SkillGap]:
    """Filter gaps that are actionable (above minimum priority)."""
    return [g for g in gaps if g.priority >= min_priority]