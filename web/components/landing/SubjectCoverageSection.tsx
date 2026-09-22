"use client";

import Image from "next/image";
import { BookOpen, Brain, Briefcase, Cpu, Languages, Map, type LucideIcon } from "lucide-react";

interface SubjectCard {
  img?: string;
  icon?: LucideIcon;
  name: string;
  label: string;
  exams: string;
  grades: string;
  bg: string;
  border: string;
  textColor: string;
  badge?: string;
  cssClass?: string;
}

const TOP_SUBJECTS: SubjectCard[] = [
  {
    img: "/kids-ui/subjects/math.png",
    name: "math",
    label: "Mathematics",
    exams: "IMO · IOM · CMO",
    grades: "Class 1–12",
    bg: "bg-gradient-math",
    border: "border-blue-200",
    textColor: "text-blue-700",
    cssClass: "subject-math",
  },
  {
    img: "/kids-ui/subjects/science.png",
    name: "science",
    label: "Science",
    exams: "NSO · IOS · CSO",
    grades: "Class 1–12",
    bg: "bg-gradient-science",
    border: "border-green-200",
    textColor: "text-green-700",
    cssClass: "subject-science",
  },
  {
    img: "/kids-ui/subjects/english.png",
    name: "english",
    label: "English",
    exams: "IEO · IOEL · CEO",
    grades: "Class 1–12",
    bg: "bg-gradient-english",
    border: "border-pink-200",
    textColor: "text-pink-700",
    cssClass: "subject-english",
  },
  {
    img: "/kids-ui/subjects/gk.png",
    name: "gk",
    label: "General Knowledge",
    exams: "IGKO · GKIO",
    grades: "Class 1–10",
    bg: "bg-gradient-gk",
    border: "border-orange-200",
    textColor: "text-orange-700",
    cssClass: "subject-gk",
  },
  {
    img: "/kids-ui/subjects/spellbee.png",
    name: "bee",
    label: "Spell Bee",
    exams: "Spell Bee Competitions",
    grades: "Class 1–12",
    bg: "bg-gradient-bee",
    border: "border-purple-200",
    textColor: "text-purple-700",
    badge: "New",
    cssClass: "subject-bee",
  },
];

const MORE_SUBJECTS: SubjectCard[] = [
  { icon: Brain,     name: "lr",      label: "Logical Reasoning", exams: "All Olympiads",      grades: "Class 1–12",  bg: "bg-cyan-50",   border: "border-cyan-200",   textColor: "text-cyan-700"   },
  { icon: Cpu,       name: "cs",      label: "Computer Science",  exams: "ICSO · CCO",         grades: "Class 1–10",  bg: "bg-indigo-50", border: "border-indigo-200", textColor: "text-indigo-700" },
  { icon: Map,       name: "sst",     label: "Social Studies",    exams: "ISSO · GKIO",        grades: "Class 3–10",  bg: "bg-teal-50",   border: "border-teal-200",   textColor: "text-teal-700"   },
  { icon: Languages, name: "hindi",   label: "Hindi",             exams: "IHO · ABHO",         grades: "Class 3–10",  bg: "bg-amber-50",  border: "border-amber-200",  textColor: "text-amber-700"  },
  { icon: Briefcase, name: "commerce",label: "Commerce",          exams: "SOF ICO",            grades: "Class 11–12", bg: "bg-rose-50",   border: "border-rose-200",   textColor: "text-rose-700",  badge: "New" },
  { icon: BookOpen,  name: "ai",      label: "Artificial Intelligence", exams: "iiO",          grades: "Class 1–10",  bg: "bg-violet-50", border: "border-violet-200", textColor: "text-violet-700", badge: "New" },
];

export function SubjectCoverageSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-blue-50 px-4 py-20">
      {/* Decorative blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-16 top-0 h-72 w-72 rounded-full bg-blue-200/30 blur-3xl" />
        <div className="absolute -right-16 bottom-0 h-72 w-72 rounded-full bg-purple-200/30 blur-3xl" />
      </div>
      <div className="relative mx-auto max-w-6xl">
        {/* Header with girl character */}
        <div className="mb-12 flex flex-col items-center gap-4 text-center sm:flex-row sm:justify-center sm:gap-6">
          <div className="relative h-28 w-20 shrink-0 sm:h-36 sm:w-28">
            <Image src="/kids-ui/hero/girl.png" alt="Student" fill className="object-contain object-bottom drop-shadow-lg animate-float-slow" />
          </div>
          <div>
            <span className="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-sm font-bold uppercase tracking-widest text-brand-700">
              Subject Coverage
            </span>
            <h2 className="mt-3 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              Olympiads We Cover
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-slate-500">
              Comprehensive preparation for top national and international Olympiads —
              mapped to official syllabi for every grade.
            </p>
          </div>
        </div>

        {/* Top 5 — big colourful cards */}
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {TOP_SUBJECTS.map(({ img, label, exams, grades, bg, border, textColor, badge, cssClass }) => (
            <div
              key={label}
              className={`card-lift ${cssClass ?? ""} relative flex flex-col items-center rounded-3xl border-2 ${border} ${bg} p-4 text-center`}
            >
              {badge && (
                <span className="absolute right-2 top-2 rounded-full bg-purple-600 px-2 py-0.5 text-[10px] font-bold text-white">
                  {badge}
                </span>
              )}
              <div className="mb-3 h-16 w-16 sm:h-20 sm:w-20">
                <Image
                  src={img!}
                  alt={label}
                  width={80}
                  height={80}
                  className="h-full w-full object-contain"
                />
              </div>
              <p className={`text-sm font-extrabold ${textColor}`}>{label}</p>
              <p className="mt-1 text-[11px] text-slate-500">{exams}</p>
              <span className="mt-2 rounded-full bg-white/60 px-2 py-0.5 text-[10px] font-semibold text-slate-500">
                {grades}
              </span>
            </div>
          ))}
        </div>

        {/* More subjects — compact list */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {MORE_SUBJECTS.map(({ icon: Icon, label, exams, grades, bg, border, textColor, badge }) => (
            <div
              key={label}
              className={`card-lift relative flex flex-col items-center rounded-2xl border ${border} ${bg} px-3 py-4 text-center`}
            >
              {badge && (
                <span className="absolute right-1.5 top-1.5 rounded-full bg-purple-600 px-1.5 py-0.5 text-[9px] font-bold text-white">
                  {badge}
                </span>
              )}
              <div className={`mb-2 rounded-xl p-2 ${bg.replace("50", "100")}`}>
                {Icon && <Icon className={`h-5 w-5 ${textColor}`} />}
              </div>
              <p className={`text-xs font-bold ${textColor}`}>{label}</p>
              <p className="mt-0.5 text-[10px] text-slate-400">{exams}</p>
              <span className="mt-1.5 rounded-full bg-white/70 px-2 py-0.5 text-[9px] font-medium text-slate-500">
                {grades}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
