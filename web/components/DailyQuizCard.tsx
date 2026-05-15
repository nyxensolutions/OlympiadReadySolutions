"use client";

import { useEffect, useState } from "react";
import { BookOpen, CheckCircle2, Loader2, Sparkles, XCircle } from "lucide-react";
import type { DailyQuizQuestion, DailyQuizAnswer } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

const STORAGE_KEY = "olympiad_daily_quiz";

type StoredState = {
  date: string;
  questionId: string;
  picked: string | null;
  correct: boolean | null;
};

function todayKey() {
  return new Date().toISOString().split("T")[0];
}

export function DailyQuizCard({ grade }: { grade: number }) {
  const [question, setQuestion] = useState<DailyQuizQuestion | null>(null);
  const [answer, setAnswer] = useState<DailyQuizAnswer | null>(null);
  const [picked, setPicked] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore today's answer from localStorage
  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    const stored: StoredState | null = raw ? JSON.parse(raw) : null;

    const fetchAndRestore = async (storedState: StoredState) => {
      try {
        const r = await fetch(`${API_URL}/api/quiz/daily?grade=${grade}`);
        const q: DailyQuizQuestion | null = r.ok ? await r.json() : null;
        if (q) {
          setQuestion(q);
          setPicked(storedState.picked);
          if (storedState.picked) {
            const a = await revealAnswer(storedState.questionId, storedState.picked);
            if (a) setAnswer(a);
          }
        }
      } finally {
        setLoading(false);
      }
    };

    if (stored && stored.date === todayKey()) {
      fetchAndRestore(stored);
      return;
    }

    // New day — fetch fresh question
    fetch(`${API_URL}/api/quiz/daily?grade=${grade}`)
      .then((r) => r.ok ? r.json() : null)
      .then((q: DailyQuizQuestion | null) => {
        if (q) setQuestion(q);
        else setError("No question available today. Check back soon!");
      })
      .catch(() => setError("Could not load today's question."))
      .finally(() => setLoading(false));
  }, [grade]);

  async function revealAnswer(questionId: string, selected: string): Promise<DailyQuizAnswer | null> {
    try {
      const r = await fetch(`${API_URL}/api/quiz/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questionId, selectedAnswer: selected }),
      });
      return r.ok ? r.json() : null;
    } catch { return null; }
  }

  async function handlePick(option: string) {
    if (picked || !question) return;
    setSubmitting(true);
    const result = await revealAnswer(question.questionId, option);
    if (result) {
      setPicked(option);
      setAnswer(result);
      const stored: StoredState = {
        date: todayKey(),
        questionId: question.questionId,
        picked: option,
        correct: result.isCorrect,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
    }
    setSubmitting(false);
  }

  const OPTIONS = ["A", "B", "C", "D"];

  return (
    <section className="overflow-hidden rounded-2xl border border-brand-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-brand-100 bg-brand-50 px-6 py-4">
        <Sparkles className="h-5 w-5 text-brand-600" />
        <h2 className="text-lg font-semibold text-slate-900">Daily Quiz</h2>
        <span className="ml-auto rounded-full bg-brand-100 px-2.5 py-0.5 text-xs font-semibold text-brand-700">
          Class {grade}
        </span>
      </div>

      <div className="p-6">
        {loading && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading question…
          </div>
        )}

        {error && (
          <p className="text-sm text-slate-500">{error}</p>
        )}

        {question && (
          <div>
            {/* Meta */}
            <div className="mb-3 flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                <BookOpen className="h-3 w-3" />
                {question.subject} · {question.topic}
              </span>
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                {question.difficulty}
              </span>
            </div>

            {/* Question */}
            <p className="text-sm font-medium leading-relaxed text-slate-800">
              {question.questionText}
            </p>

            {/* Options */}
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {question.options.map((opt, i) => {
                const letter = OPTIONS[i];
                const isChosen = picked === letter;
                const isCorrect = answer?.correctAnswer === letter;
                const revealed = !!answer;

                let style = "border-slate-200 bg-white text-slate-700 hover:bg-slate-50";
                if (revealed) {
                  if (isCorrect) style = "border-emerald-400 bg-emerald-50 text-emerald-800";
                  else if (isChosen) style = "border-red-400 bg-red-50 text-red-800";
                  else style = "border-slate-200 bg-white text-slate-400";
                } else if (isChosen) {
                  style = "border-brand-500 bg-brand-50 text-brand-800";
                }

                return (
                  <button
                    key={letter}
                    type="button"
                    disabled={!!picked || submitting}
                    onClick={() => handlePick(letter)}
                    className={`flex items-start gap-2.5 rounded-xl border p-3 text-left text-sm transition ${style} disabled:cursor-default`}
                  >
                    <span className="mt-0.5 shrink-0 rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-bold text-slate-500">
                      {letter}
                    </span>
                    <span className="leading-snug">{opt}</span>
                  </button>
                );
              })}
            </div>

            {submitting && (
              <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-400">
                <Loader2 className="h-3 w-3 animate-spin" /> Checking…
              </div>
            )}

            {/* Result */}
            {answer && (
              <div className={`mt-5 rounded-xl border p-4 ${answer.isCorrect ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"}`}>
                <div className="flex items-center gap-1.5">
                  {answer.isCorrect
                    ? <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    : <XCircle className="h-4 w-4 text-red-600" />
                  }
                  <span className={`text-sm font-semibold ${answer.isCorrect ? "text-emerald-800" : "text-red-800"}`}>
                    {answer.isCorrect ? "Correct! Well done." : `Wrong. Correct answer: ${answer.correctAnswer}`}
                  </span>
                </div>
                {answer.explanation && (
                  <p className="mt-2 text-xs leading-relaxed text-slate-600">{answer.explanation}</p>
                )}
                <p className="mt-3 text-xs text-slate-400">Come back tomorrow for a new question!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
