from datetime import datetime
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    repository_path: str = Field(
        min_length=1,
        description="Path to the repository that should be analyzed."
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        description="Optional maximum number of AI investigation units to analyze."
    )
    with_ai: bool = Field(
        default=False,
        description="Whether AI-powered repository investigation should be enabled."
    )


class AnalysisCreatedResponse(BaseModel):
    analysis_id: str
    job_id: str
    status: str


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    stage: str | None = None
    progress: int
    database_id: int | None = None
    repository_path: str | None = None
    files_discovered: int | None = None
    with_ai: bool | None = None
    analysis_limit: int | None = None


class ClaimSummary(BaseModel):
    id: int
    statement: str
    status: str
    confidence: float
    created_at: datetime


class ClaimsResponse(BaseModel):
    analysis_id: str
    claims: list[ClaimSummary]


class EvidenceItem(BaseModel):
    id: int
    source: str
    kind: str
    description: str
    language: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    content: str | None = None
    created_at: datetime

class EvidenceSummary(BaseModel):
    id: int
    source: str
    kind: str
    description: str
    language: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    created_at: datetime


class ClaimDetailResponse(BaseModel):
    id: int
    analysis_id: int
    statement: str
    status: str
    confidence: float
    created_at: datetime
    evidence: list[EvidenceItem]


class EvidenceResponse(BaseModel):
    analysis_id: str
    evidence: list[EvidenceSummary]


class AnalysisHistoryItem(BaseModel):
    id: int
    repository_path: str
    schema_version: str
    files_discovered: int
    with_ai: bool
    analysis_limit: int | None = None
    created_at: datetime
    claims_count: int
    evidence_count: int


class AnalysisHistoryResponse(BaseModel):
    analyses: list[AnalysisHistoryItem]


class RedisAnalysisState(BaseModel):
    analysis_id: str
    state: dict
    ttl: int


class RedisQueueState(BaseModel):
    queue: str
    counts: dict


class RedisChannelState(BaseModel):
    channel: str
    subscribers: int


class RedisInspectorResponse(BaseModel):
    state: RedisAnalysisState
    queue: RedisQueueState
    channel: RedisChannelState