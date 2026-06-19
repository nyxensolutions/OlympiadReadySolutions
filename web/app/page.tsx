import Link from "next/link";
import { SignedIn, SignedOut } from "@clerk/nextjs";
import { Sparkles, Award } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { PracticeShell } from "@/components/PracticeShell";
import { LandingPage } from "@/components/LandingPage";
import type { PreviewRequest } from "@/lib/types";

export default function Home({
  searchParams
}: {
  searchParams?: { subject?: string; grade?: string; difficulty?: string; topic?: string; mistakes?: string; count?: string };
}) {
  const initialConfig: Partial<PreviewRequest> | undefined =
    searchParams && Object.keys(searchParams).length > 0
      ? {
          subject: searchParams.subject,
          grade: searchParams.grade ? Number(searchParams.grade) : undefined,
          difficulty: searchParams.difficulty,
          count: searchParams.count ? Number(searchParams.count) : undefined,
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
              
              <div className="mt-6 flex flex-wrap gap-4">
                <Link href="/mock-exams" className="flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-600 shadow-md transition hover:bg-slate-50 hover:shadow-lg">
                  <Award className="h-4 w-4" />
                  Take a Full Mock Exam
                </Link>
              </div>
            </div>
          </div>

          {/* Generator content */}
          <div className="mx-auto max-w-6xl px-4 py-8">
            <PracticeShell initialConfig={initialConfig} />

            {/* FAQ Section */}
            <div className="mt-16 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm relative z-10">
              <h3 className="mb-4 flex items-center gap-2 font-bold text-slate-900">
                <Sparkles className="h-4 w-4 text-brand-500" />
                Frequently Asked Questions
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[
                  {
                    q: "How many free online attempts do I get?",
                    a: "Free users get 15 practice papers across any class or subject — enough to properly experience the platform before deciding to subscribe.",
                  },
                  {
                    q: "What happens if I subscribe to a subject?",
                    a: "Subscribed subjects unlock unlimited online practice and AI-generated questions! They no longer count towards your free attempt limit, allowing you to master those subjects fully.",
                  },
                  {
                    q: "Can I subscribe to all subjects?",
                    a: "Yes! You can choose the 'All Subjects' Max Value Bundle which unlocks unlimited practice for every subject in your grade.",
                  },
                  {
                    q: "Is there an AI Tutor to help me?",
                    a: "Yes! Every question includes an Interactive AI Doubt Chatbot. Free users get 10 free chats across all tests. Upgrading unlocks unlimited chats for that subject (up to 20 chats per question).",
                  },
                  {
                    q: "Do I get PDF downloads with my subscription?",
                    a: "Yes! Subscribed subjects include 10 free full-length (50 question) PDF paper downloads every week. The limit resets every Monday.",
                  },
                  {
                    q: "Are the questions repetitive?",
                    a: "No. Our AI generates a fresh, exam-ready paper in seconds every time you click 'Generate & Start Test', ensuring no repeats.",
                  },
                  {
                    q: "What is Exam Simulation Mode?",
                    a: "It's a full-screen, timed environment without navigation, mirroring a real exam hall. You'll view an OMR sheet upon completion.",
                  },
                ].map(({ q, a }) => (
                  <div key={q} className="rounded-xl bg-slate-50 p-4">
                    <p className="mb-1 text-sm font-semibold text-slate-800">{q}</p>
                    <p className="text-xs leading-relaxed text-slate-600">{a}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </SignedIn>
    </>
  );
}
