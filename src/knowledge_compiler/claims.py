from knowledge_compiler.models import Claim, Evidence
from knowledge_compiler.confidence import assess_confidence

def generate_claims(evidence: list[Evidence]) -> list[Claim]:
    claims: list[Claim] = []

    for item in evidence:
        statement = None

        if item.kind == "documentation":
            statement = "The repository contains documentation."
        elif item.kind == "file_content":
            statement = (f"The repository contains source code in {item.source.name}.")
        elif item.kind == "test":
            statement = "The repository contains automated tests."
        if statement is not None:
            supporting_evidence = (item,)

            claims.append(
                Claim(
                    statement=statement,
                    evidence=supporting_evidence,
                    confidence=assess_confidence(supporting_evidence),
                    status="SUPPORTED"
                )
            )

    return claims