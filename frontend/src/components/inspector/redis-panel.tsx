import type { RedisInspectorResponse } from "@/lib/api/analyses";
import { Metric, Panel } from "@/components/ui/primitives";

type RedisPanelProps = {
    analysisId: string;
    state: RedisInspectorResponse["state"] | undefined;
};

function formatTtl(ttl: number) {
    if (ttl === -2) return "Missing";
    if (ttl === -1) return "Persistent";

    const minutes = Math.floor(ttl / 60);
    const seconds = ttl % 60;

    return minutes === 0
        ? `${seconds}s`
        : `${minutes}m ${seconds}s`;
}

function getStatus(
    state: RedisInspectorResponse["state"] | undefined,
) {
    if (!state) return "Unavailable";
    if (state.ttl === -2) return "Missing";
    return state.state.status || "Available";
}

function getDescription(
    state: RedisInspectorResponse["state"] | undefined,
) {
    if (!state) {
        return "Redis state could not be retrieved.";
    }

    if (state.ttl === -2) {
        return "The temporary Redis key is no longer present. This does not mean the analysis failed; persistent results remain available.";
    }

    if (state.ttl === -1) {
        return "Redis state is available without an expiration.";
    }

    return state.state.stage
        ? `Current stage: ${state.state.stage}`
        : "Runtime state is available.";
}

export function RedisPanel({
    analysisId,
    state,
}: RedisPanelProps) {
    const status = getStatus(state);
    const description = getDescription(state);

    return (
        <Panel className="border-0">
            <div className="border-b border-border px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-accent">
                    Redis
                </p>
            </div>

            <div className="space-y-5 p-5">
                <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                        Key
                    </p>
                    <p className="mt-1 break-all font-mono text-xs text-foreground">
                        analysis:{analysisId}
                    </p>
                </div>

                <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                        Status
                    </p>
                    <p className="mt-1 text-sm text-foreground">
                        {status}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-foreground-muted">
                        {description}
                    </p>
                </div>

                <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                        TTL
                    </p>
                    <p className="mt-1 font-mono text-sm text-foreground">
                        {state ? formatTtl(state.ttl) : "—"}
                    </p>
                </div>
            </div>
        </Panel>
    );
}

type RedisSummaryProps = {
    status: string;
    description: string;
    progress: string;
    ttl: string;
};

export function RedisSummary({
    status,
    description,
    progress,
    ttl,
}: RedisSummaryProps) {
    return (
        <div className="grid grid-cols-1 divide-y divide-border md:grid-cols-3 md:divide-x md:divide-y-0">
            <Metric
                label="Status"
                value={status}
                description={description}
            />
            <Metric
                label="Progress"
                value={progress}
            />
            <Metric
                label="State TTL"
                value={ttl}
                description="Redis expiration"
            />
        </div>
    );
}