export type AnalysisStatus =
    | "queued"
    | "running"
    | "completed"
    | "failed";

export type AnalysisStage =
    | "queued"
    | "analysis"
    | "completed"
    | "failed";

export type CreateAnalysisRequest = {
    repository_path: string;
    limit: number | null;
    with_ai: boolean;
};

export type CreateAnalysisResponse = {
    analysis_id: string;
    job_id: string;
    status: AnalysisStatus;
};

export type AnalysisState = {
    analysis_id: string;
    status: AnalysisStatus;
    stage: string | null;
    progress: number;
    database_id: number | null;
    repository_path: string | null;
    files_discovered: number | null;
    with_ai: boolean | null;
    analysis_limit: number | null;
};

export type AnalysisClaim = {
    id: number;
    statement: string;
    status: ClaimStatus;
    confidence: number;
    created_at: string;
};

export type ClaimStatus =
    | "VERIFIED"
    | "SUPPORTED"
    | "WEAKLY_SUPPORTED"
    | "UNKNOWN"
    | "CONTRADICTED"
    | "STALE";

export type EvidenceKind =
    | "ai_observation"
    | "class"
    | "dependency"
    | "documentation"
    | "file_content"
    | "function"
    | "import"
    | "test";

export type ClaimEvidence = {
    id: number;
    source: string;
    kind: EvidenceKind;
    description: string;
    language: string | null;
    line_start: number | null;
    line_end: number | null;
    content: string | null;
    created_at: string;
};

export type ClaimDetail = AnalysisClaim & {
    analysis_id: number;
    evidence: ClaimEvidence[];
};

export type RecentAnalysis = {
    id: number;
    repository_path: string;
    schema_version: string;
    files_discovered: number;
    with_ai: boolean | number;
    analysis_limit: number | null;
    created_at: string;
    claims_count: number;
    evidence_count: number;
};