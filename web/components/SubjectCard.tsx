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
  type LucideIcon
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  Math: Calculator,
  Science: Atom,
  English: BookOpen,
  Hindi: Languages,
  "General Knowledge": Globe,
  "Social Studies": Map,
  "Logical Reasoning": Brain,
  Computers: Cpu,
  AI: BrainCircuit
};

export function SubjectCard({
  name,
  selected,
  onClick,
  disabled = false
}: {
  name: string;
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  const Icon = ICONS[name] ?? BookOpen;
  return (
    <button
      type="button"
      onClick={disabled ? undefined : onClick}
      title={disabled ? "Not available for this class" : undefined}
      className={`flex flex-col items-center gap-2 rounded-xl border p-4 transition ${
        disabled
          ? "cursor-not-allowed border-slate-100 bg-slate-50 text-slate-300"
          : selected
            ? "border-brand-600 bg-brand-50 text-brand-700 shadow-sm"
            : "border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50"
      }`}
    >
      <Icon className={`h-7 w-7 ${disabled ? "text-slate-300" : selected ? "text-brand-600" : "text-slate-500"}`} />
      <span className="text-center text-sm font-semibold leading-tight">{name}</span>
    </button>
  );
}
