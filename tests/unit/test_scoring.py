"""Unit tests for domain scoring logic."""

import pytest
from career_coach.domain.schemas import EvidenceLevel, JobSkillRequirement, SkillEvidence
from career_coach.domain.scoring import (
    evidence_level_to_weight,
    calculate_priority,
    compute_skill_gap,
    rank_gaps,
    calculate_readiness_score,
    get_top_gaps,
    filter_actionable_gaps,
)


class TestEvidenceWeights:
    """Test evidence level to weight conversion."""
    
    def test_none_returns_zero(self):
        assert evidence_level_to_weight(EvidenceLevel.NONE) == 0.0
    
    def test_mentioned_returns_low(self):
        assert evidence_level_to_weight(EvidenceLevel.MENTIONED) == 0.2
    
    def test_demonstrated_returns_medium(self):
        assert evidence_level_to_weight(EvidenceLevel.DEMONSTRATED) == 0.4
    
    def test_verified_returns_high(self):
        assert evidence_level_to_weight(EvidenceLevel.VERIFIED) == 0.9


class TestCalculatePriority:
    """Test priority calculation formula: R × (1-E) × C"""
    
    def test_no_evidence_max_priority(self):
        """Skill required but no evidence = high priority"""
        priority = calculate_priority(
            role_relevance=1.0,
            evidence_level=EvidenceLevel.NONE,
            extraction_confidence=1.0
        )
        assert priority == pytest.approx(1.0)
    
    def test_verified_evidence_zero_priority(self):
        """Skill verified = zero priority"""
        priority = calculate_priority(
            role_relevance=1.0,
            evidence_level=EvidenceLevel.VERIFIED,
            extraction_confidence=1.0
        )
        assert priority == pytest.approx(0.1)
    
    def test_mentioned_evidence_medium_priority(self):
        priority = calculate_priority(
            role_relevance=0.8,
            evidence_level=EvidenceLevel.MENTIONED,
            extraction_confidence=1.0
        )
        assert priority == pytest.approx(0.64)
    
    def test_demonstrated_evidence_low_priority(self):
        priority = calculate_priority(
            role_relevance=0.8,
            evidence_level=EvidenceLevel.DEMONSTRATED,
            extraction_confidence=1.0
        )
        assert priority == pytest.approx(0.48)
    
    def test_low_confidence_reduces_priority(self):
        priority = calculate_priority(
            role_relevance=1.0,
            evidence_level=EvidenceLevel.NONE,
            extraction_confidence=0.5
        )
        assert priority == pytest.approx(0.5)
    
    def test_low_relevance_reduces_priority(self):
        priority = calculate_priority(
            role_relevance=0.3,
            evidence_level=EvidenceLevel.NONE,
            extraction_confidence=1.0
        )
        assert priority == pytest.approx(0.3)
    
    def test_bounds_clamped(self):
        """Priority should be clamped to [0, 1]"""
        priority = calculate_priority(1.0, EvidenceLevel.VERIFIED, 1.0)
        assert 0.0 <= priority <= 1.0


class TestComputeSkillGap:
    """Test skill gap computation."""
    
    def test_missing_skill_creates_gap(self):
        jd_skill = JobSkillRequirement(
            canonical_skill="kubernetes",
            importance=0.9,
            evidence_phrase="Kubernetes for container orchestration",
            extraction_confidence=0.95
        )
        
        gap = compute_skill_gap(jd_skill, None)
        
        assert gap.canonical_skill == "kubernetes"
        assert gap.role_relevance == 0.9
        assert gap.evidence_strength == 0.0
        assert gap.priority == pytest.approx(0.855)
        assert "not found in resume" in gap.reason.lower()
        assert gap.jd_evidence == "Kubernetes for container orchestration"
        assert "No evidence found" in gap.resume_evidence
    
    def test_mentioned_skill_creates_gap(self):
        jd_skill = JobSkillRequirement(
            canonical_skill="docker",
            importance=0.7,
            evidence_phrase="Docker for containerization",
            extraction_confidence=0.9
        )
        
        resume_evidence = SkillEvidence(
            canonical_skill="docker",
            evidence_level=EvidenceLevel.MENTIONED,
            source="resume",
            supporting_evidence="Familiar with Docker",
            user_confirmed=False,
        )
        
        gap = compute_skill_gap(jd_skill, resume_evidence)
        
        assert gap.canonical_skill == "docker"
        assert gap.evidence_strength == 0.2
        assert gap.priority == pytest.approx(0.504)
        assert "mentioned in resume" in gap.reason.lower()
        assert gap.resume_evidence == "Familiar with Docker"
    
    def test_verified_skill_low_priority(self):
        jd_skill = JobSkillRequirement(
            canonical_skill="python",
            importance=1.0,
            evidence_phrase="5+ years Python",
            extraction_confidence=1.0
        )
        
        resume_evidence = SkillEvidence(
            canonical_skill="python",
            evidence_level=EvidenceLevel.VERIFIED,
            source="resume",
            supporting_evidence="3 years Python building pipelines",
            user_confirmed=True,
        )
        
        gap = compute_skill_gap(jd_skill, resume_evidence)
        
        assert gap.evidence_strength == 0.9
        assert gap.priority == pytest.approx(0.1)
        assert "verified in resume" in gap.reason.lower()


class TestRankGaps:
    """Test gap ranking."""
    
    def test_ranks_by_priority_descending(self):
        from career_coach.domain.schemas import SkillGap
        
        gaps = [
            SkillGap(
                canonical_skill="a", role_relevance=0.5, evidence_strength=0.5,
                extraction_confidence=1.0, priority=0.25, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="b", role_relevance=0.8, evidence_strength=0.0,
                extraction_confidence=1.0, priority=0.8, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="c", role_relevance=0.6, evidence_strength=0.2,
                extraction_confidence=1.0, priority=0.48, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
        ]
        
        ranked = rank_gaps(gaps)
        
        assert ranked[0].canonical_skill == "b"
        assert ranked[1].canonical_skill == "c"
        assert ranked[2].canonical_skill == "a"


class TestReadinessScore:
    """Test readiness score calculation."""
    
    def test_all_verified_100_percent(self):
        from career_coach.domain.schemas import SkillGap
        
        gaps = [
            SkillGap(
                canonical_skill="python", role_relevance=1.0, evidence_strength=0.9,
                extraction_confidence=1.0, priority=0.1, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="sql", role_relevance=0.8, evidence_strength=0.9,
                extraction_confidence=1.0, priority=0.08, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
        ]
        
        score = calculate_readiness_score(gaps)
        assert score == pytest.approx(0.9, abs=0.01)
    
    def test_no_skills_returns_insufficient_data(self):
        assert calculate_readiness_score([]) is None

    def test_zero_total_requirement_weight_returns_insufficient_data(self):
        from career_coach.domain.schemas import SkillGap

        gap = SkillGap(
            canonical_skill="python", role_relevance=0.0, evidence_strength=0.9,
            extraction_confidence=1.0, priority=0.0, reason="test",
            uncertainty="", jd_evidence="", resume_evidence=""
        )

        assert calculate_readiness_score([gap]) is None
    
    def test_all_missing_zero_percent(self):
        from career_coach.domain.schemas import SkillGap
        
        gaps = [
            SkillGap(
                canonical_skill="k8s", role_relevance=1.0, evidence_strength=0.0,
                extraction_confidence=1.0, priority=1.0, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
        ]
        
        score = calculate_readiness_score(gaps)
        assert score == 0.0


class TestGetTopGaps:
    """Test top N gaps selection."""
    
    def test_returns_n_gaps(self):
        from career_coach.domain.schemas import SkillGap
        
        gaps = [
            SkillGap(
                canonical_skill=f"skill_{i}", role_relevance=0.5, evidence_strength=0.0,
                extraction_confidence=1.0, priority=max(0.0, 0.5 - i*0.05), reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            )
            for i in range(10)
        ]
        
        top3 = get_top_gaps(gaps, n=3)
        
        assert len(top3) == 3
        assert top3[0].canonical_skill == "skill_0"
        assert top3[2].canonical_skill == "skill_2"


class TestFilterActionableGaps:
    """Test actionable gap filtering."""
    
    def test_filters_by_min_priority(self):
        from career_coach.domain.schemas import SkillGap
        
        gaps = [
            SkillGap(
                canonical_skill="high", role_relevance=0.8, evidence_strength=0.0,
                extraction_confidence=1.0, priority=0.8, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="medium", role_relevance=0.5, evidence_strength=0.2,
                extraction_confidence=1.0, priority=0.4, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="low", role_relevance=0.3, evidence_strength=0.4,
                extraction_confidence=1.0, priority=0.18, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
            SkillGap(
                canonical_skill="minimal", role_relevance=0.2, evidence_strength=0.9,
                extraction_confidence=1.0, priority=0.02, reason="test",
                uncertainty="", jd_evidence="", resume_evidence=""
            ),
        ]
        
        actionable = filter_actionable_gaps(gaps, min_priority=0.15)
        
        assert len(actionable) == 3
        assert actionable[0].canonical_skill == "high"
        assert actionable[1].canonical_skill == "medium"
        assert actionable[2].canonical_skill == "low"