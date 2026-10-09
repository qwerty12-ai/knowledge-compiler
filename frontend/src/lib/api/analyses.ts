import type {
  AnalysisClaim,
  AnalysisState,
  ClaimDetail,
  ClaimEvidence,
  CreateAnalysisRequest,
  CreateAnalysisResponse,
  RecentAnalysis,
} from "./types";

export type {
  AnalysisClaim,
  AnalysisState,
  ClaimDetail,
  ClaimEvidence,
  ClaimStatus,
  CreateAnalysisRequest,
  CreateAnalysisResponse,
  EvidenceKind,
  RecentAnalysis,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export type RedisAnalysisState = {
  analysis_id: string;
  state: Record<string, string>;
  ttl: number;
};

export type RedisQueueState = {
  queue: string;
  counts: Record<string, number>;
};

export type RedisChannelState = {
  channel: string;
  subscribers: number;
};

export type RedisInspectorResponse = {
  state: RedisAnalysisState;
  queue: RedisQueueState;
  channel: RedisChannelState;
};

function getApiErrorMessage(
  data: unknown,
  status: number,
): string {
  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {
    const detail = data.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }

          return null;
        })
        .filter(
          (message): message is string =>
            message !== null,
        );

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  }

  return `API request failed with status ${status}.`;
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    let data: unknown = null;

    try {
      data = await response.json();
    } catch {
      // Use the generic status message below.
    }

    throw new Error(
      getApiErrorMessage(
        data,
        response.status,
      ),
    );
  }

  return response.json();
}

export async function createAnalysis(
  request: CreateAnalysisRequest,
): Promise<CreateAnalysisResponse> {
  return apiRequest<CreateAnalysisResponse>(
    "/api/v1/analyses",
    {
      method: "POST",
      body: JSON.stringify(request),
    },
  );
}

export async function getAnalysis(
  analysisId: string,
): Promise<AnalysisState> {
  return apiRequest<AnalysisState>(
    `/api/v1/analyses/${encodeURIComponent(
      analysisId,
    )}`,
  );
}

export async function getAnalysisClaims(
  analysisId: string,
): Promise<AnalysisClaim[]> {
  const data = await apiRequest<{
    claims: AnalysisClaim[];
  }>(
    `/api/v1/analyses/${encodeURIComponent(
      analysisId,
    )}/claims`,
  );

  return data.claims;
}

export async function getClaim(
  claimId: number,
): Promise<ClaimDetail> {
  return apiRequest<ClaimDetail>(
    `/api/v1/claims/${claimId}`,
  );
}

export async function getAnalysisEvidence(
  analysisId: string,
): Promise<ClaimEvidence[]> {
  const data = await apiRequest<{
    evidence: ClaimEvidence[];
  }>(
    `/api/v1/analyses/${encodeURIComponent(
      analysisId,
    )}/evidence`,
  );

  return data.evidence;
}

export async function getRecentAnalyses(): Promise<
  RecentAnalysis[]
> {
  const data = await apiRequest<{
    analyses: RecentAnalysis[];
  }>("/api/v1/analyses");

  return data.analyses;
}

export async function getRedisInspector(
  analysisId: string,
): Promise<RedisInspectorResponse> {
  return apiRequest<RedisInspectorResponse>(
    `/api/v1/redis/inspector/${encodeURIComponent(
      analysisId,
    )}`,
  );
}