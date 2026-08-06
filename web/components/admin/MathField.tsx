"use client";

import { useMemo, useState } from "react";
import { Wand2, AlertTriangle, AlertOctagon, Undo2 } from "lucide-react";
import { MarkdownMath } from "@/components/MarkdownMath";
import { repastePdfNotation, detectNotationIssues, type RepairResult } from "@/lib/notation";

/** Characters that suggest the text carries maths worth previewing. */
const MATHY = /[$\\^_√°²³⁴⁵⁶⁷⁸⁹×÷≤≥≠∠π θαβ]|\d\s*\/\s*\d|\b[a-zA-Z]\d\b/;

interface MathFieldProps {
  value: string;
  onChange: (v: string) => void;
  /** Renders a <textarea> when set, otherwise a single-line <input>. */
  rows?: number;
  placeholder?: string;
  className?: string;
  /** Always show the preview, even when the text has no maths in it. */
  alwaysPreview?: boolean;
  ariaLabel?: string;
}

/**
 * Question-text input that understands maths notation.
 *
 * Three things a plain <textarea> cannot do:
 *   1. Repairs PDF-paste damage on paste (x2 -> x², 7x + 200 -> 7x + 20°) and shows
 *      exactly what it changed, with one-click undo.
 *   2. Renders a live preview through the same component students see, so what you
 *      type is what they get.
 *   3. Warns before save about notation that will store or render incorrectly.
 */
export function MathField({
  value, onChange, rows, placeholder, className = "", alwaysPreview = false, ariaLabel,
}: MathFieldProps) {
  const [repair, setRepair] = useState<{ before: string; changes: RepairResult["changes"] } | null>(null);

  const issues = useMemo(() => detectNotationIssues(value), [value]);
  const showPreview = value.trim().length > 0 && (alwaysPreview || MATHY.test(value));

  function handlePaste(e: React.ClipboardEvent<HTMLTextAreaElement | HTMLInputElement>) {
    const pasted = e.clipboardData.getData("text");
    if (!pasted) return;

    const { text: fixed, changes } = repastePdfNotation(pasted);
    if (changes.length === 0) return; // nothing to do — let the browser paste normally

    e.preventDefault();
    const el = e.currentTarget;
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    const next = value.slice(0, start) + fixed + value.slice(end);

    setRepair({ before: value, changes });
    onChange(next);
  }

  function fixNow() {
    const { text, changes } = repastePdfNotation(value);
    if (changes.length === 0) return;
    setRepair({ before: value, changes });
    onChange(text);
  }

  function undo() {
    if (!repair) return;
    onChange(repair.before);
    setRepair(null);
  }

  const shared = {
    value,
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => onChange(e.target.value),
    onPaste: handlePaste,
    placeholder,
    "aria-label": ariaLabel,
  };

  const manualFixable = repastePdfNotation(value).changes.length > 0;

  return (
    <div className="space-y-2">
      {rows
        ? <textarea {...shared} rows={rows} className={`input resize-none ${className}`} />
        : <input {...shared} className={`input ${className}`} />}

      {/* What the paste repair changed */}
      {repair && (
        <div className="rounded-lg border border-emerald-600/40 bg-emerald-950/40 px-3 py-2 text-xs">
          <div className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-1.5 font-medium text-emerald-300">
              <Wand2 size={13} />
              Fixed {repair.changes.length} notation {repair.changes.length === 1 ? "issue" : "issues"} on paste
            </span>
            <button type="button" onClick={undo}
              className="flex items-center gap-1 text-emerald-400 hover:text-emerald-200 underline">
              <Undo2 size={12} /> Undo
            </button>
          </div>
          <ul className="mt-1.5 space-y-0.5 text-emerald-200/80">
            {repair.changes.slice(0, 6).map((c, i) => (
              <li key={i} className="font-mono">
                <span className="text-red-300/80 line-through">{c.before}</span>
                {" → "}
                <span className="text-emerald-200">{c.after}</span>
              </li>
            ))}
            {repair.changes.length > 6 && (
              <li className="text-emerald-300/60">…and {repair.changes.length - 6} more</li>
            )}
          </ul>
        </div>
      )}

      {/* Offer a manual pass for text that was typed rather than pasted */}
      {!repair && manualFixable && (
        <button type="button" onClick={fixNow}
          className="flex items-center gap-1.5 text-xs text-indigo-300 hover:text-indigo-200 underline">
          <Wand2 size={12} /> Fix maths notation
        </button>
      )}

      {/* Problems that will store or render incorrectly */}
      {issues.length > 0 && (
        <ul className="space-y-1">
          {issues.map((iss, i) => (
            <li key={i}
              className={`flex items-start gap-1.5 text-xs ${
                iss.severity === "error" ? "text-red-300" : "text-amber-300"}`}>
              {iss.severity === "error" ? <AlertOctagon size={13} className="mt-px shrink-0" />
                                        : <AlertTriangle size={13} className="mt-px shrink-0" />}
              <span>
                {iss.message}
                {iss.sample && <code className="ml-1 rounded bg-slate-700 px-1">{iss.sample}</code>}
              </span>
            </li>
          ))}
        </ul>
      )}

      {/* Exactly what the student will see — light card, because their app is light */}
      {showPreview && (
        <div className="rounded-lg border border-slate-600 bg-white px-3 py-2">
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
            Student preview
          </p>
          <MarkdownMath content={value} className="text-sm" />
        </div>
      )}
    </div>
  );
}
