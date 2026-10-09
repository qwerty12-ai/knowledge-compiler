import type { ClaimEvidence } from "@/lib/api/analyses";
import { Panel } from "@/components/ui/primitives";
import { EvidenceCard } from "./evidence-card";

type EvidenceListProps = {
    evidence: ClaimEvidence[];
};

export function EvidenceList({
    evidence,
}: EvidenceListProps) {
    return (
        <Panel>
            <div className="border-b border-border px-5 py-3">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-foreground">
                            Source records
                        </p>

                        <p className="mt-1 text-xs text-foreground-faint">
                            Evidence captured from the
                            repository.
                        </p>
                    </div>

                    <span className="font-mono text-xs text-foreground-muted">
                        {evidence.length}
                    </span>
                </div>
            </div>

            <div className="divide-y divide-border">
                {evidence.map((item) => (
                    <EvidenceCard
                        key={item.id}
                        evidence={item}
                    />
                ))}
            </div>
        </Panel>
    );
}