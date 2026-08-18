"use client";

import { Play, Star } from "lucide-react";

const TESTIMONIALS = [
  {
    name: "Arsh Mittal",
    role: "Class 7 Student",
    school: "Amity International School, Noida",
    content:
      "My friends and I all use OlympiadReady for IMO prep. I was stuck at Level 1 for two years. This year I finally made it to Level 2 — the AI-generated papers kept pushing me past my comfort zone. 15 minutes a day, that's all it took.",
    avatar: "AM",
    gradient: "from-brand-600 to-accent-600",
    tag: "IMO Level 2 qualifier",
  },
  {
    name: "Divit Agarwal",
    role: "Class 7 Student",
    school: "Delhi Public School, Noida Extension",
    content:
      "The mock papers feel exactly like real SOF exams. I did 20+ papers before IEO and nothing surprised me on the actual exam day. Cleared with a school rank of 1. The timed tests train you to think fast under pressure.",
    avatar: "DA",
    gradient: "from-violet-500 to-brand-600",
    tag: "IEO School Rank 1",
  },
  {
    name: "Arjun Verma",
    role: "Class 9 Student",
    school: "Ryan International School, Noida",
    content:
      "Class 9 Olympiad questions are tough — especially HoTs and reasoning. OlympiadReady has it all. Qualified for NSO Level 2 for the first time this year. The AI explanation feature saved me hours of self-correction every week.",
    avatar: "AV",
    gradient: "from-emerald-500 to-brand-600",
    tag: "NSO Level 2 qualifier",
  },
  {
    name: "Aarav Sangal",
    role: "Class 6 Student",
    school: "Delhi Public School, Noida Extension",
    content:
      "I was scoring around 60% in practice. After 3 weeks on OlympiadReady, I jumped to top rank in the MELTAS Science competition. The platform explains every mistake right away — you actually learn, not just score.",
    avatar: "AS",
    gradient: "from-teal-500 to-cyan-600",
    tag: "MELTAS Science Gold",
  },
  {
    name: "Ekta Mittal",
    role: "Parent of Akul Mittal, Class 1",
    school: "Amity International School, Noida",
    content:
      "Akul is only in Class 1 but he loves the colourful questions on OlympiadReady! We practice together for 10 minutes each evening. He cleared the IGKO first round and came back asking for more. I never thought Olympiad prep could be this fun for a 6-year-old.",
    avatar: "EM",
    gradient: "from-pink-500 to-rose-600",
    tag: "IGKO Level 1 cleared",
  },
];

// Set this to your YouTube video ID once you upload the testimonial video.
// e.g. "dQw4w9WgXcQ" from https://www.youtube.com/watch?v=dQw4w9WgXcQ
const VIDEO_TESTIMONIAL_YOUTUBE_ID = "Q8BL0EB2MbA";

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

        {/* Video testimonial — shown only when VIDEO_TESTIMONIAL_YOUTUBE_ID is set */}
        {VIDEO_TESTIMONIAL_YOUTUBE_ID && (
          <div className="mb-16 mx-auto max-w-3xl">
            <div className="overflow-hidden rounded-2xl border border-slate-200 shadow-lg">
              <div className="relative w-full" style={{ paddingTop: "56.25%" }}>
                <iframe
                  className="absolute inset-0 h-full w-full"
                  src={`https://www.youtube.com/embed/${VIDEO_TESTIMONIAL_YOUTUBE_ID}?rel=0&modestbranding=1`}
                  title="Parent testimonial — OlympiadReady"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
              <div className="flex items-center gap-3 bg-slate-50 px-5 py-3 border-t border-slate-200">
                <Play className="h-4 w-4 text-brand-600 fill-brand-600 shrink-0" />
                <p className="text-sm text-slate-600">
                  <span className="font-semibold text-slate-900">Real parent, real story</span> — hear directly from a mother whose child prepared with OlympiadReady.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* First row — 3 cards */}
        <div className="grid gap-8 sm:grid-cols-3 mb-8">
          {TESTIMONIALS.slice(0, 3).map(({ name, role, school, content, avatar, gradient, tag }) => (
            <div
              key={name}
              className="flex flex-col rounded-2xl border border-slate-200 bg-slate-50 p-8 transition hover:shadow-lg"
            >
              <div className="mb-4 flex items-center justify-between gap-2">
                <div className="flex gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-achiever-600 text-achiever-600" />
                  ))}
                </div>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">{tag}</span>
              </div>
              <p className="mb-6 flex-1 leading-relaxed text-slate-700">&ldquo;{content}&rdquo;</p>
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br ${gradient} text-sm font-bold text-white`}>
                  {avatar}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{name}</p>
                  <p className="text-xs text-slate-500">{role} · {school}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Second row — 2 cards centred */}
        <div className="grid gap-8 sm:grid-cols-2 max-w-3xl mx-auto">
          {TESTIMONIALS.slice(3).map(({ name, role, school, content, avatar, gradient, tag }) => (
            <div
              key={name}
              className="flex flex-col rounded-2xl border border-slate-200 bg-slate-50 p-8 transition hover:shadow-lg"
            >
              <div className="mb-4 flex items-center justify-between gap-2">
                <div className="flex gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-achiever-600 text-achiever-600" />
                  ))}
                </div>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">{tag}</span>
              </div>
              <p className="mb-6 flex-1 leading-relaxed text-slate-700">&ldquo;{content}&rdquo;</p>
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br ${gradient} text-sm font-bold text-white`}>
                  {avatar}
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{name}</p>
                  <p className="text-xs text-slate-500">{role} · {school}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
