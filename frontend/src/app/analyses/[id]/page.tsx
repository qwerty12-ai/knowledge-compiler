"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
    getAnalysisClaims,
    getAnalysisEvidence,
    type AnalysisClaim,
    type ClaimEvidence,
} from "@/lib/api/analyses";
import { useAnalysis } from "@/lib/api/use-analysis";
import { formatTime } from "@/lib/utils/date";
import {
    EmptyState,
    Metric,
    PageContainer,
    Panel,
    SectionHeader,
} from "@/components/ui/primitives";

function getEventStatusLabel(status: string) {
    switch (status) {
        case "running":
            return "Running";
        case "completed":
            return "Completed";
        case "failed":
            return "Failed";
        case "queued":
            return "Queued";
        default:
            return status;
    }
}

function getEventStageLabel(stage: string) {
    switch (stage) {
        case "discovery":
            return "Discovery";
        case "completed":
            return "Completed";
        case "failed":
            return "Failed";
        default:
            return stage;
    }
}

function getEventDescription(
    status: string,
    stage: string,
) {
    if (status === "completed") {
        return "Analysis finished successfully.";
    }

    if (status === "failed") {
        return "Analysis could not be completed.";
    }

    if (status === "queued") {
        return "Analysis is waiting to be processed.";
    }

    if (stage === "discovery") {
        return "Repository structure discovery.";
    }

    return "Analysis is in progress.";
}

function getConnectionLabel(connection: string) {
    switch (connection) {
        case "connected":
            return "Realtime connected";
        case "connecting":
            return "Connecting to realtime";
        case "error":
            return "Realtime unavailable";
        case "closed":
            return "Realtime closed";
        default:
            return "Realtime idle";
    }
}

function getConnectionClass(connection: string) {
    switch (connection) {
        case "connected":
            return "bg-supported";
        case "error":
            return "bg-contradicted";
        case "connecting":
            return "bg-accent";
        default:
            return "bg-foreground-faint";
    }
}

function getStatusClass(status: string) {
    switch (status) {
        case "completed":
            return "text-supported";
        case "failed":
            return "text-contradicted";
        case "running":
            return "text-accent";
        case "queued":
            return "text-foreground-muted";
        default:
            return "text-foreground";
    }
}

function getStageClass(stage: string) {
    switch (stage) {
        case "completed":
            return "border-supported-muted text-supported";
        case "failed":
            return "border-contradicted-muted text-contradicted";
        case "discovery":
            return "border-accent-muted text-accent";
        default:
            return "border-border text-foreground-faint";
    }
}

export default function AnalysisPage() {
    const params = useParams<{ id: string }>();
    const analysisId = params.id;

    const {
        analysis,
        events,
        connection,
        isLoading,
        error,
        retry,
    } = useAnalysis(analysisId);

    const [claims, setClaims] =
        useState<AnalysisClaim[]>([]);

    const [evidence, setEvidence] =
        useState<ClaimEvidence[]>([]);

    const [resultsLoading, setResultsLoading] =
        useState(false);

    const [resultsError, setResultsError] =
        useState<string | null>(null);

    const [resultsRetryNonce, setResultsRetryNonce] =
        useState(0);

    const completedDatabaseId =
        analysis?.status === "completed"
            ? analysis.database_id
            : null;

    useEffect(() => {
        if (completedDatabaseId === null) {
            return;
        }

        const databaseId =
            String(completedDatabaseId);

        let cancelled = false;

        async function loadResults() {
            setResultsLoading(true);
            setResultsError(null);

            try {
                const [
                    claimsResult,
                    evidenceResult,
                ] = await Promise.all([
                    getAnalysisClaims(databaseId),
                    getAnalysisEvidence(databaseId),
                ]);

                if (cancelled) {
                    return;
                }

                setClaims(claimsResult);
                setEvidence(evidenceResult);
            } catch (error) {
                if (cancelled) {
                    return;
                }

                setResultsError(
                    error instanceof Error
                        ? error.message
                        : "Failed to load analysis results.",
                );
            } finally {
                if (!cancelled) {
                    setResultsLoading(false);
                }
            }
        }

        loadResults();

        return () => {
            cancelled = true;
        };
    }, [
        completedDatabaseId,
        resultsRetryNonce,
    ]);

    if (isLoading && !analysis) {
        return (
            <PageContainer>
                <Panel className="px-6 py-12">
                    <div className="flex items-center gap-3">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        <p className="text-sm text-foreground-muted">
                            Loading analysis...
                        </p>
                    </div>
                </Panel>
            </PageContainer>
        );
    }

    if (error && !analysis) {
        return (
            <PageContainer>
                <Panel className="border-contradicted-muted px-6 py-6">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-contradicted">
                        Analysis unavailable
                    </p>

                    <p className="mt-2 text-sm text-foreground-muted">
                        {error}
                    </p>

                    <button
                        type="button"
                        onClick={retry}
                        className="mt-5 border border-border-strong bg-surface px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                    >
                        Retry
                    </button>
                </Panel>
            </PageContainer>
        );
    }

    if (!analysis) {
        return (
            <PageContainer>
                <EmptyState
                    eyebrow="Analysis"
                    title="Analysis not found."
                    description="The compiler could not find the requested analysis."
                    action={
                        <Link
                            href="/analyses"
                            className="inline-flex border border-border-strong bg-surface px-4 py-2 text-sm text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                        >
                            Browse analyses
                        </Link>
                    }
                />
            </PageContainer>
        );
    }

    return (
        <PageContainer>
            <SectionHeader
                eyebrow="Analysis"
                title={
                    analysis.repository_path
                        ? analysis.repository_path
                        : "Analysis"
                }
                description="Track what the compiler discovered, what evidence it collected, and what knowledge it produced."
                action={
                    <div className="flex items-center gap-2 border border-border-subtle bg-surface px-3 py-2 text-xs text-foreground-muted">
                        <span
                            className={`h-1.5 w-1.5 rounded-full ${getConnectionClass(
                                connection,
                            )}`}
                        />
                        <span>
                            {getConnectionLabel(connection)}
                        </span>
                    </div>
                }
            />

            <Panel className="mt-6">
                <div className="grid grid-cols-3 divide-x divide-border">
                    <div className="p-5">
                        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint">
                            Status
                        </p>

                        <p
                            className={`mt-2 text-sm font-semibold uppercase tracking-[0.08em] ${getStatusClass(
                                analysis.status,
                            )}`}
                        >
                            {analysis.status}
                        </p>
                    </div>

                    <div className="p-5">
                        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint">
                            Stage
                        </p>

                        <p className="mt-2 text-sm font-medium text-foreground">
                            {analysis.stage ?? "—"}
                        </p>
                    </div>

                    <div className="p-5">
                        <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint">
                            Progress
                        </p>

                        <p className="mt-2 font-mono text-sm text-foreground">
                            {analysis.progress}%
                        </p>
                    </div>
                </div>

                <div className="border-t border-border px-5 py-4">
                    <div className="flex items-center gap-5">
                        <span className="shrink-0 text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint">
                            Analysis ID
                        </span>

                        <span className="min-w-0 truncate font-mono text-xs text-foreground-muted">
                            {analysis.analysis_id}
                        </span>

                        <div className="ml-auto h-1 w-36 shrink-0 overflow-hidden bg-surface-elevated">
                            <div
                                className="h-full bg-accent transition-all duration-500"
                                style={{
                                    width: `${Math.max(
                                        0,
                                        Math.min(
                                            100,
                                            analysis.progress,
                                        ),
                                    )}%`,
                                }}
                            />
                        </div>
                    </div>
                </div>
            </Panel>

            <div className="mt-7">
                <SectionHeader
                    eyebrow="Output"
                    title="Knowledge produced"
                    description="The claims and evidence generated by this analysis."
                />

                <div className="mt-4 grid grid-cols-2 gap-px border border-border bg-border">
                    <Panel className="border-0">
                        <Metric
                            label="Claims"
                            value={
                                resultsLoading
                                    ? "—"
                                    : claims.length
                            }
                            description="Knowledge statements"
                        />
                    </Panel>

                    <Panel className="border-0">
                        <Metric
                            label="Evidence"
                            value={
                                resultsLoading
                                    ? "—"
                                    : evidence.length
                            }
                            description="Repository sources"
                        />
                    </Panel>
                </div>
            </div>

            {(events.length > 0 ||
                analysis.status === "running") && (
                <Panel className="mt-7">
                    <div className="flex items-center justify-between border-b border-border px-5 py-4">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
                                Activity
                            </p>

                            <p className="mt-1 text-xs text-foreground-muted">
                                Compiler lifecycle events.
                            </p>
                        </div>

                        <div className="flex items-center gap-2 text-[11px] text-foreground-faint">
                            <span
                                className={`h-1.5 w-1.5 rounded-full ${getConnectionClass(
                                    connection,
                                )}`}
                            />

                            <span>
                                {connection === "connected"
                                    ? "Live"
                                    : "Snapshot"}
                            </span>
                        </div>
                    </div>

                    <div className="divide-y divide-border">
                        {events.length === 0 ? (
                            <div className="px-5 py-7">
                                <p className="text-sm text-foreground-muted">
                                    Waiting for compiler activity...
                                </p>

                                <p className="mt-1 text-xs text-foreground-faint">
                                    The workstation is waiting for the next lifecycle event.
                                </p>
                            </div>
                        ) : (
                            events.map((event, index) => {
                                const isLatest =
                                    index ===
                                    events.length - 1;

                                return (
                                    <div
                                        key={`${event.timestamp}-${index}`}
                                        className={`flex items-center justify-between gap-6 px-5 py-3 ${
                                            isLatest
                                                ? "bg-surface-elevated/50"
                                                : ""
                                        }`}
                                    >
                                        <div className="flex min-w-0 items-center gap-4">
                                            <span className="relative flex h-4 w-4 shrink-0 items-center justify-center">
                                                <span
                                                    className={`h-1.5 w-1.5 rounded-full ${
                                                        event.status ===
                                                        "failed"
                                                            ? "bg-contradicted"
                                                            : event.status ===
                                                                "completed"
                                                              ? "bg-supported"
                                                              : "bg-accent"
                                                    }`}
                                                />

                                                {index <
                                                    events.length - 1 && (
                                                    <span className="absolute left-1/2 top-3.5 h-7 w-px -translate-x-1/2 bg-border" />
                                                )}
                                            </span>

                                            <div className="min-w-0">
                                                <div className="flex items-center gap-3">
                                                    <span
                                                        className={`text-sm ${
                                                            isLatest
                                                                ? "text-foreground"
                                                                : "text-foreground-muted"
                                                        }`}
                                                    >
                                                        {getEventStatusLabel(
                                                            event.status,
                                                        )}
                                                    </span>

                                                    {event.stage && (
                                                        <span
                                                            className={`border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.08em] ${getStageClass(
                                                                event.stage,
                                                            )}`}
                                                        >
                                                            {getEventStageLabel(
                                                                event.stage,
                                                            )}
                                                        </span>
                                                    )}
                                                </div>

                                                <p className="mt-0.5 text-xs text-foreground-faint">
                                                    {getEventDescription(
                                                        event.status,
                                                        event.stage,
                                                    )}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex shrink-0 items-center gap-4">
                                            <span className="font-mono text-[11px] text-foreground-faint">
                                                {formatTime(
                                                    event.timestamp,
                                                )}
                                            </span>

                                            <span
                                                className={`font-mono text-[11px] ${
                                                    isLatest
                                                        ? "text-foreground"
                                                        : "text-foreground-muted"
                                                }`}
                                            >
                                                {event.progress}%
                                            </span>
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </Panel>
            )}

            {analysis.status === "failed" && (
                <Panel className="mt-6 border-contradicted-muted px-5 py-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-contradicted">
                        Analysis failed
                    </p>

                    <p className="mt-2 text-sm text-foreground-muted">
                        The compiler could not complete this analysis.
                    </p>

                    <Link
                        href="/analyses/new"
                        className="mt-4 inline-flex border border-border-strong bg-surface px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                    >
                        New analysis
                    </Link>
                </Panel>
            )}

            {analysis.status === "completed" &&
                analysis.database_id !== null && (
                    <>
                        {resultsLoading && (
                            <Panel className="mt-6 px-5 py-5">
                                <p className="text-xs text-foreground-muted">
                                    Loading analysis results...
                                </p>
                            </Panel>
                        )}

                        {resultsError && (
                            <Panel className="mt-6 border-contradicted-muted px-5 py-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-contradicted">
                                    Results unavailable
                                </p>

                                <p className="mt-2 text-sm text-foreground-muted">
                                    {resultsError}
                                </p>

                                <button
                                    type="button"
                                    onClick={() =>
                                        setResultsRetryNonce(
                                            (value) =>
                                                value + 1,
                                        )
                                    }
                                    className="mt-4 border border-border-strong bg-surface px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                                >
                                    Retry
                                </button>
                            </Panel>
                        )}

                        {!resultsLoading &&
                            !resultsError && (
                                <div className="mt-6 flex items-center gap-2">
                                    <Link
                                        href={`/claims?analysis=${analysis.database_id}`}
                                        className="border border-border-strong bg-surface px-4 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                                    >
                                        Inspect claims
                                    </Link>

                                    <Link
                                        href={`/evidence?analysis=${analysis.database_id}`}
                                        className="border border-border-subtle px-4 py-2 text-xs text-foreground-muted transition-colors hover:border-border-strong hover:text-foreground"
                                    >
                                        Inspect evidence
                                    </Link>
                                </div>
                            )}
                    </>
                )}
        </PageContainer>
    );
}