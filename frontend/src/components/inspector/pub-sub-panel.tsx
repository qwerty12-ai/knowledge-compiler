import type { RedisInspectorResponse } from "@/lib/api/analyses";
import { Panel } from "@/components/ui/primitives";

type PubSubPanelProps = {
    channel: RedisInspectorResponse["channel"] | undefined;
};

export function PubSubPanel({ channel }: PubSubPanelProps) {
    return (
        <Panel className="border-0">
            <div className="border-b border-border px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-accent">
                    Pub/Sub
                </p>
            </div>

            <div className="space-y-5 p-5">
                <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                        Channel
                    </p>
                    <p className="mt-1 break-all font-mono text-xs text-foreground">
                        {channel?.channel ?? "Unavailable"}
                    </p>
                </div>

                <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                        Subscribers
                    </p>
                    <p className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
                        {channel?.subscribers ?? "—"}
                    </p>
                </div>

                <p className="text-xs leading-5 text-foreground-muted">
                    Subscribers receive live analysis events published through Redis.
                </p>
            </div>
        </Panel>
    );
}