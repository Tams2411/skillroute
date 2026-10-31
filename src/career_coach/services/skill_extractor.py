"""Skill extraction from resume text using taxonomy + fuzzy matching."""

import re
from dataclasses import dataclass
from typing import Optional

from career_coach.domain.skill_taxonomy import SkillTaxonomy, load_taxonomy
from career_coach.config import settings


@dataclass
class SkillMatch:
    """A skill match with evidence and confidence."""
    canonical_skill: str
    evidence_level: str  # "none", "mentioned", "demonstrated", "verified"
    source: str  # "resume", "jd", "manual"
    supporting_evidence: str
    user_confirmed: bool = False
    extraction_confidence: float = 0.0


class SkillExtractor:
    """Extract and normalize skills from text using taxonomy."""

    # Patterns that suggest demonstrated/verified evidence
    DEMONSTRATED_PATTERNS = [
        r"built|developed|created|implemented|designed|architected",
        r"experience\s+(?:with|in|using)",
        r"proficient\s+(?:with|in|using)",
        r"expert\s+(?:in|with)",
        r"\d+\s*years?\s+(?:of\s+)?experience",
        r"production|deployed|launched|delivered",
        r"project|assignment|capstone|thesis",
    ]

    MENTIONED_PATTERNS = [
        r"familiar\s+(?:with|in)",
        r"knowledge\s+of",
        r"understanding\s+of",
        r"exposure\s+to",
        r"learning|studying|exploring",
    ]

    def __init__(self, taxonomy: Optional[SkillTaxonomy] = None):
        self.taxonomy = taxonomy or load_taxonomy()
        self._canonical_skills = list(self.taxonomy.skills.keys())
        self._alias_map = self.taxonomy.all_aliases()
        self._demonstrated_regex = [re.compile(p, re.IGNORECASE) for p in self.DEMONSTRATED_PATTERNS]
        self._mentioned_regex = [re.compile(p, re.IGNORECASE) for p in self.MENTIONED_PATTERNS]

    def extract_from_resume(self, resume_text: str) -> list[SkillMatch]:
        """Extract skills from resume text with evidence assessment."""
        if not resume_text or not resume_text.strip():
            return []

        text_lower = resume_text.lower()
        matches = []

        # Exact matching (canonical + aliases)
        for canonical, alias in self._alias_map:
            if self._skill_in_text(alias, text_lower):
                evidence_phrase = self._find_evidence_phrase(alias, resume_text)
                evidence_level = self._assess_evidence_level(evidence_phrase, resume_text)
                confidence = self._calculate_confidence(alias, text_lower, evidence_phrase, evidence_level)

                match = SkillMatch(
                    canonical_skill=canonical,
                    evidence_level=evidence_level,
                    source="resume",
                    supporting_evidence=evidence_phrase,
                    extraction_confidence=confidence,
                )
                matches.append(match)

        # Deduplicate by canonical skill (keep highest confidence)
        seen = {}
        for match in matches:
            if match.canonical_skill not in seen or match.extraction_confidence > seen[match.canonical_skill].extraction_confidence:
                seen[match.canonical_skill] = match

        # Sort by evidence strength, then confidence
        evidence_order = {"verified": 4, "demonstrated": 3, "mentioned": 2, "none": 1}
        result = list(seen.values())
        result.sort(key=lambda m: (evidence_order.get(m.evidence_level, 0), m.extraction_confidence), reverse=True)

        return result

    def extract_from_jd(self, jd_text: str, is_required: bool = True) -> list[SkillMatch]:
        """Extract skills from JD text."""
        if not jd_text or not jd_text.strip():
            return []

        text_lower = jd_text.lower()
        matches = []

        for canonical, alias in self._alias_map:
            if self._skill_in_text(alias, text_lower):
                evidence_phrase = self._find_evidence_phrase(alias, jd_text)
                # JD skills don't have user evidence levels, default to mentioned
                evidence_level = "mentioned"
                confidence = self._calculate_confidence(alias, text_lower, evidence_phrase, evidence_level)

                match = SkillMatch(
                    canonical_skill=canonical,
                    evidence_level=evidence_level,
                    source="jd",
                    supporting_evidence=evidence_phrase,
                    extraction_confidence=confidence,
                )
                matches.append(match)

        # Deduplicate
        seen = {}
        for match in matches:
            if match.canonical_skill not in seen or match.extraction_confidence > seen[match.canonical_skill].extraction_confidence:
                seen[match.canonical_skill] = match

        result = list(seen.values())
        result.sort(key=lambda m: m.extraction_confidence, reverse=True)
        return result

    def _skill_in_text(self, skill: str, text_lower: str) -> bool:
        """Check if skill appears in text with word boundaries."""
        skill_lower = skill.lower()
        pattern = rf"(?<!\w){re.escape(skill_lower)}(?!\w)"
        return bool(re.search(pattern, text_lower))

    def _find_evidence_phrase(self, skill: str, text: str, window: int = 150) -> str:
        """Find the phrase containing the skill mention."""
        skill_lower = skill.lower()
        text_lower = text.lower()

        idx = text_lower.find(skill_lower)
        if idx == -1:
            return ""

        start = max(0, idx - window)
        end = min(len(text), idx + len(skill) + window)
        phrase = text[start:end].strip()

        # Try to get full sentence
        sentences = re.split(r"[.!?]\s+", phrase)
        for s in sentences:
            if skill_lower in s.lower():
                return s.strip()[:300]

        return phrase[:300]

    def _assess_evidence_level(self, evidence_phrase: str, full_text: str) -> str:
        """Assess evidence level from context."""
        if not evidence_phrase:
            return "none"

        phrase_lower = evidence_phrase.lower()
        full_lower = full_text.lower()

        # Check for demonstrated patterns
        for pattern in self._demonstrated_regex:
            if pattern.search(phrase_lower) or pattern.search(full_lower):
                return "demonstrated"

        # Check for mentioned patterns
        for pattern in self._mentioned_regex:
            if pattern.search(phrase_lower):
                return "mentioned"

        # Default: skill is mentioned without context
        return "mentioned"

    def _calculate_confidence(self, skill: str, text_lower: str, evidence: str, evidence_level: str) -> float:
        """Calculate extraction confidence."""
        base = 0.6

        # Evidence level boost
        level_boost = {
            "verified": 0.3,
            "demonstrated": 0.2,
            "mentioned": 0.1,
            "none": -0.2,
        }
        base += level_boost.get(evidence_level, 0)

        # Multiple mentions boost
        mentions = len(re.findall(rf"(?<!\w){re.escape(skill.lower())}(?!\w)", text_lower))
        if mentions > 1:
            base += min(0.15, mentions * 0.03)

        # Evidence quality
        if len(evidence) > 50:
            base += 0.05
        elif len(evidence) < 20:
            base -= 0.1

        return max(0.1, min(1.0, base))

    def get_canonical_skill(self, term: str) -> Optional[str]:
        """Map a term to its canonical skill name."""
        return self.taxonomy.get_canonical(term)

    def get_all_canonical_skills(self) -> list[str]:
        """Get all canonical skill names."""
        return self.taxonomy.all_canonical()

    def add_user_confirmation(self, matches: list[SkillMatch], canonical_skill: str, confirmed: bool) -> list[SkillMatch]:
        """Update user confirmation status for a skill."""
        for match in matches:
            if match.canonical_skill == canonical_skill:
                match.user_confirmed = confirmed
                if confirmed and match.evidence_level == "mentioned":
                    match.evidence_level = "verified"
                elif not confirmed and match.evidence_level == "verified":
                    match.evidence_level = "demonstrated"
        return matches