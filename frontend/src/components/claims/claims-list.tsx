import type { AnalysisClaim } from "@/lib/api/analyses";
import { ClaimCard } from "./claim-card";
import { EmptyState, Panel } from "@/components/ui/primitives";

type ClaimsListProps = {
  claims: AnalysisClaim[];
};

export function ClaimsList({ claims }: ClaimsListProps) {
  if (claims.length === 0) {
    return (
      <EmptyState
        eyebrow="Claims"
        title="No claims were generated."
        description="The compiler did not produce any claims for this analysis."
      />
    );
  }

  return (
    <Panel>
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <div>
          <h2 className="text-sm font-semibold text-foreground">
            Claims
          </h2>

          <p className="mt-1 text-xs text-foreground-muted">
            Engineering knowledge inferred from repository evidence.
          </p>
        </div>

        <span className="font-mono text-xs text-foreground-muted">
          {claims.length}
        </span>
      </div>

      {claims.map((claim) => (
        <ClaimCard key={claim.id} claim={claim} />
      ))}
    </Panel>
  );
}