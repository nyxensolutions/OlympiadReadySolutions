"use client";

import Image from "next/image";
import { SignUpButton, SignInButton } from "@clerk/nextjs";
import { ArrowRight, Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="relative overflow-hidden bg-gradient-hero px-4 py-20 text-white">
      {/* Background blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-0 top-0 h-64 w-64 rounded-full bg-violet-600/20 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-5xl">
        <div className="flex flex-col items-center gap-8 text-center lg:flex-row lg:text-left">
          {/* Character */}
          <div className="relative h-48 w-36 shrink-0 animate-float lg:h-64 lg:w-48">
            <Image
              src="/kids-ui/internal/mascot-wave.png"
              alt="OlympiadReady mascot waving"
              fill
              sizes="192px"
              className="object-contain object-bottom drop-shadow-xl"
            />
          </div>

          {/* Copy */}
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-yellow-400/20 border border-yellow-400/30 px-4 py-1.5">
              <Sparkles className="h-3.5 w-3.5 text-yellow-300 sparkle" />
              <span className="text-sm font-bold text-yellow-200">Free to start — no credit card needed</span>
            </div>
            <h2 className="mb-4 text-3xl font-extrabold tracking-tight sm:text-5xl">
              Start your Olympiad journey today! 🚀
            </h2>
            <p className="mb-8 text-lg text-white/80 lg:max-w-xl">
              Get your first AI-generated practice paper in under 60 seconds.
              Join hundreds of students preparing smarter for IMO, NSO, IEO & more.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 lg:justify-start">
              <SignUpButton mode="modal">
                <button className="inline-flex items-center gap-2 rounded-2xl bg-cta-600 px-8 py-4 text-base font-bold text-white shadow-glow-orange transition hover:bg-cta-700 hover:scale-105 active:scale-95">
                  <Sparkles className="h-5 w-5" />
                  Create free account
                  <ArrowRight className="h-5 w-5" />
                </button>
              </SignUpButton>
              <SignInButton mode="modal">
                <button className="rounded-2xl border border-white/30 bg-white/10 px-8 py-4 text-base font-semibold text-white backdrop-blur-sm transition hover:bg-white/20 hover:scale-105 active:scale-95">
                  Already have an account?
                </button>
              </SignInButton>
            </div>
            <p className="mt-5 text-sm text-white/50">
              Covers IMO · NSO · IEO · IGKO · IHO · ICSO · iiO · Spell Bee and more
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
