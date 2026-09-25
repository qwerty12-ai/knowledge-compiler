from pathlib import Path
from knowledge_compiler.models import DiscoveredFile, Evidence, RepositoryContext


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