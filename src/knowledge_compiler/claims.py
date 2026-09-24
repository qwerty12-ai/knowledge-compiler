from knowledge_compiler.models import Claim, Evidence

def generate_claims(evidence: list[Evidence]) -> list[Claim]:
    claims: list[Claim] = []

    for item in evidence:
        if item.kind == "documentation":
            claims.append(
                Claim(
                    statement="The repository contains documentation.",
                    evidence=(item,),
                    confidence=0.9,
                    status="SUPPORTED"
                )
            )
        elif item.kind == "file_content":
            claims.append(
                Claim(
                    statement=f"The repository contains source code in {item.source.name}.",
                    evidence=(item,),
                    confidence=0.8,
                    status="SUPPORTED"
                )
            )

    return claims