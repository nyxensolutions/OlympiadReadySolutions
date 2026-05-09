"use client";

import { useState } from "react";
import { Crown, Loader2, X } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import type { CheckoutResponse } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => { open: () => void };
  }
}

type RazorpayOptions = {
  key: string;
  amount: number;
  currency: string;
  order_id: string;
  name: string;
  description: string;
  theme?: { color?: string };
  handler: (response: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }) => void | Promise<void>;
  modal?: { ondismiss?: () => void };
  prefill?: { email?: string; name?: string };
};

export function UpgradeModal({
  open,
  onClose,
  onUpgraded,
  reason
}: {
  open: boolean;
  onClose: () => void;
  onUpgraded: () => void;
  reason?: string;
}) {
  const { getToken } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  async function startCheckout() {
    setBusy(true);
    setError(null);
    try {
      if (!window.Razorpay) {
        throw new Error("Razorpay checkout failed to load. Refresh and try again.");
      }
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/billing/checkout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ plan: "ProMonthly" })
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
        handler: async (response) => {
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
                plan: order.planName
              })
            });
            if (!v.ok) throw new Error((await v.text()) || `Verify failed (${v.status})`);
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2 text-achiever-700">
          <Crown className="h-5 w-5" />
          <span className="text-sm font-semibold uppercase tracking-wide">Upgrade to Pro</span>
        </div>

        <h2 className="mt-3 text-2xl font-bold text-slate-900">
          ₹199 <span className="text-base font-medium text-slate-500">/ month</span>
        </h2>

        {reason && (
          <p className="mt-2 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{reason}</p>
        )}

        <ul className="mt-4 space-y-2 text-sm text-slate-700">
          <Bullet>Up to 50 papers per month</Bullet>
          <Bullet>Foundation, Advanced, and Olympiad-level questions</Bullet>
          <Bullet>Detailed AI explanations on every wrong answer</Bullet>
          <Bullet>Full-length timed mock tests</Bullet>
          <Bullet>Downloadable PDF with answer key</Bullet>
        </ul>

        <button
          type="button"
          onClick={startCheckout}
          disabled={busy}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {busy ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Opening secure checkout…
            </>
          ) : (
            <>Pay ₹199 with Razorpay</>
          )}
        </button>

        <p className="mt-3 text-center text-xs text-slate-500">
          Test mode · use Razorpay test card 4111 1111 1111 1111, any future expiry, any CVV.
        </p>

        {error && (
          <p className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2">
      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-600" />
      <span>{children}</span>
    </li>
  );
}
