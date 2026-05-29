"use client";

import { useEffect, useState, useCallback } from "react";
import {
  BookOpen, Download, Lock, Loader2, ChevronRight,
  FileText, Star, CheckCircle2, AlertCircle, CreditCard, BanIcon, Crown,
  ShoppingCart, Plus, Minus, X, Package
} from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type SubjectInfo = {
  subject: string;
  grade: number;
  hasFreeDownload: boolean;   // true = free slot already used
  isSubscribed?: boolean;
  subscribedDownloadsThisWeek?: number;
  freeQuestions: number;
  paidQuestions: number;
  priceInPaise: number;
  priceDisplay: string;
};

const SUBJECT_ICONS: Record<string, string> = {
  Math: "🧮", Mathematics: "🧮",
  Science: "🔬", English: "📖", Hindi: "📜",
  "General Knowledge": "🌍", "Logical Reasoning": "🧩",
  Computers: "💻", "Computer Science": "💻",
  AI: "🤖", "Social Studies": "🗺️",
  "Spell Bee": "🐝", Commerce: "💼"
};

const SUBJECT_COLORS: Record<string, { bg: string; border: string; badge: string; bar: string }> = {
  Math:               { bg: "bg-amber-50",   border: "border-amber-200",   badge: "bg-amber-100 text-amber-700",    bar: "bg-amber-400"   },
  Mathematics:        { bg: "bg-amber-50",   border: "border-amber-200",   badge: "bg-amber-100 text-amber-700",    bar: "bg-amber-400"   },
  Science:            { bg: "bg-emerald-50", border: "border-emerald-200", badge: "bg-emerald-100 text-emerald-700", bar: "bg-emerald-500" },
  English:            { bg: "bg-sky-50",     border: "border-sky-200",     badge: "bg-sky-100 text-sky-700",        bar: "bg-sky-500"     },
  Hindi:              { bg: "bg-orange-50",  border: "border-orange-200",  badge: "bg-orange-100 text-orange-700",  bar: "bg-orange-400"  },
  "General Knowledge":{ bg: "bg-purple-50",  border: "border-purple-200",  badge: "bg-purple-100 text-purple-700",  bar: "bg-purple-500"  },
  "Logical Reasoning":{ bg: "bg-rose-50",    border: "border-rose-200",    badge: "bg-rose-100 text-rose-700",      bar: "bg-rose-500"    },
  Computers:          { bg: "bg-indigo-50",  border: "border-indigo-200",  badge: "bg-indigo-100 text-indigo-700",  bar: "bg-indigo-500"  },
  "Computer Science": { bg: "bg-indigo-50",  border: "border-indigo-200",  badge: "bg-indigo-100 text-indigo-700",  bar: "bg-indigo-500"  },
  AI:                 { bg: "bg-fuchsia-50", border: "border-fuchsia-200", badge: "bg-fuchsia-100 text-fuchsia-700",bar: "bg-fuchsia-500" },
  "Social Studies":   { bg: "bg-teal-50",   border: "border-teal-200",   badge: "bg-teal-100 text-teal-700",      bar: "bg-teal-500"   },
  "Spell Bee":        { bg: "bg-violet-50", border: "border-violet-200", badge: "bg-violet-100 text-violet-700",  bar: "bg-violet-500" },
  Commerce:           { bg: "bg-amber-50",   border: "border-amber-200",   badge: "bg-amber-100 text-amber-700",    bar: "bg-amber-500"   },
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

// Must match RazorpayService.PdfUnitPriceInPaise / PdfBatchTotalInPaise
function pdfUnitPrice(count: number): number {
  if (count <= 2) return 29;
  if (count <= 5) return 25;
  return 20;
}
function pdfBatchTotal(count: number): number {
  return pdfUnitPrice(count) * count;
}
function pdfBatchSavings(count: number): number {
  return 29 * count - pdfBatchTotal(count);
}

export default function PracticePapersPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="practice-papers" />
      <PracticePapersBody />
    </div>
  );
}

function PracticePapersBody() {
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

  // ── Multi-select cart ─────────────────────────────────────────────────
  // Cart items are keyed by "subject" (grade is the current page grade)
  const [cart, setCart] = useState<Set<string>>(new Set());
  const [batchPaying, setBatchPaying] = useState(false);

  function toggleCart(subject: string) {
    setCart((prev) => {
      const next = new Set(prev);
      if (next.has(subject)) next.delete(subject);
      else next.add(subject);
      return next;
    });
  }

  // Clear cart when grade changes
  useEffect(() => { setCart(new Set()); }, [grade]);

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

  // ── Free download (one per user per subject/grade) ─────────────────────
  async function downloadFree(subject: string) {
    const key = `free-${subject}`;
    setDownloading(key);
    setNotice(null);
    try {
      const token = await getToken();
      const res   = await fetch(
        `${API_URL}/api/practice-papers/free-pdf?grade=${grade}&subject=${encodeURIComponent(subject)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (res.status === 409) {
        // Already downloaded — update local state so the button locks immediately
        setSubjects((prev) =>
          prev.map((s) => s.subject === subject ? { ...s, hasFreeDownload: true } : s)
        );
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "Free download already used.");
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "Download failed.");
      }

      const blob = await res.blob();
      triggerBlobDownload(blob, `OlympiadReady-Free-${subject}-Class${grade}.pdf`);
      // Lock the button
      setSubjects((prev) =>
        prev.map((s) => s.subject === subject ? { ...s, hasFreeDownload: true } : s)
      );
      setNotice({ kind: "ok", msg: `Your free ${subject} paper downloaded! Upgrade to get the full 50-question version.` });
    } catch (e) {
      setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Download failed." });
    } finally {
      setDownloading(null);
    }
  }

  // ── Subscribed download (Limit 10 per week) ─────────────────────────────
  async function downloadSubscribed(info: SubjectInfo) {
    const key = `subscribed-${info.subject}`;
    setDownloading(key);
    setNotice(null);
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/practice-papers/subscribed-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ grade, subject: info.subject }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message ?? "Failed to download paper.");
      }

      const blob = await res.blob();
      triggerBlobDownload(blob, `OlympiadReady-${info.subject}-Class${grade}-50Q.pdf`);
      
      // Optimistically update the count
      setSubjects((prev) =>
        prev.map((s) => s.subject === info.subject ? { ...s, subscribedDownloadsThisWeek: (s.subscribedDownloadsThisWeek || 0) + 1 } : s)
      );
      
      setNotice({ kind: "ok", msg: `Your ${info.subject} 50-question paper is downloaded! (${(info.subscribedDownloadsThisWeek || 0) + 1}/10 this week)` });
    } catch (e) {
      setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Download failed." });
    } finally {
      setDownloading(null);
    }
  }

  // ── Paid download (₹19 per download — each click = fresh payment) ───────
  async function buyAndDownload(info: SubjectInfo) {
    const key = `paid-${info.subject}`;
    setPaying(key);
    setNotice(null);
    try {
      const ready = await loadRazorpay();
      if (!ready) throw new Error("Payment gateway failed to load. Please try again.");
      if (!window.Razorpay) throw new Error("Razorpay checkout failed to load. Refresh and try again.");

      const token = await getToken();

      // Create a fresh Razorpay order for every download
      const checkoutRes = await fetch(`${API_URL}/api/practice-papers/checkout`, {
        method:  "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body:    JSON.stringify({ grade, subject: info.subject }),
      });
      if (!checkoutRes.ok) throw new Error("Could not initiate payment.");
      const order = await checkoutRes.json();

      // Open Razorpay — on success the handler verifies + downloads PDF in one call
      await new Promise<void>((resolve, reject) => {
        const rzp = new window.Razorpay!({
          key:         order.keyId,
          amount:      order.amount,
          currency:    order.currency,
          name:        "OlympiadReady",
          description: `50Q Practice Paper — ${info.subject} Class ${grade}`,
          order_id:    order.orderId,
          handler: async (response: any) => {
            try {
              setPaying(null);
              setDownloading(key);

              const verifyRes = await fetch(`${API_URL}/api/practice-papers/verify`, {
                method:  "POST",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                body: JSON.stringify({
                  orderId:   response.razorpay_order_id,
                  paymentId: response.razorpay_payment_id,
                  signature: response.razorpay_signature,
                  grade,
                  subject:   info.subject,
                }),
              });

              if (!verifyRes.ok) {
                const err = await verifyRes.json().catch(() => ({}));
                throw new Error((err as { message?: string }).message ?? "Verification failed.");
              }

              // verify returns the PDF directly
              const blob = await verifyRes.blob();
              triggerBlobDownload(blob, `OlympiadReady-${info.subject}-Class${grade}-50Q.pdf`);
              setNotice({ kind: "ok", msg: `Your ${info.subject} 50-question paper is downloading!` });
              resolve();
            } catch (e) {
              reject(e);
            } finally {
              setDownloading(null);
            }
          },
          modal: { ondismiss: () => reject(new Error("Payment cancelled.")) },
          theme: { color: "#2563eb" },
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

  // ── Batch purchase → ZIP download ────────────────────────────────────
  async function buyBatchAndDownload() {
    if (cart.size === 0) return;
    setBatchPaying(true);
    setNotice(null);
    try {
      const ready = await loadRazorpay();
      if (!ready || !window.Razorpay) throw new Error("Payment gateway failed to load. Refresh and try again.");

      const token = await getToken();
      const items = Array.from(cart).map((subject) => ({ grade, subject }));
      const count = items.length;
      const total = pdfBatchTotal(count);

      const checkoutRes = await fetch(`${API_URL}/api/practice-papers/checkout-batch`, {
        method:  "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body:    JSON.stringify({ items }),
      });
      if (!checkoutRes.ok) throw new Error("Could not initiate payment.");
      const order = await checkoutRes.json();

      await new Promise<void>((resolve, reject) => {
        const rzp = new window.Razorpay!({
          key:         order.keyId,
          amount:      order.amount,
          currency:    order.currency,
          name:        "OlympiadReady",
          description: order.description,
          order_id:    order.orderId,
          handler: async (response: any) => {
            try {
              setBatchPaying(false);
              setDownloading("batch");

              const verifyRes = await fetch(`${API_URL}/api/practice-papers/verify-batch`, {
                method:  "POST",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                body:    JSON.stringify({
                  orderId:   response.razorpay_order_id,
                  paymentId: response.razorpay_payment_id,
                  signature: response.razorpay_signature,
                  items,
                }),
              });

              if (!verifyRes.ok) {
                const err = await verifyRes.json().catch(() => ({}));
                throw new Error((err as { message?: string }).message ?? "Verification failed.");
              }

              const blob = await verifyRes.blob();
              triggerBlobDownload(blob, `OlympiadReady-Papers-${count}PDF.zip`);
              setCart(new Set());
              setNotice({ kind: "ok", msg: `${count} paper${count > 1 ? "s" : ""} downloaded as a ZIP!` });
              resolve();
            } catch (e) {
              reject(e);
            } finally {
              setDownloading(null);
            }
          },
          modal: { ondismiss: () => reject(new Error("Payment cancelled.")) },
          theme: { color: "#2563eb" },
        });
        rzp.open();
      });
    } catch (e) {
      if ((e as Error).message !== "Payment cancelled.")
        setNotice({ kind: "err", msg: e instanceof Error ? e.message : "Payment failed." });
    } finally {
      setBatchPaying(false);
      if (downloading === "batch") setDownloading(null);
    }
  }

  return (
    <>
      {/* Hero banner */}
      <div className="bg-gradient-hero px-4 py-12 text-white">
        <div className="mx-auto max-w-5xl">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-white/10 p-2.5">
              <FileText className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-brand-200">Practice Papers</p>
              <h1 className="text-2xl font-extrabold sm:text-3xl">Download Question Papers</h1>
            </div>
          </div>
          <p className="mt-3 max-w-xl text-sm text-brand-100">
            AI-generated, exam-style PDFs ready to print and practise.{" "}
            <span className="font-semibold">10 questions free</span> (once per subject)
            {" · "}
            <span className="font-semibold">50 questions from ₹20</span> per download (bundle discounts apply).
          </p>

          {/* Feature pills */}
          <div className="mt-4 flex flex-wrap gap-2">
            {[
              "AI-Generated Questions",
              "Answer Key Included",
              "Professional PDF Format",
              "Detailed Explanations",
            ].map((f) => (
              <span
                key={f}
                className="inline-flex items-center gap-1 rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white"
              >
                <CheckCircle2 className="h-3 w-3 text-emerald-300" />
                {f}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-8">
        {/* Notice banner */}
        {notice && (
          <div className={`mb-6 flex items-start gap-3 rounded-xl border px-4 py-3 text-sm ${
            notice.kind === "ok"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-red-200 bg-red-50 text-red-700"
          }`}>
            {notice.kind === "ok"
              ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
              : <AlertCircle  className="mt-0.5 h-4 w-4 shrink-0" />}
            <p>{notice.msg}</p>
          </div>
        )}

        {/* Class picker */}
        <div className="mb-8 flex items-center gap-4">
          <label htmlFor="classSelect" className="text-sm font-semibold text-slate-700">Select Class/Grade:</label>
          <select
            id="classSelect"
            value={grade}
            onChange={(e) => handleGradeChange(Number(e.target.value))}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 cursor-pointer hover:border-brand-300"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
              <option key={g} value={g}>
                Class/Grade {g}
              </option>
            ))}
          </select>
        </div>

        {/* Info strip */}
        <div className="mb-4 flex items-center justify-between gap-4">
          <h2 className="text-base font-bold text-slate-900">
            Class/Grade {grade} — Available Subjects
          </h2>
          <SignedOut>
            <span className="text-xs text-slate-500">
              <a href="/sign-in" className="text-brand-600 underline">Sign in</a> to access free & paid downloads.
            </span>
          </SignedOut>
        </div>

        {/* Spell Bee Promo */}
        <div className="mb-6 rounded-2xl border border-violet-200 bg-gradient-to-r from-violet-50 to-purple-50 p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-violet-100 p-2.5 text-violet-600">
              <span className="text-xl">🐝</span>
            </div>
            <div>
              <h3 className="font-bold text-violet-900">Looking for Spell Bee practice?</h3>
              <p className="text-sm text-violet-700">Get spelling-specific papers with vocabulary and memory tips.</p>
            </div>
          </div>
          <a href="/spell-bee" className="shrink-0 rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-violet-700">
            Go to Spell Bee →
          </a>
        </div>

        {/* Subject grid */}
        {loadingSubjects ? (
          <div className="flex items-center justify-center gap-2 py-16 text-slate-400">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm">Loading available subjects…</span>
          </div>
        ) : subjects.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center">
            <BookOpen className="mx-auto h-10 w-10 text-slate-300" />
            <p className="mt-3 font-semibold text-slate-600">No papers available for Class/Grade {grade} yet.</p>
            <p className="mt-1 text-sm text-slate-400">Our question bank is growing — check back soon.</p>
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {subjects.map((info) => {
              const colors  = SUBJECT_COLORS[info.subject] ?? SUBJECT_COLORS.Math;
              const icon    = SUBJECT_ICONS[info.subject] ?? "📄";
              const freeKey = `free-${info.subject}`;
              const paidKey = `paid-${info.subject}`;
              const isFreeDownloading = downloading === freeKey;
              const isPaying  = paying      === paidKey;
              const isPaidDl  = downloading === paidKey;

              return (
                <div
                  key={info.subject}
                  className={`group relative overflow-hidden rounded-2xl border ${info.isSubscribed ? "border-emerald-200 bg-[#f8fcf8]" : colors.border + " " + colors.bg} shadow-sm transition hover:shadow-md`}
                >
                  {/* Top colour bar */}
                  <div className={`h-1.5 w-full ${info.isSubscribed ? "bg-emerald-400" : colors.bar}`} />

                  {/* Corner Subscribed Badge */}
                  {info.isSubscribed && (
                    <div className="absolute -top-3 -right-3 opacity-0 transition-all duration-200 group-hover:top-1.5 group-hover:right-1.5 z-10">
                       <span className="text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded shadow-sm bg-emerald-500 text-white">
                         Subscribed
                       </span>
                    </div>
                  )}

                  <div className="p-5">
                    {/* Card header */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="text-3xl">{icon}</span>
                        <div>
                          <h3 className="font-bold text-slate-900">{info.subject}</h3>
                          <p className="text-xs text-slate-500">Class/Grade {info.grade} · All Difficulties</p>
                        </div>
                      </div>
                      {info.hasFreeDownload && (
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-500">
                          Free used
                        </span>
                      )}
                    </div>

                    <div className="mt-4 space-y-3">
                      {/* ── Free tier ─────────────────────────────────── */}
                      <div className={`rounded-xl border p-3 ${
                        info.hasFreeDownload
                          ? "border-slate-200 bg-slate-50"
                          : "border-slate-200 bg-white"
                      }`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className={`text-sm font-semibold ${info.hasFreeDownload ? "text-slate-400" : "text-slate-800"}`}>
                              Free — {info.freeQuestions} Questions
                            </p>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              {info.hasFreeDownload
                                ? "Already downloaded — one free paper per subject"
                                : "Mixed topics · Answer key included · One time only"}
                            </p>
                          </div>
                          <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${
                            info.hasFreeDownload
                              ? "bg-slate-100 text-slate-400"
                              : "bg-emerald-100 text-emerald-700"
                          }`}>
                            {info.hasFreeDownload ? "Used" : "FREE"}
                          </span>
                        </div>

                        {/* Free button — three states */}
                        <SignedIn>
                          {info.hasFreeDownload ? (
                            <div className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed select-none">
                              <BanIcon className="h-3.5 w-3.5" />
                              Already Downloaded
                            </div>
                          ) : (
                            <button
                              type="button"
                              disabled={isFreeDownloading}
                              onClick={() => downloadFree(info.subject)}
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
                            Sign in to download free
                          </a>
                        </SignedOut>
                      </div>

                      {/* ── Paid tier ─────────────────────────────────── */}
                      <div className={`rounded-xl border p-3 ${info.isSubscribed ? "border-emerald-200 bg-[#f8fcf8]" : "border-brand-200 bg-brand-50"}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold text-slate-800">
                              Premium — {info.paidQuestions} Questions
                            </p>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              All topics · Detailed explanations · Fresh set every download
                            </p>
                            {!info.isSubscribed && (
                              <p className="text-[10px] font-semibold text-emerald-600 mt-1.5 flex items-center gap-1">
                                <Crown className="h-3.5 w-3.5 text-emerald-500 inline shrink-0 animate-pulse" />
                                🎁 Free (up to 10/wk) with subscription!
                              </p>
                            )}
                          </div>
                          {info.isSubscribed ? (
                             <div className="group/tooltip relative">
                               <span className="shrink-0 rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-bold text-emerald-700 cursor-help flex items-center gap-1">
                                 <Crown className="h-3 w-3"/> Subscribed
                               </span>
                               <div className="absolute right-0 top-full mt-2 w-48 rounded-lg bg-slate-900 p-2 text-[10px] text-white opacity-0 pointer-events-none transition-opacity group-hover/tooltip:opacity-100 group-hover/tooltip:pointer-events-auto z-10">
                                 As a subscriber, you get 10 free full-length paper downloads per subject every week. Resets on Monday.
                               </div>
                             </div>
                          ) : (
                             <span className="shrink-0 rounded-full bg-brand-100 px-2 py-0.5 text-[11px] font-bold text-brand-700">
                               {info.priceDisplay}
                             </span>
                          )}
                        </div>

                        <SignedIn>
                          {info.isSubscribed ? (
                            <button
                              type="button"
                              disabled={downloading === `subscribed-${info.subject}` || (info.subscribedDownloadsThisWeek || 0) >= 10}
                              onClick={() => downloadSubscribed(info)}
                              className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
                            >
                              {downloading === `subscribed-${info.subject}` ? (
                                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating PDF…</>
                              ) : (info.subscribedDownloadsThisWeek || 0) >= 10 ? (
                                <><BanIcon className="h-3.5 w-3.5" /> Weekly limit (10/10) reached</>
                              ) : (
                                <><Download className="h-3.5 w-3.5" /> Download Free ({info.subscribedDownloadsThisWeek || 0}/10 this week)</>
                              )}
                            </button>
                          ) : (
                            <button
                              type="button"
                              disabled={isPaying || isPaidDl}
                              onClick={() => buyAndDownload(info)}
                              className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60"
                            >
                              {isPaying ? (
                                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Opening payment…</>
                              ) : isPaidDl ? (
                                <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Generating PDF…</>
                              ) : (
                                <>
                                  <CreditCard className="h-3.5 w-3.5" />
                                  Buy &amp; Download — {info.priceDisplay}
                                  <ChevronRight className="ml-auto h-3.5 w-3.5" />
                                </>
                              )}
                            </button>
                          )}
                        </SignedIn>
                        <SignedOut>
                          <a
                            href="/sign-in"
                            className="mt-2.5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-brand-300 bg-white px-3 py-2 text-xs font-semibold text-brand-700 transition hover:bg-brand-50"
                          >
                            <Lock className="h-3.5 w-3.5" />
                            Sign in to purchase
                          </a>
                        </SignedOut>
                      </div>
                    </div>

                    {/* ── Add to bundle strip ───────────────────────── */}
                    {!info.isSubscribed && (
                      <SignedIn>
                        <button
                          onClick={() => toggleCart(info.subject)}
                          className={`mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-all ${
                            cart.has(info.subject)
                              ? "border-brand-500 bg-brand-50 text-brand-700 shadow-sm"
                              : "border-dashed border-slate-300 bg-transparent text-slate-500 hover:border-brand-400 hover:text-brand-600"
                          }`}
                        >
                          {cart.has(info.subject) ? (
                            <><Minus className="h-3.5 w-3.5" /> Remove from bundle</>
                          ) : (
                            <><Plus className="h-3.5 w-3.5" /> Add to bundle</>
                          )}
                        </button>
                      </SignedIn>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ── Sticky batch cart bar (visible when cart has items) ────────── */}
        {cart.size > 0 && (
          <div className="fixed bottom-0 inset-x-0 z-40 bg-white border-t border-slate-200 shadow-xl px-4 py-3 sm:px-6">
            <div className="mx-auto max-w-5xl flex items-center gap-3 flex-wrap sm:flex-nowrap">
              {/* Cart summary */}
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <ShoppingCart className="h-5 w-5 shrink-0 text-brand-600" />
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">
                    {cart.size} paper{cart.size > 1 ? "s" : ""} selected
                    {" · "}
                    <span className="text-brand-700">₹{pdfBatchTotal(cart.size)}</span>
                    {pdfBatchSavings(cart.size) > 0 && (
                      <span className="ml-1 text-emerald-600 text-xs font-bold">
                        (save ₹{pdfBatchSavings(cart.size)})
                      </span>
                    )}
                  </p>
                  <p className="text-xs text-slate-400">
                    ₹{pdfUnitPrice(cart.size)}/paper · downloads as ZIP
                  </p>
                </div>
              </div>

              {/* Selected pills */}
              <div className="hidden sm:flex items-center gap-1.5 flex-wrap max-w-xs">
                {Array.from(cart).map((s) => (
                  <span key={s} className="inline-flex items-center gap-1 rounded-full bg-brand-50 border border-brand-200 px-2 py-0.5 text-[11px] font-semibold text-brand-700">
                    {s}
                    <button onClick={() => toggleCart(s)} className="hover:text-red-500">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => setCart(new Set())}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Clear
                </button>
                <SignedIn>
                  <button
                    onClick={buyBatchAndDownload}
                    disabled={batchPaying || downloading === "batch"}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-60 transition-all"
                  >
                    {batchPaying ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Opening payment…</>
                    ) : downloading === "batch" ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Building ZIP…</>
                    ) : (
                      <><Package className="h-4 w-4" /> Download {cart.size} PDF{cart.size > 1 ? "s" : ""} — ₹{pdfBatchTotal(cart.size)}</>
                    )}
                  </button>
                </SignedIn>
                <SignedOut>
                  <a href="/sign-in" className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-700">
                    <Lock className="h-4 w-4" /> Sign in to buy
                  </a>
                </SignedOut>
              </div>
            </div>
          </div>
        )}

        {/* About Our Practice Papers */}
        <div className={`mt-12 rounded-2xl border border-slate-200 bg-white p-6 ${cart.size > 0 ? "pb-24" : ""}`}>
          <h3 className="mb-4 flex items-center gap-2 font-bold text-slate-900">
            <Star className="h-4 w-4 text-amber-500" />
            About Our Practice Papers
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              {
                q: "Are questions AI-generated?",
                a: "Yes. Questions are generated using AI — not sourced from a static question bank. Each paper is freshly composed, ensuring variety and alignment with current syllabus patterns.",
              },
              {
                q: "How does the free download work?",
                a: "You get one free 10-question paper per subject per class. Once downloaded, the free slot is used. To get a new set of questions for the same subject, use the paid option (from ₹20 each when bundled).",
              },
              {
                q: "What does the PDF include?",
                a: "A professional exam-style question paper with our logo and branding, followed by a final Answer Key page with correct answers and detailed AI-generated explanations for every question.",
              },
              {
                q: "Which Olympiads do these papers prepare for?",
                a: "All major Indian school Olympiads — SOF IMO/NSO/IEO, SilverZone, NSTSE, and more. Questions are NCERT-aligned and pitched at competition level.",
              },
              {
                q: "Can I re-download a paid paper?",
                a: "Each payment gives you a fresh 50-question download. Price is ₹29 each for 1-2 papers, ₹25 each for 3-5, and ₹20 each for 6+. You can add multiple subjects to a bundle and download everything as a ZIP in one go.",
              },
              {
                q: "What benefits do subscribed subjects get?",
                a: "If you have an active subscription for a subject, you are eligible to download 10 full-length (50 questions) practice papers for that subject every week for free. The limit resets every Monday.",
              },
              {
                q: "Is payment secure?",
                a: "Yes. Payments are processed by Razorpay — India's leading payment gateway. We never store your card details. All transactions are HTTPS-encrypted.",
              },
            ].map(({ q, a }) => (
              <div key={q} className="rounded-xl bg-slate-50 p-4">
                <p className="mb-1 text-sm font-semibold text-slate-800">{q}</p>
                <p className="text-xs leading-relaxed text-slate-600">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
