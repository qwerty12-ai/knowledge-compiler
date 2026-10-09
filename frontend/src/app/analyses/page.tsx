"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  getRecentAnalyses,
  type RecentAnalysis,
} from "@/lib/api/analyses";
import {
  EmptyState,
  PageContainer,
  Panel,
  SectionHeader,
} from "@/components/ui/primitives";
import { formatDateTime } from "@/lib/utils/date";

function getRepositoryName(path: string) {
  return path.split("/").filter(Boolean).pop() ?? path;
}

export default function AnalysesPage() {
  const [analyses, setAnalyses] = useState<RecentAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryNonce, setRetryNonce] = useState(0);

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
            : "Failed to load analyses.",
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
  }, [retryNonce]);

  return (
    <PageContainer>
      <SectionHeader
        eyebrow="Workspace"
        title="Analyses"
        description="Browse every repository analysis and return to the knowledge produced by each run."
        action={
          <Link
            href="/analyses/new"
            className="bg-accent px-4 py-2 text-sm font-semibold text-black transition-colors hover:bg-accent-hover"
          >
            New analysis
          </Link>
        }
      />

      {isLoading && (
        <Panel className="mt-8 px-6 py-16 text-center">
          <p className="text-sm text-foreground-muted">
            Loading analyses...
          </p>
        </Panel>
      )}

      {!isLoading && error && (
        <Panel className="mt-8 border-contradicted-muted px-6 py-6">
          <p className="text-sm text-contradicted">{error}</p>

          <button
            type="button"
            onClick={() => setRetryNonce((value) => value + 1)}
            className="mt-4 border border-border-strong px-3 py-2 text-xs text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
          >
            Retry
          </button>
        </Panel>
      )}

      {!isLoading && !error && analyses.length === 0 && (
        <div className="mt-8">
          <EmptyState
            eyebrow="Analyses"
            title="Nothing here yet."
            description="Give the compiler a repository to interrogate and it will begin building engineering knowledge."
            action={
              <Link
                href="/analyses/new"
                className="inline-flex border border-border-strong px-4 py-2 text-sm text-foreground-muted transition-colors hover:border-accent-muted hover:text-foreground"
              >
                New analysis
              </Link>
            }
          />
        </div>
      )}

      {!isLoading && !error && analyses.length > 0 && (
        <section className="mt-8">
          <Panel>
            <div className="border-b border-border px-6 py-4">
              <div className="flex items-center justify-between gap-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
                    Analysis history
                  </p>

                  <p className="mt-2 text-sm text-foreground-muted">
                    {analyses.length}{" "}
                    {analyses.length === 1 ? "analysis" : "analyses"}{" "}
                    available
                  </p>
                </div>
              </div>
            </div>

            <div className="divide-y divide-border">
              {analyses.map((analysis) => (
                <Link
                  key={analysis.id}
                  href={`/analyses/${analysis.id}`}
                  className="group block px-6 py-5 transition-colors hover:bg-surface-elevated"
                >
                  <div className="flex items-start justify-between gap-8">
                    <div className="min-w-0">
                      <div className="flex min-w-0 items-center gap-3">
                        <p className="truncate text-sm font-medium text-foreground">
                          {getRepositoryName(analysis.repository_path)}
                        </p>

                        <span className="shrink-0 font-mono text-[11px] text-foreground-faint">
                          #{analysis.id}
                        </span>
                      </div>

                      <p className="mt-1 truncate font-mono text-xs text-foreground-muted">
                        {analysis.repository_path}
                      </p>
                    </div>

                    <span className="shrink-0 text-xs font-semibold text-foreground-faint transition-colors group-hover:text-accent">
                      Inspect →
                    </span>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-foreground-muted">
                    <span>{formatDateTime(analysis.created_at)}</span>
                    <span>{analysis.files_discovered} files</span>
                    <span>{analysis.claims_count} claims</span>
                    <span>{analysis.evidence_count} evidence</span>
                    <span>
                      AI {analysis.with_ai ? "enabled" : "disabled"}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </Panel>
        </section>
      )}
    </PageContainer>
  );
}