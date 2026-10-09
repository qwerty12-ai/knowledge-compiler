import type { RedisInspectorResponse } from "@/lib/api/analyses";
import { Panel } from "@/components/ui/primitives";

type AnalysisStatePanelProps = {
    state: RedisInspectorResponse["state"] | undefined;
};

export function AnalysisStatePanel({
    state,
}: AnalysisStatePanelProps) {
    const entries =
        state && state.ttl !== -2
            ? Object.entries(state.state)
            : [];

    return (
        <Panel className="mt-4">
            {entries.length > 0 ? (
                <div className="divide-y divide-border">
                    {entries.map(([key, value]) => (
                        <div
                            key={key}
                            className="grid grid-cols-[180px_minmax(0,1fr)] gap-6 px-6 py-4"
                        >
                            <span className="font-mono text-xs text-foreground-muted">
                                {key}
                            </span>

                            <span className="break-all font-mono text-xs text-foreground">
                                {value}
                            </span>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="px-6 py-10 text-center">
                    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-foreground-faint">
                        {state?.ttl === -2
                            ? "Redis state expired or missing"
                            : state
                              ? "No state fields"
                              : "Runtime state unavailable"}
                    </p>

                    <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-foreground-muted">
                        {state?.ttl === -2
                            ? "The temporary Redis state is no longer retained. The persistent analysis result remains available through the workstation."
                            : state
                              ? "Redis returned a state record, but it contains no fields."
                              : "The runtime state could not be retrieved. Refresh to try again. This alone does not indicate an analysis failure."}
                    </p>
                </div>
            )}
        </Panel>
    );
}