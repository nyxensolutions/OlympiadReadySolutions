"use client";

import Link from "next/link";
import { Crown, School } from "lucide-react";
import type { SubscriptionStatus } from "@/lib/types";

export function SubscriptionBadge({ status }: { status: SubscriptionStatus | null }) {
  if (!status) return null;

  const isPremium = status.tier === "Pro" || status.tier === "Modular";
  const isSchool = status.tier === "School";

  if (isSchool) {
    const daysLeft = status.school?.pilotEndsAt
      ? Math.max(0, Math.ceil((new Date(status.school.pilotEndsAt).getTime() - Date.now()) / 86_400_000))
      : null;
    return (
      <Link
        href="/dashboard#purchases"
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold cursor-pointer hover:opacity-80 transition-opacity bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
        title={status.school?.name ?? "School Pilot"}
      >
        <School className="h-3 w-3" />
        {daysLeft !== null ? `School Pilot · ${daysLeft}d left` : "School Pilot"}
      </Link>
    );
  }

  return (
    <Link
      href="/dashboard#purchases"
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold cursor-pointer hover:opacity-80 transition-opacity ${
        isPremium
          ? "bg-achiever-50 text-achiever-700 ring-1 ring-achiever-600/20"
          : "bg-slate-100 text-slate-700"
      }`}
      title={`${status.used} of ${status.limit} free papers used`}
    >
      {isPremium && <Crown className="h-3 w-3" />}
      {isPremium ? status.tier : `${status.limit - status.used} free papers left`}
    </Link>
  );
}
