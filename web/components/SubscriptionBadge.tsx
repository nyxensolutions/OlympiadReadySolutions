"use client";

import { Crown } from "lucide-react";
import type { SubscriptionStatus } from "@/lib/types";

export function SubscriptionBadge({ status }: { status: SubscriptionStatus | null }) {
  if (!status) return null;

  const isPro = status.tier === "Pro";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
        isPro
          ? "bg-achiever-50 text-achiever-700 ring-1 ring-achiever-600/20"
          : "bg-slate-100 text-slate-700"
      }`}
      title={`${status.used} of ${status.limit} papers used this month`}
    >
      {isPro && <Crown className="h-3 w-3" />}
      {status.tier} · {status.used}/{status.limit}
    </span>
  );
}
