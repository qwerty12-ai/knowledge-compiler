from knowledge_compiler.pipeline import compile_repository

from .persistence import persist_analysis
from .redis_state import set_analysis_state
from ..models import AnalysisRequest


def analyze_repository(request: AnalysisRequest, analysis_id: str) -> int:
    def report_progress(stage: str, progress: int) -> None:
        set_analysis_state(
            analysis_id=analysis_id,
            status="running",
            stage=stage,
            progress=progress,
        )

    result = compile_repository(
        repository=request.repository_path,
        with_ai=request.with_ai,
        limit=request.limit,
        progress_callback=report_progress,
    )

    report_progress("persistence", 95)

    return persist_analysis(result)