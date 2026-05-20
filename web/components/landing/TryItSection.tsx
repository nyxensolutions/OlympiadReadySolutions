"use client";

import { useState } from "react";
import { CheckCircle2, ChevronRight, Loader2, Sparkles, XCircle } from "lucide-react";
import { SignUpButton } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type TryQuestion = {
  q: string;
  options: string[];
  answer: string;
  explanation: string;
};

type TryState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "questions"; qs: TryQuestion[]; idx: number; picks: (string | null)[]; done: boolean };

const SUBJECTS = ["Math", "Science", "English", "Logical Reasoning"];

export function TryItSection() {
  const [subject, setSubject] = useState("Math");
  const [grade, setGrade] = useState(6);
  const [state, setState] = useState<TryState>({ kind: "idle" });
  const [error, setError] = useState<string | null>(null);

  async function startTry() {
    setState({ kind: "loading" });
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/generate/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, grade, difficulty: "Foundation", count: 5 }),
      });
      if (!res.ok) throw new Error("Could not load sample questions.");
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
    <section className="bg-gradient-to-br from-slate-900 to-brand-950 px-4 py-20">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 mb-4">
            <Sparkles className="h-4 w-4 text-yellow-300" />
            <span className="text-sm font-medium text-white">Try it — no sign-up needed</span>
          </div>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            Get a feel for OlympiadReady
          </h2>
          <p className="mt-3 text-slate-300 text-sm max-w-xl mx-auto">
            Pick a subject and class — we&apos;ll generate 5 real Olympiad-style questions powered by AI. No account needed.
          </p>
        </div>

        {state.kind === "idle" && (
          <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-6">
            <div className="grid gap-4 sm:grid-cols-2 mb-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Subject</label>
                <div className="grid grid-cols-2 gap-2">
                  {SUBJECTS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setSubject(s)}
                      className={`rounded-xl border px-3 py-2 text-sm font-semibold transition ${
                        subject === s
                          ? "border-brand-400 bg-brand-600 text-white"
                          : "border-white/20 bg-white/5 text-slate-300 hover:bg-white/10"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Class</label>
                <div className="flex flex-wrap gap-2">
                  {[3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
                    <button
                      key={g}
                      type="button"
                      onClick={() => setGrade(g)}
                      className={`rounded-lg border px-3 py-1.5 text-sm font-semibold transition ${
                        grade === g
                          ? "border-brand-400 bg-brand-600 text-white"
                          : "border-white/20 bg-white/5 text-slate-300 hover:bg-white/10"
                      }`}
                    >
                      {g}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {error && (
              <p className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-2 text-sm text-red-300">{error}</p>
            )}

            <button
              type="button"
              onClick={startTry}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-cta-600 px-4 py-3.5 font-bold text-white shadow-lg transition hover:bg-cta-700 hover:scale-[1.01]"
            >
              <Sparkles className="h-5 w-5" />
              Generate 5 sample questions — free
            </button>

            <p className="mt-3 text-center text-xs text-slate-500">
              AI-generated · Foundation difficulty · No account required
            </p>
          </div>
        )}

        {state.kind === "loading" && (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-12 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-brand-400 mb-4" />
            <p className="text-sm text-slate-300 font-medium">AI is crafting your {subject} questions…</p>
          </div>
        )}

        {state.kind === "questions" && !state.done && (
          <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden">
            {/* Progress */}
            <div className="bg-brand-600/30 px-6 py-4 border-b border-white/10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wide">
                  Question {state.idx + 1} of {state.qs.length} · {subject} Class {grade}
                </span>
                <span className="text-xs text-slate-400">Foundation</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/10">
                <div className="h-full rounded-full bg-brand-400 transition-all" style={{ width: `${(state.idx / state.qs.length) * 100}%` }} />
              </div>
            </div>

            <div className="p-6">
              <p className="text-white font-semibold mb-5 leading-relaxed">
                {state.qs[state.idx].q}
              </p>
              <div className="grid gap-3">
                {state.qs[state.idx].options.map((opt, i) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => pick(opt)}
                    className="flex items-center gap-3 rounded-xl border border-white/20 bg-white/5 px-4 py-3 text-left text-sm text-slate-200 transition hover:border-brand-400 hover:bg-white/10"
                  >
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-white/30 text-xs font-bold text-slate-400">
                      {String.fromCharCode(65 + i)}
                    </span>
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {state.kind === "questions" && state.done && (
          <div className="space-y-4">
            {/* Score */}
            <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center">
              <p className="text-4xl font-extrabold text-white">{Math.round((score / state.qs.length) * 100)}%</p>
              <p className="text-slate-300 mt-1">{score} / {state.qs.length} correct · {subject} Class {grade}</p>
              <p className="mt-3 text-sm text-slate-400">
                {score >= 4 ? "Excellent! You're ready for harder Olympiad questions." :
                 score >= 2 ? "Good start — keep practising to build mastery." :
                 "Keep going! Consistent practice is the key to Olympiad success."}
              </p>

              <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-center">
                <SignUpButton mode="modal">
                  <button className="inline-flex items-center justify-center gap-2 rounded-xl bg-cta-600 px-6 py-3 font-bold text-white shadow-lg transition hover:bg-cta-700">
                    <Sparkles className="h-4 w-4" />
                    Sign up free for unlimited practice
                  </button>
                </SignUpButton>
                <button
                  type="button"
                  onClick={reset}
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/5 px-6 py-3 text-sm font-semibold text-slate-300 transition hover:bg-white/10"
                >
                  Try another subject
                </button>
              </div>
            </div>

            {/* Review */}
            <div className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">
              <div className="border-b border-white/10 px-6 py-4">
                <p className="text-sm font-semibold text-slate-300">Answer review</p>
              </div>
              <div className="divide-y divide-white/5">
                {state.qs.map((q, i) => {
                  const picked = state.picks[i];
                  const correct = picked === q.answer;
                  return (
                    <div key={i} className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        {correct
                          ? <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5 text-emerald-400" />
                          : <XCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
                        }
                        <div className="min-w-0">
                          <p className="text-sm text-slate-200">{q.q}</p>
                          {!correct && (
                            <p className="mt-1 text-xs text-slate-400">
                              Your answer: <span className="text-red-300 font-medium">{picked ?? "—"}</span>{" · "}
                              Correct: <span className="text-emerald-300 font-medium">{q.answer}</span>
                            </p>
                          )}
                          <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">{q.explanation}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-xl border border-brand-400/30 bg-brand-600/10 p-4 text-center">
              <p className="text-sm text-brand-200">
                Want harder questions, all 9 subjects, topic-wise mastery, and PDF downloads?
              </p>
              <SignUpButton mode="modal">
                <button className="mt-3 inline-flex items-center gap-2 rounded-xl bg-cta-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-cta-700">
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
