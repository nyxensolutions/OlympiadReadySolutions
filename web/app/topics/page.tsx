"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BookOpen, CheckCircle2, ChevronRight, Loader2, Sparkles, Star, Award } from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { TestArena } from "@/components/TestArena";
import { ResultsScreen } from "@/components/ResultsScreen";
import { SUBJECTS, SUBJECT_GRADE_MAP, DIFFICULTIES, getSafeSubject, type Subject, type GeneratedPaper, type PreviewRequest, type AttemptResult, type DashboardSummary } from "@/lib/types";
import { TOPIC_MAP, type TopicEntry } from "@/lib/topicMap";
import { Analytics } from "@/lib/analytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type FlowState =
  | { kind: "grid" }
  | { kind: "loading"; topic: TopicEntry }
  | { kind: "arena"; config: PreviewRequest; paper: GeneratedPaper; topic: TopicEntry }
  | { kind: "results"; result: AttemptResult; topic: TopicEntry };

type ApiError = { code?: string; message?: string; upgrade?: boolean };

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

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
        <Suspense fallback={<div className="p-8 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto text-brand-600"/></div>}>
          <TopicsBody />
        </Suspense>
      </SignedIn>
    </div>
  );
}

function TopicsBody() {
  const { getToken, isLoaded } = useAuth();
  const searchParams = useSearchParams();
  const initialSubject = getSafeSubject(searchParams?.get("subject"));
  const initialGrade = searchParams?.get("grade") 
    ? Number(searchParams.get("grade")) 
    : 1;

  const [mastery, setMastery] = useState<DashboardSummary["mastery"]>([]);
  const [activeUnlocks, setActiveUnlocks] = useState<DashboardSummary["subscription"]["activeUnlocks"]>([]);
  const [loadingMastery, setLoadingMastery] = useState(true);

  const [activeSubject, setActiveSubject] = useState<Subject>(initialSubject);
  const [grade, setGrade] = useState(initialGrade);
  
  useEffect(() => {
    if (!searchParams?.get("grade") && typeof window !== "undefined") {
      const stored = localStorage.getItem("olympiad_grade");
      if (stored) setGrade(Number(stored));
    }
  }, [searchParams]);
  
  const handleGradeChange = (newGrade: number) => {
    setGrade(newGrade);
    setFlow({ kind: "grid" });
    if (typeof window !== "undefined") {
      localStorage.setItem("olympiad_grade", newGrade.toString());
    }
  };

  const [difficulty, setDifficulty] = useState("Foundation");

  const [flow, setFlow] = useState<FlowState>({ kind: "grid" });
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [quotaExceeded, setQuotaExceeded] = useState(false);

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
          if (data.subscription?.activeUnlocks) setActiveUnlocks(data.subscription.activeUnlocks);
        }
      } finally {
        setLoadingMastery(false);
      }
    })();
  }, [getToken, isLoaded]);

  const masteryLookup = new Map(
    mastery.map((m) => [`${m.subject}|${m.topic}`, m.masteryScore])
  );

  const gradeRange = SUBJECT_GRADE_MAP[activeSubject] || { min: 1, max: 12 };
  const validGrades = Array.from({ length: gradeRange.max - gradeRange.min + 1 }, (_, i) => i + gradeRange.min);
  const safeGrade = validGrades.includes(grade) ? grade : gradeRange.min;

  // Filter topics to only those valid for the selected grade
  const allTopics = TOPIC_MAP[activeSubject] ?? [];
  const topics = allTopics.filter((t) => safeGrade >= t.grades.min && safeGrade <= t.grades.max);

  async function startTopic(topic: TopicEntry) {
    setGenerateError(null);
    setQuotaExceeded(false);
    setFlow({ kind: "loading", topic });
    try {
      const token = await getToken();
      const body: PreviewRequest = {
        subject: activeSubject,
        grade: safeGrade,
        difficulty,
        count: 10,
        topic: topic.topic,
      };
      const res = await fetch(`${API_URL}/api/papers/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
      });

      if (res.status === 402) {
        Analytics.quotaExceeded(activeSubject, safeGrade);
        setQuotaExceeded(true);
        setFlow({ kind: "grid" });
        return;
      }

      if (!res.ok) {
        const err: ApiError = await res.json().catch(() => ({}));
        const code = err.code ?? "";
        if (code === "BANK_INSUFFICIENT") {
          throw new Error(
            `Not enough questions in the bank for ${activeSubject} Class/Grade ${safeGrade} — ${topic.topic} (${difficulty}). ` +
            `Try a different difficulty level, or upgrade to Pro for AI-generated papers.`
          );
        }
        throw new Error(err.message ?? "Failed to generate paper.");
      }
      const paper: GeneratedPaper = await res.json();
      setFlow({ kind: "arena", config: body, paper, topic });

      Analytics.paperGenerated({
        subject: activeSubject,
        grade: safeGrade,
        difficulty,
        count: 10,
        simulationMode: false,
        mistakesOnly: false
      });
    } catch (e) {
      setGenerateError(e instanceof Error ? e.message : "Something went wrong.");
      setFlow({ kind: "grid" });
    }
  }

  function handleSubmit(result: AttemptResult) {
    if (flow.kind !== "arena") return;
    setFlow({ kind: "results", result, topic: flow.topic });
    
    // AttemptResult has totalMarks and earnedMarks populated in TestArena submit? 
    // Wait, TestArena doesn't populate earnedMarks because it's calculated on the server.
    // Topics page uses TestArena -> then shows ResultsScreen. 
    // Wait, does ResultsScreen calculate the score if earnedMarks isn't there?
    // Let's just pass what we can or rely on ResultsScreen to log it.
    // Actually, ResultsScreen logs `Analytics.testCompleted` natively! 
  }

  function handleRestart() {
    setFlow({ kind: "grid" });
  }

  // Arena / results — full-page overlay, hide normal layout
  if (flow.kind === "arena") {
    return (
      <TestArena
        config={flow.config}
        paper={flow.paper}
        onSubmit={handleSubmit}
      />
    );
  }

  if (flow.kind === "results") {
    return (
      <ResultsScreen
        result={flow.result}
        onRestart={handleRestart}
      />
    );
  }

  return (
    <>
      {/* Page banner */}
      <div className="bg-gradient-hero px-4 py-10 text-white">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">Syllabus Map</p>
          <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">Choose a topic to master</h1>
          <p className="mt-2 max-w-xl text-sm text-brand-200">
            Pick any chapter from the NCERT syllabus. We'll generate a focused 10-question paper just on that topic.
          </p>
          <div className="mt-6 flex flex-wrap gap-4">
            <Link href="/mock-exams" className="flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-600 shadow-md transition hover:bg-slate-50 hover:shadow-lg">
              <Award className="h-4 w-4" />
              Take a Full Mock Exam
            </Link>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-4 py-8">
        {generateError && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {generateError}
          </div>
        )}

        {quotaExceeded && (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <p className="font-semibold">Monthly paper limit reached</p>
            <p className="mt-1">
              You&apos;ve used all your free papers this month.{" "}
              <a href="/" className="underline font-medium">Upgrade to Pro</a> for unlimited AI-generated papers.
            </p>
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap items-end gap-4">
          <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
            Class/Grade
            <select
              value={safeGrade}
              onChange={(e) => handleGradeChange(Number(e.target.value))}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
            >
              {validGrades.map((g) => (
                <option key={g} value={g}>Class/Grade {g}</option>
              ))}
            </select>
          </label>

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
            const range = SUBJECT_GRADE_MAP[s] || { min: 1, max: 12 };
            const available = safeGrade >= range.min && safeGrade <= range.max;
            const isSubscribed = activeUnlocks?.some((u) => u.grade === safeGrade && u.subject.toLowerCase() === s.toLowerCase());
            
            return (
              <button
                key={s}
                type="button"
                disabled={!available}
                onClick={() => setActiveSubject(s)}
                className={`rounded-full border px-4 py-1.5 text-sm font-medium transition flex items-center gap-1.5 ${
                  activeSubject === s
                    ? "border-brand-600 bg-brand-600 text-white shadow-sm"
                    : available
                    ? (isSubscribed 
                        ? "border-emerald-300 bg-[#f8fcf8] text-emerald-800 hover:bg-emerald-50" 
                        : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50")
                    : "cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300"
                }`}
              >
                {s}
                {available && (
                   <span className={`text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full ${
                     activeSubject === s 
                       ? "bg-white/20 text-white" 
                       : isSubscribed ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"
                   }`}>
                     {isSubscribed ? "Subscribed" : "Free"}
                   </span>
                )}
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
          ) : flow.kind === "loading" ? (
            <div className="flex flex-col items-center gap-3 py-24 text-sm text-slate-500">
              <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
              <p className="font-medium">Generating your {flow.topic.topic} paper…</p>
              <p className="text-xs text-slate-400">Crafting 10 questions just for this topic.</p>
            </div>
          ) : topics.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white px-6 py-12 text-center">
              <p className="text-sm text-slate-500">No topics available for {activeSubject} at Class/Grade {safeGrade}.</p>
              <p className="mt-1 text-xs text-slate-400">Try a different subject or grade.</p>
            </div>
          ) : (
            <>
              <p className="mb-4 text-xs text-slate-400">
                Showing {topics.length} topic{topics.length !== 1 ? "s" : ""} for Class/Grade {safeGrade} {activeSubject}
              </p>
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
                      className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-5 shadow-sm transition hover:border-brand-300 hover:shadow-xl"
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-brand-600 to-accent-600 opacity-0 transition duration-300 group-hover:opacity-[0.04]" />
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

                      <div className="relative z-10">
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
                          onClick={() => startTopic(topic)}
                          className="mt-4 inline-flex w-full items-center justify-center gap-1.5 rounded-xl bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 group-hover:bg-brand-700"
                        >
                          <Sparkles className="h-3.5 w-3.5" />
                          Practise this topic
                          <ChevronRight className="ml-auto h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* FAQ Section */}
        <div className="mt-12 rounded-2xl border border-slate-200 bg-white p-6">
          <h3 className="mb-4 flex items-center gap-2 font-bold text-slate-900">
            <Star className="h-4 w-4 text-brand-500" />
            Frequently Asked Questions
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              {
                q: "What is the Syllabus Map?",
                a: "The Syllabus Map breaks down the curriculum into individual chapters or topics. You can practice one specific topic at a time instead of taking a mixed full-length exam.",
              },
              {
                q: "How many free online attempts do I get?",
                a: "Free users get 5 total online practice attempts across any class or subject. These attempts use our AI generation engine to provide you a premium experience.",
              },
              {
                q: "What happens if I subscribe to a subject?",
                a: "Subscribed subjects unlock unlimited online practice! They no longer count towards your 5 free global attempts, allowing you to master those subjects fully.",
              },
              {
                q: "What if I use all my free attempts?",
                a: "Once you hit your limit of 5 free AI-generated online attempts, you will need to subscribe to continue generating fresh online practice tests.",
              },
              {
                q: "Do I have to subscribe to all subjects?",
                a: "No! You can choose to subscribe to any individual subject or any combination. Price is ₹129 per subject per month, with 5% off when you buy 3 or more subjects in one order.",
              },
            ].map(({ q, a }) => (
              <div key={q} className="rounded-xl bg-slate-50 p-4">
                <p className="mb-1 text-sm font-semibold text-slate-800">{q}</p>
                <p className="text-xs leading-relaxed text-slate-600">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
