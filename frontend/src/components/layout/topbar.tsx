"use client";

import {
    usePathname,
    useSearchParams,
} from "next/navigation";

function getPageContext(pathname: string) {
    if (pathname === "/") {
        return {
            section: "Workspace",
            title: "Overview",
        };
    }

    if (pathname === "/analyses/new") {
        return {
            section: "Workspace",
            title: "New Analysis",
        };
    }

    if (pathname === "/analyses") {
        return {
            section: "Workspace",
            title: "Analyses",
        };
    }

    if (pathname.startsWith("/analyses/")) {
        return {
            section: "Workspace",
            title: "Analysis",
        };
    }

    if (pathname.startsWith("/claims/")) {
        return {
            section: "Knowledge",
            title: "Claim",
        };
    }

    if (pathname === "/claims") {
        return {
            section: "Knowledge",
            title: "Claims",
        };
    }

    if (pathname === "/evidence") {
        return {
            section: "Knowledge",
            title: "Evidence",
        };
    }

    if (pathname.startsWith("/inspector")) {
        return {
            section: "System",
            title: "Inspector",
        };
    }

    return {
        section: "Workspace",
        title: "Knowledge Compiler",
    };
}

export function Topbar() {
    const pathname = usePathname();
    const searchParams = useSearchParams();

    const context =
        getPageContext(pathname);

    const analysisId =
        searchParams.get("analysis");

    return (
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-border-subtle bg-background px-6">
            <div className="flex min-w-0 items-center">
                <div className="flex min-w-0 items-center gap-3 text-xs">
                    <span className="text-foreground-faint">
                        {context.section}
                    </span>

                    <span className="text-foreground-faint">
                        /
                    </span>

                    <span className="font-medium text-foreground-muted">
                        {context.title}
                    </span>

                    {analysisId && (
                        <>
                            <span className="text-foreground-faint">
                                /
                            </span>

                            <span className="truncate font-mono text-[11px] text-foreground-faint">
                                analysis #{analysisId}
                            </span>
                        </>
                    )}
                </div>
            </div>

            <div className="ml-auto flex items-center">
                <div className="flex items-center gap-2 border-l border-border-subtle pl-3 text-xs text-foreground-muted">
                    <span className="h-1.5 w-1.5 rounded-full bg-supported" />

                    <span>
                        System online
                    </span>
                </div>
            </div>
        </header>
    );
}