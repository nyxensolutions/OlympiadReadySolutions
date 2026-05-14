"use client";

import { SignUpButton, SignInButton } from "@clerk/nextjs";
import { Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="bg-gradient-hero px-4 py-24 text-white">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="mb-6 text-balance text-3xl font-extrabold tracking-tight sm:text-5xl">
          Start your Olympiad journey today.
        </h2>
        <p className="mx-auto mb-10 max-w-xl text-lg text-white/90">
          Free to start. No credit card. Get your first AI-generated practice paper
          in under 60 seconds.
        </p>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <SignUpButton mode="modal">
            <button className="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 font-bold text-blue-700 shadow-lg transition hover:bg-blue-50 hover:shadow-xl">
              <Sparkles className="h-5 w-5" />
              Create free account
            </button>
          </SignUpButton>
          <SignInButton mode="modal">
            <button className="rounded-xl border border-white/30 bg-white/10 px-8 py-4 font-semibold text-white backdrop-blur-sm transition hover:bg-white/20">
              Already have an account?
            </button>
          </SignInButton>
        </div>
        <p className="mt-6 text-sm text-white/70">
          Covers IMO · NSO · IEO · IGKO · IHO · ICSO · iiO and more
        </p>
      </div>
    </section>
  );
}
