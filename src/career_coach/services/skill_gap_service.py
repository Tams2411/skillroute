"""Skill gap analysis service - combines parsing, extraction, and scoring."""

from career_coach.config import settings
from career_coach.domain.schemas import (
    EvidenceLevel,
    JobSkillRequirement,
    SkillEvidence,
    SkillGap,
    SkillRequirementType,
)
from career_coach.domain.scoring import (
    calculate_evidence_strength,
    calculate_readiness_score,
    compute_skill_gap,
    filter_actionable_gaps,
    get_top_gaps,
    rank_gaps,
)
from career_coach.domain.skill_taxonomy import SkillTaxonomy, load_taxonomy
from career_coach.services.jd_parser import JDParser
from career_coach.services.resume_parser import ResumeParser
from career_coach.services.skill_extractor import SkillExtractor, SkillMatch


class SkillGapService:
    """Orchestrate skill gap analysis from resume and JD."""

    def __init__(self, taxonomy: SkillTaxonomy | None = None):
        self.taxonomy = taxonomy or load_taxonomy()
        self.resume_parser = ResumeParser()
        self.jd_parser = JDParser(self.taxonomy)
        self.skill_extractor = SkillExtractor(self.taxonomy)

    def analyze(
        self,
        resume_text: str | None = None,
        resume_file: str | None = None,
        jd_text: str | None = None,
        user_confirmed_skills: list[str] | None = None,
    ) -> dict:
        """
        Full skill gap analysis pipeline.

        Args:
            resume_text: Raw resume text (optional if resume_file provided)
            resume_file: Path to resume file (optional if resume_text provided)
            jd_text: Job description text
            user_confirmed_skills: List of skills or aliases the user reports having

        Returns:
            Dictionary with gaps, readiness score, and metadata
        """
        # 1. Extract resume text if file provided
        if resume_file and not resume_text:
            resume_text = self.resume_parser.extract_text(resume_file)

        if not resume_text and not resume_file:
            raise ValueError("Either resume_text or resume_file must be provided")

        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is empty; provide text or upload a readable resume.")

        if len(resume_text) > settings.max_resume_length:
            raise ValueError(
                f"Resume text too long: {len(resume_text)} > "
                f"{settings.max_resume_length} characters"
            )

        if not jd_text or not jd_text.strip():
            raise ValueError("Job description text is required")

        # 2. Parse JD
        jd_result = self.jd_parser.parse(jd_text)

        # 3. Extract skills from resume
        resume_skills = self.skill_extractor.extract_from_resume(resume_text)

        # 4. Normalize and apply user-confirmed skills
        recognized_user_skills = []
        unrecognized_user_skills = []
        for entered_skill in user_confirmed_skills or []:
            if not isinstance(entered_skill, str):
                raise ValueError("Confirmed skills must be text values.")
            entered_skill = entered_skill.strip()
            if not entered_skill:
                continue

            canonical_skill = self.taxonomy.get_canonical(entered_skill)
            if canonical_skill is None:
                if entered_skill not in unrecognized_user_skills:
                    unrecognized_user_skills.append(entered_skill)
                continue
            if canonical_skill not in recognized_user_skills:
                recognized_user_skills.append(canonical_skill)

        for skill in recognized_user_skills:
            found = False
            for rs in resume_skills:
                if rs.canonical_skill == skill:
                    rs.user_confirmed = True
                    if rs.evidence_level in (
                        EvidenceLevel.NONE.value,
                        EvidenceLevel.MENTIONED.value,
                    ):
                        rs.evidence_level = EvidenceLevel.SELF_REPORTED.value
                    found = True
                    break

            if not found:
                resume_skills.append(SkillMatch(
                    canonical_skill=skill,
                    evidence_level=EvidenceLevel.SELF_REPORTED.value,
                    source="manual",
                    supporting_evidence=(
                        "Self-reported by user; not independently verified."
                    ),
                    user_confirmed=True,
                    extraction_confidence=1.0,
                ))

        # 5. Build resume evidence map
        resume_evidence_map = {
            rs.canonical_skill: SkillEvidence(
                canonical_skill=rs.canonical_skill,
                evidence_level=EvidenceLevel(rs.evidence_level),
                source=rs.source,
                supporting_evidence=rs.supporting_evidence,
                user_confirmed=rs.user_confirmed,
                extraction_confidence=rs.extraction_confidence,
            )
            for rs in resume_skills
        }

        # 6. Build JD skill requirements
        jd_requirements = []
        for skill_list in (
            jd_result["required_skills"],
            jd_result["preferred_skills"],
            jd_result["contextual_skills"],
        ):
            for rs in skill_list:
                jd_requirements.append(JobSkillRequirement(
                    canonical_skill=rs["canonical_skill"],
                    importance=rs["importance"],
                    evidence_phrase=rs["evidence_phrase"],
                    extraction_confidence=rs["extraction_confidence"],
                    requirement_type=SkillRequirementType(rs["requirement_type"]),
                ))

        # 7. Compute gaps
        gaps = []
        for jd_req in jd_requirements:
            resume_ev = resume_evidence_map.get(jd_req.canonical_skill)
            gap = compute_skill_gap(jd_req, resume_ev)
            gaps.append(gap)

        # 8. Rank and filter
        ranked_gaps = rank_gaps(gaps)
        actionable_gaps = filter_actionable_gaps(ranked_gaps)
        top_gaps = get_top_gaps(ranked_gaps)

        # 9. Calculate weighted evidence coverage when requirements are assessable.
        readiness = calculate_readiness_score(gaps)
        readiness_state = "available" if readiness is not None else "insufficient_data"

        # 10. Prepare matched skills
        matched_skills = []
        for jd_req in jd_requirements:
            if jd_req.canonical_skill in resume_evidence_map:
                matched_skills.append({
                    "canonical_skill": jd_req.canonical_skill,
                    "role_relevance": jd_req.importance,
                    "evidence_level": resume_evidence_map[jd_req.canonical_skill].evidence_level.value,
                    "evidence_strength": calculate_evidence_strength(
                        resume_evidence_map[jd_req.canonical_skill].evidence_level
                    ),
                    "evidence_source": resume_evidence_map[jd_req.canonical_skill].source,
                    "extraction_confidence": (
                        resume_evidence_map[jd_req.canonical_skill].extraction_confidence
                    ),
                    "requirement_type": jd_req.requirement_type.value,
                    "user_confirmed": resume_evidence_map[jd_req.canonical_skill].user_confirmed,
                })

        # 11. Missing skills (in JD but not in resume at all)
        missing_skills = [
            g for g in ranked_gaps
            if g.canonical_skill not in resume_evidence_map
        ]

        return {
            "readiness_state": readiness_state,
            "readiness_score": readiness,
            "readiness_percentage": round(readiness * 100) if readiness is not None else None,
            "total_jd_skills": len(jd_requirements),
            "unrecognized_user_skills": unrecognized_user_skills,
            "gaps": [g.model_dump() for g in ranked_gaps],
            "matched_skills": matched_skills,
            "missing_skills": [g.model_dump() for g in missing_skills],
            "all_gaps": [g.model_dump() for g in ranked_gaps],
            "top_gaps": [g.model_dump() for g in top_gaps],
            "actionable_gaps": [g.model_dump() for g in actionable_gaps],
            "jd_parsed": {
                "target_experience_years": jd_result["target_experience_years"],
                "sections_found": list(jd_result["sections"].keys()),
            },
            "resume_skills_extracted": len(resume_skills),
            "extraction_metadata": {
                "jd_extraction": jd_result["extraction_metadata"],
                "resume_evidence_levels": {
                    level.value: sum(1 for rs in resume_skills if rs.evidence_level == level)
                    for level in EvidenceLevel
                },
            },
        }

    def get_gap_details(self, gap: SkillGap) -> dict:
        """Get detailed explanation for a specific gap."""
        return {
            "skill": gap.canonical_skill,
            "priority": gap.priority,
            "priority_label": self._priority_label(gap.priority),
            "role_relevance": gap.role_relevance,
            "evidence_strength": gap.evidence_strength,
            "reason": gap.reason,
            "uncertainty": gap.uncertainty,
            "jd_evidence": gap.jd_evidence,
            "resume_evidence": gap.resume_evidence,
            "suggested_action": self._suggest_action(gap),
        }

    def _priority_label(self, priority: float) -> str:
        """Convert priority score to label."""
        if priority >= 0.6:
            return "Critical"
        elif priority >= 0.4:
            return "High"
        elif priority >= 0.25:
            return "Medium"
        elif priority >= 0.1:
            return "Low"
        return "Minimal"

    def _suggest_action(self, gap: SkillGap) -> str:
        """Suggest learning action based on gap characteristics."""
        if gap.evidence_strength == 0:
            return f"Learn {gap.canonical_skill} from fundamentals; build a portfolio project demonstrating it"
        elif gap.evidence_strength <= 0.2:
            return f"Deepen {gap.canonical_skill} knowledge; convert mentions to demonstrated evidence via project"
        elif gap.evidence_strength <= 0.4:
            return f"Strengthen {gap.canonical_skill} portfolio evidence; document specific achievements"
        else:
            return f"Verify {gap.canonical_skill} proficiency with certification or advanced project"