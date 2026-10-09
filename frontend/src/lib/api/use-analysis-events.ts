"use client";

import { useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export type AnalysisEvent = {
  analysis_id: string;
  status: string;
  stage: string;
  progress: number;
  database_id?: number | null;
};

export type AnalysisEventConnection =
  | "idle"
  | "connecting"
  | "connected"
  | "closed"
  | "error";

export function useAnalysisEvents(
  analysisId: string | null,
) {
  const [event, setEvent] =
    useState<AnalysisEvent | null>(null);

  const [events, setEvents] =
    useState<(AnalysisEvent & {
        timestamp: number;
    })[]>([]);

  const [connection, setConnection] =
    useState<AnalysisEventConnection>("idle");

  const [eventAnalysisId, setEventAnalysisId] =
    useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      return;
    }

    const currentAnalysisId = analysisId;

    const url =
      `${API_BASE_URL}/api/v1/analyses/` +
      `${encodeURIComponent(currentAnalysisId)}/events`;

    const source = new EventSource(url);

    source.onopen = () => {
      setConnection("connected");
    };

    source.onmessage = (message) => {
      try {
        const data =
          JSON.parse(message.data) as AnalysisEvent;

        if (
          data.analysis_id !==
          currentAnalysisId
        ) {
          return;
        }

        setEvent(data);
        setEventAnalysisId(currentAnalysisId);

        setEvents((previous) => {
          const last =
            previous[previous.length - 1];

          if (
            last &&
            last.status === data.status &&
            last.stage === data.stage &&
            last.progress === data.progress
          ) {
            return previous;
          }

          return [...previous, {...data, timestamp: Date.now()}];
        });

        if (
          data.status === "completed" ||
          data.status === "failed"
        ) {
          source.close();
          setConnection("closed");
        }
      } catch {
        // Ignore malformed events.
      }
    };

    source.onerror = () => {
      setConnection("error");
    };

    return () => {
      source.close();
    };
  }, [analysisId]);

  const currentEvent =
    eventAnalysisId === analysisId
      ? event
      : null;

  const currentEvents =
    eventAnalysisId === analysisId
      ? events
      : [];

  const isConnected =
    connection === "connected";

  return {
    event: currentEvent,
    events: currentEvents,
    connection,
    isConnected,
  };
}