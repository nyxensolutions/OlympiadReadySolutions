"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Flame, Loader2, Sparkles, Trophy } from "lucide-react";
import { useAuth, SignedIn, SignedOut } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { MasteryHeatmap } from "@/components/MasteryHeatmap";
import { RecentPapersCard } from "@/components/RecentPapersCard";
import { ScoreTrendChart } from "@/components/ScoreTrendChart";
import { SubscriptionBadge } from "@/components/SubscriptionBadge";
import type { DashboardSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

function computeStreak(results: DashboardSummary["results"]): number {
  if (results.length === 0) return 0;
  const dates = [
    ...new Set(results.map((r) => r.completedAt.split("T")[0]))
  ].sort().reverse();
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().split("T")[0];
  if (dates[0] !== today && dates[0] !== yesterday) return 0;
  let streak = 1;
  for (let i = 1; i < dates.length; i++) {
    const diff =
      (new Date(dates[i - 1]).getTime() - new Date(dates[i]).getTime()) / 86_400_000;
    if (diff === 1) streak++;
    else break;
  }
  return streak;
}

type Badge = {
  id: string;
  emoji: string;
  label: string;
  description: string;
  earned: boolean;
};

function computeBadges(data: DashboardSummary): Badge[] {
  const { results } = data;
  const streak = computeStreak(results);
  const bestPct =
    results.length === 0
      ? 0
      : Math.max(
          ...results.map((r) =>
            r.totalQuestions > 0 ? (r.score / r.totalQuestions) * 100 : 0
          )
        );

  return [
    {
      id: "first_test",
      emoji: "🚀",
      label: "First Step",
      description: "Complete your first practice test",
      earned: results.length >= 1,
    },
    {
      id: "five_tests",
      emoji: "🔁",
      label: "On a Roll",
      description: "Complete 5 practice tests",
      earned: results.length >= 5,
    },
    {
      id: "ten_tests",
      emoji: "💪",
      label: "Dedicated",
      description: "Complete 10 practice tests",
      earned: results.length >= 10,
    },
    {
      id: "sharpshooter",
      emoji: "🎯",
      label: "Sharpshooter",
      description: "Score 90% or above in any test",
      earned: bestPct >= 90,
    },
    {
      id: "perfect",
      emoji: "⭐",
      label: "Perfect Score",
      description: "Get every question right in a test",
      earned: results.some((r) => r.score === r.totalQuestions && r.totalQuestions > 0),
    },
    {
      id: "streak_3",
      emoji: "🔥",
      label: "3-Day Streak",
      description: "Practice 3 days in a row",
      earned: streak >= 3,
    },
    {
      id: "streak_7",
      emoji: "🏅",
      label: "Week Warrior",
      description: "Practice every day for a week",
      earned: streak >= 7,
    },
    {
      id: "speed",
      emoji: "⚡",
      label: "Speed Demon",
      description: "Finish a 10-question test in under 5 minutes",
      earned: results.some((r) => r.totalQuestions >= 10 && r.timeTakenSeconds < 300),
    },
  ];
}

export default function DashboardPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-10 sm:py-16">
      <AppHeader active="dashboard" />
      <SignedOut>
        <SignedOutPrompt />
      </SignedOut>
      <SignedIn>
        <DashboardBody />
      </SignedIn>
    </main>
  );
}

function SignedOutPrompt() {
  return (
    <section className="mt-20 flex flex-col items-center text-center">
      <h1 className="text-2xl font-bold text-slate-900">Sign in to view your dashboard</h1>
      <p className="mt-2 max-w-md text-sm text-slate-600">
        Your test history, score trend, and topic-wise mastery are tied to your account.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-1 text-sm font-semibold text-brand-700 hover:text-brand-600"
      >
        Go to home <ArrowRight className="h-4 w-4" />
      </Link>
    </section>
  );
}

function DashboardBody() {
  const { getToken, isLoaded } = useAuth();
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoaded) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/dashboard/summary`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        if (!res.ok) throw new Error(`Failed to load dashboard (${res.status})`);
        const summary: DashboardSummary = await res.json();
        if (!cancelled) setData(summary);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [getToken, isLoaded]);

  if (loading) {
    return (
      <div className="mt-20 flex items-center justify-center gap-2 text-sm text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading your dashboard…
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-10 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
        {error}
      </div>
    );
  }

  if (!data) return null;

  const lastResult = data.results[0];
  const streak = computeStreak(data.results);
  const badges = computeBadges(data);
  const earnedCount = badges.filter((b) => b.earned).length;
  const avg =
    data.results.length === 0
      ? 0
      : Math.round(
          data.results.reduce(
            (a, r) => a + (r.totalQuestions === 0 ? 0 : (r.score * 100) / r.totalQuestions),
            0
          ) / data.results.length
        );

  return (
    <>
      <section className="mt-8 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Your dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Track progress, spot weak topics, and pick up where you left off.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SubscriptionBadge
            status={{
              tier: data.subscription.tier,
              used: data.subscription.used,
              limit: data.subscription.limit,
              allowed: data.subscription.used < data.subscription.limit
            }}
          />
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-brand-700"
          >
            <Sparkles className="h-4 w-4" />
            New paper
          </Link>
        </div>
      </section>

      {/* Streak banner — shown only when active */}
      {streak >= 1 && (
        <div className="mt-4 flex items-center gap-3 rounded-2xl border border-orange-200 bg-orange-50 px-5 py-3">
          <Flame className="h-6 w-6 text-orange-500" />
          <div>
            <p className="text-sm font-bold text-orange-800">
              {streak}-day streak! Keep it up 🔥
            </p>
            <p className="text-xs text-orange-600">
              {streak >= 7
                ? "You're on fire — a whole week of consistent practice!"
                : "Practice again tomorrow to extend your streak."}
            </p>
          </div>
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Tests taken" value={String(data.results.length)} />
        <Stat
          label="Average score"
          value={data.results.length === 0 ? "—" : `${avg}%`}
        />
        <Stat
          label="Practice streak"
          value={streak === 0 ? "—" : `${streak} day${streak === 1 ? "" : "s"}`}
          sub={streak >= 1 ? "consecutive days" : "Start today!"}
          accent="text-orange-500"
        />
        <Stat
          label="Badges earned"
          value={`${earnedCount} / ${badges.length}`}
          sub="See below"
        />
      </div>

      {/* Achievements */}
      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-amber-500" />
          <h2 className="text-lg font-semibold text-slate-900">Achievements</h2>
          <span className="ml-auto text-xs text-slate-400">
            {earnedCount} of {badges.length} earned
          </span>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {badges.map((badge) => (
            <div
              key={badge.id}
              title={badge.description}
              className={`flex flex-col items-center gap-1.5 rounded-xl border p-4 text-center transition ${
                badge.earned
                  ? "border-amber-200 bg-amber-50"
                  : "border-slate-100 bg-slate-50 opacity-40 grayscale"
              }`}
            >
              <span className="text-2xl">{badge.emoji}</span>
              <p className={`text-xs font-bold ${badge.earned ? "text-amber-800" : "text-slate-500"}`}>
                {badge.label}
              </p>
              <p className="text-[10px] leading-tight text-slate-400">{badge.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Score trend</h2>
          <span className="text-xs text-slate-500">
            Last {data.results.length} test{data.results.length === 1 ? "" : "s"}
          </span>
        </div>
        <div className="mt-4">
          <ScoreTrendChart results={data.results} />
        </div>
      </section>

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Topic mastery</h2>
        <p className="mt-1 text-xs text-slate-500">
          Updated after every test. Shows your most recent score per topic.
        </p>
        <div className="mt-4">
          <MasteryHeatmap entries={data.mastery} />
        </div>
      </section>

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Recent papers</h2>
        <div className="mt-3">
          <RecentPapersCard papers={data.papers} />
        </div>
      </section>
    </>
  );
}

function Stat({
  label,
  value,
  sub,
  accent
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${accent ?? "text-slate-900"}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}
