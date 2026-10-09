"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
    getRecentAnalyses,
    getRedisInspector,
    type RecentAnalysis,
    type RedisInspectorResponse,
} from "@/lib/api/analyses";
import {
    EmptyState,
    PageContainer,
    Panel,
    SectionHeader,
} from "@/components/ui/primitives";
import { InspectionTarget } from "@/components/inspector/inspection-target";
import {
    RedisPanel,
    RedisSummary,
} from "@/components/inspector/redis-panel";
import { QueuePanel } from "@/components/inspector/queue-panel";
import { PubSubPanel } from "@/components/inspector/pub-sub-panel";
import { AnalysisStatePanel } from "@/components/inspector/analysis-state-panel";
import { SelectedAnalysisPanel } from "@/components/inspector/selected-analysis-panel";

function formatTtl(ttl: number) {
    if (ttl === -2) return "Missing";
    if (ttl === -1) return "Persistent";

    const minutes = Math.floor(ttl / 60);
    const seconds = ttl % 60;

    return minutes === 0
        ? `${seconds}s`
        : `${minutes}m ${seconds}s`;
}

export default function InspectorPage() {
    const [analyses, setAnalyses] = useState<RecentAnalysis[]>([]);
    const [selectedAnalysisId, setSelectedAnalysisId] =
        useState<string | null>(null);
    const [inspector, setInspector] =
        useState<RedisInspectorResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [refreshNonce, setRefreshNonce] = useState(0);

    useEffect(() => {
        let cancelled = false;

        async function loadAnalyses() {
            try {
                setIsLoading(true);
                setError(null);

                const result = await getRecentAnalyses();

                if (cancelled) return;

                setAnalyses(result);
            } catch (error) {
                if (cancelled) return;

                setError(
                    error instanceof Error
                        ? error.message
                        : "Unable to load analyses.",
                );
            } finally {
                if (!cancelled) {
                    setIsLoading(false);
                }
            }
        }

        void loadAnalyses();

        return () => {
            cancelled = true;
        };
    }, []);

    const effectiveAnalysisId =
        selectedAnalysisId ??
        (analyses.length > 0
            ? String(analyses[0].id)
            : null);

    useEffect(() => {
        if (!effectiveAnalysisId) {
            return;
        }

        const analysisId = effectiveAnalysisId;
        let cancelled = false;

        async function loadInspector() {
            try {
                setIsRefreshing(true);
                setError(null);

                const result = await getRedisInspector(
                    analysisId,
                );

                if (cancelled) return;

                setInspector(result);
            } catch (error) {
                if (cancelled) return;

                setInspector(null);

                setError(
                    error instanceof Error
                        ? error.message
                        : "Unable to inspect Redis state.",
                );
            } finally {
                if (!cancelled) {
                    setIsRefreshing(false);
                }
            }
        }

        void loadInspector();

        return () => {
            cancelled = true;
        };
    }, [effectiveAnalysisId, refreshNonce]);

    const selectedAnalysis =
        analyses.find(
            (analysis) =>
                String(analysis.id) === effectiveAnalysisId,
        ) ?? null;

    const state = inspector?.state;
    const queue = inspector?.queue;
    const channel = inspector?.channel;

    const redisStatus = !state
        ? "Unavailable"
        : state.ttl === -2
          ? "Missing"
          : state.state.status || "Available";

    const redisDescription = !state
        ? "Redis state could not be retrieved."
        : state.ttl === -2
          ? "The expected Redis state key is not present. The persistent analysis result may still be available."
          : state.ttl === -1
            ? "Redis state is available without an expiration."
            : state.state.stage
              ? `Current stage: ${state.state.stage}`
              : "Runtime state is available.";

    const progress =
        state?.state.progress !== undefined
            ? `${state.state.progress}%`
            : state?.ttl === -2
              ? "Expired or missing"
              : "—";

    // The selected analysis ID is a database ID. Use the UUID
    // returned by the Inspector when displaying the actual Redis key.
    const redisAnalysisId =
        state?.analysis_id ?? effectiveAnalysisId ?? "";

    return (
        <PageContainer>
            <SectionHeader
                eyebrow="System"
                title="Inspector"
                description="Inspect the runtime state behind repository analysis: Redis state, queue activity, and Pub/Sub."
                action={
                    <button
                        type="button"
                        disabled={!effectiveAnalysisId || isRefreshing}
                        onClick={() =>
                            setRefreshNonce((value) => value + 1)
                        }
                        className="border border-border-strong px-4 py-2 text-sm text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {isRefreshing ? "Refreshing..." : "Refresh"}
                    </button>
                }
            />

            {isLoading && (
                <Panel className="mt-8 px-6 py-16 text-center">
                    <p className="text-sm text-foreground-muted">
                        Loading analysis history...
                    </p>
                </Panel>
            )}

            {!isLoading && error && !inspector && (
                <Panel className="mt-8 px-6 py-6">
                    <p className="text-sm text-foreground-muted">
                        {error}
                    </p>
                </Panel>
            )}

            {!isLoading && !error && analyses.length === 0 && (
                <div className="mt-8">
                    <EmptyState
                        eyebrow="Inspector"
                        title="Nothing to inspect yet."
                        description="Run an analysis first. The inspector will expose the Redis state, analysis queue, and Pub/Sub channel associated with that run."
                        action={
                            <Link
                                href="/analyses/new"
                                className="inline-flex border border-border-strong px-4 py-2 text-sm text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
                            >
                                Start an analysis →
                            </Link>
                        }
                    />
                </div>
            )}

            {!isLoading && selectedAnalysis && (
                <>
                    <Panel className="mt-8">
                        <InspectionTarget
                            analysis={selectedAnalysis}
                            analyses={analyses}
                            selectedAnalysisId={effectiveAnalysisId!}
                            onAnalysisChange={setSelectedAnalysisId}
                        />

                        <RedisSummary
                            status={redisStatus}
                            description={redisDescription}
                            progress={progress}
                            ttl={state ? formatTtl(state.ttl) : "—"}
                        />
                    </Panel>

                    {error && (
                        <div className="mt-4 border border-border bg-background px-4 py-3">
                            <p className="text-xs text-foreground-muted">
                                {error}
                            </p>
                        </div>
                    )}

                    <section className="mt-10">
                        <SectionHeader
                            eyebrow="Runtime"
                            title="System state"
                            description="Live infrastructure state associated with the selected analysis."
                        />

                        <div className="mt-4 grid grid-cols-1 gap-px border border-border bg-border md:grid-cols-3">
                            <RedisPanel
                                analysisId={redisAnalysisId}
                                state={state}
                            />
                            <QueuePanel queue={queue} />
                            <PubSubPanel channel={channel} />
                        </div>
                    </section>

                    <section className="mt-10">
                        <SectionHeader
                            eyebrow="State"
                            title="Analysis state"
                            description="The exact fields currently stored in Redis for this analysis."
                        />
                        <AnalysisStatePanel state={state} />
                    </section>

                    <section className="mt-10">
                        <SectionHeader
                            eyebrow="Reference"
                            title="Selected analysis"
                            description="Persistent information associated with the inspected run."
                        />
                        <SelectedAnalysisPanel analysis={selectedAnalysis} />
                    </section>
                </>
            )}
        </PageContainer>
    );
}