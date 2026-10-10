import pytest

from knowledge_compiler import terminal_logo


def test_render_terminal_logo_returns_expected_number_of_lines():
    lines = terminal_logo.render_terminal_logo(width=32)

    assert len(lines) == 16
    assert all(line.endswith("\033[0m") for line in lines)


def test_render_terminal_logo_contains_colored_terminal_output():
    output = "\n".join(terminal_logo.render_terminal_logo(width=32))

    assert "\033[38;2;" in output
    assert "\033[48;2;" in output
    assert "▀" in output


def test_render_terminal_logo_rejects_width_below_minimum():
    with pytest.raises(ValueError, match="at least 8"):
        terminal_logo.render_terminal_logo(width=7)


def test_render_terminal_logo_rejects_missing_asset(monkeypatch, tmp_path):
    missing_logo = tmp_path / "missing.svg"
    monkeypatch.setattr(terminal_logo, "LOGO_PATH", missing_logo)

    with pytest.raises(FileNotFoundError, match="logo not found"):
        terminal_logo.render_terminal_logo(width=32)