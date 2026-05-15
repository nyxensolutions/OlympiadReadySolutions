"use client";

import { Trophy } from "lucide-react";
import { LeaderboardCard } from "@/components/LeaderboardCard";

export function LandingLeaderboard() {
  return (
    <section className="bg-slate-50 py-16">
      <div className="mx-auto max-w-2xl px-4">
        <div className="mb-8 text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-1.5 text-sm font-semibold text-amber-700">
            <Trophy className="h-4 w-4 text-amber-500" />
            Monthly Top Scorers
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">
            Who's leading this month?
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            🥇 Gold ≥ 90% · 🥈 Silver ≥ 75% · 🥉 Bronze ≥ 60%
          </p>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-6 py-4">
            <p className="text-xs text-slate-400">Best single-test score in the last 30 days</p>
          </div>
          <LeaderboardCard compact />
        </div>

        <p className="mt-4 text-center text-xs text-slate-400">
          Sign in and complete a test to appear on the leaderboard.
        </p>
      </div>
    </section>
  );
}
