"use client";

const STATS = [
  { value: "500+",  label: "Students practising",  sub: "and growing every day"        },
  { value: "8",     label: "Subjects covered",      sub: "Classes 1 through 12"         },
  { value: "∞",     label: "Unique questions",      sub: "AI-generated, never repeated" },
  { value: "10+",   label: "Olympiad exams mapped", sub: "SOF, SilverZone & more"       },
];

export function SocialProofSection() {
  return (
    <section className="bg-brand-600 px-4 py-16 text-white">
      <div className="mx-auto max-w-5xl">
        <p className="mb-8 text-center text-sm font-semibold uppercase tracking-widest text-blue-200">
          Trusted by students across India
        </p>
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {STATS.map(({ value, label, sub }) => (
            <div key={label} className="flex flex-col items-center text-center">
              <span className="text-4xl font-extrabold">{value}</span>
              <span className="mt-1 text-sm font-semibold text-blue-100">{label}</span>
              <span className="mt-0.5 text-xs text-blue-300">{sub}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
