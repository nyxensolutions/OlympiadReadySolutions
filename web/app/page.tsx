import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Sparkles } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { PracticeShell } from "@/components/PracticeShell";
import { LandingPage } from "@/components/LandingPage";
import type { PreviewRequest } from "@/lib/types";

export default function Home({
  searchParams
}: {
  searchParams?: { subject?: string; grade?: string; difficulty?: string; topic?: string; mistakes?: string };
}) {
  const initialConfig: Partial<PreviewRequest> | undefined =
    searchParams && Object.keys(searchParams).length > 0
      ? {
          subject: searchParams.subject,
          grade: searchParams.grade ? Number(searchParams.grade) : undefined,
          difficulty: searchParams.difficulty,
          topic: searchParams.topic,
          mistakesOnly: searchParams.mistakes === "true"
        }
      : undefined;

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
          <div className="bg-gradient-hero px-4 py-10 text-white">
            <div className="mx-auto max-w-6xl">
              <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">
                {initialConfig?.topic ? `Topic: ${initialConfig.topic}` : "Practice Session"}
              </p>
              <h1 className="mt-1 flex items-center gap-3 text-2xl font-extrabold sm:text-3xl">
                <Sparkles className="h-7 w-7 text-yellow-300" />
                {initialConfig?.topic
                  ? `Practice: ${initialConfig.topic}`
                  : "What would you like to practice today?"}
              </h1>
              <p className="mt-2 max-w-xl text-sm text-brand-200">
                {initialConfig?.topic
                  ? `Focused on ${initialConfig.topic} — ${initialConfig.subject ?? ""} Class ${initialConfig.grade ?? ""}.`
                  : "Pick a subject, class, and difficulty — AI generates a fresh, exam-style paper in seconds."}
              </p>
            </div>
          </div>

          {/* Generator content */}
          <div className="mx-auto max-w-6xl px-4 py-8">
            <PracticeShell initialConfig={initialConfig} />
          </div>
        </div>
      </SignedIn>
    </>
  );
}
