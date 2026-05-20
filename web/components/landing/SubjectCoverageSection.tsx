"use client";

import {
  Atom,
  BookOpen,
  Brain,
  BrainCircuit,
  Calculator,
  Cpu,
  Globe,
  Languages,
  Map,
  MicVocal,
  type LucideIcon,
} from "lucide-react";

interface SubjectRow {
  icon: LucideIcon;
  name: string;
  grades: string;
  exams: string;
  accent: string;
  badge?: string;
}

const SUBJECT_ROWS: SubjectRow[] = [
  { icon: Calculator,   name: "Mathematics",        grades: "Class 1–12", exams: "IMO · IOM · CMO",    accent: "bg-blue-50 text-blue-600"     },
  { icon: Atom,         name: "Science",             grades: "Class 1–12", exams: "NSO · IOS · CSO",    accent: "bg-emerald-50 text-emerald-600"},
  { icon: BookOpen,     name: "English",             grades: "Class 1–12", exams: "IEO · IOEL · CEO",   accent: "bg-violet-50 text-violet-600" },
  { icon: Brain,        name: "Logical Reasoning",   grades: "Class 1–12", exams: "All Olympiads",      accent: "bg-rose-50 text-rose-600"     },
  { icon: Cpu,          name: "Computers",           grades: "Class 1–10", exams: "ICSO · CCO",         accent: "bg-slate-100 text-slate-600"  },
  { icon: BrainCircuit, name: "AI",                  grades: "Class 1–10", exams: "iiO",                accent: "bg-indigo-50 text-indigo-600" },
  { icon: Globe,        name: "General Knowledge",   grades: "Class 1–10", exams: "IGKO · GKIO",        accent: "bg-amber-50 text-amber-600"   },
  { icon: Map,          name: "Social Studies",      grades: "Class 3–10", exams: "ISSO · GKIO",        accent: "bg-teal-50 text-teal-600"     },
  { icon: Languages,    name: "Hindi",               grades: "Class 3–10", exams: "IHO · ABHO",         accent: "bg-orange-50 text-orange-600" },
  { icon: MicVocal,     name: "Spell Bee",           grades: "Class 1–8",  exams: "Hummingbird Spell Bee", accent: "bg-purple-50 text-purple-600", badge: "New" },
];

export function SubjectCoverageSection() {
  return (
    <section className="bg-slate-50 px-4 py-20">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">
            Subject coverage
          </p>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
            Every subject. Every class.
          </h2>
          <p className="mt-3 text-slate-500">
            Mapped to the official syllabi of India&apos;s leading Olympiad organisations — including{" "}
            <span className="font-semibold text-purple-600">Hummingbird Spell Bee</span>.
          </p>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          {SUBJECT_ROWS.map(({ icon: Icon, name, grades, exams, accent, badge }, idx) => (
            <div
              key={name}
              className={`flex items-center gap-4 px-5 py-4 ${
                idx < SUBJECT_ROWS.length - 1 ? "border-b border-slate-100" : ""
              }`}
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${accent}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold text-slate-900">{name}</p>
                  {badge && (
                    <span className="rounded-full bg-purple-100 px-2 py-0.5 text-[10px] font-bold text-purple-700">{badge}</span>
                  )}
                </div>
                <p className="text-xs text-slate-500">{exams}</p>
              </div>
              <span className="shrink-0 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                {grades}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
