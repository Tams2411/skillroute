"""Regression tests for chip variant aliasing and icon rendering."""

from career_coach.ui.theme import render_chip, render_svg


def test_ui_chip_variants_resolve_to_themed_palette():
    """Raw UI variant names leaked into class names like "chip-teal"."""
    assert "chip-gap" in render_chip("Python", variant="teal")
    assert "chip-verified" in render_chip("Python", variant="purple")
    assert "chip-required" in render_chip("Python", variant="error")
    assert "chip-preferred" in render_chip("Python", variant="warning")
    assert "chip-matched" in render_chip("Python", variant="success")


def test_alias_does_not_leak_the_raw_variant_name():
    for variant in ("teal", "purple", "error", "warning", "success"):
        assert f"chip-{variant}" not in render_chip("Python", variant=variant)


def test_help_circle_icon_renders_svg():
    svg = render_svg("help-circle")

    assert svg.startswith("<svg")
    assert "circle" in svg
    assert 'aria-hidden="true"' in svg


def test_chip_with_icon_includes_the_svg():
    html = render_chip("Python", variant="gap", icon="help-circle")

    assert html.startswith('<span class="chip chip-gap">')
    assert "<svg" in html
