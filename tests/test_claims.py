from pathlib import Path

from knowledge_compiler.claims import generate_claims
from knowledge_compiler.models import Evidence


def test_generate_claim_from_file_content(tmp_path: Path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')\n")

    evidence = Evidence(
        source=file_path,
        kind="file_content",
        description="File contains 1 lines of source code.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository contains source code in example.py."
    )
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 0.8
    assert claims[0].status == "SUPPORTED"


def test_generate_claim_from_documentation(tmp_path: Path):
    file_path = tmp_path / "README.md"
    file_path.write_text("# Knowledge Compiler\n")

    evidence = Evidence(
        source=file_path,
        kind="documentation",
        description="Repository documentation.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == "The repository contains documentation."
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 0.9
    assert claims[0].status == "SUPPORTED"


def test_generate_claims_from_empty_evidence():
    assert generate_claims([]) == []


def test_generate_claims_ignores_unknown_evidence(tmp_path: Path):
    file_path = tmp_path / "something.bin"

    evidence = Evidence(
        source=file_path,
        kind="unknown",
        description="Unknown evidence.",
    )

    assert generate_claims([evidence]) == []