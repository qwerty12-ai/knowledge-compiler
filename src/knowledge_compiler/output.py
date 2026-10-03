import json
from dataclasses import asdict, dataclass
from pathlib import Path
from knowledge_compiler.models import Claim, Evidence

@dataclass(frozen=True)
class EvidenceOutput:
    id: str
    source: str
    kind: str
    description: str
    language: str | None
    line_start: int | None
    line_end: int | None
    content: str | None

@dataclass(frozen=True)
class ClaimOutput:
    id: str
    statement: str
    status: str
    confidence: float
    evidence_ids: tuple[str,...]

@dataclass(frozen=True)
class AnalysisResult:
    schema_version: str
    repository: str
    files_discovered: int
    with_ai: bool
    limit: int | None
    claims: tuple[ClaimOutput,...]
    evidence: tuple[EvidenceOutput,...]
    errors: tuple[str,...] = ()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

def build_analysis_result(
        repository: Path,
        files_discovered: int,
        evidence: list[Evidence],
        claims: list[Claim],
        with_ai: bool = False,
        limit: int | None = None,
        errors: list[str] | None = None
) -> AnalysisResult:
    evidence_outputs = []
    evidence_ids_by_object: dict[int, str] = {}

    for index, item in enumerate(evidence,start=1):
        evidence_id = f"evidence-{index:04d}"
        evidence_ids_by_object[id(item)] = evidence_id

        evidence_outputs.append(
            EvidenceOutput(
                id=evidence_id,
                source=str(item.source),
                kind=item.kind,
                description=item.description,
                language=item.language,
                line_start=item.line_start,
                line_end=item.line_end,
                content=item.content
            )
        )

    claim_outputs = []

    for index, claim in enumerate(claims, start=1):
        claim_evidence_ids = tuple(
            evidence_ids_by_object[id(item)] for item in claim.evidence if id(item) in evidence_ids_by_object
        )

        claim_outputs.append(
            ClaimOutput(
                id=f"claim-{index:04d}",
                statement=claim.statement,
                status=claim.status,
                confidence=claim.confidence,
                evidence_ids=claim_evidence_ids
            )
        )

    return AnalysisResult(
        schema_version="1.0",
        repository=str(repository.resolve()),
        files_discovered=files_discovered,
        with_ai=with_ai,
        limit=limit,
        claims=tuple(claim_outputs),
        evidence=tuple(evidence_outputs),
        errors=tuple(errors or [])
    )