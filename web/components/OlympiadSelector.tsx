"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export type OlympiadId =
  | "open"
  | "hbcse"
  | "sof_imo" | "sof_nso" | "sof_ieo" | "sof_nco"
  | "silverzone_math" | "silverzone_science" | "silverzone_english" | "silverzone_computer"
  | "unified_nstse" | "unified_uieo"
  | "math_olympiad"
  | "science_olympiad"
  | "computer_olympiad"
  | "english_olympiad";

type OlympiadEntry = {
  id: OlympiadId;
  name: string;
  org: string;
  orgFull: string;
  fullName: string | null;
  description: string;
  grades: string;
  icon: string;
  accent: string;
  /** CSS classes for the tile's coloured top bar */
  barClass: string;
  /** Subject this olympiad maps to for practice generation */
  subject: string | null;
};

export const OLYMPIAD_DATA: OlympiadEntry[] = [
  // ── Open practice ───────────────────────────────────────────
  {
    id: "open",
    name: "Open Practice",
    org: "OlympiadReady",
    orgFull: "OlympiadReady",
    fullName: null,
    description: "Free-form practice — any subject, any grade. No exam target needed.",
    grades: "Class 1–12",
    icon: "✨",
    accent: "brand",
    barClass: "bg-brand-500",
    subject: null,
  },

  // ── HBCSE ────────────────────────────────────────────────────
  {
    id: "hbcse",
    name: "HBCSE",
    org: "HBCSE / TIFR",
    orgFull: "Homi Bhabha Centre for Science Education",
    fullName: "National Olympiad Programme",
    description: "India's gateway to IMO, IPhO, IChO, IBO & IOI. Most prestigious school Olympiads.",
    grades: "Class 8–12",
    icon: "🏛️",
    accent: "navy",
    barClass: "bg-[#1a3a6b]",
    subject: "Math",
  },

  // ── SOF ──────────────────────────────────────────────────────
  {
    id: "sof_imo",
    name: "SOF IMO",
    org: "SOF",
    orgFull: "Science Olympiad Foundation",
    fullName: "International Mathematics Olympiad",
    description: "Logical reasoning & advanced problem-solving in Mathematics.",
    grades: "Class 1–12",
    icon: "🧮",
    accent: "amber",
    barClass: "bg-amber-500",
    subject: "Math",
  },
  {
    id: "sof_nso",
    name: "SOF NSO",
    org: "SOF",
    orgFull: "Science Olympiad Foundation",
    fullName: "National Science Olympiad",
    description: "Physics, Chemistry & Biology concepts at competition level.",
    grades: "Class 1–12",
    icon: "🔬",
    accent: "emerald",
    barClass: "bg-emerald-500",
    subject: "Science",
  },
  {
    id: "sof_ieo",
    name: "SOF IEO",
    org: "SOF",
    orgFull: "Science Olympiad Foundation",
    fullName: "International English Olympiad",
    description: "Grammar, comprehension & English language proficiency.",
    grades: "Class 1–12",
    icon: "📖",
    accent: "sky",
    barClass: "bg-sky-500",
    subject: "English",
  },
  {
    id: "sof_nco",
    name: "SOF NCO",
    org: "SOF",
    orgFull: "Science Olympiad Foundation",
    fullName: "National Cyber Olympiad",
    description: "Computer fundamentals, logical thinking & digital literacy.",
    grades: "Class 1–12",
    icon: "💻",
    accent: "indigo",
    barClass: "bg-indigo-500",
    subject: "Computers",
  },

  // ── SilverZone ───────────────────────────────────────────────
  {
    id: "silverzone_math",
    name: "SilverZone iOM",
    org: "SilverZone",
    orgFull: "SilverZone Foundation",
    fullName: "International Olympiad of Mathematics",
    description: "Analytical and conceptual Mathematics for all grades.",
    grades: "Class 1–12",
    icon: "🥈",
    accent: "slate",
    barClass: "bg-slate-500",
    subject: "Math",
  },
  {
    id: "silverzone_science",
    name: "SilverZone iOS",
    org: "SilverZone",
    orgFull: "SilverZone Foundation",
    fullName: "International Olympiad of Science",
    description: "Comprehensive Science for competitive edge at school level.",
    grades: "Class 1–12",
    icon: "⚗️",
    accent: "teal",
    barClass: "bg-teal-500",
    subject: "Science",
  },
  {
    id: "silverzone_english",
    name: "SilverZone iOEL",
    org: "SilverZone",
    orgFull: "SilverZone Foundation",
    fullName: "International Olympiad of English Language",
    description: "Vocabulary, grammar, and language excellence.",
    grades: "Class 1–12",
    icon: "📝",
    accent: "violet",
    barClass: "bg-violet-500",
    subject: "English",
  },
  {
    id: "silverzone_computer",
    name: "SilverZone iOIT",
    org: "SilverZone",
    orgFull: "SilverZone Foundation",
    fullName: "International Olympiad of Information Technology",
    description: "Programming, computer science & IT fundamentals.",
    grades: "Class 1–12",
    icon: "🖥️",
    accent: "cyan",
    barClass: "bg-cyan-500",
    subject: "Computers",
  },

  // ── Unified Council ──────────────────────────────────────────
  {
    id: "unified_nstse",
    name: "NSTSE",
    org: "Unified Council",
    orgFull: "Unified Council",
    fullName: "National Level Science Talent Search Exam",
    description: "NCERT-based analytical exam with deep conceptual questions.",
    grades: "Class 1–12",
    icon: "🎯",
    accent: "orange",
    barClass: "bg-orange-500",
    subject: "Science",
  },
  {
    id: "unified_uieo",
    name: "UIEO",
    org: "Unified Council",
    orgFull: "Unified Council",
    fullName: "Unified International English Olympiad",
    description: "Analytical English exam testing reading & writing skills.",
    grades: "Class 1–12",
    icon: "✍️",
    accent: "rose",
    barClass: "bg-rose-500",
    subject: "English",
  },

  // ── Subject-level ─────────────────────────────────────────────
  {
    id: "math_olympiad",
    name: "Maths Olympiad",
    org: "General",
    orgFull: "All Maths Olympiads",
    fullName: "Mathematics Competition Preparation",
    description: "INMO, SEAMO, Ramanujan & Aryabhata Math competition prep.",
    grades: "Class 1–12",
    icon: "π",
    accent: "purple",
    barClass: "bg-purple-600",
    subject: "Math",
  },
  {
    id: "science_olympiad",
    name: "Science Olympiad",
    org: "General",
    orgFull: "All Science Olympiads",
    fullName: "Science Competition Preparation",
    description: "Physics, Chemistry & Biology for competitive science exams.",
    grades: "Class 1–12",
    icon: "🧪",
    accent: "lime",
    barClass: "bg-lime-600",
    subject: "Science",
  },
  {
    id: "computer_olympiad",
    name: "Computers Olympiad",
    org: "General",
    orgFull: "Computing & Cyber Olympiads",
    fullName: "Computer Science Competition Prep",
    description: "ICO, ZCO & Cyber Olympiad preparation — coding, logic, IT.",
    grades: "Class 1–12",
    icon: "⌨️",
    accent: "fuchsia",
    barClass: "bg-fuchsia-600",
    subject: "Computers",
  },
  {
    id: "english_olympiad",
    name: "English Olympiad",
    org: "General",
    orgFull: "All English Olympiads",
    fullName: "English Language Competition Prep",
    description: "Covers all major English Olympiads — grammar, vocabulary, comprehension.",
    grades: "Class 1–12",
    icon: "📚",
    accent: "pink",
    barClass: "bg-pink-500",
    subject: "English",
  },
];

const ACCENT_CLASSES: Record<
  string,
  { border: string; bg: string; badge: string; nameColor: string; subColor: string }
> = {
  brand:   { border: "border-brand-500",   bg: "bg-brand-50",   badge: "bg-brand-100 text-brand-700",     nameColor: "text-brand-700",   subColor: "text-brand-500"   },
  navy:    { border: "border-[#1a3a6b]",   bg: "bg-blue-50",    badge: "bg-blue-100 text-blue-800",        nameColor: "text-blue-900",    subColor: "text-blue-700"    },
  amber:   { border: "border-amber-400",   bg: "bg-amber-50",   badge: "bg-amber-100 text-amber-700",     nameColor: "text-amber-700",   subColor: "text-amber-500"   },
  emerald: { border: "border-emerald-400", bg: "bg-emerald-50", badge: "bg-emerald-100 text-emerald-700", nameColor: "text-emerald-700", subColor: "text-emerald-500" },
  sky:     { border: "border-sky-400",     bg: "bg-sky-50",     badge: "bg-sky-100 text-sky-700",         nameColor: "text-sky-700",     subColor: "text-sky-500"     },
  indigo:  { border: "border-indigo-400",  bg: "bg-indigo-50",  badge: "bg-indigo-100 text-indigo-700",   nameColor: "text-indigo-700",  subColor: "text-indigo-500"  },
  slate:   { border: "border-slate-400",   bg: "bg-slate-100",  badge: "bg-slate-200 text-slate-700",     nameColor: "text-slate-700",   subColor: "text-slate-500"   },
  teal:    { border: "border-teal-400",    bg: "bg-teal-50",    badge: "bg-teal-100 text-teal-700",       nameColor: "text-teal-700",    subColor: "text-teal-500"    },
  violet:  { border: "border-violet-400",  bg: "bg-violet-50",  badge: "bg-violet-100 text-violet-700",   nameColor: "text-violet-700",  subColor: "text-violet-500"  },
  cyan:    { border: "border-cyan-400",    bg: "bg-cyan-50",    badge: "bg-cyan-100 text-cyan-700",       nameColor: "text-cyan-700",    subColor: "text-cyan-500"    },
  orange:  { border: "border-orange-400",  bg: "bg-orange-50",  badge: "bg-orange-100 text-orange-700",   nameColor: "text-orange-700",  subColor: "text-orange-500"  },
  rose:    { border: "border-rose-400",    bg: "bg-rose-50",    badge: "bg-rose-100 text-rose-700",       nameColor: "text-rose-700",    subColor: "text-rose-500"    },
  purple:  { border: "border-purple-400",  bg: "bg-purple-50",  badge: "bg-purple-100 text-purple-700",   nameColor: "text-purple-700",  subColor: "text-purple-500"  },
  lime:    { border: "border-lime-400",    bg: "bg-lime-50",    badge: "bg-lime-100 text-lime-700",       nameColor: "text-lime-700",    subColor: "text-lime-500"    },
  fuchsia: { border: "border-fuchsia-400", bg: "bg-fuchsia-50", badge: "bg-fuchsia-100 text-fuchsia-700", nameColor: "text-fuchsia-700", subColor: "text-fuchsia-500" },
  pink:    { border: "border-pink-400",    bg: "bg-pink-50",    badge: "bg-pink-100 text-pink-700",       nameColor: "text-pink-700",    subColor: "text-pink-500"    },
};

// Group tiles by org family for visual section headers
const ORG_GROUPS: { label: string; ids: OlympiadId[] }[] = [
  { label: "General", ids: ["open"] },
  { label: "HBCSE Olympiads", ids: ["hbcse"] },
  { label: "SOF Olympiads", ids: ["sof_imo", "sof_nso", "sof_ieo", "sof_nco"] },
  { label: "SilverZone Olympiads", ids: ["silverzone_math", "silverzone_science", "silverzone_english", "silverzone_computer"] },
  { label: "Unified Council", ids: ["unified_nstse", "unified_uieo"] },
  { label: "By Subject", ids: ["math_olympiad", "science_olympiad", "computer_olympiad", "english_olympiad"] },
];

export function OlympiadSelector({
  selected,
  onSelect,
}: {
  selected: OlympiadId;
  onSelect: (id: OlympiadId) => void;
}) {
  const selectedEntry = OLYMPIAD_DATA.find((o) => o.id === selected)!;
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canLeft,  setCanLeft]  = useState(false);
  const [canRight, setCanRight] = useState(true);

  const updateArrows = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanLeft(el.scrollLeft > 4);
    setCanRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4);
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateArrows();
    el.addEventListener("scroll", updateArrows, { passive: true });
    const ro = new ResizeObserver(updateArrows);
    ro.observe(el);
    return () => { el.removeEventListener("scroll", updateArrows); ro.disconnect(); };
  }, [updateArrows]);

  const scroll = (dir: "left" | "right") => {
    scrollRef.current?.scrollBy({ left: dir === "left" ? -360 : 360, behavior: "smooth" });
  };

  return (
    <div className="mb-6">
      <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
        I&apos;m preparing for
      </p>

      {/* Scrollable ribbon with arrow buttons */}
      <div className="relative flex items-center gap-2">
        {/* Left arrow */}
        <button
          type="button"
          onClick={() => scroll("left")}
          disabled={!canLeft}
          aria-label="Scroll left"
          className={`shrink-0 rounded-full border border-slate-200 bg-white p-1.5 shadow-sm transition hover:bg-slate-50 disabled:opacity-0 disabled:pointer-events-none`}
        >
          <ChevronLeft className="h-4 w-4 text-slate-600" />
        </button>

        {/* Scrollable track */}
        <div className="relative flex-1 overflow-hidden">
          <div
            ref={scrollRef}
            className="flex gap-4 overflow-x-auto pb-3 snap-x scroll-smooth [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          >
            {ORG_GROUPS.map((group) => (
              <div key={group.label} className="flex shrink-0 flex-col gap-1">
                {/* Group header */}
                <span className="mb-1 text-[9px] font-bold uppercase tracking-widest text-slate-300 pl-0.5">
                  {group.label}
                </span>
                <div className="flex gap-2">
                  {group.ids.map((id) => {
                    const o = OLYMPIAD_DATA.find((x) => x.id === id)!;
                    const isSelected = selected === id;
                    const a = ACCENT_CLASSES[o.accent] ?? ACCENT_CLASSES.brand;
                    return (
                      <button
                        key={id}
                        type="button"
                        onClick={() => onSelect(id)}
                        className={`snap-start shrink-0 w-40 rounded-2xl border-2 overflow-hidden text-left transition-all duration-150 ${
                          isSelected
                            ? `${a.border} ${a.bg} shadow-lg ring-2 ring-offset-1 ${a.border}`
                            : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-md"
                        }`}
                      >
                        {/* Coloured top accent bar */}
                        <div className={`h-1 w-full ${o.barClass} ${isSelected ? "opacity-100" : "opacity-40"}`} />

                        <div className="p-3.5">
                          {/* Icon + active badge */}
                          <div className="flex items-start justify-between">
                            <span className="text-xl leading-none">{o.icon}</span>
                            {isSelected && (
                              <span className={`rounded-full px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wide ${a.badge}`}>
                                Active
                              </span>
                            )}
                          </div>

                          {/* Name */}
                          <div className="mt-2">
                            <span className={`block text-[13px] font-bold leading-tight ${isSelected ? a.nameColor : "text-slate-800"}`}>
                              {o.name}
                            </span>
                            {o.fullName && (
                              <span className={`block mt-0.5 text-[9px] font-medium leading-tight ${isSelected ? a.subColor : "text-slate-400"}`}>
                                {o.fullName}
                              </span>
                            )}
                          </div>

                          {/* Description */}
                          <p className="mt-2 text-[9px] leading-relaxed text-slate-500 line-clamp-2">
                            {o.description}
                          </p>

                          {/* Org badge + grades */}
                          <div className="mt-2.5 flex flex-wrap items-center gap-1">
                            <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-semibold ${isSelected ? a.badge : "bg-slate-100 text-slate-500"}`}>
                              {o.org}
                            </span>
                            <span className="text-[9px] text-slate-400">{o.grades}</span>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Left fade */}
          {canLeft && (
            <div className="pointer-events-none absolute left-0 top-0 bottom-3 w-8 bg-gradient-to-r from-slate-50 to-transparent" />
          )}
          {/* Right fade */}
          {canRight && (
            <div className="pointer-events-none absolute right-0 top-0 bottom-3 w-8 bg-gradient-to-l from-slate-50 to-transparent" />
          )}
        </div>

        {/* Right arrow */}
        <button
          type="button"
          onClick={() => scroll("right")}
          disabled={!canRight}
          aria-label="Scroll right"
          className="shrink-0 rounded-full border border-slate-200 bg-white p-1.5 shadow-sm transition hover:bg-slate-50 disabled:opacity-0 disabled:pointer-events-none"
        >
          <ChevronRight className="h-4 w-4 text-slate-600" />
        </button>
      </div>

      {/* Context pill for selected olympiad */}
      {selected !== "open" && (
        <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-500 shadow-sm">
          <span className="text-base leading-none">{selectedEntry.icon}</span>
          <span className="font-semibold text-slate-700">{selectedEntry.name}</span>
          <span className="text-slate-300">·</span>
          <span className="text-slate-500">{selectedEntry.orgFull}</span>
          {selectedEntry.subject && (
            <>
              <span className="text-slate-300">·</span>
              <span className="font-medium text-brand-600">Practising {selectedEntry.subject}</span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
