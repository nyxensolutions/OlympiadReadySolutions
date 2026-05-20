"use client";

import { useEffect, useState, useRef } from "react";
import { GraduationCap, Sparkles, TrendingUp } from "lucide-react";
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
  const [dots, setDots] = useState(".");
  const [progress, setProgress] = useState(0);

  const messages = mistakesOnly
    ? [
        "Scanning your mistake history",
        "Retrieving past incorrect answers",
        "Building targeted review set",
        "Formatting your practice session"
      ]
    : [
        `Analysing Class ${grade} ${subject} curriculum`,
        "Gathering Olympiad question patterns",
        `Generating ${count} exam-level questions`,
        "Calibrating difficulty parameters",
        "Finalising your exam paper"
      ];

  useEffect(() => {
    const msgTimer = setInterval(() => {
      setMsgIdx((prev) => (prev < messages.length - 1 ? prev + 1 : prev));
    }, 2200);
    const dotTimer = setInterval(() => {
      setDots((d) => (d.length >= 3 ? "." : d + "."));
    }, 500);
    // Smooth progress fill over ~10s
    const progTimer = setInterval(() => {
      setProgress((p) => (p < 92 ? p + 1 : p));
    }, 110);
    return () => { clearInterval(msgTimer); clearInterval(dotTimer); clearInterval(progTimer); };
  }, [messages.length]);

  const nodes = [0, 1, 2, 3, 4];

  return (
    <div className="w-full max-w-4xl overflow-hidden rounded-2xl border border-brand-200/60 bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 shadow-2xl p-8 min-h-[420px] flex flex-col items-center justify-center relative">
      {/* Animated grid background */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: `linear-gradient(rgba(99,102,241,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.4) 1px, transparent 1px)`,
        backgroundSize: "40px 40px"
      }} />

      {/* Glowing orb */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-brand-600/10 blur-3xl pointer-events-none" />

      {/* Neural nodes animation */}
      <div className="relative flex items-center gap-3 mb-8">
        {nodes.map((i) => (
          <div
            key={i}
            className="rounded-full bg-brand-400"
            style={{
              width: i === 2 ? 14 : 8,
              height: i === 2 ? 14 : 8,
              opacity: msgIdx >= i ? 1 : 0.25,
              boxShadow: msgIdx >= i ? '0 0 10px 2px rgba(99,102,241,0.7)' : 'none',
              transition: 'all 0.5s ease',
              animation: `pulse ${1.2 + i * 0.15}s ease-in-out infinite alternate`
            }}
          />
        ))}
        <style>{`@keyframes pulse { from { transform: scale(1); } to { transform: scale(1.4); } }`}</style>
      </div>

      {/* AI Brain icon */}
      <div className="mb-5 relative">
        <div className="h-16 w-16 rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center backdrop-blur-sm">
          <Sparkles className="h-8 w-8 text-brand-300" style={{ animation: 'spin 3s linear infinite' }} />
        </div>
        <div className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-emerald-400 border-2 border-slate-900 flex items-center justify-center">
          <div className="h-2 w-2 rounded-full bg-emerald-300 animate-ping" />
        </div>
      </div>

      {/* Message */}
      <p className="text-base font-bold text-white mb-1 text-center tracking-tight transition-all duration-500">
        {messages[msgIdx]}{dots}
      </p>
      <p className="text-xs text-brand-300 mb-6 text-center">AI-powered · Olympiad-grade · Fresh every time</p>

      {/* Progress bar */}
      <div className="w-full max-w-xs">
        <div className="flex justify-between text-[10px] text-brand-400 mb-1.5 font-mono">
          <span>Generating</span>
          <span>{progress}%</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-slate-700 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-400 to-violet-400 transition-all duration-200"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Skeleton rows below */}
      <div className="mt-8 w-full max-w-xs space-y-2 opacity-20">
        {["w-3/4", "w-1/2", "w-2/3"].map((w, i) => (
          <div key={i} className={`h-2 ${w} rounded bg-slate-500 animate-pulse`} />
        ))}
      </div>
    </div>
  );
}

export function ConfigForm({
  initialConfig,
  adaptiveMessage,
  autoStart,
  onGenerated,
  onQuotaExceeded,
  onRequiresUpgrade,
  status
}: {
  initialConfig?: Partial<PreviewRequest>;
  adaptiveMessage?: string;
  autoStart?: boolean;
  onGenerated: (config: PreviewRequest, paper: GeneratedPaper, simulationMode: boolean) => void;
  onQuotaExceeded: (info: QuotaError) => void;
  onRequiresUpgrade?: () => void;
  status?: { tier: "Free" | "Pro" } | null;
}) {
  const { getToken } = useAuth();
  const [subject, setSubject] = useState<string>(initialConfig?.subject ?? "Math");
  const [grade, setGrade] = useState<number>(() => {
    if (initialConfig?.grade) return initialConfig.grade;
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("olympiad_grade");
      return stored ? Number(stored) : 1;
    }
    return 1;
  });
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
    if (typeof window !== "undefined") {
      localStorage.setItem("olympiad_grade", newGrade.toString());
    }
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
            const isLocked = lvl === "L2" && status?.tier !== "Pro";
            const info = lvl === "L1"
              ? { label: "Level 1", desc: "First round, school-level competition" }
              : { label: "Level 2", desc: "Advanced round for top Level 1 qualifiers" };
            return (
              <button
                key={lvl}
                type="button"
                title={isLocked ? "Level 2 is available for Pro subscribers only" : undefined}
                onClick={() => {
                  if (isLocked) {
                    onRequiresUpgrade?.();
                  } else {
                    setOlympiadLevel(lvl);
                    if (lvl === "L2") setDifficulty("Olympiad");
                  }
                }}
                className={`flex-1 rounded-xl border px-3 py-2.5 text-left text-sm transition relative ${
                  isActive
                    ? "border-brand-600 bg-brand-50 shadow-sm"
                    : isLocked
                      ? "border-slate-200 bg-slate-50 opacity-60 cursor-pointer hover:opacity-80 hover:border-achiever-300"
                      : "border-slate-200 bg-white hover:bg-slate-50"
                }`}
              >
                {isLocked && (
                  <div className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-slate-200">
                    <svg className="h-3 w-3 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                )}
                <span className={`font-bold block ${isActive ? "text-brand-700" : "text-slate-700"}`}>{info.label}</span>
                <span className={`text-[11px] ${isActive ? "text-brand-500" : "text-slate-400"}`}>{info.desc}</span>
              </button>
            );
          })}
        </div>
        {olympiadLevel === "L2" && (
          <p className="mt-2 text-[11px] text-brand-600 bg-brand-50 rounded-lg px-2 py-1">
            Level 2 prep: we focus on harder, application-style Olympiad questions.
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

