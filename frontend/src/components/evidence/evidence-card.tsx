import type { ClaimEvidence } from "@/lib/api/analyses";

type EvidenceCardProps = {
    evidence: ClaimEvidence;
};

function getEvidenceKindLabel(
    kind: ClaimEvidence["kind"],
) {
    switch (kind) {
        case "ai_observation":
            return "AI observation";

        case "file_content":
            return "File content";

        case "documentation":
            return "Documentation";

        case "dependency":
            return "Dependency";

        case "test":
            return "Test";

        case "class":
            return "Class";

        case "function":
            return "Function";

        case "import":
            return "Import";

        default:
            return String(kind).replaceAll(
                "_",
                " ",
            );
    }
}

function getEvidenceKindClass(
    kind: ClaimEvidence["kind"],
) {
    switch (kind) {
        case "test":
            return "border-supported-muted text-supported";

        case "ai_observation":
            return "border-accent-muted text-accent";

        case "dependency":
            return "border-weak-muted text-weak";

        case "documentation":
            return "border-border-strong text-foreground-muted";

        case "class":
        case "function":
        case "import":
            return "border-border-strong text-foreground-muted";

        case "file_content":
        default:
            return "border-border-subtle text-foreground-muted";
    }
}

export function EvidenceCard({
    evidence,
}: EvidenceCardProps) {
    return (
        <article className="group px-5 py-4 transition-colors hover:bg-surface-elevated">
            <div className="flex items-start gap-5">
                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-3">
                        <span
                            className={`border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ${getEvidenceKindClass(
                                evidence.kind,
                            )}`}
                        >
                            {getEvidenceKindLabel(
                                evidence.kind,
                            )}
                        </span>

                        {evidence.language && (
                            <span className="font-mono text-[11px] text-foreground-faint">
                                {evidence.language}
                            </span>
                        )}
                    </div>

                    <p className="mt-2 break-all font-mono text-xs leading-5 text-foreground">
                        {evidence.source}
                    </p>

                    <p className="mt-2 max-w-4xl text-sm leading-6 text-foreground-muted">
                        {evidence.description}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.08em] text-foreground-faint">
                        {evidence.line_start !== null && (
                            <span>
                                lines{" "}
                                {evidence.line_start}
                                {evidence.line_end !==
                                    null &&
                                    evidence.line_end !==
                                        evidence.line_start &&
                                    `–${evidence.line_end}`}
                            </span>
                        )}

                        <span>
                            evidence #{evidence.id}
                        </span>
                    </div>
                </div>
            </div>
        </article>
    );
}