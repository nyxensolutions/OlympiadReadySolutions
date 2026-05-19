"use client";

import { useEffect, useRef, useState } from "react";
import { X, Receipt, Crown, FileText, CheckCircle2, Clock, ChevronDown } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

interface SubscriptionRecord {
  type: "subscription";
  id: string;
  planName: string;
  startDate: string;
  endDate: string;
  isActive: boolean;
}

interface PdfRecord {
  type: "pdf";
  id: string;
  subject: string;
  grade: number;
  amountInPaise: number;
  isFree: boolean;
  razorpayOrderId: string;
  razorpayPaymentId: string;
  purchasedAt: string;
}

interface BillingHistory {
  currentTier: string;
  subscriptions: SubscriptionRecord[];
  pdfPurchases: PdfRecord[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function fmt(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

function paise(amount: number) {
  return amount === 0 ? "Free" : `₹${amount / 100}`;
}

export function PurchasesPanel({ onClose }: { onClose: () => void }) {
  const { getToken } = useAuth();
  const [data, setData] = useState<BillingHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let active = true;
    
    async function loadData() {
      try {
        const token = await getToken();
        const r = await fetch(`${API_URL}/api/billing/history`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        if (!r.ok) throw new Error("Failed to load billing history");
        const d = await r.json();
        if (active) setData(d);
      } catch (e: any) {
        if (active) setError(e.message);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadData();
    return () => { active = false; };
  }, [getToken]);

  // Close on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [onClose]);

  // Close on Escape
  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  const totalSpent = data
    ? data.pdfPurchases.reduce((sum, p) => sum + p.amountInPaise, 0)
    : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end" aria-modal="true" role="dialog">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div
        ref={panelRef}
        className="relative z-10 mr-2 mt-16 w-full max-w-sm overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
        style={{ maxHeight: "calc(100vh - 80px)" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 bg-gradient-to-r from-brand-600 to-accent-600 px-5 py-4">
          <div className="flex items-center gap-2 text-white">
            <Receipt className="h-5 w-5" />
            <span className="font-bold text-base">My Purchases</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-white/80 transition hover:bg-white/20 hover:text-white"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="overflow-y-auto" style={{ maxHeight: "calc(100vh - 160px)" }}>
          {loading && (
            <div className="flex flex-col items-center gap-3 py-12 text-slate-400">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-300 border-t-brand-600" />
              <span className="text-sm">Loading your purchases…</span>
            </div>
          )}

          {error && (
            <div className="px-5 py-8 text-center text-sm text-rose-600">{error}</div>
          )}

          {data && (
            <div className="px-5 py-4 space-y-5">
              {/* Current Plan Banner */}
              <div
                className={`flex items-center gap-3 rounded-xl p-4 ${
                  data.currentTier === "Pro"
                    ? "bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200"
                    : "bg-slate-50 border border-slate-200"
                }`}
              >
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${
                  data.currentTier === "Pro" ? "bg-amber-100" : "bg-slate-100"
                }`}>
                  <Crown className={`h-5 w-5 ${data.currentTier === "Pro" ? "text-amber-600" : "text-slate-400"}`} />
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Current Plan</p>
                  <p className={`text-lg font-bold ${data.currentTier === "Pro" ? "text-amber-700" : "text-slate-700"}`}>
                    {data.currentTier}
                  </p>
                </div>
                {totalSpent > 0 && (
                  <div className="ml-auto text-right">
                    <p className="text-xs text-slate-400">Total spent</p>
                    <p className="text-sm font-semibold text-slate-700">{paise(totalSpent)}</p>
                  </div>
                )}
              </div>

              {/* Subscriptions */}
              {data.subscriptions.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-slate-400">
                    Pro Subscriptions
                  </p>
                  <div className="space-y-2">
                    {data.subscriptions.map((s) => (
                      <div
                        key={s.id}
                        className={`rounded-xl border p-3.5 ${
                          s.isActive
                            ? "border-brand-200 bg-brand-50"
                            : "border-slate-100 bg-white"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <Crown className={`h-4 w-4 shrink-0 ${s.isActive ? "text-brand-600" : "text-slate-400"}`} />
                            <span className="text-sm font-semibold text-slate-800">{s.planName}</span>
                          </div>
                          {s.isActive ? (
                            <span className="flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
                              <CheckCircle2 className="h-3 w-3" /> Active
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-500">
                              <Clock className="h-3 w-3" /> Expired
                            </span>
                          )}
                        </div>
                        <p className="mt-1.5 text-[11px] text-slate-500">
                          {fmt(s.startDate)} → {fmt(s.endDate)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* PDF Purchases */}
              {data.pdfPurchases.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-slate-400">
                    PDF Downloads
                  </p>
                  <div className="space-y-2">
                    {data.pdfPurchases.map((p) => (
                      <div key={p.id} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-3.5">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-rose-50">
                          <FileText className="h-4 w-4 text-rose-600" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-semibold text-slate-800">
                            Class {p.grade} · {p.subject}
                          </p>
                          <p className="text-[11px] text-slate-400">{fmt(p.purchasedAt)}</p>
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${
                            p.isFree
                              ? "bg-emerald-50 text-emerald-700"
                              : "bg-rose-50 text-rose-700"
                          }`}
                        >
                          {paise(p.amountInPaise)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state */}
              {data.subscriptions.length === 0 && data.pdfPurchases.length === 0 && (
                <div className="py-10 text-center">
                  <Receipt className="mx-auto mb-3 h-10 w-10 text-slate-200" />
                  <p className="text-sm font-medium text-slate-500">No purchases yet</p>
                  <p className="mt-1 text-xs text-slate-400">
                    Upgrade to Pro or buy a PDF to see your history here.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
