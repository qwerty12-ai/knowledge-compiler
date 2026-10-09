"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
getAnalysisEvidence,
type ClaimEvidence,
} from "@/lib/api/analyses";
import {
EmptyState,
PageContainer,
Panel,
SectionHeader,
} from "@/components/ui/primitives";
import {
EvidenceFilters,
matchesEvidenceFilter,
type EvidenceFilter,
} from "@/components/evidence/evidence-filters";
import { EvidenceList } from "@/components/evidence/evidence-list";

export default function EvidencePageContent() {
const searchParams = useSearchParams();
const analysisId = searchParams.get("analysis");

const [evidence, setEvidence] = useState<ClaimEvidence[]>([]);
const [loadedAnalysisId, setLoadedAnalysisId] =
    useState<string | null>(null);
const [activeFilter, setActiveFilter] =
    useState<EvidenceFilter>("ALL");
const [error, setError] = useState<string | null>(null);
const [retryNonce, setRetryNonce] = useState(0);

useEffect(() => {
    if (!analysisId) return;

    const currentAnalysisId = analysisId;
    let cancelled = false;

    async function loadEvidence() {
        try {
            const result = await getAnalysisEvidence(
                currentAnalysisId,
            );

            if (cancelled) return;

            setEvidence(result);
            setError(null);
        } catch (error) {
            if (cancelled) return;

            setError(
                error instanceof Error
                    ? error.message
                    : "Failed to load evidence.",
            );
        } finally {
            if (!cancelled) {
                setLoadedAnalysisId(currentAnalysisId);
            }
        }
    }

    void loadEvidence();

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

const backLink = (
    <Link
        href={analysisHref}
        className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-muted transition-colors hover:text-foreground"
    >
        <span aria-hidden="true">←</span>
        <span>Back to analysis</span>
    </Link>
);

const filteredEvidence = evidence.filter((item) =>
    matchesEvidenceFilter(item, activeFilter),
);

if (!analysisId) {
    return (
        <PageContainer>
            <EmptyState
                eyebrow="Evidence"
                title="Select an analysis."
                description="Evidence belongs to a specific analysis. Choose an analysis first, then inspect the sources collected by the compiler."
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
                eyebrow="Evidence"
                title="Evidence Locker"
                description="Loading repository evidence from the selected analysis."
            />

            <Panel className="mt-6 px-5 py-10">
                <div className="flex items-center gap-3">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                    <p className="text-sm text-foreground-muted">
                        Loading evidence...
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
                eyebrow="Evidence"
                title="Evidence Locker"
                description="The compiler could not load the evidence for this analysis."
            />

            <Panel className="mt-6 px-5 py-5">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-foreground-muted">
                    Evidence unavailable
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
            title="Evidence Locker"
            description="Repository sources collected during analysis. Inspect where the compiler found the facts behind its knowledge."
        />

        <div className="mt-6">
            <EvidenceFilters
                evidence={evidence}
                activeFilter={activeFilter}
                onFilterChange={setActiveFilter}
            />
        </div>

        <div className="mt-5">
            {filteredEvidence.length === 0 ? (
                <EmptyState
                    eyebrow="Evidence"
                    title={
                        evidence.length === 0
                            ? "No evidence was collected."
                            : "No evidence matches this filter."
                    }
                    description={
                        evidence.length === 0
                            ? "The compiler did not produce evidence for this analysis."
                            : "Try another evidence type to inspect the remaining sources."
                    }
                    action={
                        evidence.length === 0 ? backLink : undefined
                    }
                />
            ) : (
                <EvidenceList evidence={filteredEvidence} />
            )}
        </div>

        <div className="mt-4 border-t border-border-subtle pt-3">
            <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                Evidence content is shown during claim investigation.
            </p>
        </div>
    </PageContainer>
);

}