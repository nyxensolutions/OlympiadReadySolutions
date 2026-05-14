import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Sparkles } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { GeneratorFlow } from "@/components/GeneratorFlow";
import { LandingPage } from "@/components/LandingPage";

export default function Home() {
  return (
    <>
      {/* Signed-out: full marketing landing page with AppHeader */}
      <SignedOut>
        <div className="min-h-screen bg-white">
          <AppHeader active="home" />
          <LandingPage />
        </div>
      </SignedOut>

      {/* Signed-in: generator app */}
      <SignedIn>
        <main className="mx-auto flex min-h-screen max-w-5xl flex-col items-center px-4 py-10 sm:py-16">
          <AppHeader active="home" />

          <section className="mt-8 flex w-full flex-col items-center gap-1 text-center">
            <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              <Sparkles className="h-6 w-6 text-brand-600" />
              Generate your practice paper
            </h1>
            <p className="text-sm text-slate-500">
              Pick a subject, class, and difficulty — AI builds a fresh paper in seconds.
            </p>
          </section>

          <section className="mt-8 flex w-full justify-center">
            <GeneratorFlow />
          </section>
        </main>
      </SignedIn>
    </>
  );
}
