"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
    useParams,
    useSearchParams,
} from "next/navigation";
import {
    getClaim,
    type ClaimDetail,
} from "@/lib/api/analyses";
import {
    EmptyState,
    Metric,
    PageContainer,
    Panel,
    SectionHeader,
    StatusBadge,
} from "@/components/ui/primitives";

function getEvidenceKindLabel(kind: string) {
    return kind.replaceAll("_", " ");
}

function getConfidenceLabel(confidence: number) {
    if (confidence >= 90) return "High";
    if (confidence >= 70) return "Moderate";
    if (confidence >= 40) return "Low";
    return "Very low";
}

export default function ClaimDetailPage() {
    const params = useParams<{ id: string }>();
    const searchParams = useSearchParams();

    const claimId = params.id;
    const contextAnalysisId = searchParams.get("analysis");

    const [claim, setClaim] = useState<ClaimDetail | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [retryNonce, setRetryNonce] = useState(0);

    useEffect(() => {
        if (!claimId) return;

        let cancelled = false;

        async function loadClaim() {
            try {
                setIsLoading(true);
                setError(null);

                const numericClaimId = Number(claimId);

                if (!Number.isInteger(numericClaimId)) {
                    throw new Error("Invalid claim identifier.");
                }

                const result = await getClaim(numericClaimId);

                if (cancelled) return;

                setClaim(result);
            } catch (error) {
                if (cancelled) return;

                setClaim(null);
                setError(
                    error instanceof Error
                        ? error.message
                        : "Failed to load claim.",
                );
            } finally {
                if (!cancelled) {
                    setIsLoading(false);
                }
            }
        }

        void loadClaim();

        return () => {
            cancelled = true;
        };
    }, [claimId, retryNonce]);

    const backAnalysisId =
        contextAnalysisId ??
        (claim ? String(claim.analysis_id) : null);

    const backHref = backAnalysisId
        ? `/claims?analysis=${encodeURIComponent(backAnalysisId)}`
        : "/claims";

    if (isLoading) {
        return (
            <PageContainer>
                <Link
                    href={backHref}
                    className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-faint transition-colors hover:text-accent"
                >
                    <span>←</span>
                    <span>Back to claims</span>
                </Link>

                <SectionHeader
                    eyebrow="Investigation"
                    title="Loading claim."
                    description="Retrieving the claim and its supporting evidence."
                />

                <Panel className="mt-6 px-5 py-10">
                    <div className="flex items-center gap-3">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        <p className="text-sm text-foreground-muted">
                            Loading claim...
                        </p>
                    </div>
                </Panel>
            </PageContainer>
        );
    }

    if (error || !claim) {
        return (
            <PageContainer>
                <Link
                    href={backHref}
                    className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-faint transition-colors hover:text-accent"
                >
                    <span>←</span>
                    <span>Back to claims</span>
                </Link>

                <SectionHeader
                    eyebrow="Investigation"
                    title="Claim unavailable."
                    description="The workstation could not retrieve this claim."
                />

                <Panel className="mt-6 border-contradicted-muted px-5 py-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-contradicted">
                        Investigation unavailable
                    </p>

                    <p className="mt-2 text-sm text-foreground-muted">
                        {error ?? "Claim not found."}
                    </p>

                    <div className="mt-4 flex items-center gap-2">
                        <button
                            type="button"
                            onClick={() =>
                                setRetryNonce((value) => value + 1)
                            }
                            className="border border-border-strong bg-surface px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                        >
                            Retry
                        </button>

                        <Link
                            href={backHref}
                            className="border border-border-subtle px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-border-strong hover:text-foreground"
                        >
                            Browse claims
                        </Link>
                    </div>
                </Panel>
            </PageContainer>
        );
    }

    const confidence = Math.round(claim.confidence * 100);

    // Preserve the API's status, including VERIFIED.
    const status = claim.status;

    return (
        <PageContainer>
            <div>
                <Link
                    href={backHref}
                    className="inline-flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-foreground-faint transition-colors hover:text-accent"
                >
                    <span>←</span>
                    <span>Back to claims</span>
                </Link>

                <div className="mt-5 max-w-5xl">
                    <div className="flex flex-wrap items-center gap-3">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-accent">
                            Claim #{claim.id}
                        </p>

                        <StatusBadge status={status} />
                    </div>

                    <h1 className="mt-3 text-2xl font-semibold leading-tight tracking-tight text-foreground">
                        {claim.statement}
                    </h1>
                </div>
            </div>

            <Panel className="mt-7">
                <div className="grid grid-cols-3 divide-x divide-border">
                    <div className="p-5">
                        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint">
                            Status
                        </p>

                        <div className="mt-2">
                            <StatusBadge status={status} />
                        </div>
                    </div>

                    <Metric
                        label="Confidence"
                        value={`${confidence}%`}
                        description={getConfidenceLabel(confidence)}
                    />

                    <Metric
                        label="Evidence"
                        value={claim.evidence.length}
                        description="Linked sources"
                    />
                </div>

                <div className="border-t border-border px-5 py-4">
                    <div className="flex items-center gap-4">
                        <span className="w-20 shrink-0 text-[10px] font-medium uppercase tracking-[0.14em] text-foreground-faint">
                            Confidence
                        </span>

                        <div className="h-1 flex-1 bg-surface-elevated">
                            <div
                                className="h-full bg-accent transition-all"
                                style={{ width: `${confidence}%` }}
                            />
                        </div>

                        <span className="w-10 text-right font-mono text-[11px] text-foreground-muted">
                            {confidence}%
                        </span>
                    </div>
                </div>
            </Panel>

            <section className="mt-8">
                <SectionHeader
                    eyebrow="Why we believe this"
                    title="Evidence"
                    description="Repository evidence connected to this claim."
                />

                {claim.evidence.length === 0 ? (
                    <div className="mt-4">
                        <EmptyState
                            eyebrow="Evidence"
                            title="No evidence is linked to this claim."
                            description="The compiler has not connected any repository evidence to this statement."
                        />
                    </div>
                ) : (
                    <div className="mt-4 space-y-3">
                        {claim.evidence.map((evidence) => (
                            <Panel
                                key={evidence.id}
                                className="overflow-hidden"
                            >
                                <div className="border-b border-border px-5 py-4">
                                    <div className="flex items-start justify-between gap-5">
                                        <div className="min-w-0">
                                            <div className="flex flex-wrap items-center gap-3">
                                                <span className="border border-accent-muted px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-accent">
                                                    {getEvidenceKindLabel(
                                                        evidence.kind,
                                                    )}
                                                </span>

                                                {evidence.language && (
                                                    <span className="font-mono text-[11px] text-foreground-faint">
                                                        {evidence.language}
                                                    </span>
                                                )}
                                            </div>

                                            <p className="mt-2 break-all font-mono text-xs leading-5 text-foreground">
                                                {evidence.source}
                                            </p>
                                        </div>

                                        <span className="shrink-0 font-mono text-[10px] text-foreground-faint">
                                            #{evidence.id}
                                        </span>
                                    </div>

                                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 font-mono text-[11px] text-foreground-faint">
                                        {evidence.line_start !== null && (
                                            <span>
                                                lines {evidence.line_start}
                                                {evidence.line_end !== null &&
                                                    evidence.line_end !==
                                                        evidence.line_start &&
                                                    `–${evidence.line_end}`}
                                            </span>
                                        )}

                                        <span>Evidence source</span>
                                    </div>
                                </div>

                                <div className="px-5 py-4">
                                    <p className="text-sm leading-6 text-foreground-muted">
                                        {evidence.description}
                                    </p>

                                    {evidence.content && (
                                        <div className="mt-4">
                                            <div className="flex items-center justify-between border border-b-0 border-border bg-surface px-3 py-2">
                                                <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-foreground-faint">
                                                    Source content
                                                </span>

                                                {evidence.line_start !== null && (
                                                    <span className="font-mono text-[10px] text-foreground-faint">
                                                        L{evidence.line_start}
                                                        {evidence.line_end !==
                                                            null &&
                                                            `–${evidence.line_end}`}
                                                    </span>
                                                )}
                                            </div>

                                            <pre className="max-h-[500px] overflow-auto border border-border bg-background p-4 font-mono text-[11px] leading-6 text-foreground">
                                                <code>{evidence.content}</code>
                                            </pre>
                                        </div>
                                    )}
                                </div>
                            </Panel>
                        ))}
                    </div>
                )}
            </section>
        </PageContainer>
    );
}