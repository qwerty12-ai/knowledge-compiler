from knowledge_compiler.evidence import Evidence

def assess_confidence(evidence: tuple[Evidence,...]) -> float:
    if not evidence:
        return 0.0

    unique_sources = {item.source for item in evidence}

    if len(unique_sources) == 1:
        return 0.6

    unique_kinds = {item.kind for item in evidence}

    if len(unique_kinds) > 1:
        return 0.9

    return 0.8