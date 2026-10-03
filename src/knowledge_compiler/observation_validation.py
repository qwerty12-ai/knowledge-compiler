from dataclasses import dataclass
from enum import Enum

from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.models import Evidence

class ValidationStatus(str, Enum):
    SUPPORTED = "SUPPORTED",
    CONTRADICTED = "CONTRADICTED",
    INCONCLUSIVE = "INCONCLUSIVE"

@dataclass(frozen=True)
class ObservationValidation:
    observation: str
    status: ValidationStatus
    supporting_evidence: tuple[Evidence, ...] = ()
    contradicting_evidence: tuple[Evidence, ...] = ()

def validate_observations(result: InvestigationResult, independent_evidence: list[Evidence], evidence_links: dict[str, list[Evidence]] | None=None) -> list[ObservationValidation]:
    
    evidence_links = evidence_links or {}
    
    independent_evidence = [
        item for item in independent_evidence if item.kind != "ai_observation"
    ]

    validations = []

    for observation in result.observations:
        linked_evidence = evidence_links.get(observation, [])
        independent_ids = {id(item) for item in linked_evidence}
        linked_evidence = [
            item for item in linked_evidence if id(item) in independent_ids
        ]
        validations.append(
            ObservationValidation(
                observation=observation,
                status=ValidationStatus.INCONCLUSIVE
            )
        )

    return validations