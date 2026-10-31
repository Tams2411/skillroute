"""Tests for escaping untrusted text in HTML render helpers."""

from career_coach.ui.theme import (
    render_alert,
    render_chip,
    render_empty_state,
    render_metric,
    render_section_header,
    render_skill_card,
    render_status,
)


def test_skill_card_escapes_resume_and_job_description_text():
    payload = '<img src=x onerror="alert(1)">'

    rendered = render_skill_card(
        {
            "canonical_skill": payload,
            "reason": payload,
            "jd_evidence": payload,
            "resume_evidence": payload,
            "uncertainty": payload,
        },
        show_priority=True,
    )

    assert "<img" not in rendered
    assert "&lt;img" in rendered


def test_skill_card_markup_has_no_blank_lines_that_split_html_blocks():
    rendered = render_skill_card(
        {
            "canonical_skill": "python",
            "priority": 0.5,
            "jd_evidence": "Preferred skills:\n\nTerraform",
            "resume_evidence": "Experience:\n\nBuilt with Python",
        },
        show_priority=True,
    )

    assert all(line.strip() for line in rendered.splitlines())
    assert "JD: Preferred skills: Terraform..." in rendered
    assert "Evidence: Experience: Built with Python..." in rendered


def test_skill_card_labels_and_discloses_self_reported_evidence():
    rendered = render_skill_card(
        {
            "canonical_skill": "kubernetes",
            "evidence_level": "self_reported",
            "resume_evidence": "Self-reported by user; not independently verified.",
        }
    )

    assert "self-reported" in rendered
    assert "Evidence: Self-reported by user; not independently verified..." in rendered


def test_skill_card_distinguishes_evidence_source_confidence_and_strength():
    rendered = render_skill_card(
        {
            "canonical_skill": "python",
            "evidence_level": "demonstrated",
            "evidence_strength": 0.4,
            "resume_evidence_source": "resume",
            "resume_extraction_confidence": 0.86,
            "resume_evidence": "Built production services using Python.",
        }
    )

    assert "Source: resume" in rendered
    assert "Extraction confidence: 86%" in rendered
    assert "Evidence strength: 40%" in rendered


def test_badges_and_alerts_escape_untrusted_text():
    payload = '<img src=x onerror="alert(1)">'

    for rendered in (
        render_chip(payload),
        render_status(payload),
        render_alert(payload),
    ):
        assert "<img" not in rendered
        assert "&lt;img" in rendered


def test_multiline_render_helpers_return_html_not_indented_code_blocks():
    for rendered in (
        render_metric("Readiness", "75%"),
        render_empty_state("No results", "Run an analysis to continue."),
        render_section_header("Learning Plan", "Four weeks"),
    ):
        assert rendered.startswith("<")
        assert "\n" not in rendered
