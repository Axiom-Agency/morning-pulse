"use client";

import { MarketIndex, MarketNarrative } from "@/lib/types";
import ChangeTag from "./ChangeTag";

interface Props {
  usMarkets: MarketIndex[];
  asiaMarkets: MarketIndex[];
  narrative?: MarketNarrative;
}

function IndexCard({ index }: { index: MarketIndex }) {
  if (index.error) {
    return (
      <div className="bg-[var(--bg-secondary)] rounded-lg p-4 opacity-50">
        <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{index.name}</p>
        <p className="text-sm text-[var(--text-muted)] mt-2">Unavailable</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
      <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{index.name}</p>
      <p className="text-xl font-semibold mt-1">{index.price?.toLocaleString()}</p>
      <div className="flex items-center gap-2 mt-1">
        <ChangeTag value={index.change_pct} />
        {index.trend_5d && (
          <span className="text-[10px] text-[var(--text-muted)]">
            5d: {index.trend_5d === "up" ? "↑" : index.trend_5d === "down" ? "↓" : "→"}
          </span>
        )}
      </div>
    </div>
  );
}

export default function USMarkets({ usMarkets, asiaMarkets, narrative }: Props) {
  const mainIndices = usMarkets.filter((i) => !i.ticker?.includes("TNX"));
  const bondYield = usMarkets.find((i) => i.ticker?.includes("TNX"));

  return (
    <div className="space-y-6">
      {narrative?.us_narrative && (
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{narrative.us_narrative}</p>
      )}

      <div>
        <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)] mb-3">US indices</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {mainIndices.map((idx) => (
            <IndexCard key={idx.ticker} index={idx} />
          ))}
        </div>
        {bondYield && !bondYield.error && (
          <div className="mt-3 bg-[var(--bg-secondary)] rounded-lg p-3 inline-block">
            <span className="text-xs text-[var(--text-muted)]">US 10yr Yield: </span>
            <span className="text-sm font-semibold">{bondYield.price?.toFixed(2)}%</span>
            <span className="ml-2"><ChangeTag value={bondYield.change_pct} /></span>
          </div>
        )}
      </div>

      {asiaMarkets && asiaMarkets.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)] mb-3">Asia</h3>
          {narrative?.asia_narrative && (
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-3">{narrative.asia_narrative}</p>
          )}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {asiaMarkets.map((idx) => (
              <IndexCard key={idx.ticker} index={idx} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
