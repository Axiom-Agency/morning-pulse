"use client";

import { LineChart, Line, ResponsiveContainer } from "recharts";

interface SparklineProps {
  data: { date: string; value: number }[];
  color: string;
  height?: number;
}

export default function SparklineChart({ data, color, height = 60 }: SparklineProps) {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
