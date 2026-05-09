"use client";

import type { DashboardSummary } from "@/lib/types";

type Entry = DashboardSummary["mastery"][number];

function bucketClass(pct: number): string {
  if (pct >= 70) return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (pct >= 40) return "bg-achiever-50 text-achiever-700 border-achiever-200";
  return "bg-red-50 text-red-700 border-red-200";
}

export function MasteryHeatmap({ entries }: { entries: Entry[] }) {
  if (entries.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Complete a test and we&rsquo;ll show your strongest and weakest topics here.
      </p>
    );
  }

  const bySubject = entries.reduce<Record<string, Entry[]>>((acc, e) => {
    (acc[e.subject] ??= []).push(e);
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      {Object.entries(bySubject).map(([subject, topics]) => {
        const sorted = [...topics].sort((a, b) => a.masteryScore - b.masteryScore);
        return (
          <div key={subject}>
            <h3 className="text-sm font-semibold text-slate-700">{subject}</h3>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {sorted.map((t) => {
                const pct = Math.round(t.masteryScore);
                return (
                  <span
                    key={t.topic}
                    title={`Last updated ${new Date(t.lastUpdated).toLocaleString()}`}
                    className={`rounded-full border px-3 py-1 text-xs font-medium ${bucketClass(pct)}`}
                  >
                    {t.topic} · {pct}%
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
        <Legend className={bucketClass(80)} label="Strong (≥70%)" />
        <Legend className={bucketClass(50)} label="Improving (40-69%)" />
        <Legend className={bucketClass(20)} label="Weak (&lt;40%)" />
      </div>
    </div>
  );
}

function Legend({ className, label }: { className: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`inline-block h-2.5 w-2.5 rounded-sm border ${className}`} />
      {label}
    </span>
  );
}
