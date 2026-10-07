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
    assert len(context.evidence) == 3

    assert any(
        evidence.kind == "function"
        and evidence.source == Path("payment.py")
        and evidence.line_start == 1
        and evidence.line_end == 2
        for evidence in context.evidence
    )

    assert any(
        evidence.source == Path("README.md")
        for evidence in context.evidence
    )

    assert any(
        evidence.language == "Python"
        for evidence in context.evidence
    )

def test_build_repository_context_extracts_python_structure(tmp_path: Path):
    source_file = tmp_path / "payment.py"
    source_file.write_text(
        "class PaymentService:\n"
        "    def execute(self):\n"
        "        pass\n"
    )

    context = build_repository_context(tmp_path)

    assert len(context.structures) == 1

    structure = context.structures[0]

    assert len(structure.classes) == 1
    assert structure.classes[0].name == "PaymentService"

    assert len(structure.functions) == 1
    assert structure.functions[0].name == "execute"
    assert structure.functions[0].parent_class == "PaymentService"