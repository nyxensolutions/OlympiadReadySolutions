"use client";

import { SignUpButton, SignInButton } from "@clerk/nextjs";
import { ArrowRight, Clock, Sparkles } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-hero px-4 pb-24 pt-20 text-white sm:pt-28">
      {/* Animated background blobs */}
      <div className="pointer-events-none absolute inset-0 opacity-30">
        <div className="absolute right-20 top-10 h-80 w-80 rounded-full bg-violet-500 blur-3xl" />
        <div className="absolute bottom-10 left-10 h-72 w-72 rounded-full bg-indigo-400 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent-600/20 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-5xl text-center">
        {/* Badge */}
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 backdrop-blur-md">
          <Sparkles className="h-4 w-4 text-yellow-300" />
          <span className="text-sm font-medium">India&apos;s first AI-powered Olympiad coach</span>
        </div>

        {/* Headline */}
        <h1 className="mb-6 text-balance text-4xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl">
          Prepare smarter for{" "}
          <span className="text-yellow-300">every Olympiad.</span>
        </h1>

        {/* Sub-headline */}
        <p className="mx-auto mb-10 max-w-2xl text-lg text-white/90 sm:text-xl">
          AI-generated practice papers, instant explanations, and topic-by-topic mastery
          tracking — built for IMO, NSO, IEO, IGKO and every major school Olympiad.
        </p>

        {/* CTAs */}
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <SignUpButton mode="modal">
            <button className="inline-flex items-center gap-2 rounded-xl bg-cta-600 px-8 py-4 font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700 hover:shadow-xl">
              Start practising — it&apos;s free
              <ArrowRight className="h-5 w-5" />
            </button>
          </SignUpButton>
          <SignInButton mode="modal">
            <button className="rounded-xl border border-white/30 bg-white/10 px-8 py-4 font-semibold text-white backdrop-blur-sm transition hover:bg-white/20">
              Sign in
            </button>
          </SignInButton>
        </div>

        {/* Inline social proof */}
        <div className="mt-12 flex flex-col items-center gap-8 sm:flex-row sm:justify-center">
          {[
            { value: "500+",  label: "Students practising" },
            { value: "8",     label: "Subjects covered"    },
            { value: "∞",     label: "Fresh questions"     },
          ].map(({ value, label }, i) => (
            <div key={label} className="flex items-center gap-4">
              {i > 0 && <div className="hidden h-10 w-px bg-white/20 sm:block" />}
              <div className="text-center">
                <div className="text-3xl font-extrabold">{value}</div>
                <div className="text-sm text-white/70">{label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Demo question card */}
        <div className="mx-auto mt-14 max-w-lg rounded-2xl border border-white/20 bg-white/10 p-5 text-left shadow-2xl backdrop-blur-sm">
          <div className="mb-3 flex items-center gap-2 text-xs font-semibold text-blue-200">
            <span className="rounded-full bg-white/10 px-2 py-0.5">
              Class 7 · Math · Olympiad Level
            </span>
            <span className="ml-auto flex items-center gap-1">
              <Clock className="h-3 w-3" /> 1:30
            </span>
          </div>
          <p className="text-sm font-semibold leading-snug text-white">
            If 3x + 7 = 22, what is the value of x²?
          </p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {["A)  5", "B)  15", "C)  25 ✓", "D)  35"].map((opt, i) => (
              <div
                key={opt}
                className={`rounded-lg border px-3 py-2 text-sm text-white ${
                  i === 2
                    ? "border-yellow-400 bg-yellow-400/10 font-semibold"
                    : "border-white/20 bg-white/5"
                }`}
              >
                {opt}
              </div>
            ))}
          </div>
          <div className="mt-3 rounded-lg border border-emerald-400/30 bg-emerald-500/20 px-3 py-2 text-xs text-emerald-200">
            <span className="font-semibold">AI Explanation:</span> Subtract 7 → 3x = 15 →
            x = 5. Therefore x² = <strong>25</strong>.
          </div>
        </div>
      </div>
    </section>
  );
}
