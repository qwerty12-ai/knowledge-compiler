import type { RedisInspectorResponse } from "@/lib/api/analyses";
import { Metric, Panel } from "@/components/ui/primitives";

type QueuePanelProps = {
    queue: RedisInspectorResponse["queue"] | undefined;
};

function getCount(
    counts: Record<string, number>,
    key: string,
) {
    return counts[key] ?? 0;
}

export function QueuePanel({ queue }: QueuePanelProps) {
    return (
        <Panel className="border-0">
            <div className="border-b border-border px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-accent">
                    Analysis queue
                </p>
            </div>

            <div className="grid grid-cols-2 divide-x divide-y divide-border">
                {(["waiting", "active", "completed", "failed"] as const).map(
                    (key) => (
                        <Metric
                            key={key}
                            label={key}
                            value={
                                queue
                                    ? getCount(queue.counts, key)
                                    : "—"
                            }
                        />
                    ),
                )}
            </div>

            <div className="border-t border-border px-5 py-4">
                <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                    Delayed
                </p>
                <p className="mt-1 font-mono text-sm text-foreground">
                    {queue ? getCount(queue.counts, "delayed") : "—"}
                </p>
            </div>
        </Panel>
    );
}