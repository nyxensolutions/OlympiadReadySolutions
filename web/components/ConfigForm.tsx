"use client";

import { useEffect, useState, useRef } from "react";
import { GraduationCap, Loader2, Sparkles, TrendingUp } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import {
  DIFFICULTIES,
  QUANTITIES,
  SUBJECTS,
  isSubjectAvailable,
  type GeneratedPaper,
  type OlympiadLevel,
  type PreviewRequest,
  type QuotaError,
  type Subject
} from "@/lib/types";
import { Analytics } from "@/lib/analytics";
import { SubjectCard } from "./SubjectCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function GenerationLoader({ subject, grade, count, mistakesOnly }: { subject: string; grade: number; count: number; mistakesOnly?: boolean }) {
  const [msgIdx, setMsgIdx] = useState(0);
  const messages = mistakesOnly
    ? [
        "Scanning database for unresolved mistakes...",
        "Retrieving your past incorrect answers...",
        "Compiling mistake review paper...",
        "Formatting your practice session..."
      ]
    : [
        `Analyzing Class ${grade} ${subject} curriculum...`,
        "Gathering past Olympiad patterns...",
        `Generating ${count} exam-level questions...`,
        "Applying difficulty scaling...",
        "Formatting your exam paper..."
      ];

  useEffect(() => {
    const timer = setInterval(() => {
      setMsgIdx((prev) => (prev < messages.length - 1 ? prev + 1 : prev));
    }, 2000);
    return () => clearInterval(timer);
  }, [messages.length]);

  return (
    <div className="w-full max-w-4xl overflow-hidden rounded-2xl border border-slate-200 bg-white/60 backdrop-blur-md shadow-lg p-8 min-h-[450px] flex flex-col items-center justify-center">
      <div className="w-full max-w-md space-y-6 animate-pulse opacity-70">
        {/* Skeleton Header */}
        <div className="flex items-center justify-between border-b border-slate-200 pb-4">
          <div className="h-6 w-1/3 bg-slate-300 rounded-md"></div>
          <div className="h-6 w-1/4 bg-slate-300 rounded-md"></div>
        </div>
        {/* Skeleton Questions */}
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-4 pt-2">
            <div className="h-4 w-3/4 bg-slate-300 rounded"></div>
            <div className="space-y-2.5 pl-4">
              <div className="h-3 w-1/2 bg-slate-200 rounded"></div>
              <div className="h-3 w-2/3 bg-slate-200 rounded"></div>
              <div className="h-3 w-1/3 bg-slate-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-12 flex flex-col items-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600 mb-4" />
        <p className="text-sm font-semibold text-brand-700 h-6 transition-all duration-300">
          {messages[msgIdx]}
        </p>
      </div>
    </div>
  );
}

export function ConfigForm({
  initialConfig,
  adaptiveMessage,
  autoStart,
  onGenerated,
  onQuotaExceeded
}: {
  initialConfig?: Partial<PreviewRequest>;
  adaptiveMessage?: string;
  autoStart?: boolean;
  onGenerated: (config: PreviewRequest, paper: GeneratedPaper, simulationMode: boolean) => void;
  onQuotaExceeded: (info: QuotaError) => void;
}) {
  const { getToken } = useAuth();
  const [subject, setSubject] = useState<string>(initialConfig?.subject ?? "Math");
  const [grade, setGrade] = useState<number>(initialConfig?.grade ?? 6);
  const [difficulty, setDifficulty] = useState<string>(initialConfig?.difficulty ?? "Foundation");
  const [count, setCount] = useState<number>(initialConfig?.count ?? 5);
  const [simMode, setSimMode] = useState(false);
  const [mistakesOnly] = useState<boolean>(initialConfig?.mistakesOnly ?? false);
  const [olympiadLevel, setOlympiadLevel] = useState<OlympiadLevel>(
    (initialConfig?.olympiadLevel) ?? "L1"
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resetNotice, setResetNotice] = useState<string | null>(null);

  const hasAutoStarted = useRef(false);

  useEffect(() => {
    if (autoStart && !hasAutoStarted.current) {
      hasAutoStarted.current = true;
      const fakeEvent = { preventDefault: () => {} } as React.FormEvent;
      onSubmit(fakeEvent);
    }
  }, [autoStart]); // eslint-disable-line react-hooks/exhaustive-deps

  function handleGradeChange(newGrade: number) {
    setGrade(newGrade);
    setResetNotice(null);
    if (!isSubjectAvailable(subject as Subject, newGrade)) {
      const fallback = SUBJECTS.find((s) => isSubjectAvailable(s, newGrade)) ?? SUBJECTS[0];
      setSubject(fallback);
      setResetNotice(`${subject} isn't offered at Class ${newGrade} — switched to ${fallback}.`);
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const config: PreviewRequest = { subject, grade, difficulty, count, mistakesOnly, olympiadLevel };
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/papers/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(config)
      });
      if (res.status === 402) {
        const info: QuotaError = await res.json();
        Analytics.quotaExceeded(subject, grade);
        onQuotaExceeded(info);
        return;
      }
      if (!res.ok) throw new Error((await res.text()) || `Request failed (${res.status})`);
      const paper: GeneratedPaper = await res.json();
      Analytics.paperGenerated({
        subject,
        grade,
        difficulty,
        count,
        simulationMode: simMode,
        mistakesOnly,
      });
      onGenerated(config, paper, simMode);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <GenerationLoader subject={subject} grade={grade} count={count} mistakesOnly={mistakesOnly} />;
  }

  return (
    <form
      onSubmit={onSubmit}
      className="w-full max-w-4xl overflow-hidden rounded-2xl border border-white/40 bg-white/70 backdrop-blur-md shadow-xl transition-all"
    >
      {/* Card header */}
      <div className="bg-gradient-hero px-6 py-5 shadow-sm">
        <h2 className="text-base font-bold text-white">Configure your practice paper</h2>
        <p className="mt-0.5 text-xs text-brand-200">
          AI generates fresh, exam-ready questions in seconds — no repeats
        </p>
      </div>

      <div className="p-6">

      {adaptiveMessage && (
        <div className="mb-5 flex items-start gap-3 rounded-xl border border-brand-200 bg-brand-50 px-4 py-3">
          <TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />
          <div>
            <p className="text-xs font-bold text-brand-800">AI Recommendation</p>
            <p className="text-xs text-brand-700">{adaptiveMessage}</p>
          </div>
        </div>
      )}

      {/* Olympiad level selector */}
      <div className="mb-5 rounded-xl border border-slate-200 bg-slate-50/80 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Preparing for</p>
        <div className="flex gap-3">
          {(["L1", "L2"] as OlympiadLevel[]).map((lvl) => {
            const isActive = olympiadLevel === lvl;
            const info = lvl === "L1"
              ? { label: "Level 1 — School Exam", desc: "First round, school-level competition" }
              : { label: "Level 2 — National Exam", desc: "Advanced round for top Level 1 qualifiers" };
            return (
              <button
                key={lvl}
                type="button"
                onClick={() => {
                  setOlympiadLevel(lvl);
                  if (lvl === "L2" && difficulty === "Foundation") setDifficulty("Advanced");
                }}
                className={`flex-1 rounded-xl border px-3 py-2.5 text-left text-sm transition ${
                  isActive
                    ? "border-brand-600 bg-brand-50 shadow-sm"
                    : "border-slate-200 bg-white hover:bg-slate-50"
                }`}
              >
                <span className={`font-bold block ${isActive ? "text-brand-700" : "text-slate-700"}`}>{info.label}</span>
                <span className={`text-[11px] ${isActive ? "text-brand-500" : "text-slate-400"}`}>{info.desc}</span>
              </button>
            );
          })}
        </div>
        {olympiadLevel === "L2" && (
          <p className="mt-2 text-[11px] text-brand-600 bg-brand-50 rounded-lg px-2 py-1">
            Level 2 prep: we&apos;ll focus on harder, application-style Olympiad questions. &quot;Olympiad&quot; difficulty recommended.
          </p>
        )}
      </div>

      {/* Grade + Level — shown first */}
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          Class
          <select
            value={grade}
            onChange={(e) => handleGradeChange(Number(e.target.value))}
            className="rounded-lg border border-slate-300 bg-white/80 backdrop-blur-sm px-3 py-2 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
              <option key={g} value={g}>
                Class {g}
              </option>
            ))}
          </select>
        </label>

        <fieldset className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          <legend>Level</legend>
          <div className="mt-1 flex gap-2">
            {DIFFICULTIES.map((d) => {
              const isRecommended = initialConfig?.difficulty === d && adaptiveMessage;
              return (
                <label
                  key={d}
                  className={`relative flex-1 cursor-pointer rounded-lg border px-3 py-2 text-center text-sm transition ${
                    difficulty === d
                      ? "border-brand-600 bg-brand-50/80 text-brand-700 shadow-sm"
                      : "border-slate-300 bg-white/80 text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {isRecommended && (
                    <span className="absolute -top-2 left-1/2 -translate-x-1/2 rounded-full bg-cta-600 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-white">
                      AI Pick
                    </span>
                  )}
                  <input
                    type="radio"
                    name="difficulty"
                    value={d}
                    checked={difficulty === d}
                    onChange={() => setDifficulty(d)}
                    className="sr-only"
                  />
                  {d}
                </label>
              );
            })}
          </div>
        </fieldset>
      </div>

      {/* Subject selection — below grade/level */}
      <div className="mt-6">
        <p className="text-sm font-semibold text-slate-700">Pick a subject</p>
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SUBJECTS.map((s) => {
            const unavailable = !isSubjectAvailable(s, grade);
            return (
              <SubjectCard
                key={s}
                name={s}
                selected={subject === s}
                onClick={() => { setSubject(s); setResetNotice(null); }}
                disabled={unavailable}
              />
            );
          })}
        </div>
        {resetNotice && (
          <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            {resetNotice}
          </p>
        )}
      </div>

      <div className="mt-6">
        <p className="text-sm font-semibold text-slate-700">Number of questions</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {QUANTITIES.map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setCount(n)}
              className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${
                count === n
                  ? "border-brand-600 bg-brand-600 text-white shadow-sm"
                  : "border-slate-300 bg-white/80 backdrop-blur-sm text-slate-700 hover:bg-slate-50"
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Larger sets take longer to generate (35 ≈ 30–60s).
        </p>
      </div>

      {/* Simulation mode toggle */}
      <label className="mt-5 flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-white/60 backdrop-blur-sm px-4 py-3 shadow-sm hover:bg-slate-50/80 transition-colors">
        <div className="relative mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center">
          <input
            type="checkbox"
            checked={simMode}
            onChange={(e) => setSimMode(e.target.checked)}
            className="peer sr-only"
          />
          <div className={`h-5 w-5 rounded border-2 transition ${simMode ? "border-brand-600 bg-brand-600" : "border-slate-300 bg-white"}`}>
            {simMode && (
              <svg className="h-full w-full p-0.5 text-white" viewBox="0 0 12 12" fill="none">
                <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <GraduationCap className="h-3.5 w-3.5 text-brand-600" />
            <span className="text-sm font-semibold text-slate-800">Exam Simulation Mode</span>
          </div>
          <p className="mt-0.5 text-xs text-slate-500">
            Full-screen, no navigation, timed pressure — mirrors a real exam hall. View OMR sheet on completion.
          </p>
        </div>
      </label>

      <button
        type="submit"
        disabled={loading}
        className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cta-600 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-cta-600/30 transform transition-all hover:bg-cta-700 hover:scale-[1.02] disabled:cursor-not-allowed disabled:bg-slate-400 disabled:scale-100 disabled:shadow-none"
      >
        <Sparkles className="h-5 w-5" />
        {simMode ? "Enter Exam Hall" : "Generate & Start Test"}
      </button>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <p className="font-semibold">Generation failed</p>
          <p className="mt-1 whitespace-pre-wrap break-words">{error}</p>
        </div>
      )}
      </div>{/* end p-6 */}
    </form>
  );
}

