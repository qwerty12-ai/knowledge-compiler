from knowledge_compiler.models import Claim, Evidence
from knowledge_compiler.confidence import assess_confidence
from knowledge_compiler.observation_validation import ObservationValidation

def generate_claims(evidence: list[Evidence], validations: list[ObservationValidation] | None = None) -> list[Claim]:
    grouped_evidence: dict[str,list[Evidence]] = {} 

    validation_by_observation = {
        validation.observation: validation for validation in (validations or [])
    }

    for item in evidence:
        statement = None

        if item.kind == "documentation":
            statement = "The repository contains documentation."
        elif item.kind == "file_content":
            statement = (f"The repository contains source code in {item.source.name}.")
        elif item.kind == "test":
            statement = "The repository contains automated tests."
        elif item.kind == "ai_observation":
            statement = item.description
        
        if statement is not None:
            if statement not in grouped_evidence:
                grouped_evidence[statement] = []

            grouped_evidence[statement].append(item)

    claims: list[Claim] = []

    for statement, supported_evidence in grouped_evidence.items():
        evidence_tuple = tuple(supported_evidence)

        status = "SUPPORTED"
        claim_evidence = evidence_tuple

        validation = validation_by_observation.get(statement)

        if validation is not None:
            if validation.status.value == "SUPPORTED":
                status = "SUPPORTED"
                claim_evidence = validation.supporting_evidence

            elif validation.status.value == "CONTRADICTED":
                status = "CONTRADICTED"
                claim_evidence = validation.contradicting_evidence

            elif validation.status.value == "INCONCLUSIVE":
                status = "UNKNOWN"
                claim_evidence = evidence_tuple

        elif any(
            item.kind == "ai_observation"
            for item in evidence_tuple
        ):
            status = "UNKNOWN"

        claims.append(
            Claim(
                statement=statement,
                evidence=tuple(claim_evidence),
                confidence=assess_confidence(
                    tuple(claim_evidence)
                ),
                status=status,
            )
        )

    return claims