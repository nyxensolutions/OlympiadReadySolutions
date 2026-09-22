"use client";

import Image from "next/image";
import { SignUpButton, SignInButton } from "@clerk/nextjs";
import { ArrowRight, Bot, Sparkles, TrendingUp } from "lucide-react";

const STATS = [
  { value: "50,000+", label: "Questions" },
  { value: "9",       label: "Olympiads"  },
  { value: "Class 1–12", label: "All Subjects & Levels" },
];

const PILLS = [
  { icon: <Bot className="h-4 w-4" />,         label: "AI Doubt Solver",       sub: "Get instant help",       color: "bg-blue-500/20 border-blue-400/30 text-blue-100" },
  { icon: <Sparkles className="h-4 w-4" />,    label: "Personalised Practice", sub: "As per your level",      color: "bg-violet-500/20 border-violet-400/30 text-violet-100" },
  { icon: <TrendingUp className="h-4 w-4" />,  label: "Track Your Progress",   sub: "See real improvement",   color: "bg-emerald-500/20 border-emerald-400/30 text-emerald-100" },
];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-hero px-4 pb-16 pt-10 text-white sm:pt-16">

      {/* Background blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute right-0 top-0 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute bottom-0 left-0 h-[400px] w-[400px] rounded-full bg-violet-700/20 blur-3xl" />
      </div>

      {/* Doodles overlay */}
      <div className="doodle-overlay absolute inset-0 bg-[url('/kids-ui/decor/doodles.png')] bg-cover bg-center" />

      <div className="relative mx-auto max-w-6xl">
        <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">

          {/* ── Left: copy ── */}
          <div className="order-2 text-center lg:order-1 lg:text-left">
            {/* Badge */}
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-yellow-400/40 bg-yellow-400/10 px-4 py-1.5 backdrop-blur-sm">
              <Sparkles className="h-3.5 w-3.5 text-yellow-300 sparkle" />
              <span className="text-sm font-semibold text-yellow-200">India&apos;s #1 AI-Powered Olympiad Coach</span>
            </div>

            {/* Headline */}
            <h1 className="mb-5 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
              Prepare smarter<br />
              for{" "}
              <span className="gradient-text">every Olympiad.</span>
            </h1>

            {/* Sub-headline */}
            <p className="mb-8 text-base leading-relaxed text-white/80 sm:text-lg lg:max-w-lg">
              AI-generated practice papers, interactive AI doubt chatbot, and topic-by-topic mastery
              tracking — for IMO, NSO, IEO, IGKO, Spell Bee & every major school Olympiad.
              Prepare for{" "}
              <span className="font-bold text-yellow-300">Level 1 or Level 2</span>{" "}
              with questions calibrated to your round.
            </p>

            {/* CTAs — all three on one row, wrap gracefully */}
            <div className="mb-8 flex flex-wrap items-center justify-center gap-3 lg:justify-start">
              <SignUpButton mode="modal">
                <button className="inline-flex items-center gap-2 rounded-2xl bg-cta-600 px-6 py-3 text-base font-bold text-white shadow-glow-orange transition hover:bg-cta-700 hover:scale-105 active:scale-95">
                  Start practising — it&apos;s free
                  <ArrowRight className="h-5 w-5" />
                </button>
              </SignUpButton>
              <a
                href="#try-it"
                className="inline-flex items-center gap-2 rounded-2xl border border-white/30 bg-white/10 px-5 py-3 text-base font-semibold text-white backdrop-blur-sm transition hover:bg-white/20 hover:scale-105 active:scale-95"
              >
                <Sparkles className="h-4 w-4 text-yellow-300" />
                Try it now
              </a>
              <SignInButton mode="modal">
                <button className="rounded-2xl border border-white/20 bg-transparent px-5 py-3 text-base font-semibold text-white transition hover:bg-white/10 hover:scale-105 active:scale-95">
                  Sign in
                </button>
              </SignInButton>
            </div>

            {/* Feature pills — single row on sm+ */}
            <div className="flex flex-wrap items-center justify-center gap-2 lg:justify-start">
              {PILLS.map(({ icon, label, sub, color }, i) => (
                <div
                  key={label}
                  className={`pill-animate pill-animate-d${i + 1} flex items-center gap-2 rounded-2xl border px-3 py-2 backdrop-blur-sm ${color}`}
                >
                  <div className="shrink-0">{icon}</div>
                  <div className="text-left">
                    <p className="text-xs font-bold leading-none sm:text-sm">{label}</p>
                    <p className="mt-0.5 text-[10px] opacity-70 sm:text-xs">{sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── Right: character ── */}
          <div className="relative order-1 flex justify-center lg:order-2 lg:justify-end">
            {/* Glow circle behind character */}
            <div className="absolute bottom-0 left-1/2 h-48 w-48 -translate-x-1/2 rounded-full bg-blue-500/20 blur-3xl sm:h-64 sm:w-64" />

            {/* Boy + Dream Learn grouped so they stay together at every screen size */}
            <div className="relative w-fit animate-float">
              {/* Hero character */}
              <div className="relative z-0 h-72 w-56 sm:h-96 sm:w-72 lg:h-[480px] lg:w-80">
                <Image
                  src="/kids-ui/hero/boy.png"
                  alt="OlympiadReady student"
                  fill
                  sizes="(max-width: 640px) 224px, (max-width: 1024px) 288px, 320px"
                  className="object-contain object-bottom drop-shadow-2xl"
                  priority
                />
              </div>

              {/* "Dream Learn Achieve" — always top-right of the boy, never detaches */}
              <div className="absolute -right-14 top-4 z-10 w-20 animate-float-slow sm:-right-16 sm:top-6 sm:w-28 lg:-right-20 lg:top-8 lg:w-36">
                <Image
                  src="/kids-ui/hero/dream-learn-achieve.png"
                  alt="Dream Learn Achieve"
                  width={144}
                  height={96}
                  className="object-contain drop-shadow-lg"
                />
              </div>
            </div>
          </div>
        </div>

        {/* ── Stats bar ── */}
        <div className="mt-10 grid grid-cols-3 gap-4 rounded-2xl border border-white/10 bg-white/5 py-6 backdrop-blur-sm sm:gap-8">
          {STATS.map(({ value, label }, i) => (
            <div key={label} className="relative flex flex-col items-center text-center">
              {i > 0 && (
                <div className="absolute left-0 top-1/2 h-8 w-px -translate-y-1/2 bg-white/20" />
              )}
              <span className="stat-num text-2xl font-extrabold text-white sm:text-3xl">{value}</span>
              <span className="mt-1 text-xs font-medium text-white/60 sm:text-sm">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
