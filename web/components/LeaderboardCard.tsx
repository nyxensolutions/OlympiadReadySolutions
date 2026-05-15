"use client";

import { useEffect, useState } from "react";
import { Trophy, Loader2 } from "lucide-react";
import type { LeaderboardEntry } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

const MEDAL_STYLES: Record<string, { bg: string; text: string; ring: string; label: string }> = {
  Gold:   { bg: "bg-amber-50",   text: "text-amber-700",  ring: "ring-amber-300",  label: "🥇" },
  Silver: { bg: "bg-slate-50",   text: "text-slate-600",  ring: "ring-slate-300",  label: "🥈" },
  Bronze: { bg: "bg-orange-50",  text: "text-orange-700", ring: "ring-orange-300", label: "🥉" },
  None:   { bg: "bg-white",      text: "text-slate-500",  ring: "ring-slate-200",  label: ""   },
};

const RANK_STYLES: Record<number, string> = {
  1: "text-amber-600 font-black",
  2: "text-slate-500 font-bold",
  3: "text-orange-600 font-bold",
};

export function LeaderboardCard({ compact = false }: { compact?: boolean }) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/api/leaderboard`)
      .then((r) => r.ok ? r.json() : [])
      .then(setEntries)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading leaderboard…
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="py-10 text-center text-sm text-slate-400">
        No scores yet this month. Be the first on the board!
      </div>
    );
  }

  const rows = compact ? entries.slice(0, 5) : entries;

  return (
    <div className="divide-y divide-slate-100">
      {rows.map((entry) => {
        const m = MEDAL_STYLES[entry.medal] ?? MEDAL_STYLES.None;
        const rankStyle = RANK_STYLES[entry.rank] ?? "text-slate-400 font-semibold";
        return (
          <div
            key={entry.rank}
            className={`flex items-center gap-4 px-4 py-3 transition ${m.bg}`}
          >
            {/* Rank */}
            <span className={`w-6 shrink-0 text-center text-sm ${rankStyle}`}>
              {entry.rank <= 3 ? m.label : `#${entry.rank}`}
            </span>

            {/* Avatar placeholder */}
            <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ring-2 ${m.ring} bg-white text-sm font-bold ${m.text}`}>
              {entry.displayName[0]?.toUpperCase() ?? "?"}
            </div>

            {/* Name */}
            <span className="min-w-0 flex-1 truncate text-sm font-medium text-slate-800">
              {entry.displayName}
            </span>

            {/* Score + medal */}
            <div className="flex items-center gap-2 shrink-0">
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ring-1 ${m.ring} ${m.bg} ${m.text}`}>
                {entry.bestScorePct}%
              </span>
              {entry.medal !== "None" && (
                <span className={`hidden rounded-full px-2 py-0.5 text-[10px] font-semibold sm:inline ${m.bg} ${m.text}`}>
                  {entry.medal}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function LeaderboardSection() {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 px-6 py-4">
        <Trophy className="h-5 w-5 text-amber-500" />
        <h2 className="text-lg font-semibold text-slate-900">Top Scorers</h2>
        <span className="ml-auto text-xs text-slate-400">Last 30 days</span>
      </div>
      <LeaderboardCard />
    </section>
  );
}
