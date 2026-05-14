"use client";

import { useEffect, useRef, useState } from "react";
import { Download, RotateCcw } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import type { AttemptResult } from "@/lib/types";
import { CircularScore } from "./CircularScore";
import { ReviewCard } from "./ReviewCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

export function ResultsScreen({
  result,
  onRestart
}: {
  result: AttemptResult;
  onRestart: () => void;
}) {
  const { paperId, questions, userAnswers, flagged, timeTakenSeconds, config } = result;
  const { getToken } = useAuth();
  const score = questions.reduce(
    (acc, q, i) => acc + (userAnswers[i] === q.answer ? 1 : 0),
    0
  );
  const attempted = userAnswers.filter((a) => a !== null).length;

  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submitted = useRef(false);

  // Persist the result once. Strict-mode guarded so the double-mount in dev doesn't double-insert.
  useEffect(() => {
    if (submitted.current) return;
    submitted.current = true;
    (async () => {
      const token = await getToken();
      fetch(`${API_URL}/api/tests/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          paperId,
          answers: userAnswers,
          timeTakenSeconds
        })
      }).catch((e) => console.warn("Test submit failed:", e));
    })();
  }, [paperId, userAnswers, timeTakenSeconds, getToken]);

  async function downloadPdf() {
    setDownloading(true);
    setError(null);
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/export/pdf/${paperId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error((await res.text()) || `Download failed (${res.status})`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `OlympiadReady-${config.subject}-Class${config.grade}-${config.difficulty}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="w-full max-w-5xl">
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="bg-gradient-brand px-6 py-5">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">Result</p>
          <h2 className="mt-0.5 text-lg font-bold text-white">
            Class {config.grade} {config.subject} · {config.difficulty}
          </h2>
        </div>
        <div className="p-6">
          <div className="flex flex-wrap items-center gap-6">
            <CircularScore score={score} total={questions.length} />
            <div className="grid grid-cols-3 gap-6 text-sm">
              <Stat label="Attempted" value={`${attempted} / ${questions.length}`} />
              <Stat label="Time taken" value={formatDuration(timeTakenSeconds)} />
              <Stat label="Flagged" value={String(flagged.filter(Boolean).length)} />
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={downloadPdf}
              disabled={downloading}
              className="inline-flex items-center gap-2 rounded-xl bg-cta-600 px-4 py-2.5 text-sm font-bold text-white shadow-md shadow-cta-600/20 transition hover:bg-cta-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              <Download className="h-4 w-4" />
              {downloading ? "Generating PDF…" : "Download PDF"}
            </button>
            <button
              type="button"
              onClick={onRestart}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              <RotateCcw className="h-4 w-4" />
              New paper
            </button>
          </div>

          {error && (
            <p className="mt-3 text-sm text-red-700">{error}</p>
          )}
        </div>
      </section>

      <section className="mt-6 grid gap-3">
        <h2 className="text-lg font-semibold text-slate-900">Review answers</h2>
        {questions.map((q, i) => (
          <ReviewCard
            key={i}
            question={q}
            index={i}
            userAnswer={userAnswers[i]}
            flagged={flagged[i]}
          />
        ))}
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-900">{value}</p>
    </div>
  );
}
