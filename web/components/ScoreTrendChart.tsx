"use client";

import type { DashboardSummary } from "@/lib/types";

type Result = DashboardSummary["results"][number];

export function ScoreTrendChart({ results }: { results: Result[] }) {
  if (results.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No tests submitted yet. Take a test to see your score trend.
      </p>
    );
  }

  // API returns most-recent first; show oldest → newest left to right.
  const series = [...results].reverse().map((r) => ({
    pct: r.totalQuestions === 0 ? 0 : Math.round((r.score * 100) / r.totalQuestions),
    when: r.completedAt
  }));

  const W = 600;
  const H = 160;
  const padX = 36;
  const padY = 16;
  const innerW = W - 2 * padX;
  const innerH = H - 2 * padY;

  const xs = series.map((_, i) =>
    series.length === 1 ? padX + innerW / 2 : padX + (i * innerW) / (series.length - 1)
  );
  const ys = series.map((p) => padY + ((100 - p.pct) * innerH) / 100);

  const path = xs.map((x, i) => `${i === 0 ? "M" : "L"}${x},${ys[i]}`).join(" ");
  const areaPath =
    `M${xs[0]},${padY + innerH} ` +
    xs.map((x, i) => `L${x},${ys[i]}`).join(" ") +
    ` L${xs[xs.length - 1]},${padY + innerH} Z`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Score trend">
      {[0, 50, 100].map((g) => {
        const y = padY + ((100 - g) * innerH) / 100;
        return (
          <g key={g}>
            <line
              x1={padX}
              y1={y}
              x2={W - padX / 2}
              y2={y}
              stroke="#e2e8f0"
              strokeDasharray="3 3"
            />
            <text x={padX - 6} y={y + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
              {g}%
            </text>
          </g>
        );
      })}
      <path d={areaPath} fill="#2563eb" fillOpacity="0.08" />
      <path d={path} stroke="#2563eb" strokeWidth="2" fill="none" />
      {xs.map((x, i) => (
        <circle key={i} cx={x} cy={ys[i]} r="3.5" fill="#2563eb">
          <title>
            {series[i].pct}% · {new Date(series[i].when).toLocaleString()}
          </title>
        </circle>
      ))}
    </svg>
  );
}
