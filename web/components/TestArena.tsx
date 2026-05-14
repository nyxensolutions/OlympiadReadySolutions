"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, Flag, Timer } from "lucide-react";
import {
  SECONDS_PER_QUESTION,
  type AttemptResult,
  type GeneratedPaper,
  type PreviewRequest
} from "@/lib/types";

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function TestArena({
  config,
  paper,
  onSubmit
}: {
  config: PreviewRequest;
  paper: GeneratedPaper;
  onSubmit: (result: AttemptResult) => void;
}) {
  const questions = paper.questions;
  const total = questions.length;
  const totalSeconds = total * SECONDS_PER_QUESTION;

  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<(string | null)[]>(() =>
    Array(total).fill(null)
  );
  const [flagged, setFlagged] = useState<boolean[]>(() => Array(total).fill(false));
  const [remaining, setRemaining] = useState(totalSeconds);
  const startedAt = useRef<number>(Date.now());

  // We submit on timeout via this ref so the interval doesn't carry stale state
  const submitRef = useRef<() => void>();
  submitRef.current = () => {
    onSubmit({
      paperId: paper.paperId,
      questions,
      userAnswers: answers,
      flagged,
      timeTakenSeconds: Math.floor((Date.now() - startedAt.current) / 1000),
      config
    });
  };

  useEffect(() => {
    const id = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          window.clearInterval(id);
          submitRef.current?.();
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, []);

  const q = questions[current];
  const progress = useMemo(
    () => Math.round(((totalSeconds - remaining) / totalSeconds) * 100),
    [remaining, totalSeconds]
  );

  function pick(option: string) {
    setAnswers((prev) => {
      const next = [...prev];
      next[current] = option;
      return next;
    });
  }

  function toggleFlag() {
    setFlagged((prev) => {
      const next = [...prev];
      next[current] = !next[current];
      return next;
    });
  }

  return (
    <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[1fr_240px]">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between text-sm">
          <span className="font-semibold text-slate-700">
            Question {current + 1} of {total}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1 font-mono text-slate-700">
            <Timer className="h-3.5 w-3.5" />
            {formatTime(remaining)}
          </span>
        </div>

        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full bg-brand-600 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className="mt-6 text-base leading-relaxed text-slate-900">{q.q}</p>

        <ul className="mt-5 grid gap-2">
          {q.options.map((opt, i) => {
            const isPicked = answers[current] === opt;
            return (
              <li key={i}>
                <button
                  type="button"
                  onClick={() => pick(opt)}
                  className={`flex w-full items-center gap-3 rounded-lg border px-4 py-3 text-left text-sm transition ${
                    isPicked
                      ? "border-brand-600 bg-brand-50 text-brand-900"
                      : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  <span
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-mono text-xs ${
                      isPicked ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {String.fromCharCode(65 + i)}
                  </span>
                  <span>{opt}</span>
                </button>
              </li>
            );
          })}
        </ul>

        <div className="mt-6 flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setCurrent((c) => Math.max(0, c - 1))}
            disabled={current === 0}
            className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4" /> Prev
          </button>
          <button
            type="button"
            onClick={toggleFlag}
            className={`inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-sm font-medium transition ${
              flagged[current]
                ? "border-achiever-600 bg-achiever-50 text-achiever-700"
                : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
            }`}
          >
            <Flag className="h-4 w-4" />
            {flagged[current] ? "Unflag" : "Review later"}
          </button>
          <div className="ml-auto flex gap-2">
            {current < total - 1 ? (
              <button
                type="button"
                onClick={() => setCurrent((c) => Math.min(total - 1, c + 1))}
                className="inline-flex items-center gap-1 rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white hover:bg-brand-700"
              >
                Next <ChevronRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={() => submitRef.current?.()}
                className="rounded-xl bg-cta-600 px-4 py-2 text-sm font-bold text-white shadow-md shadow-cta-600/20 transition hover:bg-cta-700"
              >
                Submit test
              </button>
            )}
          </div>
        </div>
      </div>

      <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Question grid
        </p>
        <div className="mt-3 grid grid-cols-5 gap-1.5 lg:grid-cols-4">
          {questions.map((_, i) => {
            const answered = answers[i] !== null;
            const isFlag = flagged[i];
            const isCurrent = i === current;
            return (
              <button
                key={i}
                type="button"
                onClick={() => setCurrent(i)}
                className={`h-8 w-8 rounded text-xs font-semibold transition ${
                  isCurrent
                    ? "bg-brand-600 text-white"
                    : isFlag
                    ? "bg-achiever-50 text-achiever-700 ring-1 ring-achiever-600"
                    : answered
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
        <div className="mt-4 space-y-1 text-xs text-slate-600">
          <Legend color="bg-emerald-100" label="Answered" />
          <Legend color="bg-achiever-50 ring-1 ring-achiever-600" label="Flagged" />
          <Legend color="bg-slate-100" label="Unanswered" />
        </div>
      </aside>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`inline-block h-3 w-3 rounded ${color}`} />
      <span>{label}</span>
    </div>
  );
}
