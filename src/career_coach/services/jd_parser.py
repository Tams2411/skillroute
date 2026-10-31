"""Job Description parser with section detection."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, TypedDict

from career_coach.config import settings
from career_coach.domain.skill_taxonomy import SkillTaxonomy, load_taxonomy
from career_coach.domain.schemas import SkillRequirementType


class JDSectionType(str, Enum):
    """Types of JD sections."""
    REQUIREMENTS = "requirements"
    PREFERRED = "preferred"
    RESPONSIBILITIES = "responsibilities"
    BENEFITS = "benefits"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    OTHER = "other"


@dataclass
class JDSection:
    """A section extracted from a job description."""
    section_type: JDSectionType
    content: str
    start_pos: int
    end_pos: int


class ExtractedSkill(TypedDict):
    canonical_skill: str
    importance: float
    evidence_phrase: str
    extraction_confidence: float
    requirement_type: str


class JDParser:
    """Parse job descriptions and extract structured skill requirements."""

    # Section header patterns (case-insensitive, multiline)
    SECTION_PATTERNS = {
        JDSectionType.REQUIREMENTS: [
            r"(?:^|\n)\s*(?:required\s+skills?|must[-\s]?have\s+skills?)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:required|requirements|must[-\s]?have|qualifications)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:what\s+(?:you|we)\'?re\s+looking\s+for)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:we\'?re\s+looking\s+for)(?:\s*:|\n|$)",
        ],
        JDSectionType.PREFERRED: [
            r"(?:^|\n)\s*(?:preferred\s+skills?|nice[-\s]?to[-\s]?have\s+skills?)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:preferred|nice[-\s]?to[-\s]?have|bonus\s+points|would\s+be\s+a\s+plus)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:what\'?s\s+preferred)(?:\s*:|\n|$)",
        ],
        JDSectionType.RESPONSIBILITIES: [
            r"(?:^|\n)\s*(?:responsibilities|duties|what\s+you\'?ll\s+do)(?:\s*:|\n|$)",
            r"(?:^|\n)\s*(?:job\s+duties)(?:\s*:|\n|$)",
        ],
        JDSectionType.BENEFITS: [
            r"(?:^|\n)\s*(?:benefits|what\s+we\s+offer|perks)(?:\s*:|\n|$)",
        ],
        JDSectionType.EXPERIENCE: [
            r"(?:^|\n)\s*(?:experience|years\s+of\s+experience)(?:\s*:|\n|$)",
        ],
        JDSectionType.EDUCATION: [
            r"(?:^|\n)\s*(?:education|degree)(?:\s*:|\n|$)",
        ],
        JDSectionType.SKILLS: [
            r"(?:^|\n)\s*(?:skills|technical\s+skills|technologies)(?:\s*:|\n|$)",
        ],
    }

    # Bullet point patterns
    BULLET_PATTERNS = [
        r"^\s*[-•*]\s+",
        r"^\s*\d+[.)]\s+",
        r"^\s*\([a-z]\)\s+",
    ]

    # Experience extraction patterns
    EXPERIENCE_PATTERNS = [
        r"(\d+)\+?\s*years?",
        r"experience\s+of\s+(\d+)\s*years?",
        r"(\d+)\s*years?\s+of\s+experience",
        r"(\d+)\+\s*years?",
        r"(\d{1,2})\s*-\s*\d+\s*years?",
    ]

    def __init__(self, taxonomy: Optional[SkillTaxonomy] = None):
        self.taxonomy = taxonomy or load_taxonomy()
        self._compiled_patterns = {
            section_type: [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]
            for section_type, patterns in self.SECTION_PATTERNS.items()
        }
        self._bullet_regex = re.compile("|".join(self.BULLET_PATTERNS), re.MULTILINE)
        self._experience_regex = [re.compile(p, re.IGNORECASE) for p in self.EXPERIENCE_PATTERNS]

    def parse(self, jd_text: str) -> dict:
        """
        Parse job description and extract structured information.

        Args:
            jd_text: Raw job description text

        Returns:
            Dictionary with parsed information including sections, skills, experience
        """
        if not jd_text or not jd_text.strip():
            raise ValueError("Job description text is empty")

        if len(jd_text) > settings.max_jd_length:
            raise ValueError(f"JD too long: {len(jd_text)} > {settings.max_jd_length} chars")

        # Normalize whitespace
        text = self._normalize_text(jd_text)

        # Detect sections
        sections = self._detect_sections(text)

        # Extract skills with their section context intact.
        requirements_text = self._get_section_text(sections, JDSectionType.REQUIREMENTS)
        preferred_text = self._get_section_text(sections, JDSectionType.PREFERRED)
        skills_text = self._get_section_text(sections, JDSectionType.SKILLS)
        experience_text = self._get_section_text(sections, JDSectionType.EXPERIENCE)
        responsibilities_text = self._get_section_text(sections, JDSectionType.RESPONSIBILITIES)
        education_text = self._get_section_text(sections, JDSectionType.EDUCATION)

        candidates = []
        section_inputs = (
            (requirements_text, SkillRequirementType.REQUIRED),
            (skills_text, SkillRequirementType.SKILLS),
            (preferred_text, SkillRequirementType.PREFERRED),
            (responsibilities_text, SkillRequirementType.RESPONSIBILITY),
            (experience_text, SkillRequirementType.EXPERIENCE),
            (education_text, SkillRequirementType.EDUCATION),
        )
        for content, requirement_type in section_inputs:
            candidates.extend(
                self._extract_skills_with_context(content, requirement_type)
            )

        best_by_skill: dict[str, ExtractedSkill] = {}
        for candidate in candidates:
            current = best_by_skill.get(candidate["canonical_skill"])
            if current is None or candidate["importance"] > current["importance"]:
                best_by_skill[candidate["canonical_skill"]] = candidate

        selected = sorted(
            best_by_skill.values(),
            key=lambda skill: skill["importance"] * skill["extraction_confidence"],
            reverse=True,
        )
        required_types = {SkillRequirementType.REQUIRED.value, SkillRequirementType.SKILLS.value}
        required_skills = [
            skill for skill in selected if skill["requirement_type"] in required_types
        ]
        preferred_skills = [
            skill for skill in selected
            if skill["requirement_type"] == SkillRequirementType.PREFERRED.value
        ]
        contextual_skills = [
            skill for skill in selected
            if skill["requirement_type"] not in required_types
            and skill["requirement_type"] != SkillRequirementType.PREFERRED.value
        ]

        # Extract experience requirement
        target_experience = self._extract_experience(experience_text or text)

        return {
            "raw_text": jd_text,
            "normalized_text": text,
            "sections": {s.section_type.value: s.content for s in sections},
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "contextual_skills": contextual_skills,
            "target_experience_years": target_experience,
            "extraction_metadata": {
                "required_section_chars": len(requirements_text) + len(skills_text),
                "preferred_section_chars": len(preferred_text),
                "contextual_section_chars": (
                    len(responsibilities_text) + len(experience_text) + len(education_text)
                ),
                "total_skills_found": len(selected),
            },
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and encoding."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[^\S\n]+", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()

    def _detect_sections(self, text: str) -> list[JDSection]:
        """Detect and extract sections from JD text."""
        sections = []

        # Find all section headers
        header_matches = []
        for section_type, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    header_matches.append((match.start(), match.end(), section_type))

        # Sort by position
        header_matches.sort(key=lambda x: x[0])

        # Extract content between headers
        for i, (start, end, section_type) in enumerate(header_matches):
            content_start = end
            content_end = header_matches[i + 1][0] if i + 1 < len(header_matches) else len(text)
            content = text[content_start:content_end].strip()

            if content:
                sections.append(JDSection(
                    section_type=section_type,
                    content=content,
                    start_pos=content_start,
                    end_pos=content_end,
                ))

        # If no sections found, treat entire text as requirements
        if not sections:
            sections.append(JDSection(
                section_type=JDSectionType.REQUIREMENTS,
                content=text,
                start_pos=0,
                end_pos=len(text),
            ))

        return sections

    def _get_section_text(self, sections: list[JDSection], section_type: JDSectionType) -> str:
        """Get combined text for a section type."""
        contents = [s.content for s in sections if s.section_type == section_type]
        return "\n".join(contents) if contents else ""

    def _extract_skills_with_context(
        self,
        text: str,
        requirement_type: SkillRequirementType,
    ) -> list[ExtractedSkill]:
        """Extract skills from text with evidence phrases and confidence."""
        if not text:
            return []

        results: list[ExtractedSkill] = []
        text_lower = text.lower()
        importance_by_type = {
            SkillRequirementType.REQUIRED: (0.8, 0.7),
            SkillRequirementType.PREFERRED: (0.5, 0.4),
            SkillRequirementType.SKILLS: (0.75, 0.65),
            SkillRequirementType.RESPONSIBILITY: (0.65, 0.55),
            SkillRequirementType.EXPERIENCE: (0.7, 0.6),
            SkillRequirementType.EDUCATION: (0.6, 0.5),
        }
        canonical_importance, alias_importance = importance_by_type[requirement_type]

        # Get all canonical skills and aliases
        for canonical, entry in self.taxonomy.skills.items():
            # Check canonical name
            if self._skill_in_text(canonical, text_lower):
                evidence = self._find_evidence_phrase(canonical, text)
                confidence = self._calculate_confidence(canonical, text_lower, evidence)
                results.append({
                    "canonical_skill": canonical,
                    "importance": canonical_importance,
                    "evidence_phrase": evidence,
                    "extraction_confidence": confidence,
                    "requirement_type": requirement_type.value,
                })
                continue

            # Check aliases
            for alias in entry.aliases:
                if self._skill_in_text(alias, text_lower):
                    evidence = self._find_evidence_phrase(alias, text)
                    confidence = self._calculate_confidence(alias, text_lower, evidence)
                    results.append({
                        "canonical_skill": canonical,
                        "importance": alias_importance,
                        "evidence_phrase": evidence,
                        "extraction_confidence": confidence,
                        "requirement_type": requirement_type.value,
                    })
                    break

        # Sort by importance * confidence
        results.sort(key=lambda x: x["importance"] * x["extraction_confidence"], reverse=True)
        return results

    def _skill_in_text(self, skill: str, text_lower: str) -> bool:
        """Check if skill appears in text with word boundaries."""
        skill_lower = skill.lower()
        # Word boundary pattern
        pattern = rf"(?<!\w){re.escape(skill_lower)}(?!\w)"
        return bool(re.search(pattern, text_lower))

    def _find_evidence_phrase(self, skill: str, text: str, window: int = 100) -> str:
        """Find the phrase containing the skill mention."""
        skill_lower = skill.lower()
        text_lower = text.lower()

        idx = text_lower.find(skill_lower)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(skill) + window)
        phrase = text[start:end].strip()

        # Try to get full sentence/bullet
        sentences = re.split(r"[.!?]\s+", phrase)
        for s in sentences:
            if skill_lower in s.lower():
                return s.strip()[:200]

        return phrase[:200]

    def _calculate_confidence(self, skill: str, text_lower: str, evidence: str) -> float:
        """Calculate extraction confidence based on context."""
        base_confidence = 0.7

        # Boost for explicit section context
        if any(kw in text_lower for kw in ["required", "must have", "essential", "mandatory"]):
            base_confidence += 0.15

        # Boost for multiple mentions
        mentions = len(re.findall(rf"(?<!\w){re.escape(skill.lower())}(?!\w)", text_lower))
        if mentions > 1:
            base_confidence += min(0.1, mentions * 0.02)

        # Reduce for very short evidence (likely false positive)
        if len(evidence) < 20:
            base_confidence -= 0.1

        return max(0.1, min(1.0, base_confidence))

    def _extract_experience(self, text: str) -> int:
        """Extract years of experience requirement."""
        if not text:
            return 0

        text_lower = text.lower()
        years_found = []

        for pattern in self._experience_regex:
            matches = pattern.findall(text_lower)
            for match in matches:
                try:
                    years = int(match) if isinstance(match, str) else int(match[0])
                    if 0 < years < 50:  # Sanity check
                        years_found.append(years)
                except (ValueError, IndexError):
                    continue

        if years_found:
            # Return the maximum reasonable requirement
            return max(years_found)

        return 0


def parse_jd(jd_text: str, taxonomy: Optional[SkillTaxonomy] = None) -> dict:
    """Convenience function for JD parsing."""
    parser = JDParser(taxonomy)
    return parser.parse(jd_text)