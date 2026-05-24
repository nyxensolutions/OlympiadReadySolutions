"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Calendar, Crown, Lock, Sparkles, Timer, Trophy } from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import type { DashboardSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function getWeekLabel(): string {
  const now = new Date();
  const start = new Date(now);
  start.setDate(now.getDate() - now.getDay() + 1); // Monday
  const end = new Date(start);
  end.setDate(start.getDate() + 6); // Sunday
  const fmt = (d: Date) =>
    d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  return `${fmt(start)} – ${fmt(end)}`;
}

function getCountdownToSunday(): string {
  const now = new Date();
  const sunday = new Date(now);
  sunday.setDate(now.getDate() + (7 - now.getDay()) % 7 || 7);
  sunday.setHours(23, 59, 59, 999);
  const diff = sunday.getTime() - now.getTime();
  const h = Math.floor(diff / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  return `${h}h ${m}m`;
}

const PRIZES = [
  { rank: "1st", prize: "Gold Medal + Certificate", color: "from-amber-400 to-yellow-300", icon: "🥇" },
  { rank: "2nd", prize: "Silver Medal + Certificate", color: "from-slate-400 to-slate-300", icon: "🥈" },
  { rank: "3rd", prize: "Bronze Medal + Certificate", color: "from-orange-400 to-amber-300", icon: "🥉" },
  { rank: "Top 10", prize: "Participation Certificate", color: "from-brand-400 to-accent-400", icon: "🎖️" },
];

export default function WeeklyExamPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="weekly-exam" />
      <SignedOut>
        <UnauthPrompt />
      </SignedOut>
      <SignedIn>
        <WeeklyExamBody />
      </SignedIn>
    </div>
  );
}

function UnauthPrompt() {
  return (
    <div className="flex flex-col items-center py-32 text-center px-4">
      <Crown className="h-12 w-12 text-amber-400" />
      <h1 className="mt-4 text-2xl font-bold text-slate-900">Weekly Exam</h1>
      <p className="mt-2 max-w-sm text-sm text-slate-500">
        Sign in to participate in this week's competitive exam and win medals and certificates.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-brand-600/20 transition hover:bg-brand-700"
      >
        <Sparkles className="h-4 w-4" />
        Sign in to participate
      </Link>
    </div>
  );
}

function WeeklyExamBody() {
  const { getToken, isLoaded } = useAuth();
  const [tier, setTier] = useState<"Free" | "Pro" | "Modular" | null>(null);
  const [countdown, setCountdown] = useState(getCountdownToSunday());

  useEffect(() => {
    const id = setInterval(() => setCountdown(getCountdownToSunday()), 60_000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!isLoaded) return;
    (async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/dashboard/summary`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        if (res.ok) {
          const data: DashboardSummary = await res.json();
          setTier(data.subscription.tier);
        }
      } catch {}
    })();
  }, [getToken, isLoaded]);

  const isPro = tier === "Pro";

  return (
    <>
      {/* Banner */}
      <div className="bg-gradient-hero px-4 py-12 text-white">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-1.5 text-sm font-semibold backdrop-blur-sm">
            <Crown className="h-4 w-4 text-yellow-300" />
            Weekly Competitive Exam
          </div>
          <h1 className="text-3xl font-extrabold sm:text-4xl">Win Medals &amp; Certificates</h1>
          <p className="mt-3 text-orange-100">
            A fresh 30-question Olympiad-level exam every week. Top scorers win real prizes.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-5 py-2.5 text-sm font-semibold backdrop-blur-sm">
            <Timer className="h-4 w-4" />
            Closes in: {countdown}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-10 space-y-8">
        {/* Week info */}
        <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="inline-flex rounded-xl bg-gradient-to-br from-brand-600 to-accent-600 p-2.5 text-white shadow-sm">
              <Calendar className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">This week's exam</p>
              <p className="mt-0.5 text-lg font-bold text-slate-900">{getWeekLabel()}</p>
            </div>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            {[
              { label: "Questions", value: "30", bg: "bg-brand-50", text: "text-brand-700", sub: "text-brand-600" },
              { label: "Duration", value: "45 min", bg: "bg-emerald-50", text: "text-emerald-700", sub: "text-emerald-600" },
              { label: "Level", value: "Olympiad", bg: "bg-violet-50", text: "text-violet-700", sub: "text-violet-600" },
            ].map((s) => (
              <div key={s.label} className={`rounded-xl ${s.bg} p-4 text-center`}>
                <p className={`text-xl font-extrabold ${s.text}`}>{s.value}</p>
                <p className={`mt-0.5 text-xs ${s.sub}`}>{s.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Prizes */}
        <section>
          <div className="mb-4 flex items-center gap-3">
            <div className="inline-flex rounded-xl bg-gradient-to-br from-amber-500 to-yellow-500 p-2.5 text-white shadow-sm">
              <Trophy className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-semibold text-slate-900">Prizes this week</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {PRIZES.map((p) => (
              <div
                key={p.rank}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 shadow-sm"
              >
                <div className={`h-2 bg-gradient-to-r ${p.color}`} />
                <div className="p-5 text-center">
                  <span className="text-3xl">{p.icon}</span>
                  <p className="mt-2 font-bold text-slate-900">{p.rank} Place</p>
                  <p className="mt-1 text-xs text-slate-500">{p.prize}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        {isPro === false && tier !== null && (
          <div className="rounded-2xl border border-brand-200 bg-brand-50 p-8 text-center">
            <Lock className="mx-auto h-10 w-10 text-brand-400" />
            <h3 className="mt-4 text-xl font-bold text-slate-900">Pro plan required</h3>
            <p className="mt-2 text-sm text-slate-600">
              The weekly exam is exclusively for Pro subscribers. Upgrade to compete for medals, certificates, and prizes.
            </p>
            <Link
              href="/billing"
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 font-bold text-white shadow-md shadow-brand-600/20 transition hover:bg-brand-700"
            >
              <Crown className="h-4 w-4" />
              Upgrade to Pro
            </Link>
          </div>
        )}

        {isPro && (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center">
            <Crown className="mx-auto h-10 w-10 text-amber-500" />
            <h3 className="mt-4 text-xl font-bold text-slate-900">You're eligible to compete!</h3>
            <p className="mt-2 text-sm text-slate-600">
              This week's exam is available now. You can attempt it once — make it count!
            </p>
            <button
              type="button"
              disabled
              className="mt-6 inline-flex cursor-not-allowed items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 font-bold text-white opacity-60 shadow-md"
            >
              <Sparkles className="h-4 w-4" />
              Coming soon — exam launching next week
            </button>
            <p className="mt-3 text-xs text-slate-400">
              The exam engine is being built. Subscribe to updates below.
            </p>
          </div>
        )}

        {/* Rules */}
        <section className="rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Rules &amp; Guidelines</h2>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            {[
              "Each participant may attempt the exam only once per week.",
              "The exam consists of 30 Olympiad-level multiple-choice questions.",
              "Total time allowed: 45 minutes. The timer starts when you click 'Start Exam'.",
              "Do not refresh or navigate away — your progress is auto-saved every question.",
              "Results and rank are published on Sunday at 11:59 PM.",
              "Certificates are issued digitally via email within 48 hours of results.",
              "Physical medals (where applicable) are dispatched within 7–10 business days.",
              "Cheating or using external aids results in disqualification.",
            ].map((rule, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-0.5 shrink-0 rounded-full bg-brand-100 px-1.5 py-0.5 text-[10px] font-bold text-brand-700">
                  {i + 1}
                </span>
                {rule}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </>
  );
}
