"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  getRecentAnalyses,
  type RecentAnalysis,
} from "@/lib/api/analyses";
import {
  EmptyState,
  Metric,
  PageContainer,
  Panel,
  SectionHeader,
} from "@/components/ui/primitives";
import { formatDateTime } from "@/lib/utils/date";

function getRepositoryName(path: string) {
  return path.split("/").filter(Boolean).pop() ?? path;
}

export function Overview() {
  const [analyses, setAnalyses] = useState<RecentAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAnalyses() {
      try {
        setIsLoading(true);
        setError(null);

        const result = await getRecentAnalyses();

        if (cancelled) return;

        setAnalyses(result);
      } catch (err) {
        if (cancelled) return;

        console.error(err);
        setError("Unable to load analysis history.");
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

  const latestAnalysis = analyses[0];

  return (
    <PageContainer>
      <SectionHeader
        eyebrow="Workspace"
        title="Overview"
        description="See what the compiler has learned and decide where to investigate next."
        action={
          <Link
            href="/analyses/new"
            className="shrink-0 bg-accent px-5 py-3 text-sm font-semibold !text-[#111111] transition-colors hover:bg-accent-hover"
          >
            Analyze repository →
          </Link>
        }
      />

      {isLoading && (
        <Panel className="mt-8 px-6 py-16 text-center">
          <p className="text-sm text-foreground-muted">
            Loading workspace...
          </p>
        </Panel>
      )}

      {!isLoading && error && (
        <Panel className="mt-8 border-contradicted-muted px-6 py-6">
          <p className="text-sm text-contradicted">{error}</p>
        </Panel>
      )}

      {!isLoading && !error && analyses.length === 0 && (
        <div className="mt-8">
          <EmptyState
            eyebrow="Nothing here yet"
            title="No repository has been analyzed."
            description="Give the compiler a repository to interrogate. It will discover structure, collect evidence, and build engineering knowledge from what it can prove."
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

      {!isLoading && !error && latestAnalysis && (
        <>
          <Panel className="mt-8">
            <div className="border-b border-border px-6 py-4">
              <div className="flex items-center justify-between gap-6">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
                    Latest analysis
                  </p>

                  <p className="mt-2 text-sm text-foreground-muted">
                    {formatDateTime(latestAnalysis.created_at)}
                  </p>
                </div>

                <Link
                  href={`/analyses/${latestAnalysis.id}`}
                  className="text-xs font-semibold text-accent transition-colors hover:text-accent-hover"
                >
                  Open analysis →
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-1 divide-y divide-border md:grid-cols-2 md:divide-x md:divide-y-0 xl:grid-cols-4">
              <div className="p-6 xl:col-span-2">
                <p className="text-xs uppercase tracking-[0.14em] text-foreground-muted">
                  Repository
                </p>

                <p className="mt-2 text-lg font-medium text-foreground">
                  {getRepositoryName(latestAnalysis.repository_path)}
                </p>

                <p className="mt-1 break-all font-mono text-xs leading-5 text-foreground-muted">
                  {latestAnalysis.repository_path}
                </p>
              </div>

              <Metric
                label="Files"
                value={latestAnalysis.files_discovered}
              />

              <Metric
                label="Claims"
                value={latestAnalysis.claims_count}
              />
            </div>

            <div className="grid grid-cols-1 divide-y divide-border border-t border-border md:grid-cols-3 md:divide-x md:divide-y-0">
              <Metric
                label="Evidence"
                value={latestAnalysis.evidence_count}
              />

              <div className="p-6">
                <p className="text-xs uppercase tracking-[0.14em] text-foreground-muted">
                  Investigation
                </p>

                <p className="mt-2 text-sm font-medium text-foreground">
                  {latestAnalysis.with_ai
                    ? "AI investigation enabled"
                    : "Deterministic analysis only"}
                </p>

                <p className="mt-1 text-xs text-foreground-muted">
                  {latestAnalysis.with_ai
                    ? "Local AI was available during this run."
                    : "No AI investigation was requested."}
                </p>
              </div>

              <div className="p-6">
                <p className="text-xs uppercase tracking-[0.14em] text-foreground-muted">
                  Analysis ID
                </p>

                <p className="mt-2 font-mono text-sm text-foreground">
                  #{latestAnalysis.id}
                </p>

                <Link
                  href={`/analyses/${latestAnalysis.id}`}
                  className="mt-1 inline-block text-xs text-accent transition-colors hover:text-accent-hover"
                >
                  Inspect findings →
                </Link>
              </div>
            </div>
          </Panel>

          <section className="mt-10">
            <SectionHeader
              eyebrow="Investigation"
              title="Start with the findings."
              description="Jump directly into the knowledge produced by the latest analysis."
            />

            <div className="mt-4 grid grid-cols-1 gap-px border border-border bg-border md:grid-cols-2">
              <Link
                href={`/claims?analysis=${latestAnalysis.id}`}
                className="bg-background p-6 transition-colors hover:bg-surface-elevated"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-accent">
                  Claims
                </p>

                <div className="mt-3 flex items-end justify-between gap-6">
                  <div>
                    <p className="text-2xl font-semibold tracking-tight text-foreground">
                      {latestAnalysis.claims_count}
                    </p>

                    <p className="mt-1 text-sm text-foreground-muted">
                      statements about how the repository behaves
                    </p>
                  </div>

                  <span className="text-xs font-semibold text-foreground-muted">
                    Investigate →
                  </span>
                </div>
              </Link>

              <Link
                href={`/evidence?analysis=${latestAnalysis.id}`}
                className="bg-background p-6 transition-colors hover:bg-surface-elevated"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-accent">
                  Evidence
                </p>

                <div className="mt-3 flex items-end justify-between gap-6">
                  <div>
                    <p className="text-2xl font-semibold tracking-tight text-foreground">
                      {latestAnalysis.evidence_count}
                    </p>

                    <p className="mt-1 text-sm text-foreground-muted">
                      source records supporting the findings
                    </p>
                  </div>

                  <span className="text-xs font-semibold text-foreground-muted">
                    Inspect →
                  </span>
                </div>
              </Link>
            </div>
          </section>

          <section className="mt-10">
            <SectionHeader
              eyebrow="History"
              title="Recent analyses"
              description="Previous compiler runs and their findings."
              action={
                <Link
                  href="/analyses"
                  className="text-xs font-semibold text-foreground-muted transition-colors hover:text-foreground"
                >
                  View all →
                </Link>
              }
            />

            <Panel className="mt-4">
              {analyses.slice(0, 5).map((analysis) => (
                <Link
                  key={`${analysis.id}-${analysis.created_at}`}
                  href={`/analyses/${analysis.id}`}
                  className="block border-b border-border px-6 py-5 last:border-b-0 transition-colors hover:bg-surface-elevated"
                >
                  <div className="flex items-center justify-between gap-6">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">
                        {getRepositoryName(analysis.repository_path)}
                      </p>

                      <p className="mt-1 truncate font-mono text-xs text-foreground-muted">
                        {analysis.repository_path}
                      </p>
                    </div>

                    <div className="flex shrink-0 items-center gap-6 text-xs text-foreground-muted">
                      <span>{analysis.claims_count} claims</span>
                      <span>{analysis.evidence_count} evidence</span>
                      <span className="font-mono">#{analysis.id}</span>
                    </div>
                  </div>

                  <div className="mt-3 flex flex-wrap items-center gap-4 text-[11px] text-foreground-faint">
                    <span>{formatDateTime(analysis.created_at)}</span>
                    <span>{analysis.files_discovered} files</span>
                    <span>
                      AI {analysis.with_ai ? "enabled" : "disabled"}
                    </span>
                  </div>
                </Link>
              ))}
            </Panel>
          </section>
        </>
      )}
    </PageContainer>
  );
}