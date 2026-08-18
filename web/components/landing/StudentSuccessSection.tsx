"use client";

import Image from "next/image";

const WINNERS = [
  {
    src: "/students/1.png",
    detail: "Grade 7 · IEO School Rank 1",
    alt: "Student with Olympiad medals",
  },
  {
    src: "/students/2.jpg",
    detail: "Grade 7 & Grade 1 · IMO & IGKO qualifiers",
    alt: "Students proudly showing their Olympiad medals",
  },
  {
    src: "/students/3.png",
    detail: "Grade 9 · NSO Level 2 qualifier",
    alt: "Student with NSO gold medal",
  },
  {
    src: "/students/4.png",
    detail: "Grade 7 · International Rank Holder",
    alt: "Student with Olympiad certificates and medal",
  },
  {
    src: "/students/5.png",
    detail: "Grade 7 · IMO Level 2 · IOS Certificate",
    alt: "Student displaying medals and IOS certificate",
  },
  {
    src: "/students/6.png",
    detail: "Grade 6 · MELTAS Science Gold",
    alt: "Student with MELTAS Science competition certificate",
  },
];

export function StudentSuccessSection() {
  return (
    <section id="winners" className="bg-slate-50 px-4 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-12 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Wall of Champions
          </p>
          <h2 className="mt-2 text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Real students. Real medals. Real results.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            These students prepared with OlympiadReady and came home with medals,
            certificates, and rank letters. Yours could be next.
          </p>
        </div>

        {/* Photo grid */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:gap-6">
          {WINNERS.map(({ src, detail, alt }) => (
            <div
              key={src}
              className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-lg hover:-translate-y-1 duration-200"
            >
              {/* Photo */}
              <div className="relative aspect-[3/4] w-full overflow-hidden">
                <Image
                  src={src}
                  alt={alt}
                  fill
                  className="object-cover object-top transition duration-300 group-hover:scale-105"
                  sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 320px"
                />
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/70 via-transparent to-transparent" />
              </div>

              {/* Caption */}
              <div className="absolute bottom-0 left-0 right-0 p-4">
                <p className="text-xs font-semibold text-slate-200 drop-shadow">
                  {detail}
                </p>
              </div>

              {/* Medal badge */}
              <div className="absolute right-3 top-3 rounded-full bg-achiever-500 px-2 py-1 text-xs font-bold text-white shadow">
                🥇 Winner
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA nudge */}
        <p className="mt-10 text-center text-sm text-slate-500">
          Join <span className="font-semibold text-slate-700">500+ students</span> across India who are already on their Olympiad journey with us.
        </p>
      </div>
    </section>
  );
}
