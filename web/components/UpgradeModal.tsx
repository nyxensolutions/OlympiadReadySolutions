"use client";

import { useEffect, useState, useMemo } from "react";
import { Crown, Loader2, X, Check, Info } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import { SUBJECTS, isSubjectAvailable, type CheckoutResponse } from "@/lib/types";
import { Analytics } from "@/lib/analytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

declare global {
  interface Window {
    Razorpay?: new (options: any) => { open: () => void };
  }
}

export function UpgradeModal({
  open,
  onClose,
  onUpgraded,
  reason,
  initialGrade,
  initialSubject
}: {
  open: boolean;
  onClose: () => void;
  onUpgraded: () => void;
  reason?: string;
  initialGrade?: number;
  initialSubject?: string;
}) {
  const { getToken } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [grade, setGrade] = useState<number>(initialGrade || 5);
  const [billingCycle, setBillingCycle] = useState<"Monthly" | "Annual">("Annual");
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>(
    initialSubject ? [initialSubject] : []
  );
  const [step, setStep] = useState<"build" | "confirm">("build");

  // When props change, respect them
  useEffect(() => {
    if (initialGrade) setGrade(initialGrade);
    if (initialSubject && !selectedSubjects.includes(initialSubject)) {
      setSelectedSubjects([initialSubject]);
    }
  }, [initialGrade, initialSubject]);

  useEffect(() => {
    if (open) Analytics.upgradeModalOpened(reason);
  }, [open, reason]);

  const availableSubjects = useMemo(() => {
    return SUBJECTS.filter((s) => isSubjectAvailable(s, grade));
  }, [grade]);

  // If user changes grade and some selected subjects are not available, remove them
  useEffect(() => {
    setSelectedSubjects((prev) => prev.filter((s) => availableSubjects.includes(s as any) || s === "All"));
  }, [availableSubjects]);

  const isAllSelected = selectedSubjects.includes("All") || selectedSubjects.length === availableSubjects.length;

  function handleToggleSubject(subj: string) {
    if (isAllSelected && subj !== "All") {
      // If "All" was selected, and user clicks a specific subject, we switch to ONLY that subject.
      setSelectedSubjects([subj]);
      return;
    }

    if (subj === "All") {
      setSelectedSubjects(isAllSelected ? [] : ["All"]);
    } else {
      setSelectedSubjects((prev) => {
        // Remove "All" if it was explicitly there
        let next = prev.filter(s => s !== "All");
        if (next.includes(subj)) {
          next = next.filter((s) => s !== subj);
        } else {
          next.push(subj);
        }
        return next;
      });
    }
  }

  // Calculate Prices Locally — must match backend RazorpayService.CalculatePrice exactly.
  // ₹129 per subject/month. 3+ subjects in one purchase → 5% off total.
  // Annual = monthly (rounded up) × 10.
  const isAnnual = billingCycle === "Annual";
  const count = isAllSelected ? availableSubjects.length : selectedSubjects.length;

  const perSubject = 129;
  const discount   = count >= 3 ? 0.95 : 1.0;
  const monthly    = count > 0 ? Math.ceil(count * perSubject * discount) : 0;
  const price      = count > 0 ? (isAnnual ? monthly * 10 : monthly) : 0;
  // Show annual saving vs paying monthly for 12 months
  const originalPrice = isAnnual && count > 0 ? monthly * 12 : 0;

  if (!open) return null;

  async function startCheckout() {
    if (count === 0) {
      setError("Please select at least one subject.");
      return;
    }
    
    setBusy(true);
    setError(null);
    try {
      if (!window.Razorpay) {
        throw new Error("Razorpay checkout failed to load. Refresh and try again.");
      }
      const token = await getToken();
      
      // Determine what to send
      const payloadSubjects = isAllSelected ? availableSubjects : selectedSubjects;

      const res = await fetch(`${API_URL}/api/billing/checkout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ 
          billingCycle,
          grade,
          subjects: payloadSubjects
        })
      });
      if (!res.ok) throw new Error((await res.text()) || `Checkout failed (${res.status})`);
      const order: CheckoutResponse = await res.json();

      const rzp = new window.Razorpay({
        key: order.keyId,
        amount: order.amount,
        currency: order.currency,
        order_id: order.orderId,
        name: "Olympiad Ready",
        description: order.planDisplayName,
        theme: { color: "#2563eb" },
        modal: {
          ondismiss: () => setBusy(false)
        },
        handler: async (response: any) => {
          try {
            const verifyToken = await getToken();
            const v = await fetch(`${API_URL}/api/billing/verify`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                ...(verifyToken ? { Authorization: `Bearer ${verifyToken}` } : {})
              },
              body: JSON.stringify({
                orderId: response.razorpay_order_id,
                paymentId: response.razorpay_payment_id,
                signature: response.razorpay_signature,
                billingCycle,
                grade,
                subjects: payloadSubjects
              })
            });
            if (!v.ok) throw new Error((await v.text()) || `Verify failed (${v.status})`);
            Analytics.upgradeCompleted();
            onUpgraded();
            onClose();
          } catch (err) {
            setError(err instanceof Error ? err.message : "Verification failed");
          } finally {
            setBusy(false);
          }
        }
      });
      rzp.open();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50">
      <div className="flex min-h-full items-center justify-center p-4 py-8">
        <div className="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>

        {step === "build" ? (
          <>
            <div className="flex items-center gap-2 text-brand-700">
              <Crown className="h-5 w-5" />
              <span className="text-sm font-semibold uppercase tracking-wide">Unlock Practice</span>
            </div>

            <h2 className="mt-2 text-2xl font-bold text-slate-900">
              Build Your Subscription
            </h2>

            {reason && (
              <p className="mt-2 rounded-lg bg-blue-50 border border-blue-100 p-3 text-sm text-blue-800">
                <Info className="inline h-4 w-4 mr-1 mb-0.5" />
                {reason}
              </p>
            )}

            {/* Grade Selection */}
            <div className="mt-6">
              <label className="text-sm font-semibold text-slate-700">Select Class/Grade</label>
              <select 
                value={grade}
                onChange={(e) => setGrade(Number(e.target.value))}
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                {Array.from({ length: 12 }).map((_, i) => (
                  <option key={i + 1} value={i + 1}>Class/Grade {i + 1}</option>
                ))}
              </select>
            </div>

        {/* Subjects Selection */}
        <div className="mt-6">
          <label className="flex items-center justify-between text-sm font-semibold text-slate-700">
            <span>Select Subjects</span>
            {count >= 3 && (
              <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                5% off applied
              </span>
            )}
          </label>
          
          <div className="mt-3 grid grid-cols-2 gap-2">
            <button
              onClick={() => handleToggleSubject("All")}
              className={`relative flex items-center justify-between rounded-lg border p-3 text-sm font-medium transition-colors ${
                isAllSelected
                  ? "border-purple-600 bg-purple-50 text-purple-900 shadow-sm"
                  : "border-slate-200 hover:border-purple-300 hover:bg-purple-50/50 text-slate-700"
              }`}
            >
              All Subjects
              {isAllSelected && <Check className="h-4 w-4 text-purple-600" />}
            </button>
            
            {availableSubjects.map((subj) => {
              const isSelected = isAllSelected || selectedSubjects.includes(subj);
              return (
                <button
                  key={subj}
                  onClick={() => handleToggleSubject(subj)}
                  className={`flex items-center justify-between rounded-lg border p-3 text-sm font-medium transition-colors ${
                    isSelected
                      ? "border-brand-600 bg-brand-50 text-brand-900 shadow-sm"
                      : "border-slate-200 hover:border-brand-300 hover:bg-brand-50/50 text-slate-700"
                  }`}
                >
                  {subj}
                  {isSelected && <Check className="h-4 w-4 text-brand-600" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Billing Cycle Toggle */}
        <div className="mt-6 flex justify-center">
          <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1">
            <button
              onClick={() => setBillingCycle("Monthly")}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-all ${
                billingCycle === "Monthly" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle("Annual")}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-all ${
                billingCycle === "Annual" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Annual
              <span className="ml-1.5 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-700 uppercase tracking-wide">
                2 months free
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Display */}
        <div className="mt-6 text-center">
          <div className="flex items-end justify-center gap-2">
            <span className="text-4xl font-bold text-slate-900">₹{price}</span>
            <span className="text-base font-medium text-slate-500 mb-1">/ {billingCycle === "Annual" ? "yr" : "mo"}</span>
          </div>
          {isAnnual && originalPrice > 0 && (
            <p className="mt-1 text-sm text-slate-500">
              vs monthly{" "}
              <span className="line-through">₹{originalPrice}/yr</span>.{" "}
              <span className="font-semibold text-emerald-600">Save ₹{originalPrice - price}!</span>
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={() => { if (count > 0) setStep("confirm"); }}
          disabled={count === 0}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400 transition-all"
        >
          Review &amp; Confirm
        </button>
        </>
        ) : (
          <>
            <div className="flex items-center gap-2 text-brand-700">
              <Check className="h-5 w-5" />
              <span className="text-sm font-semibold uppercase tracking-wide">Confirm Purchase</span>
            </div>
            <h2 className="mt-2 text-2xl font-bold text-slate-900">
              Review your choices
            </h2>
            
            <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-4">
               <div className="flex justify-between border-b border-slate-200 pb-3">
                 <span className="text-sm text-slate-500">Class/Grade</span>
                 <span className="font-semibold text-slate-900">{grade}</span>
               </div>
               <div className="flex justify-between border-b border-slate-200 pb-3">
                 <span className="text-sm text-slate-500">Subjects ({count})</span>
                 <span className="font-semibold text-slate-900 text-right">
                   {isAllSelected ? "All Subjects" : selectedSubjects.join(", ")}
                 </span>
               </div>
               <div className="flex justify-between border-b border-slate-200 pb-3">
                 <span className="text-sm text-slate-500">Plan Duration</span>
                 <span className="font-semibold text-slate-900">{billingCycle}</span>
               </div>
               <div className="flex justify-between pt-1">
                 <span className="text-base font-bold text-slate-900">Total Amount</span>
                 <span className="text-xl font-bold text-brand-700">₹{price}</span>
               </div>
            </div>

            <button
              type="button"
              onClick={startCheckout}
              disabled={busy}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400 transition-all"
            >
              {busy ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" /> Processing securely…
                </>
              ) : (
                <>Confirm &amp; Pay ₹{price}</>
              )}
            </button>
            <button
              type="button"
              onClick={() => setStep("build")}
              disabled={busy}
              className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Back to edit
            </button>
          </>
        )}

        <p className="mt-3 text-center text-xs text-slate-500">
          Secured by Razorpay. Use test card 4111 1111 1111 1111.
        </p>

        {error && (
          <p className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </p>
        )}
        </div>
      </div>
    </div>
  );
}
