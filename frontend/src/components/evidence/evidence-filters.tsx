import type { ClaimEvidence, EvidenceKind } from "@/lib/api/analyses";

export type EvidenceFilter =
    | "ALL"
    | "FILE_CONTENT"
    | "TEST"
    | "DOCUMENTATION"
    | "DEPENDENCY"
    | "CODE_STRUCTURE"
    | "AI_OBSERVATION";

type EvidenceFiltersProps = {
    evidence: ClaimEvidence[];
    activeFilter: EvidenceFilter;
    onFilterChange: (filter: EvidenceFilter) => void;
};

const filters: Array<{
    label: string;
    value: EvidenceFilter;
}> = [
    { label: "All", value: "ALL" },
    { label: "File content", value: "FILE_CONTENT" },
    { label: "Tests", value: "TEST" },
    { label: "Documentation", value: "DOCUMENTATION" },
    { label: "Dependencies", value: "DEPENDENCY" },
    { label: "Code structure", value: "CODE_STRUCTURE" },
    { label: "AI observations", value: "AI_OBSERVATION" },
];

const codeStructureKinds = new Set<EvidenceKind>([
    "class",
    "function",
    "import",
]);

export function matchesEvidenceFilter(
    item: ClaimEvidence,
    filter: EvidenceFilter,
) {
    if (filter === "ALL") {
        return true;
    }

    if (filter === "CODE_STRUCTURE") {
        return codeStructureKinds.has(item.kind);
    }

    const kindMap: Record<
        Exclude<
            EvidenceFilter,
            "ALL" | "CODE_STRUCTURE"
        >,
        EvidenceKind
    > = {
        FILE_CONTENT: "file_content",
        TEST: "test",
        DOCUMENTATION: "documentation",
        DEPENDENCY: "dependency",
        AI_OBSERVATION: "ai_observation",
    };

    return item.kind === kindMap[filter];
}

export function EvidenceFilters({
    evidence,
    activeFilter,
    onFilterChange,
}: EvidenceFiltersProps) {
    const filteredCount = evidence.filter((item) =>
        matchesEvidenceFilter(
            item,
            activeFilter,
        ),
    ).length;

    return (
        <div className="border-y border-border-subtle">
            <div className="flex items-center justify-between gap-4 py-3">
                <div className="flex flex-wrap items-center gap-1.5">
                    {filters.map((filter) => {
                        const isActive =
                            activeFilter ===
                            filter.value;

                        const count =
                            evidence.filter(
                                (item) =>
                                    matchesEvidenceFilter(
                                        item,
                                        filter.value,
                                    ),
                            ).length;

                        return (
                            <button
                                key={filter.value}
                                type="button"
                                onClick={() =>
                                    onFilterChange(
                                        filter.value,
                                    )
                                }
                                className={`border px-2.5 py-1.5 text-[11px] font-medium transition-colors ${
                                    isActive
                                        ? "border-accent-muted bg-surface-elevated text-foreground"
                                        : "border-transparent text-foreground-faint hover:border-border-subtle hover:text-foreground-muted"
                                }`}
                            >
                                <span>
                                    {filter.label}
                                </span>

                                <span className="ml-1.5 font-mono text-foreground-faint">
                                    {count}
                                </span>
                            </button>
                        );
                    })}
                </div>

                <span className="shrink-0 font-mono text-[11px] text-foreground-faint">
                    {filteredCount}
                    {filteredCount !==
                        evidence.length &&
                        ` / ${evidence.length}`}
                </span>
            </div>

            <div className="flex items-center justify-between border-t border-border-subtle py-2.5 text-[10px] uppercase tracking-[0.14em] text-foreground-faint">
                <span>
                    {filteredCount}{" "}
                    {filteredCount === 1
                        ? "source"
                        : "sources"}
                </span>

                <span>
                    Repository evidence
                </span>
            </div>
        </div>
    );
}