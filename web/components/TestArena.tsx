"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, ChevronLeft, ChevronRight, Flag, Timer } from "lucide-react";
import {
  SECONDS_PER_QUESTION,
  type AttemptResult,
  type GeneratedPaper,
  type PreviewRequest
} from "@/lib/types";
import { MarkdownMath } from "./MarkdownMath";

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export function TestArena({
  config,
  paper,
  simulationMode = false,
  onSubmit
}: {
  config: PreviewRequest;
  paper: GeneratedPaper;
  simulationMode?: boolean;
  onSubmit: (result: AttemptResult) => void;
}) {
  const questions = paper.questions;
  const total = questions.length;
  const totalSeconds = paper.isMockExam ? 3600 : total * SECONDS_PER_QUESTION;

  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<(string | null)[]>(() => Array(total).fill(null));
  const [flagged, setFlagged] = useState<boolean[]>(() => Array(total).fill(false));
  const [remaining, setRemaining] = useState(totalSeconds);
  const startedAt = useRef<number>(Date.now());
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);

  const flaggedCount = useMemo(() => flagged.filter(Boolean).length, [flagged]);

  function handleManualSubmitClick() {
    if (flaggedCount > 0) {
      setShowSubmitConfirm(true);
    } else {
      submitRef.current?.();
    }
  }

  const submitRef = useRef<() => void>();
  submitRef.current = () => {
    const timeTaken = Math.floor((Date.now() - startedAt.current) / 1000);
    onSubmit({
      paperId: paper.paperId,
      questions,
      userAnswers: answers,
      flagged,
      timeTakenSeconds: timeTaken,
      config,
      isMockExam: paper.isMockExam
    });
  };

  useEffect(() => {
    const id = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) { window.clearInterval(id); submitRef.current?.(); return 0; }
        return r - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    // 1. Intercept browser close / refresh / address bar typing
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "An exam is currently in progress. If you leave, you will lose your progress. Are you sure?";
      return e.returnValue;
    };
    window.addEventListener("beforeunload", handleBeforeUnload);

    // 2. Intercept browser back/forward buttons
    // We push a dummy state on mount so there is a state in history we can pop.
    window.history.pushState(null, "", window.location.href);

    const handlePopState = (e: PopStateEvent) => {
      const confirmed = window.confirm(
        "An exam is currently in progress. Leaving this page will cancel your progress and result in loss of this exam. Are you sure you want to leave?"
      );
      if (confirmed) {
        // If confirmed, allow the navigation
        window.history.back();
      } else {
        // Otherwise, stay on the current page by restoring the dummy state
        window.history.pushState(null, "", window.location.href);
      }
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  const answeredCount = useMemo(
    () => answers.filter((a) => a !== null).length,
    [answers]
  );
  const progress = useMemo(
    () => Math.round((answeredCount / total) * 100),
    [answeredCount, total]
  );
  const timeProgress = useMemo(
    () => Math.round(((totalSeconds - remaining) / totalSeconds) * 100),
    [remaining, totalSeconds]
  );
  const isUrgent = remaining <= 60;
  const q = questions[current];

  function pick(option: string) {
    setAnswers((prev) => { const next = [...prev]; next[current] = option; return next; });
  }
  function toggleFlag() {
    setFlagged((prev) => { const next = [...prev]; next[current] = !next[current]; return next; });
  }

  // ── Simulation mode: full-screen exam hall ──────────────────────────────
  const confirmModal = showSubmitConfirm && (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md transform rounded-2xl border border-slate-100 bg-white p-6 shadow-2xl transition-all duration-300 scale-in animate-scaleIn">
        <div className="flex items-center gap-3 text-amber-600 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-50">
            <Flag className="h-5 w-5 animate-bounce text-amber-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Review Flagged Questions?</h3>
            <p className="text-xs text-slate-500">{paper.isMockExam ? "Mock Exam" : "Practice Test"} Submission</p>
          </div>
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          You have <strong className="text-slate-900 font-bold">{flaggedCount}</strong> question{flaggedCount === 1 ? "" : "s"} marked as <strong>"Review Later"</strong> / <strong>"Flagged"</strong>.
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Would you like to go back and review these questions, or proceed with submitting your test?
        </p>
        <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={() => setShowSubmitConfirm(false)}
            className="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
          >
            Go Back &amp; Review
          </button>
          <button
            type="button"
            onClick={() => {
              setShowSubmitConfirm(false);
              submitRef.current?.();
            }}
            className="rounded-xl bg-brand-600 hover:bg-brand-700 px-5 py-2.5 text-sm font-bold text-white shadow-md transition"
          >
            Submit Anyway
          </button>
        </div>
      </div>
    </div>
  );

  if (simulationMode) {
    return (
      <>
        <div className="fixed inset-0 z-50 flex flex-col overflow-auto bg-white">
        {/* Exam header bar */}
        <div className={`flex shrink-0 items-center justify-between border-b px-6 py-3 ${isUrgent ? "border-red-300 bg-red-50" : "border-slate-200 bg-slate-50"}`}>
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">{paper.isMockExam ? "Mock Exam" : "Exam Simulation"}</p>
            <p className="text-sm font-bold text-slate-800">
              Class {config.grade} {config.subject} {paper.isMockExam ? "" : `· ${config.difficulty}`}
            </p>
          </div>
          <div className={`flex items-center gap-2 rounded-xl px-4 py-2 font-mono text-xl font-black ${isUrgent ? "animate-pulse bg-red-100 text-red-700" : "bg-slate-100 text-slate-800"}`}>
            {isUrgent && <AlertTriangle className="h-5 w-5" />}
            {formatTime(remaining)}
          </div>
          <p className="text-sm font-semibold text-slate-500">
            Q {current + 1} / {total}
          </p>
        </div>

        {/* Dual progress bar: answers (primary) + time (secondary) */}
        <div className="shrink-0">
          <div className="h-1.5 bg-slate-200">
            <div
              className="h-full transition-all duration-300 bg-brand-500"
              style={{ width: `${progress}%` }}
              title={`${answeredCount} of ${total} answered`}
            />
          </div>
          <div className="h-0.5 bg-slate-100">
            <div
              className={`h-full transition-all ${isUrgent ? "bg-red-400" : "bg-slate-400"}`}
              style={{ width: `${timeProgress}%` }}
            />
          </div>
        </div>

        {/* Question area */}
        <div className="mx-auto w-full max-w-3xl flex-1 px-6 py-8">
          {/* Section Banner */}
          {q.sectionName && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-indigo-50 px-3 py-2 text-sm font-bold text-indigo-800 border border-indigo-100">
              {q.sectionName} {q.marks ? `(${q.marks} Marks)` : ""}
            </div>
          )}

          {/* Flag banner */}
          {flagged[current] && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
              <Flag className="h-3.5 w-3.5" /> Marked for review
            </div>
          )}

          <MarkdownMath content={q.q} className="text-lg font-semibold" />
          {q.imageUrl && (
            <div className="mt-4 flex justify-start">
              <img src={q.imageUrl} alt="Question Diagram" className="max-h-48 rounded-lg border border-slate-200 shadow-sm" />
            </div>
          )}

          <ul className="mt-6 grid gap-3">
            {q.options.map((opt, i) => {
              const isPicked = answers[current] === opt;
              return (
                <li key={i}>
                  <button
                    type="button"
                    onClick={() => pick(opt)}
                    className={`flex w-full items-center gap-4 rounded-xl border-2 px-5 py-4 text-left text-sm transition ${
                      isPicked
                        ? "border-brand-600 bg-brand-50 text-brand-900"
                        : "border-slate-200 bg-white text-slate-700 hover:border-brand-300 hover:bg-slate-50"
                    }`}
                  >
                    <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-mono font-bold text-sm ${isPicked ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"}`}>
                      {String.fromCharCode(65 + i)}
                    </span>
                    <MarkdownMath content={opt} className="flex-1" />
                    {isPicked && (
                      <svg className="h-5 w-5 shrink-0 text-brand-600" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                      </svg>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>

          {/* Question navigation */}
          <div className="mt-8 flex items-center gap-3">
            <button
              type="button"
              onClick={() => setCurrent((c) => Math.max(0, c - 1))}
              disabled={current === 0}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" /> Prev
            </button>
            <button
              type="button"
              onClick={toggleFlag}
              className={`inline-flex items-center gap-1 rounded-lg border px-4 py-2.5 text-sm font-medium transition ${
                flagged[current]
                  ? "border-amber-400 bg-amber-50 text-amber-700"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              <Flag className="h-4 w-4" />
              {flagged[current] ? "Unflag" : "Flag"}
            </button>

            <div className="ml-auto flex gap-2">
              {current < total - 1 ? (
                <button
                  type="button"
                  onClick={() => setCurrent((c) => Math.min(total - 1, c + 1))}
                  className="inline-flex items-center gap-1 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleManualSubmitClick}
                  className="rounded-xl bg-cta-600 px-6 py-2.5 text-sm font-bold text-white shadow-md transition hover:bg-cta-700"
                >
                  Submit Exam
                </button>
              )}
            </div>
          </div>

          {/* Question palette (compact, bottom of sim) */}
          <div className="mt-10 border-t border-slate-100 pt-6">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Question Palette</p>
            <div className="flex flex-wrap gap-1.5">
              {questions.map((_, i) => {
                const answered = answers[i] !== null;
                const isFlag = flagged[i];
                const isCur = i === current;
                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setCurrent(i)}
                    className={`h-8 w-8 rounded text-xs font-bold transition ${
                      isCur ? "bg-brand-600 text-white"
                      : isFlag ? "bg-amber-100 text-amber-700 ring-1 ring-amber-400"
                      : answered ? "bg-emerald-100 text-emerald-800"
                      : "bg-slate-100 text-slate-500 hover:bg-slate-200"
                    }`}
                  >
                    {i + 1}
                  </button>
                );
              })}
            </div>
            <div className="mt-3 flex gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded bg-emerald-100" />Answered</span>
              <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded bg-amber-100 ring-1 ring-amber-400" />Flagged</span>
              <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded bg-slate-100" />Unanswered</span>
            </div>
          </div>
        </div>
      </div>
      {confirmModal}
      </>
    );
  }

  // ── Normal mode ──────────────────────────────────────────────────────────
  return (
    <>
      <div className="grid w-full max-w-6xl gap-6 lg:grid-cols-[1fr_240px]">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between text-sm">
          <span className="font-semibold text-slate-700">
            Question {current + 1} of {total}
          </span>
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-mono ${isUrgent ? "animate-pulse bg-red-100 text-red-700" : "bg-slate-100 text-slate-700"}`}>
            <Timer className="h-3.5 w-3.5" />
            {formatTime(remaining)}
          </span>
        </div>

        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full transition-all duration-300 bg-brand-600 rounded-full"
            style={{ width: `${progress}%` }}
            title={`${answeredCount} of ${total} answered`}
          />
        </div>
        <div className="mt-1 flex justify-between text-[10px] text-slate-400">
          <span>{answeredCount} answered</span>
          <span>{total - answeredCount} remaining</span>
        </div>

        {q.sectionName && (
          <div className="mt-4 flex items-center gap-2 rounded bg-indigo-50 px-2 py-1.5 text-xs font-bold text-indigo-800 border border-indigo-100 w-fit">
            {q.sectionName} {q.marks ? `(${q.marks} Marks)` : ""}
          </div>
        )}

        <MarkdownMath content={q.q} className="mt-6 text-base" />
        {q.imageUrl && (
          <div className="mt-4 flex justify-start">
            <img src={q.imageUrl} alt="Question Diagram" className="max-h-48 rounded-lg border border-slate-200 shadow-sm" />
          </div>
        )}

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
                  <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-mono text-xs ${isPicked ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"}`}>
                    {String.fromCharCode(65 + i)}
                  </span>
                  <MarkdownMath content={opt} className="flex-1" />
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
                onClick={handleManualSubmitClick}
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
                  isCurrent ? "bg-brand-600 text-white"
                  : isFlag ? "bg-achiever-50 text-achiever-700 ring-1 ring-achiever-600"
                  : answered ? "bg-emerald-100 text-emerald-800"
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
    {confirmModal}
    </>
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
