"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { BarChart2, GraduationCap, Loader2, Lock } from "lucide-react";
import { MasteryHeatmap } from "@/components/MasteryHeatmap";
import { ScoreTrendChart } from "@/components/ScoreTrendChart";
import { RecentPapersCard } from "@/components/RecentPapersCard";
import type { DashboardSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export default function ParentDashboardPage() {
  const params = useParams<{ token: string }>();
  const token = params?.token ?? "";

  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/share/${token}/summary`);
        if (res.status === 401) { setError("This link has expired or is invalid."); return; }
        if (!res.ok) { setError("Failed to load dashboard."); return; }
        setData(await res.json());
      } catch { setError("Failed to load dashboard."); }
      finally { setLoading(false); }
    })();
  }, [token]);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Minimal header — no nav, just brand */}
      <header className="sticky top-0 z-50 border-b border-slate-200/50 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-brand-600" />
            <span className="text-lg font-bold tracking-tight text-slate-900">OlympiadReady</span>
          </div>
          <span className="flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            <Lock className="h-3 w-3" /> Parent view · read-only
          </span>
        </div>
      </header>

      {/* Page banner */}
      <div className="bg-gradient-hero px-4 py-10 text-white">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">Parent Dashboard</p>
          <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">Student progress overview</h1>
          <p className="mt-2 max-w-xl text-sm text-brand-200">
            Read-only view shared by your child. Track their test history, topic mastery, and consistency.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        {loading && (
          <div className="flex items-center justify-center gap-2 py-20 text-sm text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="font-semibold text-red-800">{error}</p>
            <p className="mt-1 text-sm text-red-600">Ask your child to generate a fresh share link from their dashboard.</p>
          </div>
        )}

        {data && <ParentBody data={data} />}
      </div>
    </div>
  );
}

function ParentBody({ data }: { data: DashboardSummary }) {
  const results = data.results;
  const tests = results.length;
  const avg = tests === 0 ? 0 : Math.round(
    results.reduce((a, r) => a + (r.totalQuestions > 0 ? (r.score / r.totalQuestions) * 100 : 0), 0) / tests
  );

  // Streak computation
  const dates = [...new Set(results.map((r) => r.completedAt.split("T")[0]))].sort().reverse();
  const today = new Date().toISOString().split("T")[0];
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().split("T")[0];
  let streak = 0;
  if (dates.length > 0 && (dates[0] === today || dates[0] === yesterday)) {
    streak = 1;
    for (let i = 1; i < dates.length; i++) {
      const diff = (new Date(dates[i - 1]).getTime() - new Date(dates[i]).getTime()) / 86_400_000;
      if (diff === 1) streak++; else break;
    }
  }

  const subjectsTried = new Set(results.map((r) => r.subject)).size;
  const bestScore = tests === 0 ? 0 : Math.max(...results.map((r) =>
    r.totalQuestions > 0 ? Math.round((r.score / r.totalQuestions) * 100) : 0
  ));

  const statCards = [
    { label: "Tests completed", value: String(tests), color: "from-brand-600 to-accent-600" },
    { label: "Average score", value: tests === 0 ? "—" : `${avg}%`, color: "from-accent-600 to-brand-600" },
    { label: "Best score ever", value: tests === 0 ? "—" : `${bestScore}%`, color: "from-emerald-500 to-brand-600" },
    { label: "Practice streak", value: streak === 0 ? "—" : `${streak} day${streak === 1 ? "" : "s"}`, color: "from-cta-600 to-amber-500" },
    { label: "Subjects tried", value: String(subjectsTried), color: "from-violet-500 to-accent-600" },
    { label: "Subscription", value: data.subscription.tier, color: "from-slate-400 to-slate-600" },
  ];

  return (
    <>
      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((s) => (
          <div key={s.label} className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className={`absolute left-0 right-0 top-0 h-1 bg-gradient-to-r ${s.color}`} />
            <p className="text-xs uppercase tracking-wide text-slate-500">{s.label}</p>
            <p className="mt-1 text-2xl font-bold text-slate-900">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Weekly summary */}
      {tests > 0 && (
        <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center gap-2 border-b border-slate-100 px-6 py-4">
            <BarChart2 className="h-5 w-5 text-brand-600" />
            <h2 className="text-lg font-semibold text-slate-900">Score Trend</h2>
          </div>
          <div className="p-6">
            <ScoreTrendChart results={results} />
          </div>
        </section>
      )}

      {/* Topic mastery */}
      {data.mastery.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Topic Mastery</h2>
          <p className="mt-1 text-xs text-slate-500">Most recent score per topic across all subjects.</p>
          <div className="mt-4">
            <MasteryHeatmap entries={data.mastery} />
          </div>
        </section>
      )}

      {/* Recent papers */}
      {data.papers.length > 0 && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Recent Papers</h2>
          <div className="mt-3">
            <RecentPapersCard papers={data.papers} />
          </div>
        </section>
      )}

      <p className="text-center text-xs text-slate-400">
        This is a read-only view. Scores update when your child completes a test.
      </p>
    </>
  );
}
