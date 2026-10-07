from knowledge_compiler.models import Claim, Evidence, ClaimStatus
from knowledge_compiler.confidence import assess_confidence
from knowledge_compiler.observation_validation import ObservationValidation


def generate_claims(
    evidence: list[Evidence],
    validations: list[ObservationValidation] | None = None,
) -> list[Claim]:

    grouped_evidence: dict[str, list[Evidence]] = {}

    for item in evidence:
        statement = None

        if item.kind == "documentation":
            statement = "The repository contains documentation."

        elif item.kind == "file_content":
            statement = (
                f"The repository contains source code in {item.source}."
            )

        elif item.kind == "test":
            statement = "The repository contains automated tests."

        elif item.kind == "dependency":
            statement = (
                f"The repository declares dependencies in {item.source.name}."
            )

        elif item.kind == "ai_observation":
            continue

        if statement is not None:
            if statement not in grouped_evidence:
                grouped_evidence[statement] = []

            grouped_evidence[statement].append(item)

    claims: list[Claim] = []

    
    for statement, supported_evidence in grouped_evidence.items():
        evidence_tuple = tuple(supported_evidence)

        claims.append(
            Claim(
                statement=statement,
                evidence=evidence_tuple,
                confidence=1.0,
                status=ClaimStatus.VERIFIED,
            )
        )

    
    for validation in validations or []:
        observation = validation.observation
        statement = observation.statement

        if validation.status.value == "SUPPORTED":
            status = ClaimStatus.SUPPORTED
            claim_evidence = validation.supporting_evidence

        elif validation.status.value == "CONTRADICTED":
            status = ClaimStatus.CONTRADICTED
            claim_evidence = validation.contradicting_evidence

        else:
            status = ClaimStatus.UNKNOWN
            claim_evidence = ()

        confidence = assess_confidence(
            tuple(claim_evidence)
        )

        if status == ClaimStatus.CONTRADICTED:
            confidence = 1.0 - confidence

        claims.append(
            Claim(
                statement=statement,
                evidence=tuple(claim_evidence),
                confidence=confidence,
                status=status,
            )
        )

    return claims