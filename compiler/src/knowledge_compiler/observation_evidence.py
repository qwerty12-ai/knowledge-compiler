from knowledge_compiler.models import Evidence
from knowledge_compiler.investigator import InvestigationResult

def convert_observations_to_evidence(result: InvestigationResult) -> list[Evidence]:
    evidence = []

    for observation in result.observations:
        evidence.append(
            Evidence(
                source=result.unit.source,
                kind="ai_observation",
                description=observation.statement,
                origin="ai",
                language=result.unit.source.suffix.lstrip(".") or None,
                content=result.unit.content,
                line_start=result.unit.line_start,
                line_end=result.unit.line_end,
                unit_id=result.unit.unit_id
            )
        )

    return evidence