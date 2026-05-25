import Link from "next/link";
import { Swords, Trophy, ArrowRight } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";

import { getSafeSubject } from "@/lib/types";

export default function ChallengePage({
  searchParams,
}: {
  searchParams?: {
    s?: string;
    g?: string;
    d?: string;
    c?: string;
    score?: string;
    total?: string;
    pct?: string;
  };
}) {
  const subject = getSafeSubject(searchParams?.s);
  const grade = searchParams?.g ? Number(searchParams.g) : 6;
  const difficulty = searchParams?.d ?? "Foundation";
  const count = searchParams?.c ? Number(searchParams.c) : 10;
  const score = searchParams?.score ? Number(searchParams.score) : null;
  const total = searchParams?.total ? Number(searchParams.total) : null;
  const pct = searchParams?.pct ? Number(searchParams.pct) : null;

  // Build the practice URL pre-filled with the same config
  const practiceHref = `/?subject=${encodeURIComponent(subject)}&grade=${grade}&difficulty=${encodeURIComponent(difficulty)}`;

  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="home" />

      <div className="bg-gradient-hero px-4 py-12 text-white">
        <div className="mx-auto max-w-2xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium backdrop-blur-sm">
            <Swords className="h-4 w-4 text-yellow-300" />
            You've been challenged!
          </div>
          <h1 className="text-3xl font-extrabold sm:text-4xl">
            Can you beat this score?
          </h1>
          <p className="mt-3 text-brand-200">
            Class {grade} {subject} · {difficulty} · {count} questions
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-lg px-4 py-10">
        {/* Score to beat */}
        {score !== null && total !== null && pct !== null && (
          <div className="mb-8 overflow-hidden rounded-2xl border border-amber-200 bg-amber-50 shadow-sm">
            <div className="flex items-center gap-3 border-b border-amber-200 bg-amber-100 px-6 py-4">
              <Trophy className="h-5 w-5 text-amber-600" />
              <h2 className="font-semibold text-amber-900">Score to beat</h2>
            </div>
            <div className="flex items-center gap-6 px-6 py-6">
              <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-amber-200 text-2xl font-black text-amber-800">
                {pct}%
              </div>
              <div>
                <p className="text-2xl font-extrabold text-slate-900">
                  {score} / {total}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {pct >= 80
                    ? "That's a strong score — good luck beating it!"
                    : pct >= 60
                    ? "A decent score. Think you can do better?"
                    : "A low bar — this should be easy to beat!"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Accept challenge CTA */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm text-center">
          <h3 className="text-lg font-bold text-slate-900">Ready to take on the challenge?</h3>
          <p className="mt-2 text-sm text-slate-500">
            Sign in (or create a free account) to generate your own paper with the same config and compare scores.
          </p>
          <Link
            href={practiceHref}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-cta-600 px-6 py-3 font-bold text-white shadow-md shadow-cta-600/20 transition hover:bg-cta-700"
          >
            Accept Challenge
            <ArrowRight className="h-4 w-4" />
          </Link>
          <p className="mt-3 text-xs text-slate-400">
            You'll get your own freshly generated paper — same subject, class, and difficulty.
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          After completing, use <strong>Challenge a friend</strong> on your results to share your own score back!
        </p>
      </div>
    </div>
  );
}
