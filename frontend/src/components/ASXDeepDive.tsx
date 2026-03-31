"use client";

import { useState } from "react";
import { ASXDeepDive as ASXData } from "@/lib/types";
import ChangeTag from "./ChangeTag";

interface Props {
  data: ASXData;
  onDeepDive: (context: string) => void;
}

export default function ASXDeepDive({ data, onDeepDive }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!data) {
    return <p className="text-sm text-[var(--text-muted)]">ASX data unavailable.</p>;
  }

  return (
    <div className="space-y-4">
      {data.overview && (
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{data.overview}</p>
      )}

      <div className="bg-[var(--bg-secondary)] rounded-lg p-4 inline-block">
        <span className="text-xs text-[var(--text-muted)] uppercase tracking-wide">ASX 200</span>
        <p className="text-2xl font-semibold mt-1">{data.asx200?.level?.toLocaleString()}</p>
        {data.asx200?.change_pct != null && (
          <div className="mt-1"><ChangeTag value={data.asx200.change_pct} size="lg" /></div>
        )}
      </div>

      <div className="space-y-1">
        {data.sectors?.map((sector) => {
          const isExpanded = expanded === sector.name;
          const isPositive = sector.change_pct >= 0;

          return (
            <div key={sector.name} className="border border-[var(--border)] rounded-lg overflow-hidden">
              <button
                onClick={() => setExpanded(isExpanded ? null : sector.name)}
                className="w-full flex items-center justify-between p-3 hover:bg-[var(--bg-secondary)] transition-colors"
              >
                <span className="text-sm font-medium">{sector.name}</span>
                <div className="flex items-center gap-2">
                  <ChangeTag value={sector.change_pct} />
                  <span className="text-xs text-[var(--text-muted)]">{isExpanded ? "▲" : "▼"}</span>
                </div>
              </button>

              {isExpanded && (
                <div className="px-3 pb-3 space-y-3">
                  {sector.summary && (
                    <p className="text-xs text-[var(--text-secondary)]">{sector.summary}</p>
                  )}
                  <div className="space-y-2">
                    {sector.movers?.map((mover) => (
                      <div key={mover.ticker} className="flex items-start gap-3 bg-[var(--bg-secondary)] rounded p-2.5">
                        <div className="shrink-0">
                          <span className="text-xs font-mono font-semibold">{mover.ticker}</span>
                          <p className="text-xs text-[var(--text-muted)]">${mover.price}</p>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{mover.explanation}</p>
                        </div>
                        <ChangeTag value={mover.change_pct} />
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => onDeepDive(`ASX Sector: ${sector.name}\nPerformance: ${sector.change_pct}%\nSummary: ${sector.summary}`)}
                    className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                  >
                    Deep dive on {sector.name} →
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
