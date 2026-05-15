"use client";

export type OlympiadId = "open" | "imo" | "nso" | "ieo" | "ntse" | "ioqm";

export const OLYMPIAD_DATA = [
  {
    id: "open" as OlympiadId,
    name: "Open Practice",
    org: "OlympiadReady",
    fullName: null,
    description: "Free-form practice — any subject, any grade. No exam target needed.",
    grades: "Class 1–12",
    icon: "✨",
    accent: "brand",
  },
  {
    id: "imo" as OlympiadId,
    name: "IMO",
    org: "SOF",
    fullName: "International Mathematics Olympiad",
    description: "Logical reasoning & advanced problem-solving in Mathematics.",
    grades: "Class 1–12",
    icon: "🧮",
    accent: "amber",
  },
  {
    id: "nso" as OlympiadId,
    name: "NSO",
    org: "SOF",
    fullName: "National Science Olympiad",
    description: "Physics, chemistry & biology concepts at competition level.",
    grades: "Class 1–12",
    icon: "🔬",
    accent: "emerald",
  },
  {
    id: "ieo" as OlympiadId,
    name: "IEO",
    org: "SOF",
    fullName: "International English Olympiad",
    description: "Grammar, comprehension & language proficiency skills.",
    grades: "Class 1–12",
    icon: "📖",
    accent: "sky",
  },
  {
    id: "ntse" as OlympiadId,
    name: "NTSE",
    org: "NCERT",
    fullName: "National Talent Search Examination",
    description: "Prestigious scholarship exam covering SAT, MAT & science.",
    grades: "Class 10",
    icon: "🏆",
    accent: "purple",
  },
  {
    id: "ioqm" as OlympiadId,
    name: "IOQM",
    org: "HBCSE",
    fullName: "Indian Olympiad Qualifier in Mathematics",
    description: "Gateway to national & international math competitions.",
    grades: "Class 8–12",
    icon: "📐",
    accent: "rose",
  },
] as const;

const ACCENT: Record<
  string,
  { border: string; bg: string; badge: string; nameColor: string; subColor: string }
> = {
  brand:   { border: "border-brand-500",   bg: "bg-brand-50",   badge: "bg-brand-100 text-brand-700",   nameColor: "text-brand-700",   subColor: "text-brand-500"   },
  amber:   { border: "border-amber-400",   bg: "bg-amber-50",   badge: "bg-amber-100 text-amber-700",   nameColor: "text-amber-700",   subColor: "text-amber-500"   },
  emerald: { border: "border-emerald-400", bg: "bg-emerald-50", badge: "bg-emerald-100 text-emerald-700", nameColor: "text-emerald-700", subColor: "text-emerald-500" },
  sky:     { border: "border-sky-400",     bg: "bg-sky-50",     badge: "bg-sky-100 text-sky-700",       nameColor: "text-sky-700",     subColor: "text-sky-500"     },
  purple:  { border: "border-purple-400",  bg: "bg-purple-50",  badge: "bg-purple-100 text-purple-700", nameColor: "text-purple-700",  subColor: "text-purple-500"  },
  rose:    { border: "border-rose-400",    bg: "bg-rose-50",    badge: "bg-rose-100 text-rose-700",     nameColor: "text-rose-700",    subColor: "text-rose-500"    },
};

export function OlympiadSelector({
  selected,
  onSelect,
}: {
  selected: OlympiadId;
  onSelect: (id: OlympiadId) => void;
}) {
  return (
    <div className="mb-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
        I&apos;m preparing for
      </p>
      <div className="flex gap-3 overflow-x-auto pb-2 snap-x scroll-smooth [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {OLYMPIAD_DATA.map((o) => {
          const isSelected = selected === o.id;
          const a = ACCENT[o.accent];
          return (
            <button
              key={o.id}
              type="button"
              onClick={() => onSelect(o.id)}
              className={`snap-start shrink-0 w-44 rounded-2xl border-2 p-4 text-left transition-all duration-150 ${
                isSelected
                  ? `${a.border} ${a.bg} shadow-md`
                  : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
              }`}
            >
              <span className="text-2xl leading-none">{o.icon}</span>

              <div className="mt-2.5 flex items-baseline gap-1.5">
                <span className={`text-sm font-bold ${isSelected ? a.nameColor : "text-slate-800"}`}>
                  {o.name}
                </span>
                {isSelected && (
                  <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wide ${a.badge}`}>
                    Active
                  </span>
                )}
              </div>

              {o.fullName && (
                <p className={`mt-0.5 text-[10px] font-medium leading-tight ${isSelected ? a.subColor : "text-slate-400"}`}>
                  {o.fullName}
                </p>
              )}

              <p className="mt-2 text-[10px] leading-relaxed text-slate-500">
                {o.description}
              </p>

              <div className="mt-3 flex flex-wrap items-center gap-1">
                <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-semibold ${isSelected ? a.badge : "bg-slate-100 text-slate-500"}`}>
                  {o.org}
                </span>
                <span className="text-[9px] text-slate-400">{o.grades}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
