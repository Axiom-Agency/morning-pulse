"use client";

import { BriefingData } from "@/lib/types";
import ChangeTag from "./ChangeTag";
import SeverityDot from "./SeverityDot";

interface Props {
  data: BriefingData;
  onDeepDive: (context: string) => void;
}

export default function Overview({ data, onDeepDive }: Props) {
  const asx = data.asx_deep_dive?.asx200 || data.asx200;
  const sp500 = data.us_markets?.find((i) => i.ticker?.includes("GSPC") || i.name?.includes("S&P"));
  const audusd = data.fx?.find((f) => f.name?.includes("AUD/USD"));
  const btc = data.crypto?.find((c) => c.symbol === "BTC");
  const topStories = (data.world_news || []).slice(0, 3);

  const metrics = [
    { label: "ASX 200", value: asx?.level?.toLocaleString() || "—", change: asx?.change_pct },
    { label: "S&P 500", value: sp500?.price?.toLocaleString() || "—", change: sp500?.change_pct },
    { label: "AUD/USD", value: audusd?.current_rate?.toFixed(4) || "—", change: audusd?.change_pct },
    { label: "BTC/AUD", value: btc?.current_price ? `$${btc.current_price.toLocaleString()}` : "—", change: btc?.change_24h_pct },
  ];

  return (
    <div className="space-y-6">
      {data.narrative?.us_narrative && (
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
          {data.narrative.us_narrative} {data.narrative.asia_narrative}
        </p>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="bg-[var(--bg-secondary)] rounded-lg p-4">
            <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{m.label}</p>
            <p className="text-xl font-semibold mt-1">{m.value}</p>
            {m.change != null && (
              <div className="mt-1">
                <ChangeTag value={m.change} />
              </div>
            )}
          </div>
        ))}
      </div>

      {topStories.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)] mb-3">Top stories</h3>
          <div className="space-y-3">
            {topStories.map((story, i) => (
              <div key={i} className="flex gap-3 items-start">
                <SeverityDot severity={story.severity} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium leading-snug">{story.headline}</p>
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5">{story.region}</p>
                </div>
                <button
                  onClick={() => onDeepDive(`News: ${story.headline}\n\n${story.summary}`)}
                  className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0"
                >
                  Analyse →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
