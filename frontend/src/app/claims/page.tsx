import { Suspense } from "react";
import ClaimsPageContent from "./claims-page-content";

export default function ClaimsPage() {
    return (
        <Suspense
            fallback={
                <div className="mx-auto w-full max-w-[1600px] px-8 py-8">
                    <section className="border border-border bg-surface px-5 py-10">
                        <p className="text-sm text-foreground-muted">
                            Loading claims...
                        </p>
                    </section>
                </div>
            }
        >
            <ClaimsPageContent />
        </Suspense>
    );
}