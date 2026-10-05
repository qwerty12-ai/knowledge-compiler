from dataclasses import dataclass
from enum import Enum
from typing import Callable

from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.models import Evidence

class ValidationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INCONCLUSIVE = "INCONCLUSIVE"

@dataclass(frozen=True)
class ObservationValidation:
    observation: str
    status: ValidationStatus
    supporting_evidence: tuple[Evidence, ...] = ()
    contradicting_evidence: tuple[Evidence, ...] = ()

def validate_observations(
    result: InvestigationResult, 
    independent_evidence: list[Evidence], 
    evidence_links: dict[str, list[Evidence]] | None=None,
    verifier: Callable[[tuple[str,...], str],list[ValidationStatus]] | None = None
) -> list[ObservationValidation]:
    
    evidence_links = evidence_links or {}
    
    independent_evidence = [
        item for item in independent_evidence if item.kind != "ai_observation"
    ]

    if not result.observations:
        return []

    source_evidence = [
        item for item in independent_evidence if item.source == result.unit.source
    ]

    if not source_evidence or verifier is None:
        return [
            ObservationValidation(
                observation=observation,
                status=ValidationStatus.INCONCLUSIVE
            )
            for observation in result.observations
        ]

    source_content = "\n".join(
        item.content or item.description for item in source_evidence
    )

    statuses = verifier(
        result.observations,
        source_content
    )

    if len(statuses) != len(result.observations):
        raise ValueError("Verifier returned a different number of results ""than observations.")

    validations = []

    for observation, status in zip(
        result.observations,
        statuses
    ):
        linked_evidence = evidence_links.get(observation,source_evidence)

        supporting = ()
        contradicting = ()

        if status == ValidationStatus.SUPPORTED:
            supporting = tuple(linked_evidence)
        elif status == ValidationStatus.CONTRADICTED:
            contradicting = tuple(linked_evidence)

        validations.append(
            ObservationValidation(
                observation=observation,
                status=status,
                supporting_evidence=supporting,
                contradicting_evidence=contradicting
            )
        )

    return validations
        

def verify_with_ai(observations: tuple[str,...], source_content: str) -> list[ValidationStatus]:
    from ollama import Client

    client = Client()

    formatted_observations = "\n".join(
        f"{index + 1}. {observation}" for index, observation in enumerate(observations)
    )

    prompt = f"""
You are verifying software-engineering observations against source code.

SOURCE CODE:
{source_content}

OBSERVATIONS:
{formatted_observations}

For EACH observation, determine whether the source code:

- SUPPORTS it
- CONTRADICTS it
- INCONCLUSIVE: the source does not provide enough evidence

Return ONLY valid JSON in this exact structure:

{{
  "results": [
    {{
      "index": 1,
      "status": "SUPPORTED"
    }},
    {{
      "index": 2,
      "status": "INCONCLUSIVE"
    }}
  ]
}}

Rules:
- Return exactly one result for every observation.
- Preserve the observation order.
- SUPPORTED means the source directly provides evidence.
- CONTRADICTED means the source directly conflicts with it.
- INCONCLUSIVE means there is insufficient evidence.
- Do not assume behavior that is not visible in the source.
"""

    response = client.chat(
        model="qwen3:4b",
        think=False,
        format="json",
        options = {
            "temperature": 0.0,
            "num_predict": 200
        },
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    import json

    data = json.loads(response["message"].content)

    results = data.get("results", [])

    if len(results) != len(observations):
        return [
            ValidationStatus.INCONCLUSIVE for _ in observations
        ]

    return [
        ValidationStatus(item["status"]) for item in data["results"]
    ]