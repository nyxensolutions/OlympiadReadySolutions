"use client";

import { Award, BookOpen, Clock, FileText } from "lucide-react";

const STEPS = [
  {
    icon: FileText,
    title: "Generate paper",
    description:
      "Pick your subject, class, and difficulty. Claude AI instantly builds a fresh exam-style paper — Foundation, Advanced, or full Olympiad level.",
  },
  {
    icon: Clock,
    title: "Take the test",
    description:
      "Solve questions under a real countdown timer, just like the actual Olympiad. Flag tricky questions and jump between them freely.",
  },
  {
    icon: BookOpen,
    title: "Review explanations",
    description:
      "Get instant results with AI-written step-by-step explanations for every question — not just correct/wrong.",
  },
  {
    icon: Award,
    title: "Track & improve",
    description:
      "Your mastery heatmap and score trend update after every test. Spot weak topics, earn badges, and watch your confidence grow.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="bg-slate-50 px-4 py-20 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            How it works
          </p>
          <h2 className="mt-2 text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Four steps to Olympiad confidence
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            From paper generation to mastery tracking in minutes.
          </p>
        </div>

        <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map(({ icon: Icon, title, description }, index) => (
            <div key={title} className="relative">
              {/* Connector line */}
              {index < STEPS.length - 1 && (
                <div className="absolute -right-6 top-7 hidden h-0.5 w-12 bg-gradient-to-r from-brand-600 to-accent-600 lg:block" />
              )}

              <div className="flex flex-col items-start">
                {/* Step number circle */}
                <div className="mb-6 inline-flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-brand-600 to-accent-600 text-2xl font-bold text-white shadow-md">
                  {index + 1}
                </div>

                {/* Icon */}
                <div className="mb-4 rounded-xl bg-brand-50 p-3 text-brand-600">
                  <Icon className="h-6 w-6" />
                </div>

                <h3 className="mb-2 text-lg font-bold text-slate-900">{title}</h3>
                <p className="leading-relaxed text-slate-600">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
