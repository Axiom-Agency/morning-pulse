import { BriefingData } from "./types";

const GITHUB_RAW =
  "https://raw.githubusercontent.com/Axiom-Agency/morning-pulse/main/data";

export async function fetchBriefing(type: string): Promise<BriefingData> {
  // Try GitHub first (always up-to-date), fall back to local static file
  try {
    const res = await fetch(`${GITHUB_RAW}/latest-${type}.json`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (res.ok) return res.json();
  } catch (_) {}

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
