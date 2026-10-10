import json
import os
import sys

from knowledge_compiler.cli import analyze, serialize_result
from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.models import Claim, Evidence
from knowledge_compiler.output import build_analysis_result
from knowledge_compiler.cli import TerminalStyle
from pathlib import Path

def fake_investigate(unit):
    return InvestigationResult(
        unit=unit,
        observations=("The unit contains a test observation.",)
    )

def test_analyze_existing_repository(capsys, monkeypatch):
    monkeypatch.setattr(
        "knowledge_compiler.pipeline.investigate",
        fake_investigate
    )

    result = analyze(".")

    assert result is not None
    assert result.files_discovered > 0
    assert len(result.claims) > 0

def test_analyze_missing_repository(capsys):
    import pytest

    with pytest.raises(ValueError, match="repository does not exist"):
        analyze("./does-not-exist")

def test_compact_json_omits_source_content(tmp_path):
    evidence = Evidence(
        source=Path("payment.py"),
        kind="file_content",
        description="Payment source code.",
        content="def process_payment():\n    return True",
        line_start=1,
        line_end=2,
    )

    claim = Claim(
        statement="The payment source exists.",
        evidence=(evidence,),
        confidence=0.8,
        status="SUPPORTED",
    )

    result = build_analysis_result(
        repository=tmp_path,
        files_discovered=1,
        evidence=[evidence],
        claims=[claim],
    )

    payload = json.loads(serialize_result(result, compact=True))

    assert payload["evidence"][0]["content"] is None
    assert payload["evidence"][0]["source"] == "payment.py"
    assert payload["evidence"][0]["description"] == "Payment source code."
    assert payload["claims"][0]["evidence_ids"] == ["evidence-0001"]


def test_full_json_preserves_source_content(tmp_path):
    evidence = Evidence(
        source=Path("payment.py"),
        kind="file_content",
        description="Payment source code.",
        content="def process_payment():\n    return True",
    )

    result = build_analysis_result(
        repository=tmp_path,
        files_discovered=1,
        evidence=[evidence],
        claims=[],
    )

    payload = json.loads(serialize_result(result))

    assert payload["evidence"][0]["content"] == (
        "def process_payment():\n    return True"
    )

def test_colors_enabled_for_terminal_without_no_color(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert TerminalStyle.colors_enabled() is True


def test_colors_disabled_when_no_color_is_set(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("NO_COLOR", "")

    assert TerminalStyle.colors_enabled() is False


def test_colors_disabled_when_output_is_redirected(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert TerminalStyle.colors_enabled() is False

def test_human_output_shows_claim_evidence_and_workstation_guidance(
    tmp_path, capsys, monkeypatch
):
    evidence = Evidence(
        source=Path("payment.py"),
        kind="file_content",
        description="Payment processing implementation.",
        content="def process_payment(amount): return amount > 0",
        line_start=1,
        line_end=8,
    )

    claim = Claim(
        statement="Payment processing rejects non-positive amounts.",
        evidence=(evidence,),
        confidence=0.9,
        status="SUPPORTED",
    )

    result = build_analysis_result(
        repository=tmp_path,
        files_discovered=1,
        evidence=[evidence],
        claims=[claim],
    )

    monkeypatch.setattr(
        TerminalStyle,
        "colors_enabled",
        staticmethod(lambda: False),
    )

    from knowledge_compiler.cli import print_human_result
    print_human_result(result)

    output = capsys.readouterr().out

    assert "Payment processing rejects non-positive amounts." in output
    assert "SUPPORTED" in output
    assert "Confidence: 90%" in output
    assert "[file content] payment.py:1-8" in output
    assert "Payment processing implementation." in output
    assert "Preview: def process_payment(amount): return amount > 0" in output
    assert "Create a new analysis of this same repository" in output
    assert "does not automatically appear in the workstation" in output


def test_human_output_does_not_repeat_preview_for_shared_evidence(
    tmp_path, capsys, monkeypatch
):
    evidence = Evidence(
        source=Path("shared.py"),
        kind="file_content",
        description="Shared source evidence.",
        content="shared source preview",
        line_start=1,
        line_end=2,
    )

    first_claim = Claim(
        statement="First claim supported by the source.",
        evidence=(evidence,),
        confidence=0.9,
        status="SUPPORTED",
    )
    second_claim = Claim(
        statement="Second claim supported by the same source.",
        evidence=(evidence,),
        confidence=0.8,
        status="SUPPORTED",
    )

    result = build_analysis_result(
        repository=tmp_path,
        files_discovered=1,
        evidence=[evidence],
        claims=[first_claim, second_claim],
    )

    monkeypatch.setattr(
        TerminalStyle,
        "colors_enabled",
        staticmethod(lambda: False),
    )

    from knowledge_compiler.cli import print_human_result
    print_human_result(result)

    output = capsys.readouterr().out

    assert output.count("Preview: shared source preview") == 1
    assert output.count("[file content] shared.py:1-2") == 2
    assert output.count("Shared source evidence.") == 2
    assert "First claim supported by the source." in output
    assert "Second claim supported by the same source." in output


def test_human_output_bounds_evidence_preview(
    tmp_path, capsys, monkeypatch
):
    evidence = Evidence(
        source=Path("large.py"),
        kind="file_content",
        description="Large source file.",
        content="x" * 1000,
    )

    claim = Claim(
        statement="A source file exists.",
        evidence=(evidence,),
        confidence=0.7,
        status="WEAKLY_SUPPORTED",
    )

    result = build_analysis_result(
        repository=tmp_path,
        files_discovered=1,
        evidence=[evidence],
        claims=[claim],
    )

    monkeypatch.setattr(
        TerminalStyle,
        "colors_enabled",
        staticmethod(lambda: False),
    )

    from knowledge_compiler.cli import print_human_result
    print_human_result(result)

    output = capsys.readouterr().out

    assert "x" * 177 + "..." in output
    assert "x" * 181 not in output
