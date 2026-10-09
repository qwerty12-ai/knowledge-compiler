import type { ReactNode } from "react";
import type { ClaimStatus } from "@/lib/api/types";

type PanelProps = {
    children: ReactNode;
    className?: string;
};

export function Panel({
    children,
    className = "",
}: PanelProps) {
    return (
        <section
            className={`border border-border bg-surface ${className}`}
        >
            {children}
        </section>
    );
}

type PageContainerProps = {
    children: ReactNode;
    className?: string;
};

export function PageContainer({
    children,
    className = "",
}: PageContainerProps) {
    return (
        <div
            className={`mx-auto w-full max-w-[1600px] px-8 py-8 ${className}`}
        >
            {children}
        </div>
    );
}

type SectionHeaderProps = {
    eyebrow?: string;
    title: string;
    description?: string;
    action?: ReactNode;
    className?: string;
};

export function SectionHeader({
    eyebrow,
    title,
    description,
    action,
    className = "",
}: SectionHeaderProps) {
    return (
        <div
            className={`flex items-start justify-between gap-6 ${className}`}
        >
            <div className="min-w-0">
                {eyebrow && (
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
                        {eyebrow}
                    </p>
                )}

                <h2 className="mt-2 text-lg font-semibold tracking-tight text-foreground">
                    {title}
                </h2>

                {description && (
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-foreground-muted">
                        {description}
                    </p>
                )}
            </div>

            {action && (
                <div className="shrink-0">
                    {action}
                </div>
            )}
        </div>
    );
}

const statusStyles: Record<ClaimStatus, string> = {
    VERIFIED: "text-supported",
    SUPPORTED: "text-supported",
    WEAKLY_SUPPORTED: "text-weak",
    UNKNOWN: "text-unknown",
    CONTRADICTED: "text-contradicted",
    STALE: "text-stale",
};

export function StatusBadge({
    status,
}: {
    status: ClaimStatus;
}) {
    return (
        <span
            className={`text-[11px] font-semibold uppercase tracking-[0.14em] ${statusStyles[status]}`}
        >
            {status.replaceAll("_", " ")}
        </span>
    );
}

type MetricProps = {
    label: string;
    value: ReactNode;
    description?: string;
};

export function Metric({
    label,
    value,
    description,
}: MetricProps) {
    return (
        <div className="p-6">
            <p className="text-xs uppercase tracking-[0.14em] text-foreground-muted">
                {label}
            </p>

            <p className="mt-2 text-2xl font-semibold tracking-tight text-foreground">
                {value}
            </p>

            {description && (
                <p className="mt-1 text-xs text-foreground-muted">
                    {description}
                </p>
            )}
        </div>
    );
}

type EmptyStateProps = {
    eyebrow?: string;
    title: string;
    description?: string;
    action?: ReactNode;
};

export function EmptyState({
    eyebrow,
    title,
    description,
    action,
}: EmptyStateProps) {
    return (
        <Panel className="px-6 py-16 text-center">
            {eyebrow && (
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-foreground-muted">
                    {eyebrow}
                </p>
            )}

            <h2 className="mt-3 text-lg font-semibold text-foreground">
                {title}
            </h2>

            {description && (
                <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-foreground-muted">
                    {description}
                </p>
            )}

            {action && (
                <div className="mt-6">
                    {action}
                </div>
            )}
        </Panel>
    );
}