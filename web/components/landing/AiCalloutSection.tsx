"use client";

import { Sparkles } from "lucide-react";

const POINTS = [
  "Fresh questions generated on demand — never repeated",
  "Step-by-step explanations, not just correct / wrong",
  "Questions calibrated to Foundation, Advanced & Olympiad levels",
  "Aligned to SOF, SilverZone, Unified Council syllabi",
];

export function AiCalloutSection() {
  return (
    <section className="bg-white px-4 py-20">
      <div className="mx-auto max-w-4xl">
        <div className="overflow-hidden rounded-3xl bg-gradient-hero p-8 text-white shadow-xl sm:p-12">
          <div className="grid gap-8 sm:grid-cols-2 sm:items-center">
            <div>
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold">
                <Sparkles className="h-3.5 w-3.5 text-yellow-300" />
                Powered by AI
              </div>
              <h2 className="text-2xl font-extrabold leading-tight sm:text-3xl">
                Not a question bank.
                <br />
                A personal AI coach.
              </h2>
              <p className="mt-4 text-sm leading-relaxed text-blue-100">
                Every other platform serves the same recycled question pool to every
                student. OlympiadReady uses advanced AI to generate fresh,
                syllabus-aligned questions tailored to your exact class and level.
                Every. Single. Session.
              </p>
            </div>
            <div className="space-y-3">
              {POINTS.map((point) => (
                <div key={point} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-400/20 text-emerald-300">
                    <svg
                      viewBox="0 0 12 12"
                      className="h-3 w-3"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M2 6l3 3 5-5" />
                    </svg>
                  </div>
                  <p className="text-sm text-blue-100">{point}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
