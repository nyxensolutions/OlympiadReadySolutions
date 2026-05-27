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

const TITLE_STYLES: Record<string, string> = {
  "Olympiad Legend":    "text-purple-700 bg-purple-50 ring-purple-200",
  "Champion Scholar":   "text-indigo-700 bg-indigo-50 ring-indigo-200",
  "Olympiad Contender": "text-blue-700   bg-blue-50   ring-blue-200",
  "Knowledge Seeker":   "text-teal-700   bg-teal-50   ring-teal-200",
  "Rising Star":        "text-amber-700  bg-amber-50  ring-amber-200",
  "Rookie Scholar":     "text-slate-600  bg-slate-50  ring-slate-200",
};

// Emoji for each badge id — kept in sync with dashboard
const BADGE_EMOJI: Record<string, string> = {
  first_test: "🚀", five_tests: "🔁", ten_tests: "💪", twenty_five_tests: "🎓", century: "💯",
  sharpshooter: "🎯", perfect: "⭐", on_fire: "🔴", comeback: "📈",
  streak_3: "🔥", streak_7: "🏅", streak_30: "🗓️",
  speed: "⚡", lightning: "🌩️",
  explorer: "🌍", all_rounder: "🌟",
  mock_exam: "📋", mock_3: "🏆",
};

interface ExtendedEntry extends LeaderboardEntry {
  title?: string;
  badgeCount?: number;
  earnedBadgeIds?: string[];
}

export function LeaderboardCard({ compact = false }: { compact?: boolean }) {
  const [entries, setEntries] = useState<ExtendedEntry[]>([]);
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
        const titleStyle = TITLE_STYLES[entry.title ?? ""] ?? "text-slate-500 bg-slate-50 ring-slate-200";
        const badgeIcons = (entry.earnedBadgeIds ?? []).slice(0, compact ? 6 : 18);

        return (
          <div key={entry.rank} className={`flex items-center gap-3 px-4 py-3 transition ${m.bg}`}>
            {/* Rank */}
            <span className={`w-6 shrink-0 text-center text-sm ${rankStyle}`}>
              {entry.rank <= 3 ? m.label : `#${entry.rank}`}
            </span>

            {/* Avatar */}
            <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ring-2 ${m.ring} bg-white text-sm font-bold ${m.text}`}>
              {entry.displayName[0]?.toUpperCase() ?? "?"}
            </div>

            {/* Name + title + badge icons */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-semibold text-slate-800 truncate">
                  {entry.displayName}
                </span>
                {entry.title && entry.title !== "Newcomer" && (
                  <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ring-1 shrink-0 ${titleStyle}`}>
                    {entry.title}
                  </span>
                )}
              </div>
              {badgeIcons.length > 0 && (
                <div className="flex flex-wrap gap-0.5 mt-1">
                  {badgeIcons.map((id) => (
                    <span key={id} className="text-[11px]" title={id.replace(/_/g, " ")}>
                      {BADGE_EMOJI[id] ?? "🏅"}
                    </span>
                  ))}
                  {(entry.earnedBadgeIds?.length ?? 0) > (compact ? 6 : 18) && (
                    <span className="text-[9px] text-slate-400 self-center">
                      +{(entry.earnedBadgeIds?.length ?? 0) - (compact ? 6 : 18)}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Score */}
            <div className="flex items-center gap-1.5 shrink-0">
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ring-1 ${m.ring} ${m.bg} ${m.text}`}>
                {entry.bestScorePct}%
              </span>
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
