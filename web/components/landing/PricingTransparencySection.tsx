"use client";

import { SignUpButton } from "@clerk/nextjs";
import { ArrowRight, Check, X } from "lucide-react";

const COMPARISON = [
  { label: "Unlimited practice papers", olympiadReady: true, tutor: false },
  { label: "AI explanations for every question", olympiadReady: true, tutor: false },
  { label: "Available 24/7", olympiadReady: true, tutor: false },
  { label: "SOF-aligned, Level 1 & 2 ready", olympiadReady: true, tutor: true },
  { label: "Progress tracking & weak area alerts", olympiadReady: true, tutor: false },
  { label: "Practice on any device", olympiadReady: true, tutor: false },
];

export function PricingTransparencySection() {
  return (
    <section className="bg-slate-50 px-4 py-20 sm:py-28">
      <div className="mx-auto max-w-5xl">
        <div className="mb-12 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Honest pricing
          </p>
          <h2 className="mt-2 text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Less than one tutor session.<br />Every day of the year.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600">
            The average Olympiad tutor charges ₹600–₹1,200 per hour. OlympiadReady costs ₹129 per subject per month — that&apos;s unlimited practice, every day.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 max-w-2xl mx-auto mb-10">
          {/* OlympiadReady card */}
          <div className="rounded-2xl border-2 border-brand-500 bg-white p-6 shadow-lg relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-600 px-4 py-1 text-xs font-bold text-white">
              Best value
            </div>
            <div className="mb-4 text-center">
              <p className="text-sm font-semibold text-brand-600 uppercase tracking-wide">OlympiadReady</p>
              <div className="mt-2">
                <span className="text-4xl font-extrabold text-slate-900">₹129</span>
                <span className="text-slate-500 text-sm ml-1">/ subject / month</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">≈ ₹4.30 per day</p>
            </div>
            <ul className="space-y-2">
              {COMPARISON.map(({ label, olympiadReady }) => (
                <li key={label} className="flex items-center gap-2 text-sm">
                  {olympiadReady
                    ? <Check className="h-4 w-4 shrink-0 text-emerald-500" />
                    : <X className="h-4 w-4 shrink-0 text-slate-300" />}
                  <span className={olympiadReady ? "text-slate-700" : "text-slate-400"}>{label}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Tutor card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <div className="mb-4 text-center">
              <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Private Tutor</p>
              <div className="mt-2">
                <span className="text-4xl font-extrabold text-slate-900">₹800+</span>
                <span className="text-slate-500 text-sm ml-1">/ hour</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">₹3,200+ for 4 sessions/month</p>
            </div>
            <ul className="space-y-2">
              {COMPARISON.map(({ label, tutor }) => (
                <li key={label} className="flex items-center gap-2 text-sm">
                  {tutor
                    ? <Check className="h-4 w-4 shrink-0 text-emerald-500" />
                    : <X className="h-4 w-4 shrink-0 text-slate-300" />}
                  <span className={tutor ? "text-slate-700" : "text-slate-400"}>{label}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="text-center">
          <SignUpButton mode="modal">
            <button className="inline-flex items-center gap-2 rounded-xl bg-cta-600 px-8 py-4 font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700 hover:shadow-xl">
              Start practising — it&apos;s free
              <ArrowRight className="h-5 w-5" />
            </button>
          </SignUpButton>
          <p className="mt-3 text-sm text-slate-500">No credit card required. Cancel anytime.</p>
        </div>
      </div>
    </section>
  );
}
