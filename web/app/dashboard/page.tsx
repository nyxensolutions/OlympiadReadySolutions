"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Flame, Lock, Loader2, Shield, Sparkles, Trophy } from "lucide-react";
import { useAuth, SignedIn, SignedOut } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { MasteryHeatmap } from "@/components/MasteryHeatmap";
import { RecentPapersCard } from "@/components/RecentPapersCard";
import { ScoreTrendChart } from "@/components/ScoreTrendChart";
import { SubscriptionBadge } from "@/components/SubscriptionBadge";
import type { DashboardSummary } from "@/lib/types";
import { getShieldState, useShield as consumeShield } from "@/lib/streakShield";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function computeStreak(
  results: DashboardSummary["results"],
  shieldedDates: string[] = []
): number {
  if (results.length === 0 && shieldedDates.length === 0) return 0;
  const practicedDates = new Set(results.map((r) => r.completedAt.split("T")[0]));
  shieldedDates.forEach((d) => practicedDates.add(d));
  const dates = [...practicedDates].sort().reverse();
  if (dates.length === 0) return 0;
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
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="dashboard" />
      <SignedOut>
        <SignedOutPrompt />
      </SignedOut>
      <SignedIn>
        <DashboardBody />
      </SignedIn>
    </div>
  );
}

function SignedOutPrompt() {
  return (
    <section className="flex flex-col items-center py-32 text-center">
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
  const [shieldState, setShieldState] = useState<{ shields: number; usedDates: string[] }>({
    shields: 0,
    usedDates: [],
  });

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
        if (!cancelled) {
          setData(summary);
          const tier = summary.subscription.tier as "Free" | "Pro";
          const ss = getShieldState(tier);
          setShieldState({ shields: ss.shields, usedDates: ss.usedDates });
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [getToken, isLoaded]);

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-40 text-sm text-slate-500">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading your dashboard…
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      </div>
    );
  }

  if (!data) return null;

  const streak = computeStreak(data.results, shieldState.usedDates);
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
      {/* Gradient page banner */}
      <div className="bg-gradient-brand px-4 py-10 text-white">
        <div className="mx-auto max-w-6xl flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">
              Dashboard
            </p>
            <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">
              Your progress at a glance
            </h1>
            <p className="mt-2 max-w-xl text-sm text-brand-200">
              Track scores, spot weak topics, and keep your streak alive.
            </p>
          </div>
          <div className="flex items-center gap-3">
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
              className="inline-flex items-center gap-1.5 rounded-xl bg-cta-600 px-4 py-2.5 text-sm font-bold text-white shadow-md shadow-cta-600/30 transition hover:bg-cta-700"
            >
              <Sparkles className="h-4 w-4" />
              New paper
            </Link>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">

        {/* Streak banner */}
        {streak >= 1 ? (
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-orange-200 bg-orange-50 px-5 py-4">
            <Flame className="h-6 w-6 shrink-0 text-orange-500" />
            <div className="flex-1">
              <p className="text-sm font-bold text-orange-800">
                {streak}-day streak! Keep it up 🔥
              </p>
              <p className="text-xs text-orange-600">
                {streak >= 7
                  ? "You're on fire — a whole week of consistent practice!"
                  : "Practice again tomorrow to extend your streak."}
              </p>
            </div>
            {data.subscription.tier === "Pro" && shieldState.shields > 0 && (
              <div className="flex items-center gap-1.5 rounded-xl bg-indigo-100 px-3 py-1.5 text-xs font-semibold text-indigo-700">
                <Shield className="h-3.5 w-3.5" />
                {shieldState.shields} shield{shieldState.shields === 1 ? "" : "s"} left this month
              </div>
            )}
          </div>
        ) : (
          /* Streak broken — show shield option for Pro */
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
            <Flame className="h-6 w-6 shrink-0 text-slate-300" />
            <div className="flex-1">
              <p className="text-sm font-bold text-slate-700">No active streak</p>
              <p className="text-xs text-slate-500">
                {data.subscription.tier === "Pro" && shieldState.shields > 0
                  ? "Use a streak shield to protect yesterday's progress, or practise today to start a new streak."
                  : "Practise today to start building your streak!"}
              </p>
            </div>
            {data.subscription.tier === "Pro" && shieldState.shields > 0 && (
              <button
                type="button"
                onClick={() => {
                  const ok = consumeShield(data.subscription.tier as "Free" | "Pro");
                  if (ok) {
                    const updated = getShieldState(data.subscription.tier as "Free" | "Pro");
                    setShieldState({ shields: updated.shields, usedDates: updated.usedDates });
                  }
                }}
                className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-brand-700"
              >
                <Shield className="h-3.5 w-3.5" />
                Use shield ({shieldState.shields} left)
              </button>
            )}
            {data.subscription.tier === "Free" && (
              <div className="rounded-xl border border-brand-200 bg-brand-50 px-3 py-2 text-xs text-brand-700">
                <span className="font-bold">Pro</span> users get 2 streak shields/month.
              </div>
            )}
          </div>
        )}

        {/* Stat cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Tests taken" value={String(data.results.length)} gradient="from-brand-600 to-accent-600" />
          <Stat
            label="Average score"
            value={data.results.length === 0 ? "—" : `${avg}%`}
            gradient="from-accent-600 to-brand-600"
          />
          <Stat
            label="Practice streak"
            value={streak === 0 ? "—" : `${streak} day${streak === 1 ? "" : "s"}`}
            sub={streak >= 1 ? "consecutive days" : "Start today!"}
            accent="text-orange-500"
            gradient="from-cta-600 to-amber-500"
          />
          <Stat
            label="Badges earned"
            value={`${earnedCount} / ${badges.length}`}
            sub="See below"
            gradient="from-amber-500 to-cta-600"
          />
        </div>

        {/* Achievements */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
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
                className={`relative flex flex-col items-center gap-1.5 rounded-xl border p-4 text-center transition ${
                  badge.earned
                    ? "border-amber-200 bg-gradient-to-b from-amber-50 to-white shadow-sm"
                    : "border-slate-200 bg-white"
                }`}
              >
                {!badge.earned && (
                  <span className="absolute right-2 top-2 rounded-full bg-slate-100 p-0.5">
                    <Lock className="h-3 w-3 text-slate-400" />
                  </span>
                )}
                <span className={`text-2xl ${badge.earned ? "" : "grayscale opacity-50"}`}>
                  {badge.emoji}
                </span>
                <p className={`text-xs font-bold ${badge.earned ? "text-amber-800" : "text-slate-500"}`}>
                  {badge.label}
                </p>
                <p className={`text-[10px] leading-tight ${badge.earned ? "text-amber-600" : "text-slate-400"}`}>
                  {badge.description}
                </p>
                {badge.earned && (
                  <span className="mt-0.5 rounded-full bg-amber-200 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wide text-amber-800">
                    Earned
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Score trend */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
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

        {/* Topic mastery */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Topic mastery</h2>
          <p className="mt-1 text-xs text-slate-500">
            Updated after every test. Shows your most recent score per topic.
          </p>
          <div className="mt-4">
            <MasteryHeatmap entries={data.mastery} />
          </div>
        </section>

        {/* Recent papers */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Recent papers</h2>
          <div className="mt-3">
            <RecentPapersCard papers={data.papers} />
          </div>
        </section>

      </div>
    </>
  );
}

function Stat({
  label,
  value,
  sub,
  accent,
  gradient,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
  gradient?: string;
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      {gradient && (
        <div className={`absolute left-0 right-0 top-0 h-1 bg-gradient-to-r ${gradient}`} />
      )}
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${accent ?? "text-slate-900"}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}
