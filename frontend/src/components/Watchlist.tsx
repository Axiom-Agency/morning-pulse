"use client";

import { useState } from "react";
import { WatchlistStock } from "@/lib/types";
import ChangeTag from "./ChangeTag";

interface Props {
  stocks: WatchlistStock[];
  onDeepDive: (context: string) => void;
}

export default function Watchlist({ stocks, onDeepDive }: Props) {
  const [filter, setFilter] = useState("");

  if (!stocks || stocks.length === 0) {
    return <p className="text-sm text-[var(--text-muted)]">Watchlist data unavailable.</p>;
  }

  const filtered = stocks.filter(
    (s) =>
      s.ticker.toLowerCase().includes(filter.toLowerCase()) ||
      s.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <input
        type="text"
        placeholder="Filter watchlist..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--text-muted)]"
      />

      <div className="space-y-2">
        {filtered.map((stock) => (
          <div key={stock.ticker} className="border border-[var(--border)] rounded-lg p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono font-semibold">{stock.ticker}</span>
                  {stock.has_announcement && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200">
                      ASX Ann
                    </span>
                  )}
                </div>
                <p className="text-xs text-[var(--text-muted)]">{stock.name}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-semibold">${stock.price?.toFixed(2)}</p>
                <ChangeTag value={stock.change_pct} />
              </div>
            </div>

            <div className="mt-3 bg-[var(--bg-secondary)] rounded p-3">
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{stock.news_digest}</p>
            </div>

            <div className="mt-2 flex items-center justify-between text-[10px] text-[var(--text-muted)]">
              <div className="flex gap-3">
                <span>52w: ${stock.week52_low?.toFixed(2)} – ${stock.week52_high?.toFixed(2)}</span>
                {stock.volume_vs_avg && (
                  <span>Vol: {stock.volume_vs_avg.toFixed(1)}x avg</span>
                )}
              </div>
              <button
                onClick={() => onDeepDive(`Stock: ${stock.ticker} (${stock.name})\nPrice: $${stock.price}\nChange: ${stock.change_pct}%\n52w range: $${stock.week52_low} – $${stock.week52_high}\nRecent: ${stock.news_digest}`)}
                className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                Analyse →
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="border border-dashed border-[var(--border)] rounded-lg p-4 text-center">
        <p className="text-xs text-[var(--text-muted)]">
          Edit watchlist: modify <code className="font-mono bg-[var(--bg-secondary)] px-1 rounded">pipeline/config/watchlist.json</code> and redeploy
        </p>
      </div>
    </div>
  );
}
