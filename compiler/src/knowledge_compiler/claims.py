from knowledge_compiler.models import Claim, Evidence
from knowledge_compiler.confidence import assess_confidence

def generate_claims(evidence: list[Evidence]) -> list[Claim]:
    grouped_evidence: dict[str,list[Evidence]] = {} 

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
            if any(item.kind == "ai_observation" for item in evidence_tuple):
                status = "UNKNOWN"
            claims.append(
                Claim(
                    statement=statement,
                    evidence=evidence_tuple,
                    confidence=assess_confidence(evidence_tuple),
                    status=status
                )
            )

    return claims