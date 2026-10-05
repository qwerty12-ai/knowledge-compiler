from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    repository_path: str = Field(
        min_length=1,
        description="Path to the repository that should be analyzed."
    )
    limit: int | None = Field(
        default=None,
        ge=1,
        description="Optional maximum number of files to analyze."
    )
    with_ai: bool = Field(
        default=False,
        description="Whether AI-powered repository investigation should be enabled."
    )