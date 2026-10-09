/**
 * Shared date and time formatting for Knowledge Compiler.
 *
 * Explicit timezone offsets are respected.
 * Timezone-less timestamps are interpreted as UTC.
 * Display formatting uses the viewer's browser timezone.
 *
 * IMPORTANT:
 * This assumes timezone-less API timestamps represent UTC.
 * Confirm that convention before relying on this for production data.
 */

export function formatDateTime(value: string | Date): string {
    const raw =
        value instanceof Date
            ? value.toISOString()
            : value.trim();

    const hasTimezone =
        /(?:Z|[+-]\d{2}:?\d{2})$/i.test(raw);

    const normalized = hasTimezone
        ? raw
        : `${raw.replace(" ", "T")}Z`;

    const date = new Date(normalized);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
}

/**
 * Format an event timestamp for the viewer's local timezone.
 * The analysis event hook currently supplies milliseconds from Date.now().
 */
export function formatTime(value: number | string | Date): string {
    const date =
        value instanceof Date
            ? value
            : typeof value === "number"
              ? new Date(value)
              : new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(undefined, {
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
    }).format(date);
}

/**
 * Returns the browser's IANA timezone, e.g. Asia/Kolkata.
 * No location permission is needed.
 */
export function getUserTimeZone(): string {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}