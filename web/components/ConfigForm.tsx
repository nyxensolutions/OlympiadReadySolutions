"use client";

import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import {
  DIFFICULTIES,
  QUANTITIES,
  SUBJECTS,
  isSubjectAvailable,
  type GeneratedPaper,
  type PreviewRequest,
  type QuotaError,
  type Subject
} from "@/lib/types";
import { SubjectCard } from "./SubjectCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export function ConfigForm({
  onGenerated,
  onQuotaExceeded
}: {
  onGenerated: (config: PreviewRequest, paper: GeneratedPaper) => void;
  onQuotaExceeded: (info: QuotaError) => void;
}) {
  const { getToken } = useAuth();
  const [subject, setSubject] = useState<string>("Math");
  const [grade, setGrade] = useState<number>(6);
  const [difficulty, setDifficulty] = useState<string>("Foundation");
  const [count, setCount] = useState<number>(5);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resetNotice, setResetNotice] = useState<string | null>(null);

  function handleGradeChange(newGrade: number) {
    setGrade(newGrade);
    setResetNotice(null);
    if (!isSubjectAvailable(subject as Subject, newGrade)) {
      const fallback = SUBJECTS.find((s) => isSubjectAvailable(s, newGrade)) ?? SUBJECTS[0];
      setSubject(fallback);
      setResetNotice(`${subject} isn't offered at Class ${newGrade} — switched to ${fallback}.`);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const config: PreviewRequest = { subject, grade, difficulty, count };
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/papers/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(config)
      });
      if (res.status === 402) {
        const info: QuotaError = await res.json();
        onQuotaExceeded(info);
        return;
      }
      if (!res.ok) throw new Error((await res.text()) || `Request failed (${res.status})`);
      const paper: GeneratedPaper = await res.json();
      onGenerated(config, paper);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      className="w-full max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div>
        <p className="text-sm font-semibold text-slate-700">Pick a subject</p>
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SUBJECTS.map((s) => {
            const unavailable = !isSubjectAvailable(s, grade);
            return (
              <SubjectCard
                key={s}
                name={s}
                selected={subject === s}
                onClick={() => { setSubject(s); setResetNotice(null); }}
                disabled={unavailable}
              />
            );
          })}
        </div>
      </div>

      {resetNotice && (
        <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          {resetNotice}
        </p>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          Class
          <select
            value={grade}
            onChange={(e) => handleGradeChange(Number(e.target.value))}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
              <option key={g} value={g}>
                Class {g}
              </option>
            ))}
          </select>
        </label>

        <fieldset className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          <legend>Level</legend>
          <div className="mt-1 flex gap-2">
            {DIFFICULTIES.map((d) => (
              <label
                key={d}
                className={`flex-1 cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                  difficulty === d
                    ? "border-brand-600 bg-brand-50 text-brand-700"
                    : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                }`}
              >
                <input
                  type="radio"
                  name="difficulty"
                  value={d}
                  checked={difficulty === d}
                  onChange={() => setDifficulty(d)}
                  className="sr-only"
                />
                {d}
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="mt-6">
        <p className="text-sm font-semibold text-slate-700">Number of questions</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {QUANTITIES.map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setCount(n)}
              className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${
                count === n
                  ? "border-brand-600 bg-brand-600 text-white"
                  : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Larger sets take longer to generate (35 ≈ 30–60s).
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating {count} questions…
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            Generate &amp; Start Test
          </>
        )}
      </button>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <p className="font-semibold">Generation failed</p>
          <p className="mt-1 whitespace-pre-wrap break-words">{error}</p>
        </div>
      )}
    </form>
  );
}
