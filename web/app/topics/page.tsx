"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { BookOpen, CheckCircle2, ChevronRight, Loader2, Sparkles } from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { SUBJECTS, SUBJECT_GRADE_MAP, DIFFICULTIES, type Subject } from "@/lib/types";
import { TOPIC_MAP, type TopicEntry } from "@/lib/topicMap";
import type { DashboardSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export default function TopicsPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="topics" />
      <SignedOut>
        <div className="flex flex-col items-center py-32 text-center">
          <BookOpen className="h-12 w-12 text-brand-300" />
          <h1 className="mt-4 text-2xl font-bold text-slate-900">Sign in to explore topics</h1>
          <p className="mt-2 text-sm text-slate-500">See your mastery across every chapter and jump into focused practice.</p>
          <Link href="/" className="mt-6 text-sm font-semibold text-brand-700 hover:text-brand-600">Go home →</Link>
        </div>
      </SignedOut>
      <SignedIn>
        <TopicsBody />
      </SignedIn>
    </div>
  );
}

function TopicsBody() {
  const { getToken, isLoaded } = useAuth();
  const router = useRouter();
  const [mastery, setMastery] = useState<DashboardSummary["mastery"]>([]);
  const [loadingMastery, setLoadingMastery] = useState(true);

  const [activeSubject, setActiveSubject] = useState<Subject>("Math");
  const [grade, setGrade] = useState(6);
  const [difficulty, setDifficulty] = useState("Foundation");

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
          setMastery(data.mastery);
        }
      } finally {
        setLoadingMastery(false);
      }
    })();
  }, [getToken, isLoaded]);

  // Map mastery to a quick lookup: "subject|topic" → masteryScore
  const masteryLookup = new Map(
    mastery.map((m) => [`${m.subject}|${m.topic}`, m.masteryScore])
  );

  const topics = TOPIC_MAP[activeSubject] ?? [];
  const gradeRange = SUBJECT_GRADE_MAP[activeSubject];
  const validGrades = Array.from({ length: gradeRange.max - gradeRange.min + 1 }, (_, i) => i + gradeRange.min);
  const safeGrade = validGrades.includes(grade) ? grade : gradeRange.min;

  function practiseTopic(topic: TopicEntry) {
    const params = new URLSearchParams({
      subject: activeSubject,
      grade: String(safeGrade),
      difficulty,
      topic: topic.topic,
    });
    router.push(`/?${params.toString()}`);
  }

  return (
    <>
      {/* Page banner */}
      <div className="bg-gradient-brand px-4 py-10 text-white">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">Syllabus Map</p>
          <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">Choose a topic to master</h1>
          <p className="mt-2 max-w-xl text-sm text-brand-200">
            Pick any chapter from the NCERT syllabus. We'll generate a focused practice paper just on that topic.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-8">
        {/* Controls */}
        <div className="flex flex-wrap items-end gap-4">
          {/* Grade */}
          <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
            Class
            <select
              value={safeGrade}
              onChange={(e) => setGrade(Number(e.target.value))}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
            >
              {validGrades.map((g) => (
                <option key={g} value={g}>Class {g}</option>
              ))}
            </select>
          </label>

          {/* Difficulty */}
          <div className="flex flex-col gap-1 text-sm font-medium text-slate-700">
            <span>Level</span>
            <div className="flex gap-2">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty(d)}
                  className={`rounded-lg border px-3 py-2 text-sm transition ${
                    difficulty === d
                      ? "border-brand-600 bg-brand-50 text-brand-700"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Subject tabs */}
        <div className="mt-6 flex flex-wrap gap-2">
          {SUBJECTS.map((s) => {
            const range = SUBJECT_GRADE_MAP[s];
            const available = safeGrade >= range.min && safeGrade <= range.max;
            return (
              <button
                key={s}
                type="button"
                disabled={!available}
                onClick={() => setActiveSubject(s)}
                className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${
                  activeSubject === s
                    ? "border-brand-600 bg-brand-600 text-white"
                    : available
                    ? "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                    : "cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300"
                }`}
              >
                {s}
              </button>
            );
          })}
        </div>

        {/* Topics grid */}
        <div className="mt-6">
          {loadingMastery ? (
            <div className="flex items-center gap-2 py-12 text-sm text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading mastery data…
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {topics.map((topic) => {
                const score = masteryLookup.get(`${activeSubject}|${topic.topic}`);
                const practiced = score !== undefined;
                const pct = practiced ? Math.round(score) : null;
                const scoreBand =
                  pct === null ? null
                  : pct >= 80 ? "good"
                  : pct >= 50 ? "mid"
                  : "low";

                return (
                  <div
                    key={topic.topic}
                    className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-brand-300 hover:shadow-md"
                  >
                    {/* Mastery score bar */}
                    {practiced && (
                      <div className="absolute bottom-0 left-0 right-0 h-1">
                        <div
                          className={`h-full transition-all ${
                            scoreBand === "good" ? "bg-emerald-400"
                            : scoreBand === "mid" ? "bg-amber-400"
                            : "bg-red-400"
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    )}

                    <div className="flex items-start justify-between gap-2">
                      <span className="text-2xl">{topic.emoji}</span>
                      {practiced && (
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                          scoreBand === "good"
                            ? "bg-emerald-100 text-emerald-700"
                            : scoreBand === "mid"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-red-100 text-red-700"
                        }`}>
                          {pct}% last score
                        </span>
                      )}
                    </div>

                    <h3 className="mt-2 font-semibold text-slate-900">{topic.topic}</h3>
                    <p className="mt-0.5 text-xs text-slate-500">{topic.description}</p>

                    {practiced && (
                      <div className="mt-2 flex items-center gap-1 text-[10px] text-emerald-600">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Practised</span>
                      </div>
                    )}

                    <button
                      type="button"
                      onClick={() => practiseTopic(topic)}
                      className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-xl bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 group-hover:bg-brand-700"
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      Practise this topic
                      <ChevronRight className="ml-auto h-3.5 w-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
