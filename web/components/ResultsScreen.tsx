"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Download, LayoutDashboard, MessageCircle, RotateCcw, Share2, XCircle } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import type { AttemptResult } from "@/lib/types";
import { Analytics } from "@/lib/analytics";
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
  simulationMode = false,
  onRestart
}: {
  result: AttemptResult;
  simulationMode?: boolean;
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
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);
  const [badgeEarned, setBadgeEarned] = useState<string | null>(null);
  const submitted = useRef(false);

  const pct = questions.length > 0 ? Math.round((score / questions.length) * 100) : 0;

  async function copyToClipboard(text: string) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.cssText = "position:fixed;top:-9999px;left:-9999px;opacity:0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // silent — button still shows feedback
    }
  }

  function shareToParent() {
    const msg =
      `\u{1F393} Great news! My child scored ${pct}% on their OlympiadReady practice test!\n\n` +
      `\u{1F4DA} Subject: ${config.subject} · Class ${config.grade} · Level: ${config.difficulty}\n` +
      `\u{2705} Score: ${score}/${questions.length} questions correct\n\n` +
      `Consistent daily practice is the key to Olympiad success \u{1F3C6}\n` +
      `Practice at: https://olympiadready.com`;
    window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, "_blank");
    Analytics.sharedToParent(pct);
    setShared(true);
    setTimeout(() => setShared(false), 3000);
  }

  // Persist the result once. Strict-mode guarded so the double-mount in dev doesn't double-insert.
  useEffect(() => {
    if (submitted.current) return;
    submitted.current = true;

    // Track test completion in Umami
    Analytics.testCompleted({
      subject: config.subject,
      grade: config.grade,
      difficulty: config.difficulty,
      totalQuestions: questions.length,
      scorePct: pct,
      timeTakenSeconds,
    });

    (async () => {
      const token = await getToken();
      try {
        await fetch(`${API_URL}/api/tests/submit`, {
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
        });
        // Check for first-test badge
        const prevCount = Number(localStorage.getItem("testCount") ?? "0");
        const newCount = prevCount + 1;
        localStorage.setItem("testCount", String(newCount));
        if (prevCount === 0) setBadgeEarned("🚀 First Step badge earned! Check your achievements on the dashboard.");
        else if (newCount === 5) setBadgeEarned("🔁 On a Roll badge earned! You've completed 5 tests.");
        else if (newCount === 10) setBadgeEarned("💪 Dedicated badge earned! 10 tests done.");
        else if (pct >= 90) setBadgeEarned("🎯 Sharpshooter badge earned! Great score!");
        else if (pct === 100) setBadgeEarned("⭐ Perfect Score badge earned!");
      } catch (e) {
        console.warn("Test submit failed:", e);
      }
    })();
  }, [paperId, userAnswers, timeTakenSeconds, getToken]); // eslint-disable-line react-hooks/exhaustive-deps

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
      Analytics.pdfDownloaded(config.subject, config.grade, config.difficulty);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="w-full max-w-5xl">
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 shadow-sm">
        <div className="bg-gradient-hero px-6 py-5">
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
              onClick={() => {
                const url = new URL("/challenge", window.location.origin);
                url.searchParams.set("s", config.subject);
                url.searchParams.set("g", String(config.grade));
                url.searchParams.set("d", config.difficulty);
                url.searchParams.set("c", String(questions.length));
                url.searchParams.set("score", String(score));
                url.searchParams.set("total", String(questions.length));
                url.searchParams.set("pct", String(pct));
                void copyToClipboard(url.toString());
                Analytics.challengeShared(config.subject, config.grade);
              }}
              className="inline-flex items-center gap-2 rounded-xl border border-brand-300 bg-brand-50 px-4 py-2.5 text-sm font-semibold text-brand-700 transition hover:bg-brand-100"
            >
              <Share2 className="h-4 w-4" />
              {copied ? "Link copied!" : "Challenge a friend"}
            </button>
            <button
              type="button"
              onClick={shareToParent}
              className="inline-flex items-center gap-2 rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-100"
            >
              <MessageCircle className="h-4 w-4" />
              {shared ? "Sent to WhatsApp!" : "Share to Parent"}
            </button>
            <button
              type="button"
              onClick={onRestart}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              <RotateCcw className="h-4 w-4" />
              New paper
            </button>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl border border-brand-200 bg-brand-50 px-4 py-2.5 text-sm font-semibold text-brand-700 transition hover:bg-brand-100"
            >
              <LayoutDashboard className="h-4 w-4" />
              View achievements
            </Link>
          </div>

          {error && (
            <p className="mt-3 text-sm text-red-700">{error}</p>
          )}
          {badgeEarned && (
            <div className="mt-3 flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-800">
              <span className="text-lg">🏆</span>
              <span className="font-semibold">{badgeEarned}</span>
            </div>
          )}
        </div>
      </section>

      {/* OMR sheet — shown in simulation mode before the full review */}
      {simulationMode && (
        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="bg-slate-800 px-6 py-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300">OMR Answer Sheet</h2>
            <p className="mt-0.5 text-xs text-slate-400">Your responses vs. correct answers</p>
          </div>
          <div className="overflow-x-auto p-4">
            <table className="w-full text-center text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  <th className="pb-2 pr-4 text-left">Q</th>
                  {["A", "B", "C", "D"].map((l) => (
                    <th key={l} className="w-10 pb-2">{l}</th>
                  ))}
                  <th className="pb-2 pl-4 text-left">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {questions.map((q, i) => {
                  const correctIdx = q.options.indexOf(q.answer);
                  const userIdx = userAnswers[i] !== null ? q.options.indexOf(userAnswers[i]!) : -1;
                  const isCorrect = userIdx === correctIdx;
                  return (
                    <tr key={i} className={`${isCorrect ? "bg-emerald-50/40" : userAnswers[i] === null ? "" : "bg-red-50/40"}`}>
                      <td className="py-1.5 pr-4 text-left font-semibold text-slate-600">{i + 1}</td>
                      {[0, 1, 2, 3].map((optIdx) => {
                        const isCorrectBubble = optIdx === correctIdx;
                        const isUserBubble = optIdx === userIdx;
                        return (
                          <td key={optIdx} className="py-1.5">
                            <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition ${
                              isCorrectBubble && isUserBubble
                                ? "bg-emerald-500 text-white"
                                : isUserBubble
                                ? "bg-red-500 text-white"
                                : isCorrectBubble
                                ? "bg-emerald-200 text-emerald-800 ring-2 ring-emerald-400"
                                : "bg-slate-100 text-slate-400"
                            }`}>
                              {String.fromCharCode(65 + optIdx)}
                            </span>
                          </td>
                        );
                      })}
                      <td className="py-1.5 pl-4 text-left">
                        {userAnswers[i] === null ? (
                          <span className="text-xs text-slate-400">—</span>
                        ) : isCorrect ? (
                          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="border-t border-slate-100 px-6 py-3 text-xs text-slate-500">
            <span className="mr-4"><span className="inline-block h-3 w-3 rounded-full bg-emerald-500 align-middle" /> Correct answer picked</span>
            <span className="mr-4"><span className="inline-block h-3 w-3 rounded-full bg-red-500 align-middle" /> Wrong answer picked</span>
            <span><span className="inline-block h-3 w-3 rounded-full bg-emerald-200 ring-1 ring-emerald-400 align-middle" /> Correct answer (not chosen)</span>
          </div>
        </section>
      )}

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
