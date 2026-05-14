"use client";

import { Star } from "lucide-react";

const TESTIMONIALS = [
  {
    name: "Aarav Patel",
    role: "Class 10 Student",
    school: "Delhi Public School, Noida",
    content:
      "My NSO score improved by 40 marks in one month. The AI explanations are incredible — every wrong answer becomes a learning moment instead of just a red mark.",
    avatar: "AP",
    gradient: "from-brand-600 to-accent-600",
  },
  {
    name: "Priya Singh",
    role: "Class 8 Student",
    school: "Cathedral & John Connon School, Mumbai",
    content:
      "I love the mastery heatmap — it showed me I was weak in Mensuration even when I thought I was fine. Fixed that in two sessions. The timed tests are exactly like the real exam.",
    avatar: "PS",
    gradient: "from-violet-500 to-brand-600",
  },
  {
    name: "Rohan Gupta",
    role: "Class 9 Student",
    school: "Bombay International School",
    content:
      "Best part? Every paper is completely different. No more feeling like I'm re-doing the same questions. Already qualified for nationals in Math Olympiad this year!",
    avatar: "RG",
    gradient: "from-emerald-500 to-brand-600",
  },
];

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="bg-white px-4 py-20 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Student stories
          </p>
          <h2 className="mt-2 text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Real results from real students
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            See what students across India are saying about their Olympiad journey.
          </p>
        </div>

        <div className="grid gap-8 sm:grid-cols-3">
          {TESTIMONIALS.map(({ name, role, school, content, avatar, gradient }) => (
            <div
              key={name}
              className="flex flex-col rounded-2xl border border-slate-200 bg-slate-50 p-8 transition hover:shadow-lg"
            >
              {/* Stars */}
              <div className="mb-4 flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-achiever-600 text-achiever-600" />
                ))}
              </div>

              {/* Content */}
              <p className="mb-6 flex-1 leading-relaxed text-slate-700">
                &ldquo;{content}&rdquo;
              </p>

              {/* Author */}
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br ${gradient} text-sm font-bold text-white`}
                >
                  {avatar}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{name}</p>
                  <p className="text-xs text-slate-500">
                    {role} · {school}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
