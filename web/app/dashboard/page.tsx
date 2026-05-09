"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Loader2, Sparkles } from "lucide-react";
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

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Stat label="Tests taken" value={String(data.results.length)} />
        <Stat
          label="Average score"
          value={data.results.length === 0 ? "—" : `${avg}%`}
        />
        <Stat
          label="Last test"
          value={
            lastResult
              ? `${lastResult.score}/${lastResult.totalQuestions} · ${formatDuration(
                  lastResult.timeTakenSeconds
                )}`
              : "—"
          }
          sub={lastResult ? new Date(lastResult.completedAt).toLocaleString() : undefined}
        />
      </div>

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
  sub
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}
