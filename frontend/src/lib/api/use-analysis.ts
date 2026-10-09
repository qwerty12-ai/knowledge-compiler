"use client";

import { useEffect, useState } from "react";
import {
    getAnalysis,
    type AnalysisState,
} from "./analyses";
import { useAnalysisEvents } from "./use-analysis-events";

export function useAnalysis(analysisId: string) {
    const [initialAnalysis, setInitialAnalysis] =
        useState<AnalysisState | null>(null);

    const [loadedAnalysisId, setLoadedAnalysisId] =
        useState<string | null>(null);

    const [error, setError] =
        useState<string | null>(null);

    const [errorAnalysisId, setErrorAnalysisId] =
        useState<string | null>(null);

    const [retryNonce, setRetryNonce] =
        useState(0);

    const {
        event,
        events,
        connection,
    } = useAnalysisEvents(analysisId);

    useEffect(() => {
        let cancelled = false;

        async function loadInitialAnalysis() {
            try {
                const result =
                    await getAnalysis(analysisId);

                if (cancelled) {
                    return;
                }

                setInitialAnalysis(result);
                setLoadedAnalysisId(analysisId);
                setError(null);
                setErrorAnalysisId(null);
            } catch (error) {
                if (cancelled) {
                    return;
                }

                setError(
                    error instanceof Error
                        ? error.message
                        : "Failed to fetch analysis.",
                );

                setErrorAnalysisId(analysisId);
                setLoadedAnalysisId(analysisId);
            }
        }

        loadInitialAnalysis();

        return () => {
            cancelled = true;
        };
    }, [analysisId, retryNonce]);

    useEffect(() => {
        if (event?.status !== "completed") {
            return;
        }

        let cancelled = false;

        async function refreshCompletedAnalysis() {
            try {
                const result =
                    await getAnalysis(analysisId);

                if (cancelled) {
                    return;
                }

                setInitialAnalysis(result);
                setLoadedAnalysisId(analysisId);
                setError(null);
                setErrorAnalysisId(null);
            } catch (error) {
                if (cancelled) {
                    return;
                }

                setError(
                    error instanceof Error
                        ? error.message
                        : "Failed to refresh completed analysis.",
                );

                setErrorAnalysisId(analysisId);
                setLoadedAnalysisId(analysisId);
            }
        }

        refreshCompletedAnalysis();

        return () => {
            cancelled = true;
        };
    }, [analysisId, event?.status]);

    const analysis: AnalysisState | null =
        initialAnalysis
            ? {
                  ...initialAnalysis,
                  ...(event
                      ? {
                            status:
                                event.status as AnalysisState["status"],
                            stage: event.stage,
                            progress: event.progress,
                        }
                      : {}),
              }
            : null;

    const currentAnalysis =
        loadedAnalysisId === analysisId
            ? analysis
            : null;

    const currentError =
        errorAnalysisId === analysisId
            ? error
            : null;

    const isLoading =
        currentAnalysis === null &&
        currentError === null;

    const isRealtime =
        connection === "connected";

    const retry = () => {
        setRetryNonce((value) => value + 1);
    };

    return {
        analysis: currentAnalysis,
        events,
        connection,
        isLoading,
        error: currentError,
        isRealtime,
        retry,
    };
}