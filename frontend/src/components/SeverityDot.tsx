"use client";

const colors = {
  high: "#E24B4A",
  medium: "#EF9F27",
  low: "#1D9E75",
};

export default function SeverityDot({ severity }: { severity: "high" | "medium" | "low" }) {
  return (
    <span
      className="inline-block w-2.5 h-2.5 rounded-full shrink-0 mt-1.5"
      style={{ backgroundColor: colors[severity] }}
      title={severity}
    />
  );
}
