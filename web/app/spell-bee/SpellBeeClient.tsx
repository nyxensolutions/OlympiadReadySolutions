"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  BookOpen, CheckCircle2, ChevronRight, Loader2,
  Lock, MicVocal, Star, Trophy, XCircle, Download, BanIcon, AlertCircle, CreditCard, Sparkles
} from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { DailyQuizCard } from "@/components/DailyQuizCard";
import { TOPIC_MAP } from "@/lib/topicMap";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type SubjectInfo = {
  subject: string;
  grade: number;
  hasFreeDownload: boolean;
  isSubscribed?: boolean;
  subscribedDownloadsThisWeek?: number;
  freeQuestions: number;
  paidQuestions: number;
  priceInPaise: number;
  priceDisplay: string;
};

function loadRazorpay(): Promise<boolean> {
  return new Promise((resolve) => {
    if (typeof window.Razorpay !== "undefined") { resolve(true); return; }
    const s = document.createElement("script");
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.onload  = () => resolve(true);
    s.onerror = () => resolve(false);
    document.head.appendChild(s);
  });
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function SpellBeePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="spell-bee" />
      <div className="bg-gradient-hero px-4 py-12 text-white">
        <div className="mx-auto max-w-5xl">
          <div className="flex items-center gap-3 mb-3">
            <div className="rounded-xl bg-white/10 p-2.5">
              <MicVocal className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-violet-200">Spell Bee</p>
              <h1 className="text-2xl font-extrabold sm:text-3xl">Spell Bee Prep</h1>
            </div>
          </div>
          <p className="max-w-xl text-sm text-violet-100">
            Practice spelling for the Spell Bee competitions.
            Download offline papers or challenge yourself with the daily quiz. Available for Class 1 to 12.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {["Class 1–12", "Topic-wise Downloads", "Answer Keys Included", "Daily Challenge"].map((f) => (
              <span key={f} className="inline-flex items-center gap-1 rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white">
                <CheckCircle2 className="h-3 w-3 text-emerald-300" />
                {f}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-8">
        <SpellBeeBody />
      </div>
    </div>
  );
}

function SpellBeeBody() {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  const [grade, setGrade] = useState(1);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem("olympiad_grade");
    if (stored) {
      setGrade(Number(stored));
    }
  }, []);
  
  const handleGradeChange = (newGrade: number) => {
    setGrade(newGrade);
    setNotice(null);
    if (typeof window !== "undefined") {
      localStorage.setItem("olympiad_grade", newGrade.toString());
    }
  };
  const [subjects, setSubjects] = useState<SubjectInfo[]>([]);
  const [loadingSubjects, setLoadingSubjects] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [paying, setPaying] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ kind: "ok" | "err"; msg: string } | null>(null);

  const fetchSubjects = useCallback(async () => {
    setLoadingSubjects(true);
    setSubjects([]);
    try {
      const token = isSignedIn ? await getToken() : null;
      const res = await fetch(`${API_URL}/api/practice-papers/subjects?grade=${grade}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) setSubjects(await res.json());
    } finally {
      setLoadingSubjects(false);
    }
  }, [grade, getToken, isSignedIn]);

  useEffect(() => {
    if (isLoaded) void fetchSubjects();
  }, [grade, isLoaded, fetchSubjects]);

  const spellBeeTopics = TOPIC_MAP["Spell Bee"]?.filter(t => grade >= t.grades.min && grade <= t.grades.max) || [];

  async function downloadFree(topicName: string) {
    const key = `free-${topicName}`;
    setDownloading(key);
    setNotice(null);
    try {
      const token = await getToken();
      const res = await fetch(
        `${API_URL}/api/practice-papers/free-pdf?grade=${grade}&subject=${encodeURIComponent("Spell Bee")}&topic=${encodeURIComponent(topicName)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const purchaseKey = `Spell Bee|${topicName}`;

      if (res.status === 409) {
        setSubjects((prev) =>
          prev.map((s) => s.subject === purchaseKey ? { ...s, hasFreeDownload: true } : s)
        );
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "Free download already used.");
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "Download failed.");
      }

      const blob = await res.blob();
      triggerBlobDownload(blob, `OlympiadReady-Free-SpellBee-${topicName.replace(/\s+/g, "")}-Class${grade}.pdf`);
      
      if (!subjects.find(s => s.subject === purchaseKey)) {
          setSubjects(prev => [...prev, { subject: purchaseKey, grade, hasFreeDownload: true, freeQuestions: 10, paidQuestions: 50, priceInPaise: 1900, priceDisplay: "₹19" }]);
      } else {
          setSubjects((prev) =>
            prev.map((s) => s.subject === purchaseKey ? { ...s, hasFreeDownload: true } : s)
          );
      }

      setNotice({ kind: "ok", msg: `Your free ${topicName} paper downloaded!` });
    } catch (e) {
      setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Download failed." });
    } finally {
      setDownloading(null);
    }
  }

  async function buyAndDownload(topicName: string) {
    const key = `paid-${topicName}`;
    setPaying(key);
    setNotice(null);
    try {
      const ready = await loadRazorpay();
      if (!ready) throw new Error("Payment gateway failed to load. Please try again.");
      if (!window.Razorpay) throw new Error("Razorpay checkout failed to load. Refresh and try again.");

      const token = await getToken();

      const checkoutRes = await fetch(`${API_URL}/api/practice-papers/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ grade, subject: "Spell Bee", topic: topicName }),
      });
      
      if (!checkoutRes.ok) throw new Error("Could not initiate payment.");
      const order = await checkoutRes.json();

      await new Promise<void>((resolve, reject) => {
        const rzp = new window.Razorpay!({
          key: order.keyId,
          amount: order.amount,
          currency: order.currency,
          name: "OlympiadReady",
          description: `50Q Spell Bee Paper — ${topicName} Class ${grade}`,
          order_id: order.orderId,
          handler: async (response: any) => {
            try {
              setPaying(null);
              setDownloading(key);

              const verifyRes = await fetch(`${API_URL}/api/practice-papers/verify`, {
                method: "POST",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                body: JSON.stringify({
                  orderId: response.razorpay_order_id,
                  paymentId: response.razorpay_payment_id,
                  signature: response.razorpay_signature,
                  grade,
                  subject: "Spell Bee",
                  topic: topicName
                }),
              });

              if (!verifyRes.ok) {
                const err = await verifyRes.json().catch(() => ({}));
                throw new Error((err as { message?: string }).message ?? "Verification failed.");
              }

              const blob = await verifyRes.blob();
              triggerBlobDownload(blob, `OlympiadReady-SpellBee-${topicName.replace(/\s+/g, "")}-Class${grade}-50Q.pdf`);
              setNotice({ kind: "ok", msg: `Your 50-question ${topicName} paper is downloading!` });
              resolve();
            } catch (e) {
              reject(e);
            } finally {
              setDownloading(null);
            }
          },
          modal: { ondismiss: () => reject(new Error("Payment cancelled.")) },
          theme: { color: "#7c3aed" },
        });
        rzp.open();
      });
    } catch (e) {
      if ((e as Error).message !== "Payment cancelled.")
        setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Payment failed." });
    } finally {
      setPaying(null);
      setDownloading(null);
    }
  }

  async function downloadSubscribed(topicName: string) {
    const key = `subscribed-${topicName}`;
    setDownloading(key);
    setNotice(null);
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/practice-papers/subscribed-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ grade, subject: "Spell Bee", topic: topicName }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "Download failed.");
      }

      const blob = await res.blob();
      triggerBlobDownload(blob, `OlympiadReady-SpellBee-${topicName.replace(/\s+/g, "")}-Class${grade}-50Q.pdf`);
      
      const purchaseKey = `Spell Bee|${topicName}`;
      setSubjects(prev => prev.map(s => {
        if (s.subject === purchaseKey) {
          return { ...s, subscribedDownloadsThisWeek: (s.subscribedDownloadsThisWeek || 0) + 1 };
        }
        return s;
      }));
      setNotice({ kind: "ok", msg: `Your 50-question ${topicName} paper downloaded successfully!` });
    } catch (e) {
      setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Download failed." });
    } finally {
      setDownloading(null);
    }
  }

  return (
    <>
      {notice && (
        <div className={`mb-6 flex items-start gap-3 rounded-xl border px-4 py-3 text-sm ${
          notice.kind === "ok"
            ? "border-emerald-200 bg-emerald-50 text-emerald-800"
            : "border-red-200 bg-red-50 text-red-700"
        }`}>
          {notice.kind === "ok"
            ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
            : <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />}
          <p>{notice.msg}</p>
        </div>
      )}

      {/* Class picker and Navigation */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <label htmlFor="classSelect" className="text-sm font-semibold text-slate-700">Select Class/Grade:</label>
          <select
            id="classSelect"
            value={grade}
            onChange={(e) => handleGradeChange(Number(e.target.value))}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 cursor-pointer hover:border-violet-300"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
              <option key={g} value={g}>
                Class/Grade {g}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/?subject=Spell Bee&grade=${grade}`}
            className="inline-flex items-center gap-1.5 rounded-xl bg-violet-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition hover:bg-violet-700"
          >
            <Sparkles className="h-4 w-4" />
            Practice Online
          </Link>
          <Link
            href={`/topics?subject=Spell Bee&grade=${grade}`}
            className="inline-flex items-center gap-1.5 rounded-xl border border-violet-200 bg-white px-4 py-2 text-sm font-bold text-violet-700 shadow-sm transition hover:bg-violet-50"
          >
            <BookOpen className="h-4 w-4" />
            Syllabus Map
          </Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_350px]">
        {/* Main Section: Downloads */}
        <div>
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 className="text-lg font-bold text-slate-900">
              Class {grade} — Spell Bee Topics
            </h2>
            <SignedOut>
              <span className="text-xs text-slate-500">
                <a href="/sign-in" className="text-violet-600 underline">Sign in</a> to access free & paid downloads.
              </span>
            </SignedOut>
          </div>

          {loadingSubjects ? (
            <div className="flex items-center justify-center gap-2 py-16 text-slate-400">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span className="text-sm">Loading available topics…</span>
            </div>
          ) : spellBeeTopics.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center">
              <BookOpen className="mx-auto h-10 w-10 text-slate-300" />
              <p className="mt-3 font-semibold text-slate-600">No topics available for Class {grade} yet.</p>
              <p className="mt-1 text-sm text-slate-400">Our question bank is growing — check back soon.</p>
            </div>
          ) : (
            <div className="grid gap-5 sm:grid-cols-2">
              {spellBeeTopics.map((topic) => {
                const purchaseKey = `Spell Bee|${topic.topic}`;
                const subjectInfo = subjects.find(s => s.subject === purchaseKey);
                const hasFreeDownload = subjectInfo?.hasFreeDownload ?? false;

                const baseSubjectInfo = subjects.find(s => s.subject === "Spell Bee");
                const isSubscribed = baseSubjectInfo?.isSubscribed ?? false;
                const subscribedDownloadsThisWeek = baseSubjectInfo?.subscribedDownloadsThisWeek ?? 0;

                const freeKey = `free-${topic.topic}`;
                const paidKey = `paid-${topic.topic}`;
                const isFreeDownloading = downloading === freeKey;
                const isPaying = paying === paidKey;
                const isPaidDl = downloading === paidKey;

                return (
                  <div
                    key={topic.topic}
                    className="relative overflow-hidden rounded-2xl border border-violet-200 bg-violet-50/30 shadow-sm transition hover:shadow-md group"
                  >
                    {/* Corner Subscribed Badge */}
                    {isSubscribed && (
                      <div className="absolute -top-3 -right-3 opacity-0 transition-all duration-200 group-hover:top-1.5 group-hover:right-1.5 z-10 group-hover:opacity-100">
                         <span className="text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded shadow-sm bg-emerald-500 text-white">
                           Subscribed
                         </span>
                      </div>
                    )}
                    <div className="h-1.5 w-full bg-violet-400" />

                    <div className="p-5">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <span className="text-3xl">{topic.emoji}</span>
                          <div>
                            <h3 className="font-bold text-slate-900">{topic.topic}</h3>
                            <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{topic.description}</p>
                          </div>
                        </div>
                        {hasFreeDownload && (
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500 shrink-0">
                            Free used
                          </span>
                        )}
                      </div>

                      <div className="mt-4 space-y-3">
                        {/* ── Free tier ─────────────────────────────────── */}
                        <div className={`rounded-xl border p-3 ${
                          hasFreeDownload
                            ? "border-slate-200 bg-slate-50"
                            : "border-slate-200 bg-white"
                        }`}>
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className={`text-sm font-semibold ${hasFreeDownload ? "text-slate-400" : "text-slate-800"}`}>
                                Free — 10 Questions
                              </p>
                              <p className="text-[11px] text-slate-400 mt-0.5">
                                {hasFreeDownload
                                  ? "Already downloaded — one free paper per topic"
                                  : "Answer key included · One time only"}
                              </p>
                            </div>
                            <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${
                              hasFreeDownload
                                ? "bg-slate-100 text-slate-400"
                                : "bg-emerald-100 text-emerald-700"
                            }`}>
                              {hasFreeDownload ? "Used" : "FREE"}
                            </span>
                          </div>

                          <SignedIn>
                            {hasFreeDownload ? (
                              <div className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed select-none">
                                <BanIcon className="h-3.5 w-3.5" />
                                Already Downloaded
                              </div>
                            ) : (
                              <button
                                type="button"
                                disabled={isFreeDownloading}
                                onClick={() => downloadFree(topic.topic)}
                                className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                              >
                                {isFreeDownloading
                                  ? <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating…</>
                                  : <><Download className="h-3.5 w-3.5" /> Download Free PDF</>}
                              </button>
                            )}
                          </SignedIn>
                          <SignedOut>
                            <a
                              href="/sign-in"
                              className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50"
                            >
                              <Lock className="h-3.5 w-3.5" />
                              Sign in to download
                            </a>
                          </SignedOut>
                        </div>

                        {/* ── Paid tier ─────────────────────────────────── */}
                        <div className={`rounded-xl border p-3 ${
                          isSubscribed
                            ? "border-emerald-200 bg-emerald-50"
                            : "border-violet-200 bg-violet-50"
                        }`}>
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <p className={`text-sm font-semibold ${isSubscribed ? "text-emerald-800" : "text-slate-800"}`}>
                                Premium — 50 Questions
                              </p>
                              <p className="text-[11px] text-slate-500 mt-0.5">
                                Full set · Fresh paper every download
                              </p>
                            </div>
                            {isSubscribed ? (
                              <div className="flex items-center gap-1 shrink-0">
                                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-bold text-emerald-700">
                                  {10 - subscribedDownloadsThisWeek} left
                                </span>
                                <div className="group relative flex items-center justify-center cursor-help">
                                  <AlertCircle className="h-3.5 w-3.5 text-emerald-500" />
                                  <div className="pointer-events-none absolute bottom-full right-0 mb-1.5 w-48 opacity-0 transition-opacity group-hover:opacity-100 z-20">
                                    <div className="rounded-lg bg-slate-800 p-2 text-[10px] text-slate-100 shadow-xl">
                                      <p className="font-bold mb-0.5 text-emerald-300">Subscribed Benefit</p>
                                      You can download 10 full papers per week for this subject. Resets every Monday.
                                    </div>
                                    <div className="absolute top-full right-1.5 border-4 border-transparent border-t-slate-800" />
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <span className="shrink-0 rounded-full bg-violet-100 px-2 py-0.5 text-[11px] font-bold text-violet-700">
                                ₹19
                              </span>
                            )}
                          </div>

                          <SignedIn>
                            {isSubscribed ? (
                              <button
                                type="button"
                                disabled={downloading === `subscribed-${topic.topic}` || subscribedDownloadsThisWeek >= 10}
                                onClick={() => downloadSubscribed(topic.topic)}
                                className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                              >
                                {downloading === `subscribed-${topic.topic}` ? (
                                  <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating PDF…</>
                                ) : (
                                  <>
                                    <Download className="h-3.5 w-3.5" />
                                    Download Full Paper (Free)
                                  </>
                                )}
                              </button>
                            ) : (
                              <button
                                type="button"
                                disabled={isPaying || isPaidDl}
                                onClick={() => buyAndDownload(topic.topic)}
                                className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-violet-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-violet-700 disabled:opacity-60"
                              >
                                {isPaying ? (
                                  <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Opening payment…</>
                                ) : isPaidDl ? (
                                  <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating PDF…</>
                                ) : (
                                  <>
                                    <CreditCard className="h-3.5 w-3.5" />
                                    Buy &amp; Download — ₹19
                                    <ChevronRight className="ml-auto h-3.5 w-3.5" />
                                  </>
                                )}
                              </button>
                            )}
                          </SignedIn>
                          <SignedOut>
                            <a
                              href="/sign-in"
                              className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-violet-300 bg-white px-3 py-2 text-xs font-semibold text-violet-700 transition hover:bg-violet-50"
                            >
                              <Lock className="h-3.5 w-3.5" />
                              Sign in to purchase
                            </a>
                          </SignedOut>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Sidebar Section: Daily Quiz */}
        <div className="space-y-6">
          <DailyQuizCard grade={grade} subject="Spell Bee" />
          
          <div className="rounded-2xl border border-slate-200 bg-white p-5">
            <h3 className="font-bold text-slate-900 flex items-center gap-2 mb-3">
              <Star className="h-4 w-4 text-amber-500" />
              Frequently Asked Questions
            </h3>
            <div className="space-y-3">
              {[
                {
                  q: "What is Spell Bee?",
                  a: "Spell Bee competitions are popular national-level contests for school students testing spelling, vocabulary, and language skills.",
                },
                {
                  q: "How does the free download work?",
                  a: "You get one free 10-question paper per topic. Once downloaded, the free slot is used. To get a new set of 50 questions for the same topic, use the ₹19 paid option (August offer).",
                },
                {
                  q: "What benefits do subscribed subjects get?",
                  a: "If you have an active subscription for Spell Bee, you can download 10 full-length (50 questions) practice papers every week for free. The limit resets every Monday.",
                },
                {
                  q: "Are the questions repetitive?",
                  a: "No. Questions are dynamically generated using AI from our extensive word bank. Each download gives you a fresh, challenging set of words.",
                }
              ].map(({ q, a }) => (
                <div key={q} className="rounded-xl bg-slate-50 p-3">
                  <p className="mb-1 text-xs font-semibold text-slate-800">{q}</p>
                  <p className="text-[11px] leading-relaxed text-slate-600">{a}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-xl border border-amber-100 bg-amber-50 p-3 text-[11px] text-amber-800">
              <span className="font-semibold">Coming soon:</span> Interactive online practice rounds, audio pronunciation, and leaderboards!
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
