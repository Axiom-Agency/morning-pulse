"use client";

import { CultureEvent } from "@/lib/types";

interface Props {
  events: CultureEvent[];
}

export default function Culture({ events }: Props) {
  if (!events || events.length === 0) {
    return (
      <p className="text-sm text-[var(--text-muted)] italic">
        No events meet the significance threshold today.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event, i) => (
        <div key={i} className="border border-[var(--border)] rounded-lg p-4">
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-200">
                {event.significance_tag}
              </span>
              <h4 className="text-sm font-medium mt-2">{event.title}</h4>
              <p className="text-xs text-[var(--text-muted)] mt-0.5">
                {event.venue} · {event.city} · {event.dates}
              </p>
            </div>
          </div>
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed mt-2">{event.description}</p>
          {event.url && (
            <a
              href={event.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] mt-2 inline-block"
            >
              More info →
            </a>
          )}
        </div>
      ))}
    </div>
  );
}
