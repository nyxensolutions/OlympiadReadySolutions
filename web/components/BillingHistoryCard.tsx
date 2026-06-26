"use client";

import { useEffect, useState } from "react";
import { CreditCard, CalendarDays, Download, Loader2, CheckCircle2, Crown } from "lucide-react";
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
              {history.subscriptions.map(sub => (
                <div key={sub.id} className="flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-brand-200 transition-colors">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-base font-bold text-slate-900">Class {sub.grade} {sub.subject}</p>
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
                      {(sub.amountInPaise ?? 0) > 0 ? `₹${(sub.amountInPaise ?? 0) / 100}` : "₹0"}
                    </span>
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
              ))}
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
    </section>
  );
}
