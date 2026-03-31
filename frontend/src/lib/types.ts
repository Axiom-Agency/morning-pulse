export interface BriefingMeta {
  briefing_type: string;
  generated_at: string;
  date: string;
  display_date: string;
  display_time: string;
}

export interface NewsStory {
  headline: string;
  summary: string;
  severity: "high" | "medium" | "low";
  region: string;
  aus_impact: boolean;
  aus_impact_note?: string;
  sources: string[];
}

export interface MarketIndex {
  ticker: string;
  name: string;
  price: number;
  change: number;
  change_pct: number;
  trend_5d?: string;
  error?: string;
}

export interface ASXMover {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  explanation: string;
}

export interface ASXSector {
  name: string;
  change_pct: number;
  summary: string;
  movers: ASXMover[];
}

export interface ASXDeepDive {
  overview: string;
  asx200: { level: number; change_pct: number };
  sectors: ASXSector[];
}

export interface WatchlistStock {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  volume_vs_avg: number;
  week52_high: number;
  week52_low: number;
  news_digest: string;
  has_announcement: boolean;
}

export interface CryptoData {
  coin_id: string;
  name: string;
  symbol: string;
  current_price: number;
  change_24h_pct: number;
  yoy_change_pct: number;
  history: { date: string; price: number }[];
  error?: string;
}

export interface FXData {
  ticker: string;
  name: string;
  current_rate: number;
  change_pct: number;
  yoy_change_pct: number;
  history: { date: string; rate: number }[];
  error?: string;
}

export interface CultureEvent {
  title: string;
  venue: string;
  city: string;
  dates: string;
  description: string;
  significance_tag: string;
  url: string;
}

export interface MarketNarrative {
  us_narrative: string;
  asia_narrative: string;
}

export interface Commodity {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  error?: string;
}

export interface BriefingData {
  meta: BriefingMeta;
  world_news?: NewsStory[];
  us_markets?: MarketIndex[];
  asia_markets?: MarketIndex[];
  asx_deep_dive?: ASXDeepDive;
  watchlist?: WatchlistStock[];
  crypto?: CryptoData[];
  fx?: FXData[];
  culture?: CultureEvent[];
  narrative?: MarketNarrative;
  commodities?: Commodity[];
  asx200?: { level: number; change_pct: number };
}
