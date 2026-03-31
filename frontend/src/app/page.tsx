"use client";

import { useState, useEffect } from "react";
import { BriefingData } from "@/lib/types";
import { fetchBriefing } from "@/lib/api";
import BriefingSelector from "@/components/BriefingSelector";
import Overview from "@/components/Overview";
import WorldNews from "@/components/WorldNews";
import USMarkets from "@/components/USMarkets";
import ASXDeepDive from "@/components/ASXDeepDive";
import Watchlist from "@/components/Watchlist";
import Charts from "@/components/Charts";
import Culture from "@/components/Culture";
import DeepDiveChat from "@/components/DeepDiveChat";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "news", label: "World News" },
  { id: "markets", label: "US & Asia" },
  { id: "asx", label: "ASX" },
  { id: "watchlist", label: "Watchlist" },
  { id: "charts", label: "Charts" },
  { id: "culture", label: "Culture" },
];

export default function Home() {
  const [briefingType, setBriefingType] = useState("8am");
  const [data, setData] = useState<BriefingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [deepDiveContext, setDeepDiveContext] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchBriefing(briefingType)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [briefingType]);

  const openDeepDive = (context: string) => setDeepDiveContext(context);

  return (
    <main className="min-h-screen">
      <div className="max-w-[720px] mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Morning Pulse</h1>
              {data?.meta && (
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  {data.meta.display_date} · {data.meta.display_time}
                </p>
              )}
            </div>
            <BriefingSelector selected={briefingType} onSelect={setBriefingType} />
          </div>

          {/* Tab navigation */}
          <nav className="flex gap-1 overflow-x-auto pb-1 -mx-1 px-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? "bg-[var(--text-primary)] text-[var(--bg-primary)]"
                    : "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </header>

        {/* Content */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block w-6 h-6 border-2 border-[var(--border)] border-t-[var(--text-primary)] rounded-full animate-spin" />
            <p className="text-sm text-[var(--text-muted)] mt-3">Loading briefing...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-20">
            <p className="text-sm text-[var(--negative)]">Failed to load briefing data.</p>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              Make sure briefing JSON files exist in /public/data/
            </p>
          </div>
        )}

        {data && !loading && (
          <div>
            {activeTab === "overview" && <Overview data={data} onDeepDive={openDeepDive} />}
            {activeTab === "news" && <WorldNews stories={data.world_news || []} onDeepDive={openDeepDive} />}
            {activeTab === "markets" && (
              <USMarkets
                usMarkets={data.us_markets || []}
                asiaMarkets={data.asia_markets || []}
                narrative={data.narrative}
              />
            )}
            {activeTab === "asx" && data.asx_deep_dive && (
              <ASXDeepDive data={data.asx_deep_dive} onDeepDive={openDeepDive} />
            )}
            {activeTab === "watchlist" && (
              <Watchlist stocks={data.watchlist || []} onDeepDive={openDeepDive} />
            )}
            {activeTab === "charts" && <Charts crypto={data.crypto || []} fx={data.fx || []} />}
            {activeTab === "culture" && <Culture events={data.culture || []} />}
          </div>
        )}
      </div>

      {/* Deep Dive panel */}
      {deepDiveContext && (
        <DeepDiveChat context={deepDiveContext} onClose={() => setDeepDiveContext(null)} />
      )}
    </main>
  );
}
