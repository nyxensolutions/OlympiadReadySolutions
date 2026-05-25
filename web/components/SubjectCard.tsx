"use client";

import {
  Atom,
  BookOpen,
  Brain,
  BrainCircuit,
  Briefcase,
  Calculator,
  Cpu,
  Globe,
  Languages,
  Map,
  MicVocal,
  type LucideIcon
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  Math: Calculator,
  Mathematics: Calculator,
  Science: Atom,
  English: BookOpen,
  Hindi: Languages,
  "General Knowledge": Globe,
  "Social Studies": Map,
  "Logical Reasoning": Brain,
  Computers: Cpu,
  "Computer Science": Cpu,
  AI: BrainCircuit,
  "Spell Bee": MicVocal,
  Commerce: Briefcase
};

export function SubjectCard({
  name,
  selected,
  onClick,
  disabled = false,
  isSubscribed = false
}: {
  name: string;
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
  isSubscribed?: boolean;
}) {
  const Icon = ICONS[name] ?? BookOpen;
  return (
    <button
      type="button"
      onClick={disabled ? undefined : onClick}
      title={disabled ? "Not available for this class" : undefined}
      className={`group relative flex flex-col items-center gap-2 rounded-xl border p-4 transition overflow-hidden ${
        disabled
          ? "cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300"
          : selected
            ? (isSubscribed ? "border-emerald-500 bg-emerald-100 text-emerald-900 shadow-sm" : "border-brand-600 bg-brand-50 text-brand-700 shadow-sm")
            : (isSubscribed ? "border-emerald-200 bg-[#f8fcf8] text-emerald-800 hover:border-emerald-300 hover:bg-emerald-50" : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50")
      }`}
    >
      <Icon className={`h-7 w-7 ${disabled ? "text-slate-300" : isSubscribed ? "text-emerald-600" : selected ? "text-brand-600" : "text-slate-500"}`} />
      <span className="text-center text-sm font-semibold leading-tight">{name}</span>
      
      {!disabled && (
        <div className="absolute top-1.5 right-1.5 z-10">
           <span className={`text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded shadow-sm ${isSubscribed ? "bg-emerald-500 text-white" : "bg-slate-500 text-white"}`}>
             {isSubscribed ? "Subscribed" : "Free"}
           </span>
        </div>
      )}
    </button>
  );
}
