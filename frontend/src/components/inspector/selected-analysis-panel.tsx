import type { RecentAnalysis } from "@/lib/api/analyses";
import { Panel } from "@/components/ui/primitives";
import { formatDateTime } from "@/lib/utils/date";

type SelectedAnalysisPanelProps = {
    analysis: RecentAnalysis;
};

export function SelectedAnalysisPanel({
    analysis,
}: SelectedAnalysisPanelProps) {
    return (
        <Panel className="mt-4">
            <div className="grid grid-cols-1 divide-y divide-border md:grid-cols-2 md:divide-x md:divide-y-0">
                <div className="space-y-5 p-6">
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                            Repository
                        </p>
                        <p className="mt-1 break-all font-mono text-xs text-foreground">
                            {analysis.repository_path}
                        </p>
                    </div>

                    <div>
                        <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                            Created
                        </p>
                        <p className="mt-1 text-sm text-foreground">
                            {formatDateTime(analysis.created_at)}
                        </p>
                    </div>
                </div>

                <div className="space-y-5 p-6">
                    <div>
                        <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                            Database ID
                        </p>
                        <p className="mt-1 font-mono text-sm text-foreground">
                            #{analysis.id}
                        </p>
                    </div>

                    <div>
                        <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                            Compiler output
                        </p>
                        <div className="mt-1 flex gap-4 text-sm text-foreground">
                            <span>{analysis.claims_count} claims</span>
                            <span>{analysis.evidence_count} evidence</span>
                        </div>
                    </div>
                </div>
            </div>
        </Panel>
    );
}