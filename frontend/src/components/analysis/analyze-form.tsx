"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createAnalysis } from "@/lib/api/analyses";
import { Panel } from "@/components/ui/primitives";

export function AnalyzeForm() {
  const [repositoryPath, setRepositoryPath] = useState("");
  const [limit, setLimit] = useState("100");
  const [withAi, setWithAi] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const path = repositoryPath.trim();

    if (!path) {
      setError("Enter the path to the project you want to analyze.");
      return;
    }

    if (withAi) {
      const parsedLimit = Number(limit);

      if (!Number.isInteger(parsedLimit) || parsedLimit < 1) {
        setError(
          "AI investigation limit must be a whole number greater than 0",
        );
        return;
      }
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const result = await createAnalysis({
        repository_path: path,
        limit: withAi ? Number(limit) : null,
        with_ai: withAi,
      });

      router.push(`/analyses/${result.analysis_id}`);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong while starting the analysis.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Panel className="max-w-3xl">
      <form onSubmit={handleSubmit}>
        <div className="border-b border-border px-6 py-5">
          <h2 className="text-sm font-semibold text-foreground">
            Repository
          </h2>

          <p className="mt-1 text-sm text-foreground-muted">
            Choose the project directory you want Knowledge Compiler to
            analyze.
          </p>
        </div>

        <div className="space-y-8 px-6 py-6">
          <div>
            <label
              htmlFor="repository-path"
              className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-foreground-muted"
            >
              Project root path
            </label>

            <input
              id="repository-path"
              type="text"
              value={repositoryPath}
              onChange={(event) => setRepositoryPath(event.target.value)}
              placeholder="/workspace/my-project"
              required
              className="w-full border border-border-strong bg-background px-3 py-2.5 font-mono text-sm text-foreground outline-none transition focus:border-accent focus:ring-1 focus:ring-[var(--focus-ring)]"
            />

            <p className="mt-2 text-xs leading-5 text-foreground-muted">
              Enter the path to the root directory of the project you want
              to analyze. The project must be available in the workstation&apos;s
              shared workspace.
            </p>

            <p className="mt-2 text-xs leading-5 text-foreground-muted">
              Example project:{" "}
              <code>/workspace/my-project</code>
              <br />
              Example subdirectory:{" "}
              <code>/workspace/my-project/src</code>
            </p>

            <p className="mt-2 text-xs leading-5 text-foreground-muted">
              Put your project in the configured projects directory and use
              its corresponding workspace path. The directory must be
              accessible to both the API and worker.
            </p>
          </div>

          <div className="border-t border-border pt-6">
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="text-sm font-medium text-foreground">
                  AI investigation
                </p>

                <p className="mt-1 max-w-xl text-sm leading-5 text-foreground-muted">
                  Allow the compiler to investigate selected project
                  context with the configured AI investigator.
                </p>

                {!withAi && (
                  <p className="mt-2 text-xs text-foreground-faint">
                    Enable AI investigation to configure this limit.
                  </p>
                )}
              </div>

              <button
                type="button"
                onClick={() => setWithAi((value) => !value)}
                className="relative flex h-8 w-14 shrink-0 items-center rounded-full border border-border bg-surface-elevated p-1"
                aria-pressed={withAi}
                aria-label="Toggle AI investigation"
              >
                <span
                  className={`flex h-6 w-6 items-center justify-center rounded-full bg-white text-[10px] font-semibold text-black transition-transform duration-200 ${
                    withAi ? "translate-x-6" : "translate-x-0"
                  }`}
                >
                  {withAi ? "AI" : ""}
                </span>
              </button>
            </div>
          </div>

          <div
            className={`transition-opacity ${
              withAi ? "opacity-100" : "opacity-60"
            }`}
          >
            <label
              htmlFor="ai-limit"
              className="mb-2 block text-xs font-medium uppercase tracking-[0.14em] text-foreground-muted"
            >
              AI investigation limit
            </label>

            <input
              id="ai-limit"
              type="number"
              min="1"
              step="1"
              value={limit}
              disabled={!withAi}
              onChange={(event) => setLimit(event.target.value)}
              className="w-40 border border-border-strong bg-background px-3 py-2.5 font-mono text-sm text-foreground outline-none transition focus:border-accent focus:ring-1 focus:ring-[var(--focus-ring)] disabled:cursor-not-allowed"
            />

            <p className="mt-2 text-xs text-foreground-muted">
              Maximum number of investigation units the AI investigator may
              investigate. Deterministic repository analysis runs
              independently of this limit.
            </p>
          </div>
        </div>

        {error && (
          <div className="border-t border-border px-6 py-4">
            <p className="text-sm text-contradicted">{error}</p>
          </div>
        )}

        <div className="flex items-center justify-end gap-3 border-t border-border px-6 py-4">
          <button
            type="submit"
            disabled={isSubmitting || !repositoryPath.trim()}
            className="bg-accent px-4 py-2.5 text-sm font-semibold text-[#111] transition hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? "Starting analysis..." : "Analyze repository →"}
          </button>
        </div>
      </form>
    </Panel>
  );
}