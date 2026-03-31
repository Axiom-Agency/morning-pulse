"use client";

const briefings = [
  { id: "7am", label: "7 AM", desc: "Pre-market" },
  { id: "8am", label: "8 AM", desc: "Full briefing" },
  { id: "5pm", label: "5 PM", desc: "ASX close" },
];

interface Props {
  selected: string;
  onSelect: (type: string) => void;
}

export default function BriefingSelector({ selected, onSelect }: Props) {
  return (
    <div className="flex gap-2">
      {briefings.map((b) => (
        <button
          key={b.id}
          onClick={() => onSelect(b.id)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selected === b.id
              ? "bg-[var(--text-primary)] text-[var(--bg-primary)]"
              : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          }`}
        >
          {b.label}
          <span className="hidden sm:inline text-xs ml-1 opacity-60">{b.desc}</span>
        </button>
      ))}
    </div>
  );
}
