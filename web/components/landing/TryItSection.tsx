"use client";

import { useState, useEffect } from "react";
import { CheckCircle2, ChevronRight, Loader2, Sparkles, XCircle } from "lucide-react";
import { SignUpButton } from "@clerk/nextjs";
import { SUBJECT_GRADE_MAP } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type TryQuestion = {
  q: string;
  imageUrl?: string;
  options: string[];
  answer: string;
  explanation: string;
};

type TryState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "questions"; qs: TryQuestion[]; idx: number; picks: (string | null)[]; done: boolean };

// Full subject list with icons for the Try It section
const ALL_SUBJECTS = [
  { id: "Mathematics",      icon: "🧮" },
  { id: "Science",          icon: "🔬" },
  { id: "English",          icon: "📖" },
  { id: "Hindi",            icon: "🇮🇳" },
  { id: "Social Studies",   icon: "🗺️" },
  { id: "General Knowledge",icon: "🌍" },
  { id: "Logical Reasoning",icon: "🧠" },
  { id: "Computer Science", icon: "💻" },
  { id: "AI",               icon: "🤖" },
  { id: "Spell Bee",        icon: "🐝" },
  { id: "Commerce",         icon: "💼" },
] as const;

type SubjectId = (typeof ALL_SUBJECTS)[number]["id"];

function isAvailable(subjectId: SubjectId, grade: number): boolean {
  const range = SUBJECT_GRADE_MAP[subjectId as keyof typeof SUBJECT_GRADE_MAP];
  if (!range) return true;
  return grade >= range.min && grade <= range.max;
}

export function TryItSection() {
  const [subject, setSubject] = useState<SubjectId>("Mathematics");
  const [grade, setGrade] = useState(1);
  const [state, setState] = useState<TryState>({ kind: "idle" });
  const [error, setError] = useState<string | null>(null);

  // When grade changes, auto-switch subject if it's no longer available
  useEffect(() => {
    if (!isAvailable(subject, grade)) {
      const fallback = ALL_SUBJECTS.find((s) => isAvailable(s.id, grade));
      if (fallback) setSubject(fallback.id);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [grade]);

  function handleGradeChange(newGrade: number) {
    setGrade(newGrade);
    setState({ kind: "idle" });
    setError(null);
  }

  async function startTry() {
    setState({ kind: "loading" });
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/generate/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, grade, difficulty: "Foundation", count: 5 }),
      });
      if (!res.ok) throw new Error("Could not load AI questions.");
      const qs: TryQuestion[] = await res.json();
      setState({ kind: "questions", qs, idx: 0, picks: Array(qs.length).fill(null), done: false });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setState({ kind: "idle" });
    }
  }

  function pick(option: string) {
    if (state.kind !== "questions" || state.done) return;
    const newPicks = [...state.picks];
    newPicks[state.idx] = option;
    if (state.idx + 1 >= state.qs.length) {
      setState({ ...state, picks: newPicks, done: true });
    } else {
      setState({ ...state, picks: newPicks, idx: state.idx + 1 });
    }
  }

  function reset() { setState({ kind: "idle" }); }

  const score = state.kind === "questions" && state.done
    ? state.qs.filter((q, i) => state.picks[i] === q.answer).length
    : 0;

  return (
    <section id="try-it" className="bg-slate-50 px-4 py-20">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-2 mb-4">
            <Sparkles className="h-4 w-4 text-brand-600" />
            <span className="text-sm font-medium text-brand-700">Try it — no sign-up needed</span>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">
            Get a feel for OlympiadReady
          </h2>
          <p className="mt-3 text-slate-600 text-sm max-w-xl mx-auto">
            Pick a subject and class — we'll generate intelligent AI questions tailored for olympiad aspirants. No account needed.
          </p>
        </div>

        {state.kind === "idle" && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            {/* Class dropdown — placed first, above subject */}
            <div className="mb-5">
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
                Class / Grade
              </label>
              <select
                value={grade}
                onChange={(e) => handleGradeChange(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition"
              >
                {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
                  <option key={g} value={g}>Class {g}</option>
                ))}
              </select>
            </div>

            {/* Subject picker — filtered by grade */}
            <div className="mb-6">
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
                Subject
                <span className="ml-2 font-normal normal-case text-slate-400">— for Class {grade}</span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {ALL_SUBJECTS.map(({ id, icon }) => {
                  const available = isAvailable(id, grade);
                  const isSelected = subject === id;
                  return (
                    <button
                      key={id}
                      type="button"
                      disabled={!available}
                      onClick={() => available && setSubject(id)}
                      title={!available ? `${id} is not available for Class ${grade}` : undefined}
                      className={`flex items-center gap-2 rounded-xl border px-3 py-2.5 text-sm font-semibold transition ${
                        isSelected
                          ? "border-brand-500 bg-brand-600 text-white shadow-sm"
                          : available
                          ? "border-slate-200 bg-white text-slate-600 hover:bg-brand-50 hover:border-brand-300"
                          : "border-slate-100 bg-slate-50 text-slate-300 cursor-not-allowed"
                      }`}
                    >
                      <span className={available ? "" : "opacity-40"}>{icon}</span>
                      <span className="truncate">{id}</span>
                      {!available && <span className="ml-auto text-[9px] font-normal text-slate-300">N/A</span>}
                    </button>
                  );
                })}
              </div>
            </div>

            {error && (
              <p className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-2 text-sm text-red-600">{error}</p>
            )}

            <button
              type="button"
              onClick={startTry}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-cta-600 px-4 py-3.5 font-bold text-white shadow-md transition hover:bg-cta-700 hover:shadow-lg"
            >
              <Sparkles className="h-5 w-5" />
              Generate questions via AI - free
            </button>

            <p className="mt-3 text-center text-xs text-slate-500">
              Real questions · Foundation difficulty · No account required
            </p>
          </div>
        )}

        {state.kind === "loading" && (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-brand-500 mb-4" />
            <p className="text-sm text-slate-600 font-medium">Crafting your {subject} questions…</p>
          </div>
        )}

        {state.kind === "questions" && !state.done && (
          <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            {/* Progress */}
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                  Question {state.idx + 1} of {state.qs.length} · {subject} Class {grade}
                </span>
                <span className="text-xs text-slate-500">Foundation</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden relative">
                <div 
                  className="absolute left-0 top-0 h-full bg-brand-500 transition-all duration-300 ease-out" 
                  style={{ width: `${Math.round(((state.idx + 1) / state.qs.length) * 100)}%` }} 
                />
              </div>
            </div>

            <div className="p-6">
              <p className="text-slate-900 font-semibold mb-5 leading-relaxed">
                {state.qs[state.idx].q}
              </p>
              {state.qs[state.idx].imageUrl && (
                <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={state.qs[state.idx].imageUrl}
                    alt="Question visual"
                    className="max-h-64 w-full object-contain p-2"
                  />
                </div>
              )}
              <div className="grid gap-3">
                {state.qs[state.idx].options.map((opt, i) => {
                  const isImageUrl = opt.startsWith("http://") || opt.startsWith("https://");
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => pick(opt)}
                      className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm text-slate-700 transition hover:border-brand-500 hover:bg-brand-50 hover:text-brand-900"
                    >
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-slate-300 bg-slate-50 text-xs font-bold text-slate-500 group-hover:border-brand-300 group-hover:bg-brand-100 group-hover:text-brand-700">
                        {String.fromCharCode(65 + i)}
                      </span>
                      {isImageUrl ? (
                        /* eslint-disable-next-line @next/next/no-img-element */
                        <img src={opt} alt={`Option ${String.fromCharCode(65 + i)}`} className="max-h-24 object-contain rounded" />
                      ) : (
                        <span>{opt}</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {state.kind === "questions" && state.done && (
          <div className="space-y-4">
            {/* Score */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
              <p className="text-4xl font-extrabold text-slate-900">{Math.round((score / state.qs.length) * 100)}%</p>
              <p className="text-slate-600 mt-1">{score} / {state.qs.length} correct · {subject} Class {grade}</p>
              <p className="mt-3 text-sm text-slate-600">
                {score >= 4 ? "Excellent! You're ready for harder Olympiad questions." :
                 score >= 2 ? "Good start — keep practising to build mastery." :
                 "Keep going! Consistent practice is the key to Olympiad success."}
              </p>

              <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center">
                <SignUpButton mode="modal">
                  <button className="inline-flex items-center justify-center gap-2 rounded-xl bg-cta-600 px-6 py-3 font-bold text-white shadow-md transition hover:bg-cta-700 hover:shadow-lg">
                    <Sparkles className="h-4 w-4" />
                    Sign up free for unlimited practice
                  </button>
                </SignUpButton>
                <button
                  type="button"
                  onClick={reset}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
                >
                  Try another subject
                </button>
              </div>
            </div>

            {/* Review */}
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                <p className="text-sm font-semibold text-slate-700">Answer review</p>
              </div>
              <div className="divide-y divide-slate-100">
                {state.qs.map((q, i) => {
                  const picked = state.picks[i];
                  const correct = picked === q.answer;
                  return (
                    <div key={i} className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        {correct
                          ? <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-500" />
                          : <XCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-500" />
                        }
                        <div className="min-w-0">
                          <p className="text-sm text-slate-800 font-medium">{q.q}</p>
                          {q.imageUrl && (
                            <div className="mt-2 mb-2 overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img src={q.imageUrl} alt="" className="max-h-32 object-contain p-1" />
                            </div>
                          )}
                          {!correct && (
                            <div className="mt-2 text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
                              <div className="mb-2">
                                <span className="block mb-1">Your answer:</span>
                                {picked?.startsWith("http://") || picked?.startsWith("https://") ? (
                                  /* eslint-disable-next-line @next/next/no-img-element */
                                  <img src={picked} className="max-h-16 object-contain rounded border border-red-200 p-1 bg-white" alt="Your answer" />
                                ) : (
                                  <span className="text-red-600 font-medium">{picked ?? "—"}</span>
                                )}
                              </div>
                              <div>
                                <span className="block mb-1">Correct answer:</span>
                                {q.answer?.startsWith("http://") || q.answer?.startsWith("https://") ? (
                                  /* eslint-disable-next-line @next/next/no-img-element */
                                  <img src={q.answer} className="max-h-16 object-contain rounded border border-emerald-200 p-1 bg-white" alt="Correct answer" />
                                ) : (
                                  <span className="text-emerald-600 font-medium">{q.answer}</span>
                                )}
                              </div>
                            </div>
                          )}
                          <p className="mt-1.5 text-xs text-slate-600 leading-relaxed">{q.explanation}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-xl border border-brand-200 bg-brand-50 p-4 text-center">
              <p className="text-sm text-brand-800">
                Want harder questions, all 9 subjects, topic-wise mastery, and PDF downloads?
              </p>
              <SignUpButton mode="modal">
                <button className="mt-3 inline-flex items-center gap-2 rounded-xl bg-cta-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-cta-700 shadow-sm">
                  Create your free account <ChevronRight className="h-4 w-4" />
                </button>
              </SignUpButton>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
