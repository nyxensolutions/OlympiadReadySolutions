"use client";

import { Star } from "lucide-react";

const TESTIMONIALS = [
  {
    name: "Sunita Sharma",
    role: "Parent of Class 6 student",
    school: "Delhi Public School, R.K. Puram",
    content:
      "My son qualified for SOF IMO Level 2 this year — first time in his school! He practiced 15 minutes a day on OlympiadReady. Less than ₹129 a month is nothing compared to the ₹800/hr tutor we were considering.",
    avatar: "SS",
    gradient: "from-brand-600 to-accent-600",
    tag: "IMO Level 2 qualifier",
  },
  {
    name: "Kavitha Reddy",
    role: "Parent of Class 4 student",
    school: "Kendriya Vidyalaya, Hyderabad",
    content:
      "I was sceptical — my daughter has tried many apps. But the questions here are actually at the right level. She got a Gold Medal in NSO this year. The timed tests gave her confidence for the real exam.",
    avatar: "KR",
    gradient: "from-violet-500 to-brand-600",
    tag: "NSO Gold Medal",
  },
  {
    name: "Arjun Mehta",
    role: "Class 9 Student",
    school: "Ryan International School, Bengaluru",
    content:
      "Every paper is different — I never feel like I'm redoing questions. The AI explanation shows exactly where I went wrong. Cleared IEO Level 1 and 2 both this year after just 3 weeks of practice.",
    avatar: "AM",
    gradient: "from-emerald-500 to-brand-600",
    tag: "IEO Level 1 & 2 cleared",
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
          {TESTIMONIALS.map(({ name, role, school, content, avatar, gradient, tag }) => (
            <div
              key={name}
              className="flex flex-col rounded-2xl border border-slate-200 bg-slate-50 p-8 transition hover:shadow-lg"
            >
              {/* Stars + tag */}
              <div className="mb-4 flex items-center justify-between gap-2">
                <div className="flex gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-achiever-600 text-achiever-600" />
                  ))}
                </div>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">{tag}</span>
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
