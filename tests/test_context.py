from pathlib import Path
from knowledge_compiler.models import DiscoveredFile, Evidence, RepositoryContext
from knowledge_compiler.context import build_repository_context

def test_repository_context_contains_files_and_evidence(tmp_path: Path):
    file_path = Path("src/payment.py")

    discovered_file = DiscoveredFile(
        path=file_path,
        extension=".py",
        language="Python",
        size_bytes=100,
        category="source",
    )

    evidence = Evidence(
        source=file_path,
        kind="file_content",
        description="File contains 10 lines of source code.",
        language="Python",
    )

    context = RepositoryContext(
        files=(discovered_file,),
        evidence=(evidence,),
    )

    assert context.files == (discovered_file,)
    assert context.evidence == (evidence,)

def test_build_repository_context_from_repository(tmp_path: Path):
    source_file = tmp_path / "payment.py"
    source_file.write_text(
        "def execute_payment():\n"
        "    pass\n"
    )

    readme_file = tmp_path / "README.md"
    readme_file.write_text("# Payment Service\n")

    context = build_repository_context(tmp_path)

    assert len(context.files) == 2
    assert len(context.evidence) == 2

    assert any(
        file.path == Path("payment.py")
        for file in context.files
    )

    assert any(
        evidence.source == readme_file
        for evidence in context.evidence
    )

    assert any(
        evidence.language == "Python"
        for evidence in context.evidence
    )