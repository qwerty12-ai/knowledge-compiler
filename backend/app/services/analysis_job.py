from dataclasses import dataclass

QUEUED = "queued"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"

@dataclass(frozen=True)
class AnalysisJob:
    job_id: str
    repository_path: str
    status: str