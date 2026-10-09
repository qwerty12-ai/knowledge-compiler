import Link from "next/link";
import type { AnalysisClaim } from "@/lib/api/analyses";
import { StatusBadge } from "@/components/ui/primitives";

type ClaimCardProps = {
    claim: AnalysisClaim;
    analysisId?: string;
};

export function ClaimCard({
    claim,
    analysisId,
}: ClaimCardProps) {
    const confidence = Math.round(
        claim.confidence * 100,
    );

    const href = analysisId
        ? `/claims/${claim.id}?analysis=${encodeURIComponent(
              analysisId,
          )}`
        : `/claims/${claim.id}`;

    return (
        <Link
            href={href}
            className="group block border-b border-border px-5 py-4 transition-colors last:border-b-0 hover:bg-surface-elevated"
        >
            <article>
                <div className="flex items-start gap-5">
                    <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-3">
                            <StatusBadge status={claim.status} />

                            <span className="font-mono text-[11px] text-foreground-faint">
                                confidence {confidence}%
                            </span>
                        </div>

                        <p className="mt-2 max-w-4xl text-sm leading-6 text-foreground transition-colors group-hover:text-foreground">
                            {claim.statement}
                        </p>

                        <div className="mt-3 flex items-center gap-3 text-[11px] text-foreground-faint">
                            <span>
                                Claim #{claim.id}
                            </span>

                            <span className="text-border-strong">
                                /
                            </span>

                            <span className="font-medium text-foreground-muted transition-colors group-hover:text-accent">
                                Investigate
                            </span>
                        </div>
                    </div>

                    <div className="hidden w-20 shrink-0 pt-1 sm:block">
                        <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.12em] text-foreground-faint">
                            <span>Confidence</span>
                        </div>

                        <div className="mt-2 h-1 w-full bg-surface-elevated">
                            <div
                                className="h-full bg-accent transition-all"
                                style={{
                                    width: `${confidence}%`,
                                }}
                            />
                        </div>

                        <p className="mt-1 text-right font-mono text-[10px] text-foreground-muted">
                            {confidence}%
                        </p>
                    </div>

                    <span className="shrink-0 font-mono text-[10px] text-foreground-faint">
                        #{claim.id}
                    </span>
                </div>
            </article>
        </Link>
    );
}