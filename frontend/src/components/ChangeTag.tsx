"use client";

export default function ChangeTag({ value, size = "sm" }: { value: number; size?: "sm" | "lg" }) {
  const isPositive = value >= 0;
  const bg = isPositive ? "bg-[#1D9E75]" : "bg-[#E24B4A]";
  const textSize = size === "lg" ? "text-sm" : "text-xs";

  return (
    <span className={`${bg} text-white ${textSize} font-medium px-2 py-0.5 rounded-full inline-block`}>
      {isPositive ? "+" : ""}{value.toFixed(2)}%
    </span>
  );
}
