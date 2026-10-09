from pathlib import Path
from typing import Callable

from knowledge_compiler.claims import generate_claims
from knowledge_compiler.context import build_repository_context
from knowledge_compiler.investigation import build_investigation_units
from knowledge_compiler.investigator import investigate
from knowledge_compiler.observation_evidence import convert_observations_to_evidence
from knowledge_compiler.observation_validation import (
    validate_observations,
    verify_with_ai,
)
from knowledge_compiler.output import AnalysisResult, build_analysis_result


def compile_repository(
    repository: str | Path,
    with_ai: bool = False,
    limit: int | None = None,
    progress_callback: Callable[[str, int], None] | None = None,
) -> AnalysisResult:
    path = Path(repository)

    if not path.exists():
        raise ValueError(f"repository does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"repository is not a directory: {path}")

    if limit is not None and limit < 1:
        raise ValueError("--limit must be at least 1")

    context = build_repository_context(
        path,
        progress_callback=progress_callback,
    )

    if progress_callback:
        progress_callback("context", 30)

    all_evidence = list(context.evidence)
    all_validations = []
    errors = []

    if with_ai:
        units = build_investigation_units(context)

        units = [
            unit
            for unit in units
            if unit.kind in {"function", "class", "documentation"}
        ]

        if limit is not None:
            units = units[:limit]

        total_units = len(units)

        for index, unit in enumerate(units, start=1):
            try:
                result = investigate(unit)
            except Exception as exc:
                errors.append(str(exc))

                if progress_callback and total_units:
                    progress = 30 + int((index / total_units) * 45)
                    progress_callback("ai_investigation", progress)

                continue

            validations = validate_observations(
                result=result,
                independent_evidence=list(context.evidence),
                verifier=verify_with_ai,
            )

            all_validations.extend(validations)

            observation_evidence = convert_observations_to_evidence(result)
            all_evidence.extend(observation_evidence)

            if progress_callback and total_units:
                progress = 30 + int((index / total_units) * 45)
                progress_callback("ai_investigation", progress)

        if progress_callback:
            progress_callback("ai_investigation", 75)

    else:
        if progress_callback:
            progress_callback("claim_generation", 75)

    claims = generate_claims(
        all_evidence,
        validations=all_validations,
    )

    if progress_callback:
        progress_callback("claim_generation", 90)

    return build_analysis_result(
        repository=path,
        files_discovered=len(context.files),
        evidence=all_evidence,
        claims=claims,
        with_ai=with_ai,
        limit=limit,
        errors=errors,
    )