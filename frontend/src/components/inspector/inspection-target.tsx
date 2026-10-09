import type { RecentAnalysis } from "@/lib/api/analyses";

type InspectionTargetProps = {
    analysis: RecentAnalysis;
    analyses: RecentAnalysis[];
    selectedAnalysisId: string;
    onAnalysisChange: (analysisId: string) => void;
};

function getRepositoryName(path: string) {
    return path.split("/").filter(Boolean).pop() ?? path;
}

export function InspectionTarget({
    analysis,
    analyses,
    selectedAnalysisId,
    onAnalysisChange,
}: InspectionTargetProps) {
    return (
        <section className="border-b border-border px-6 py-4">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
                        Inspection target
                    </p>

                    <p className="mt-2 text-sm font-medium text-foreground">
                        {getRepositoryName(analysis.repository_path)}
                    </p>

                    <p className="mt-1 break-all font-mono text-xs text-foreground-muted">
                        {analysis.repository_path}
                    </p>
                </div>

                <div className="shrink-0">
                    <label
                        htmlFor="analysis-select"
                        className="mb-2 block text-[10px] font-medium uppercase tracking-[0.16em] text-foreground-faint"
                    >
                        Analysis
                    </label>

                    <select
                        id="analysis-select"
                        value={selectedAnalysisId}
                        onChange={(event) =>
                            onAnalysisChange(event.target.value)
                        }
                        className="h-9 min-w-52 border border-border-strong bg-surface px-3 text-xs text-foreground outline-none transition-colors focus:border-accent-muted"
                    >
                        {analyses.map((item) => (
                            <option
                                key={item.id}
                                value={String(item.id)}
                            >
                                #{item.id} · {getRepositoryName(item.repository_path)}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
        </section>
    );
}