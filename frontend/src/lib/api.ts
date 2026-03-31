import { BriefingData } from "./types";

export async function fetchBriefing(type: string): Promise<BriefingData> {
  const res = await fetch(`/data/latest-${type}.json`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch ${type} briefing`);
  return res.json();
}

export async function deepDive(
  context: string,
  question: string,
  history: { role: string; parts: { text: string }[] }[] = []
): Promise<ReadableStream<Uint8Array>> {
  const res = await fetch("/api/deep-dive", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context, question, history }),
  });
  if (!res.ok) throw new Error("Deep dive request failed");
  return res.body!;
}
