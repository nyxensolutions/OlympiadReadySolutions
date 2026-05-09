"use client";

import { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, Flag, XCircle } from "lucide-react";
import type { Question } from "@/lib/types";

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
  const [open, setOpen] = useState(false);
  const correct = userAnswer === question.answer;
  const unanswered = userAnswer === null;

  return (
    <article
      className={`rounded-xl border bg-white p-5 shadow-sm ${
        unanswered
          ? "border-slate-200"
          : correct
          ? "border-emerald-200"
          : "border-red-200"
      }`}
    >
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
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs">
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
              <span>{opt}</span>
              {isCorrect && <CheckCircle2 className="ml-auto h-4 w-4 text-emerald-600" />}
              {isUser && !isCorrect && <XCircle className="ml-auto h-4 w-4 text-red-600" />}
            </li>
          );
        })}
      </ul>

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-600"
      >
        {open ? (
          <>
            Hide explanation <ChevronUp className="h-4 w-4" />
          </>
        ) : (
          <>
            Show explanation <ChevronDown className="h-4 w-4" />
          </>
        )}
      </button>

      {open && (
        <div className="mt-3 rounded-lg bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
          {question.explanation}
        </div>
      )}
    </article>
  );
}
