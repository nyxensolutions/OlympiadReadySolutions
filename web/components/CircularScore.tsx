"use client";

export function CircularScore({
  score,
  total,
  size = 140
}: {
  score: number;
  total: number;
  size?: number;
}) {
  const pct = total === 0 ? 0 : Math.round((score / total) * 100);
  const stroke = 12;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = (pct / 100) * c;

  // Brand blue >= 70, Amber 40-69, Red < 40
  const color = pct >= 70 ? "#2563eb" : pct >= 40 ? "#f59e0b" : "#dc2626";

  return (
    <div className="flex items-center gap-4">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke="#e2e8f0"
          strokeWidth={stroke}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={`${dash} ${c}`}
          strokeLinecap="round"
        />
      </svg>
      <div>
        <p className="text-3xl font-bold text-slate-900">
          {score}
          <span className="text-base font-medium text-slate-500"> / {total}</span>
        </p>
        <p className="text-sm font-semibold" style={{ color }}>
          {pct}%
        </p>
      </div>
    </div>
  );
}
