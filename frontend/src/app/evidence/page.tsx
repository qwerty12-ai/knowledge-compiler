import { Suspense } from "react";
import EvidencePageContent from "./evidence-page-content";

export default function EvidencePage() {
    return (
        <Suspense
            fallback={
                <div className="mx-auto w-full max-w-[1600px] px-8 py-8">
                    <section className="border border-border bg-surface px-5 py-10">
                        <p className="text-sm text-foreground-muted">
                            Loading evidence...
                        </p>
                    </section>
                </div>
            }
        >
            <EvidencePageContent />
        </Suspense>
    );
}