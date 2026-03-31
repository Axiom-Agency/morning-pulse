"use client";

import { useState } from "react";
import { NewsStory } from "@/lib/types";
import SeverityDot from "./SeverityDot";

interface Props {
  stories: NewsStory[];
  onDeepDive: (context: string) => void;
}

export default function WorldNews({ stories, onDeepDive }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  if (!stories || stories.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">No news available for this briefing.</p>;
  }

  return (
    <div className="space-y-2">
      {stories.map((story, i) => (
        <div key={i} className="border-b border-[var(--border)] pb-3 last:border-0">
          <button
            onClick={() => setExpanded(expanded === i ? null : i)}
            className="w-full text-left flex gap-3 items-start"
          >
            <SeverityDot severity={story.severity} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium leading-snug">{story.headline}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--bg-secondary)] text-[var(--text-muted)] shrink-0">
                  {story.region}
                </span>
                {story.aus_impact && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200 shrink-0">
                    AUS
                  </span>
                )}
              </div>
              {expanded !== i && (
                <p className="text-xs text-[var(--text-secondary)] mt-1 line-clamp-1">{story.summary}</p>
              )}
            </div>
          </button>

          {expanded === i && (
            <div className="ml-6 mt-2 space-y-2">
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{story.summary}</p>
              {story.aus_impact && story.aus_impact_note && (
                <p className="text-xs text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950 rounded p-2">
                  Australian impact: {story.aus_impact_note}
                </p>
              )}
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-[var(--text-muted)]">
                  Sources: {story.sources?.join(", ")}
                </span>
                <button
                  onClick={() => onDeepDive(`News story: ${story.headline}\n\nSummary: ${story.summary}\nRegion: ${story.region}`)}
                  className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                >
                  Deep dive →
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
