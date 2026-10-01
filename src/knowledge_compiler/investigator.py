from dataclasses import dataclass
from knowledge_compiler.investigation import InvestigationUnit

@dataclass(frozen=True)
class InvestigationResult:
    unit: InvestigationUnit
    observations: tuple[str,...]

def investigate(unit: InvestigationUnit) -> InvestigationResult:
    observations = []

    if unit.kind == "function":
        observations.append(f"The unit defines a function named {unit.name}.")
    elif unit.kind == "class":
        observations.append(f"The unit defines a class named {unit.name}.")
    if unit.kind == "documentation":
        observations.append(f"The unit contains documentation.")

    return InvestigationResult(unit=unit, observations=tuple(observations))