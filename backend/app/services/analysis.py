from knowledge_compiler.cli import analyze as run_analysis
from .persistance import persist_analysis
from ..models import AnalysisRequest

def analyze_repository(request: AnalysisRequest):
    result = run_analysis(
        repository=request.repository_path,
        limit=request.limit
    )
    persist_analysis(result)
    return result