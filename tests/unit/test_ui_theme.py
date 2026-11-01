from career_coach.ui import theme


def test_theme_keeps_sidebar_reopen_control_visible(monkeypatch):
    styles = []
    monkeypatch.setattr(theme.st, "html", styles.append)

    theme.apply_theme()

    assert len(styles) == 1
    assert "header { visibility: hidden; }" not in styles[0]
