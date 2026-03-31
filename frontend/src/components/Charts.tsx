"use client";

import { CryptoData, FXData } from "@/lib/types";
import SparklineChart from "./SparklineChart";
import ChangeTag from "./ChangeTag";

interface Props {
  crypto: CryptoData[];
  fx: FXData[];
}

const COLORS: Record<string, string> = {
  BTC: "#EF9F27",
  ETH: "#534AB7",
  "AUD/USD": "#185FA5",
  "NZD/USD": "#1D9E75",
  "AUD/NZD": "#D85A30",
};

function CryptoCard({ coin }: { coin: CryptoData }) {
  if (coin.error) return null;

  const chartData = coin.history?.map((h) => ({ date: h.date, value: h.price })) || [];
  const color = COLORS[coin.symbol] || "#888";

  return (
    <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
      <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{coin.name} ({coin.symbol}/AUD)</p>
      <p className="text-xl font-semibold mt-1">${coin.current_price?.toLocaleString()}</p>
      <div className="flex items-center gap-2 mt-1">
        <ChangeTag value={coin.change_24h_pct} />
        <span className="text-[10px] text-[var(--text-muted)]">24h</span>
      </div>
      {chartData.length > 0 && (
        <div className="mt-3">
          <SparklineChart data={chartData} color={color} height={50} />
          <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-1">
            <span>{chartData[0]?.date}</span>
            <span>YoY: {coin.yoy_change_pct >= 0 ? "+" : ""}{coin.yoy_change_pct}%</span>
            <span>{chartData[chartData.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function FXCard({ pair }: { pair: FXData }) {
  if (pair.error) return null;

  const chartData = pair.history?.map((h) => ({ date: h.date, value: h.rate })) || [];
  const color = COLORS[pair.name] || "#888";

  return (
    <div className="bg-[var(--bg-secondary)] rounded-lg p-4">
      <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{pair.name}</p>
      <p className="text-xl font-semibold mt-1">{pair.current_rate?.toFixed(4)}</p>
      <div className="flex items-center gap-2 mt-1">
        <ChangeTag value={pair.change_pct} />
        <span className="text-[10px] text-[var(--text-muted)]">1d</span>
      </div>
      {chartData.length > 0 && (
        <div className="mt-3">
          <SparklineChart data={chartData} color={color} height={50} />
          <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-1">
            <span>{chartData[0]?.date}</span>
            <span>YoY: {pair.yoy_change_pct >= 0 ? "+" : ""}{pair.yoy_change_pct}%</span>
            <span>{chartData[chartData.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Charts({ crypto, fx }: Props) {
  return (
    <div className="space-y-6">
      {crypto && crypto.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)] mb-3">Crypto</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {crypto.map((coin) => (
              <CryptoCard key={coin.coin_id} coin={coin} />
            ))}
          </div>
        </div>
      )}

      {fx && fx.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)] mb-3">FX rates</h3>
          <div className="space-y-3">
            {fx.map((pair) => (
              <FXCard key={pair.ticker} pair={pair} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
