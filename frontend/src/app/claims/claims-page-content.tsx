"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
getAnalysisClaims,
type AnalysisClaim,
type ClaimStatus,
} from "@/lib/api/analyses";
import {
EmptyState,
PageContainer,
Panel,
SectionHeader,
} from "@/components/ui/primitives";
import { ClaimCard } from "@/components/claims/claim-card";

const filters: Array<{
label: string;
value: ClaimStatus | "ALL";
}> = [
{ label: "All", value: "ALL" },
{ label: "Verified", value: "VERIFIED" },
{ label: "Supported", value: "SUPPORTED" },
{ label: "Weak", value: "WEAKLY_SUPPORTED" },
{ label: "Unknown", value: "UNKNOWN" },
{ label: "Contradicted", value: "CONTRADICTED" },
{ label: "Stale", value: "STALE" },
];

function normalizeStatus(status: string): string {
return status.trim().toUpperCase();
}

export default function ClaimsPageContent() {
const searchParams = useSearchParams();
const analysisId = searchParams.get("analysis");

const [claims, setClaims] = useState<AnalysisClaim[]>([]);
const [loadedAnalysisId, setLoadedAnalysisId] =
    useState<string | null>(null);
const [filterSelection, setFilterSelection] = useState<{
    analysisId: string | null;
    value: ClaimStatus | "ALL";
}>({
    analysisId: null,
    value: "ALL",
});
const [error, setError] = useState<string | null>(null);
const [retryNonce, setRetryNonce] = useState(0);

const activeFilter =
    filterSelection.analysisId === analysisId
        ? filterSelection.value
        : "ALL";

function setActiveFilter(value: ClaimStatus | "ALL") {
    setFilterSelection({ analysisId, value });
}

useEffect(() => {
    if (!analysisId) return;

    const currentAnalysisId = analysisId;
    let cancelled = false;

    async function loadClaims() {
        try {
            const result = await getAnalysisClaims(
                currentAnalysisId,
            );

            if (cancelled) return;

            setClaims(result);
            setError(null);
        } catch (error) {
            if (cancelled) return;

            setError(
                error instanceof Error
                    ? error.message
                    : "Failed to load claims.",
            );
        } finally {
            if (!cancelled) {
                setLoadedAnalysisId(currentAnalysisId);
            }
        }
    }

    void loadClaims();

    return () => {
        cancelled = true;
    };
}, [analysisId, retryNonce]);

const isLoading =
    analysisId !== null &&
    loadedAnalysisId !== analysisId;

const currentError =
    loadedAnalysisId === analysisId ? error : null;

const analysisHref = analysisId
    ? `/analyses/${encodeURIComponent(analysisId)}`
    : "/analyses";

const filteredClaims =
    activeFilter === "ALL"
        ? claims
        : claims.filter(
              (claim) =>
                  normalizeStatus(claim.status) ===
                  activeFilter,
          );

const backLink = (
    <Link
        href={analysisHref}
        className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-muted transition-colors hover:text-foreground"
    >
        <span aria-hidden="true">←</span>
        <span>Back to analysis</span>
    </Link>
);

if (!analysisId) {
    return (
        <PageContainer>
            <EmptyState
                eyebrow="Claims"
                title="Select an analysis."
                description="Claims belong to a specific analysis. Choose an analysis first, then inspect the knowledge it produced."
                action={
                    <Link
                        href="/analyses"
                        className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-muted transition-colors hover:text-foreground"
                    >
                        <span aria-hidden="true">←</span>
                        <span>Browse analyses</span>
                    </Link>
                }
            />
        </PageContainer>
    );
}

if (isLoading) {
    return (
        <PageContainer>
            <div className="mb-5">{backLink}</div>

            <SectionHeader
                eyebrow="Knowledge"
                title="Claims"
                description="Loading engineering knowledge from the selected analysis."
            />

            <Panel className="mt-6 px-5 py-10">
                <div className="flex items-center gap-3">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                    <p className="text-sm text-foreground-muted">
                        Loading claims...
                    </p>
                </div>
            </Panel>
        </PageContainer>
    );
}

if (currentError) {
    return (
        <PageContainer>
            <div className="mb-5">{backLink}</div>

            <SectionHeader
                eyebrow="Knowledge"
                title="Claims"
                description="The compiler could not load the claims for this analysis."
            />

            <Panel className="mt-6 px-5 py-5">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-foreground-muted">
                    Claims unavailable
                </p>

                <p className="mt-2 text-sm text-foreground-muted">
                    {currentError}
                </p>

                <button
                    type="button"
                    onClick={() =>
                        setRetryNonce((value) => value + 1)
                    }
                    className="mt-4 border border-border-strong bg-surface px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                >
                    Retry
                </button>
            </Panel>
        </PageContainer>
    );
}

return (
    <PageContainer>
        <div className="mb-5">{backLink}</div>

        <SectionHeader
            eyebrow="Knowledge"
            title="Claims"
            description="Engineering knowledge inferred from repository evidence."
        />

        <div className="mt-6 flex flex-col border-y border-border-subtle">
            <div className="flex items-center justify-between gap-4 py-3">
                <div className="flex flex-wrap items-center gap-1.5">
                    {filters.map((filter) => {
                        const isActive =
                            activeFilter === filter.value;

                        const count =
                            filter.value === "ALL"
                                ? claims.length
                                : claims.filter(
                                      (claim) =>
                                          normalizeStatus(
                                              claim.status,
                                          ) === filter.value,
                                  ).length;

                        return (
                            <button
                                key={filter.value}
                                type="button"
                                onClick={() =>
                                    setActiveFilter(filter.value)
                                }
                                className={`border px-2.5 py-1.5 text-[11px] font-medium transition-colors ${
                                    isActive
                                        ? "border-accent-muted bg-surface-elevated text-foreground"
                                        : "border-transparent text-foreground-faint hover:border-border-subtle hover:text-foreground-muted"
                                }`}
                            >
                                <span>{filter.label}</span>
                                <span className="ml-1.5 font-mono text-foreground-faint">
                                    {count}
                                </span>
                            </button>
                        );
                    })}
                </div>

                <span className="shrink-0 font-mono text-[11px] text-foreground-faint">
                    {filteredClaims.length}
                    {filteredClaims.length !== claims.length &&
                        ` / ${claims.length}`}
                </span>
            </div>

            <div className="flex items-center justify-between border-t border-border-subtle py-2.5 text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                <span>
                    {filteredClaims.length} knowledge{" "}
                    {filteredClaims.length === 1
                        ? "statement"
                        : "statements"}
                </span>

                <span>
                    Select a claim to investigate its evidence
                </span>
            </div>
        </div>

        <div className="mt-5">
            {filteredClaims.length === 0 ? (
                <EmptyState
                    eyebrow="Claims"
                    title={
                        claims.length === 0
                            ? "No claims were generated."
                            : "No claims match this filter."
                    }
                    description={
                        claims.length === 0
                            ? "The compiler did not produce any claims for this analysis."
                            : "Try another status filter to inspect the remaining knowledge."
                    }
                    action={
                        claims.length === 0 ? backLink : undefined
                    }
                />
            ) : (
                <Panel>
                    <div className="border-b border-border px-5 py-3">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-foreground">
                                    Knowledge statements
                                </p>

                                <p className="mt-1 text-xs text-foreground-faint">
                                    Evidence-backed conclusions from this analysis.
                                </p>
                            </div>

                            <span className="font-mono text-xs text-foreground-muted">
                                {filteredClaims.length}
                            </span>
                        </div>
                    </div>

                    {filteredClaims.map((claim) => (
                        <ClaimCard
                            key={claim.id}
                            claim={claim}
                            analysisId={analysisId}
                        />
                    ))}
                </Panel>
            )}
        </div>
    </PageContainer>
);

}