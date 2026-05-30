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
  const [billingCycle, setBillingCycle] = useState<"Monthly" | "Annual">("Monthly");
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
  // Champion (All subjects): ₹649/mo · ₹3,999/yr (fixed).
  // Linear: ₹129/subject/month, 10% off for 3+, annual = monthly × 8.
  const isAnnual = billingCycle === "Annual";
  const count = isAllSelected ? availableSubjects.length : selectedSubjects.length;

  const isChampion = isAllSelected;
  let price = 0;
  let originalPrice = 0; // vs monthly × 12 for savings display
  let monthlyEquiv = 0;  // shown as "= ₹X/month" anchor under annual price

  if (isChampion) {
    price         = isAnnual ? 3999 : 649;
    originalPrice = isAnnual ? 649 * 12 : 0;
    monthlyEquiv  = isAnnual ? Math.round(3999 / 12) : 0;
  } else if (count > 0) {
    const perSubject = 129;
    const discount   = count >= 3 ? 0.90 : 1.0;
    const monthly    = Math.ceil(count * perSubject * discount);
    price         = isAnnual ? monthly * 8 : monthly;
    originalPrice = isAnnual ? monthly * 12 : 0;
    monthlyEquiv  = isAnnual ? Math.round(price / 12) : 0;
  }

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
      
      // Champion = send ["All"] sentinel; backend expands to every subject for the grade
      const payloadSubjects = isAllSelected ? ["All"] : selectedSubjects;

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
        <div className="relative w-full max-w-lg md:max-w-3xl rounded-2xl bg-white p-6 shadow-xl transition-all">
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

            <div className="mt-6 md:grid md:grid-cols-2 md:gap-6">
              {/* Left Column: Grade & Subjects */}
              <div className="flex flex-col min-h-0">
                {/* Grade Selection */}
                <div>
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
                <div className="mt-4 flex-1 flex flex-col min-h-0">
                  <label className="flex items-center justify-between text-sm font-semibold text-slate-700 mb-1.5">
                    <span>Select Subjects</span>
                    {!isChampion && count >= 3 && (
                      <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                        10% off
                      </span>
                    )}
                    {isChampion && (
                      <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">
                        Champion — Best Value
                      </span>
                    )}
                  </label>
                  
                  {/* Scrollable Container with custom height so it fits in laptop screen viewport */}
                  <div className="overflow-y-auto max-h-[200px] rounded-lg border border-slate-200 bg-slate-50/50 p-2 pr-1">
                    <div className="grid grid-cols-2 gap-1.5">
                      <button
                        onClick={() => handleToggleSubject("All")}
                        className={`relative flex items-center justify-between rounded-lg border p-2.5 text-xs font-medium transition-colors ${
                          isAllSelected
                            ? "border-purple-600 bg-purple-50 text-purple-900 shadow-sm"
                            : "border-slate-200 hover:border-purple-300 hover:bg-purple-50/50 text-slate-700 bg-white"
                        }`}
                      >
                        All Subjects
                        {isAllSelected && <Check className="h-3.5 w-3.5 text-purple-600 shrink-0" />}
                      </button>
                      
                      {availableSubjects.map((subj) => {
                        const isSelected = isAllSelected || selectedSubjects.includes(subj);
                        return (
                          <button
                            key={subj}
                            onClick={() => handleToggleSubject(subj)}
                            className={`flex items-center justify-between rounded-lg border p-2.5 text-xs font-medium transition-colors ${
                              isSelected
                                ? "border-brand-600 bg-brand-50 text-brand-900 shadow-sm"
                                : "border-slate-200 hover:border-brand-300 hover:bg-brand-50/50 text-slate-700 bg-white"
                            }`}
                          >
                            <span className="truncate mr-1">{subj}</span>
                            {isSelected && <Check className="h-3.5 w-3.5 text-brand-600 shrink-0" />}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Pricing & Checkout */}
              <div className="mt-6 md:mt-0 flex flex-col justify-between rounded-xl bg-slate-50 border border-slate-200 p-4">
                {/* Billing Cycle Toggle */}
                <div className="flex justify-center">
                  <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1">
                    <button
                      onClick={() => setBillingCycle("Monthly")}
                      className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                        billingCycle === "Monthly" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      Monthly
                    </button>
                    <button
                      onClick={() => setBillingCycle("Annual")}
                      className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                        billingCycle === "Annual" ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      Annual
                      <span className="ml-1 inline-block rounded-full bg-emerald-100 px-1.5 py-0.5 text-[9px] font-bold text-emerald-700 uppercase tracking-wide">
                        4 mos free
                      </span>
                    </button>
                  </div>
                </div>

                {/* Pricing Display */}
                <div className="my-auto py-4 text-center">
                  <div className="flex items-end justify-center gap-1">
                    <span className="text-3xl font-bold text-slate-900">₹{price}</span>
                    <span className="text-sm font-medium text-slate-500 mb-0.5">/ {billingCycle === "Annual" ? "yr" : "mo"}</span>
                  </div>
                  {isAnnual && monthlyEquiv > 0 && (
                    <p className="mt-0.5 text-xs font-semibold text-brand-600">= ₹{monthlyEquiv}/month</p>
                  )}
                  {isAnnual && originalPrice > 0 && (
                    <p className="mt-1 text-[11px] text-slate-500 leading-tight">
                      vs monthly billing{" "}
                      <span className="line-through">₹{originalPrice}/yr</span>
                      <br />
                      <span className="font-semibold text-emerald-600">Save ₹{originalPrice - price}</span>
                    </p>
                  )}
                </div>

                {/* Actions & CTA */}
                <div>
                  <button
                    type="button"
                    onClick={() => { if (count > 0) setStep("confirm"); }}
                    disabled={count === 0}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400 transition-all"
                  >
                    Review &amp; Confirm
                  </button>

                  {/* School / custom packages CTA */}
                  <p className="mt-2 text-center text-[10px] text-slate-400">
                    Need school pricing?{" "}
                    <a href="/contact?type=school" className="text-brand-600 underline hover:text-brand-700">
                      Custom packages →
                    </a>
                  </p>
                </div>
              </div>
            </div>
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
