import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Sparkles } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { GeneratorFlow } from "@/components/GeneratorFlow";
import { LandingPage } from "@/components/LandingPage";

export default function Home() {
  return (
    <>
      {/* ── Signed-out: full marketing landing page ── */}
      <SignedOut>
        <div className="min-h-screen bg-white">
          <AppHeader active="home" />
          <LandingPage />
        </div>
      </SignedOut>

      {/* ── Signed-in: full-page generator experience ── */}
      <SignedIn>
        <div className="min-h-screen bg-slate-50">
          <AppHeader active="home" />

          {/* Gradient page banner */}
          <div className="bg-gradient-brand px-4 py-10 text-white">
            <div className="mx-auto max-w-6xl">
              <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">
                Practice Session
              </p>
              <h1 className="mt-1 flex items-center gap-3 text-2xl font-extrabold sm:text-3xl">
                <Sparkles className="h-7 w-7 text-yellow-300" />
                What would you like to practice today?
              </h1>
              <p className="mt-2 max-w-xl text-sm text-brand-200">
                Pick a subject, class, and difficulty — Claude AI generates a fresh,
                exam-style paper in seconds.
              </p>
            </div>
          </div>

          {/* Generator content */}
          <div className="mx-auto max-w-6xl px-4 py-8">
            <GeneratorFlow />
          </div>
        </div>
      </SignedIn>
    </>
  );
}
