"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { CreditCard, CalendarDays, Download, Loader2, CheckCircle2, Crown, X, AlertTriangle } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type BillingHistory = {
  currentTier: string;
  onSchoolPilot?: boolean;
  school?: { name: string; logoUrl?: string; pilotEndsAt?: string } | null;
  subscriptions: Array<{
    id: string;
    planName: string;
    grade: number;
    subject: string;
    startDate: string;
    endDate: string;
    isActive: boolean;
    amountInPaise?: number;
    razorpaySubscriptionId?: string;
    isAutoRenewing?: boolean;
  }>;
  pdfPurchases: Array<{
    id: string;
    subject: string;
    grade: number;
    amountInPaise: number;
    isFree: boolean;
    purchasedAt: string;
  }>;
  freeAttemptsUsed: number;
  freeAttemptsLimit: number;
};

export function BillingHistoryCard({ onPurchaseMore }: { onPurchaseMore?: () => void } = {}) {
  const { getToken, isLoaded } = useAuth();
  const [history, setHistory] = useState<BillingHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [cancelPromptId, setCancelPromptId] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const executeCancellation = async (razorpaySubscriptionId: string) => {
    setCancellingId(razorpaySubscriptionId);
    setCancelPromptId(null);
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/billing/cancel-subscription`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ subscriptionId: razorpaySubscriptionId })
      });
      if (res.ok) {
        setHistory(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            subscriptions: prev.subscriptions.map(s => 
              s.razorpaySubscriptionId === razorpaySubscriptionId 
                ? { ...s, isAutoRenewing: false } 
                : s
            )
          };
        });
        setToastMsg("Auto-renewal successfully cancelled.");
        setTimeout(() => setToastMsg(""), 4000);
      } else {
        alert("Failed to cancel subscription. Please try again or contact support.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to cancel subscription.");
    } finally {
      setCancellingId(null);
    }
  };

  useEffect(() => {
    if (!isLoaded) return;
    (async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/billing/history`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        if (res.ok) {
          setHistory(await res.json());
        }
      } catch (err) {
        console.error("Failed to load billing history", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [getToken, isLoaded]);

  if (loading) {
    return (
      <div className="flex h-32 items-center justify-center rounded-2xl border border-white/40 bg-white/60">
        <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!history) {
    return null;
  }

  return (
    <section className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-md p-6 shadow-lg transition-all hover:shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-3">
          <div className="inline-flex rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 p-2.5 text-white shadow-sm">
            <CreditCard className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Purchases & Unlocks</h2>
            <p className="text-xs text-slate-500">View your active subscriptions, PDF downloads, and invoices.</p>
          </div>
        </div>
        {onPurchaseMore && !history.onSchoolPilot && (
          <button
            type="button"
            onClick={onPurchaseMore}
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-md shadow-indigo-600/20 transition hover:bg-indigo-700"
          >
            <Crown className="h-3.5 w-3.5" />
            Unlock More Subjects
          </button>
        )}
      </div>

      {!history.onSchoolPilot && (
        <div className="mt-6">
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-slate-50/80 p-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-800">Free Practice Attempts</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm">
                Use these global attempts to practice any unpaid class or subject. Paid subjects have unlimited practice!
              </p>
            </div>
            <div className="flex flex-col items-end gap-1.5">
              <span className="text-lg font-bold text-slate-900">
                {history.freeAttemptsUsed} <span className="text-sm font-medium text-slate-500">/ {history.freeAttemptsLimit} Used</span>
              </span>
              <div className="h-2 w-32 rounded-full bg-slate-200 overflow-hidden">
                <div
                  className="h-full bg-brand-500 rounded-full"
                  style={{ width: `${Math.min(100, (history.freeAttemptsUsed / history.freeAttemptsLimit) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 space-y-6">
        {history.subscriptions.length > 0 ? (
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Subject Subscriptions</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {Array.from(
                history.subscriptions.reduce((acc, sub) => {
                  const key = sub.razorpaySubscriptionId || sub.id;
                  if (!acc.has(key)) acc.set(key, []);
                  acc.get(key)!.push(sub);
                  return acc;
                }, new Map<string, typeof history.subscriptions>()).values()
              ).map((group) => {
                const sub = group[0]; // representative subscription
                const isPackage = group.length > 1;
                const totalAmount = group.reduce((sum, s) => sum + (s.amountInPaise || 0), 0);
                const title = isPackage ? `Class ${sub.grade} - ${sub.planName || `${group.length} Subjects`}` : `Class ${sub.grade} ${sub.subject}`;
                const subjectList = isPackage ? group.map(s => s.subject).join(", ") : null;

                return (
                  <div key={sub.id} className="flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-brand-200 transition-colors">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-base font-bold text-slate-900">{title}</p>
                        {subjectList && <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1" title={subjectList}>{subjectList}</p>}
                        <div className="mt-1 flex items-center gap-1.5 text-xs text-slate-500">
                          <CalendarDays className="h-3.5 w-3.5" />
                          {new Date(sub.startDate).toLocaleDateString()} - {new Date(sub.endDate).toLocaleDateString()}
                        </div>
                      </div>
                      {sub.isActive ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold uppercase text-emerald-700 ring-1 ring-emerald-600/20">
                          <CheckCircle2 className="h-3 w-3" /> Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold uppercase text-slate-500">
                          Expired
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-4 rounded-lg bg-indigo-50/50 p-3 text-sm">
                      <p className="font-semibold text-indigo-900 mb-1">Your Benefits:</p>
                      <ul className="text-indigo-800 space-y-1 text-xs">
                        <li className="flex items-center gap-1.5">✓ Unlimited AI Practice Generation</li>
                        <li className="flex items-center gap-1.5">✓ Level 2 (Achievers) Access</li>
                        <li className="flex items-center gap-1.5">✓ Detailed Step-by-Step Explanations</li>
                      </ul>
                    </div>

                    <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                      <span className="text-sm font-bold text-slate-700">
                        {totalAmount > 0 ? `₹${totalAmount / 100}` : "₹0"}
                      </span>
                      <div className="flex gap-4 items-center">
                        {sub.isActive && sub.isAutoRenewing && sub.razorpaySubscriptionId && (
                          <button
                            onClick={() => setCancelPromptId(sub.razorpaySubscriptionId!)}
                            disabled={cancellingId === sub.razorpaySubscriptionId}
                            className="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline disabled:opacity-50"
                          >
                            {cancellingId === sub.razorpaySubscriptionId ? "Cancelling..." : "Cancel Auto-Renewal"}
                          </button>
                        )}
                        <a
                          href={`/invoice/${sub.id}?type=subscription`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline"
                        >
                          View Invoice
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : history.onSchoolPilot ? (
          <div className="rounded-xl border border-dashed border-emerald-200 bg-emerald-50/50 p-6 text-center">
            <p className="text-sm font-semibold text-emerald-800">Full access via School Pilot</p>
            <p className="text-xs text-emerald-700 mt-1">
              {history.school?.name ?? "Your school"} has provided full platform access. No individual subject purchase needed during the pilot period.
            </p>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center">
            <p className="text-sm font-semibold text-slate-700">No active subscriptions yet</p>
            <p className="text-xs text-slate-500 mt-1 mb-4">Unlock individual subjects or get the All Subjects bundle for unlimited practice and Level 2 exams.</p>
            {onPurchaseMore && (
              <button
                type="button"
                onClick={onPurchaseMore}
                className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-md shadow-indigo-600/20 transition hover:bg-indigo-700"
              >
                <Crown className="h-3.5 w-3.5" /> Unlock Subjects Now
              </button>
            )}
          </div>
        )}

        {history.pdfPurchases.length > 0 && (
          <div className="pt-2">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">PDF Downloads</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {history.pdfPurchases.map(pdf => (
                <div key={pdf.id} className="flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-brand-200 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg bg-rose-50 p-2 text-rose-600">
                        <Download className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900">Class {pdf.grade} {pdf.subject}</p>
                        <p className="text-xs text-slate-500">{new Date(pdf.purchasedAt).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                    <span className="text-sm font-bold text-slate-700">
                      {pdf.isFree ? "Free" : `₹${pdf.amountInPaise / 100}`}
                    </span>
                    <a
                      href={`/invoice/${pdf.id}?type=pdf`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline"
                    >
                      View Invoice
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {mounted && createPortal(
        <>
          {/* Cancellation Modal */}
          {cancelPromptId && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
              <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-rose-100">
                  <AlertTriangle className="h-6 w-6 text-rose-600" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Cancel Auto-Renewal?</h3>
                <p className="mt-2 text-sm text-slate-500 leading-relaxed">
                  Are you sure you want to cancel your auto-renewal? You will keep full access to your subjects until the end of your current billing period, but you will not be charged again.
                </p>
                <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                  <button
                    type="button"
                    onClick={() => setCancelPromptId(null)}
                    className="rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition"
                  >
                    Keep Subscription
                  </button>
                  <button
                    type="button"
                    onClick={() => executeCancellation(cancelPromptId)}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-rose-700 transition"
                  >
                    Yes, Cancel It
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Disappearing Success Toast */}
          {toastMsg && (
            <div className="fixed bottom-6 left-1/2 z-[100] -translate-x-1/2 transform rounded-xl bg-emerald-600 px-4 py-3 text-sm font-medium text-white shadow-xl flex items-center gap-2 animate-in fade-in slide-in-from-bottom-5 duration-300">
              <CheckCircle2 className="h-4 w-4" />
              {toastMsg}
              <button onClick={() => setToastMsg("")} className="ml-2 rounded-full p-1 hover:bg-emerald-700 transition">
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
        </>,
        document.body
      )}
    </section>
  );
}
