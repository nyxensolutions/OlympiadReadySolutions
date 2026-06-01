"use client";

import { useState } from "react";
import { BookOpen, CheckCircle2, ChevronDown, ChevronUp, Flag, Sparkles, XCircle } from "lucide-react";
import type { Question } from "@/lib/types";

function isImageOption(opt: string) {
  return opt.startsWith("http://") || opt.startsWith("https://") || opt.startsWith("/question-images/");
}

export function ReviewCard({
  question,
  index,
  userAnswer,
  flagged
}: {
  question: Question;
  index: number;
  userAnswer: string | null;
  flagged: boolean;
}) {
  const correct = userAnswer === question.answer;
  const unanswered = userAnswer === null;
  // Auto-expand explanation for wrong/unanswered — the micro-lesson moment
  const [open, setOpen] = useState(!correct);

  return (
    <article
      className={`overflow-hidden rounded-xl border bg-white shadow-sm ${
        unanswered
          ? "border-slate-200"
          : correct
          ? "border-emerald-200"
          : "border-red-200"
      }`}
    >
      {/* Top accent strip */}
      <div className={`h-1 w-full ${
        unanswered ? "bg-slate-200" : correct ? "bg-emerald-400" : "bg-red-400"
      }`} />

      <div className="p-5">
        <div className="flex items-start gap-3">
          <span
            className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
              unanswered
                ? "bg-slate-100 text-slate-600"
                : correct
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {index + 1}
          </span>
          <div className="flex-1">
            <p className="text-base font-medium leading-relaxed text-slate-900">
              {question.q}
            </p>
            {question.imageUrl && (
              <div className="mt-4 mb-2 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={question.imageUrl} alt="Question visual" className="max-h-48 object-contain p-2" />
              </div>
            )}
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
              {unanswered ? (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600">
                  Not attempted
                </span>
              ) : correct ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 font-medium text-emerald-700">
                  <CheckCircle2 className="h-3 w-3" /> Correct
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700">
                  <XCircle className="h-3 w-3" /> Incorrect
                </span>
              )}
              {flagged && (
                <span className="inline-flex items-center gap-1 rounded-full bg-achiever-50 px-2 py-0.5 font-medium text-achiever-700">
                  <Flag className="h-3 w-3" /> Flagged
                </span>
              )}
              {question.topic && (
                <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2 py-0.5 font-medium text-brand-700">
                  <BookOpen className="h-3 w-3" />
                  {question.topic}
                </span>
              )}
            </div>
          </div>
        </div>

        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {question.options.map((opt, i) => {
            const isCorrect = opt === question.answer;
            const isUser = opt === userAnswer;
            let cls = "border-slate-200 bg-slate-50 text-slate-700";
            if (isCorrect) cls = "border-emerald-300 bg-emerald-50 text-emerald-900";
            else if (isUser) cls = "border-red-300 bg-red-50 text-red-900";
            return (
              <li
                key={i}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${cls}`}
              >
                <span className="font-mono text-xs text-slate-500">
                  {String.fromCharCode(65 + i)}.
                </span>
                {isImageOption(opt) ? (
                  <div className="flex-1 overflow-hidden rounded bg-white">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={opt} alt={`Option ${String.fromCharCode(65 + i)}`} className="max-h-24 object-contain" />
                  </div>
                ) : (
                  <span className="flex-1">{opt}</span>
                )}
                {isCorrect && <CheckCircle2 className="ml-auto h-4 w-4 shrink-0 text-emerald-600" />}
                {isUser && !isCorrect && <XCircle className="ml-auto h-4 w-4 shrink-0 text-red-500" />}
              </li>
            );
          })}
        </ul>

        {/* Explanation toggle */}
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-600"
        >
          {open ? (
            <>Hide explanation <ChevronUp className="h-4 w-4" /></>
          ) : (
            <>Show explanation <ChevronDown className="h-4 w-4" /></>
          )}
        </button>

        {open && (
          <div className={`mt-3 rounded-xl border p-4 text-sm leading-relaxed ${
            correct
              ? "border-emerald-200 bg-emerald-50 text-emerald-900"
              : "border-indigo-200 bg-indigo-50 text-indigo-900"
          }`}>
            <div className="mb-2 flex items-center gap-1.5">
              <Sparkles className={`h-3.5 w-3.5 ${correct ? "text-emerald-600" : "text-brand-600"}`} />
              <span className={`text-xs font-bold uppercase tracking-wide ${
                correct ? "text-emerald-700" : "text-brand-700"
              }`}>
                AI Explanation
              </span>
            </div>
            <p>{question.explanation}</p>
          </div>
        )}
      </div>
    </article>
  );
}
