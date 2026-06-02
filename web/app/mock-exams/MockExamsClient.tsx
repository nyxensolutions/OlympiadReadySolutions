"use client";

import { useState, useEffect, useRef } from "react";
import { Award, Clock, FileText, ChevronRight, CheckCircle2, AlertTriangle, Loader2, Sparkles, Star, Check } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { OLYMPIAD_PATTERNS, getAvailableOlympiads, type OlympiadLevel } from "@/lib/olympiadPatterns";
import { SUBJECT_GRADE_MAP, type Subject, type GeneratedPaper, type AttemptResult } from "@/lib/types";
import { TestArena } from "@/components/TestArena";
import { ResultsScreen } from "@/components/ResultsScreen";
import { useAuth } from "@clerk/nextjs";
import { AuthGate } from "@/components/AuthGate";
import { Analytics } from "@/lib/analytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

const GENERATION_MESSAGES = [
  "Analyzing curriculum & subject syllabus",
  "Curating high-fidelity Olympiad question patterns",
  "Calibrating Achievers section difficulty",
  "Structuring marking scheme & sections",
  "Finalizing your real-time simulator exam"
];

export default function MockExamsPage() {
  const { isSignedIn, getToken } = useAuth();
  const [subject, setSubject] = useState<Subject>("Mathematics");
  const [grade, setGrade] = useState<number>(6);
  const [level, setLevel] = useState<OlympiadLevel>("L1");
  const [complexity, setComplexity] = useState<"Foundation" | "Advanced" | "Olympiad">("Advanced");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [generatedPaper, setGeneratedPaper] = useState<GeneratedPaper | null>(null);
  const [paper, setPaper] = useState<GeneratedPaper | null>(null);
  const [result, setResult] = useState<AttemptResult | null>(null);

  const [loadingMsgIdx, setLoadingMsgIdx] = useState(0);
  const [loadingDots, setLoadingDots] = useState(".");
  const [loadingProgress, setLoadingProgress] = useState(0);
  const errorRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to error banner whenever an error appears
  useEffect(() => {
    if (error && errorRef.current) {
      errorRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [error]);

  useEffect(() => {
    if (!loading) return;
    setLoadingMsgIdx(0);
    setLoadingProgress(0);
    
    const msgTimer = setInterval(() => {
      setLoadingMsgIdx((prev) => (prev < GENERATION_MESSAGES.length - 1 ? prev + 1 : prev));
    }, 2200);
    const dotTimer = setInterval(() => {
      setLoadingDots((d) => (d.length >= 3 ? "." : d + "."));
    }, 500);
    const progTimer = setInterval(() => {
      setLoadingProgress((p) => (p < 95 ? p + 1 : p));
    }, 90);
    
    return () => {
      clearInterval(msgTimer);
      clearInterval(dotTimer);
      clearInterval(progTimer);
    };
  }, [loading]);

  const availablePatterns = getAvailableOlympiads(subject, grade, level);
  const selectedPattern = availablePatterns.length > 0 ? availablePatterns[0] : null;

  const gradeRange = SUBJECT_GRADE_MAP[subject] || { min: 1, max: 12 };
  const gradeOptions = [];
  for (let g = gradeRange.min; g <= gradeRange.max; g++) {
    gradeOptions.push(g);
  }

  const handleSubjectChange = (newSubject: Subject) => {
    setSubject(newSubject);
    setGeneratedPaper(null);
    const range = SUBJECT_GRADE_MAP[newSubject] || { min: 1, max: 12 };
    if (grade < range.min) {
      setGrade(range.min);
    } else if (grade > range.max) {
      setGrade(range.max);
    }
  };

  async function startMockExam() {
    if (!selectedPattern) return;
    setLoading(true);
    setError("");
    setGeneratedPaper(null);

    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/mock-exams/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          patternId: selectedPattern.id,
          subject,
          grade,
          level,
          complexity,
          olympiadId: selectedPattern.id,
          totalTimeMinutes: selectedPattern.totalTimeMinutes,
          sections: selectedPattern.sections
        })
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.message || `Server error (${res.status})`);
      }

      const paperData = await res.json();
      setGeneratedPaper(paperData);
    } catch (err: any) {
      setError(err.message || "Failed to generate mock exam. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleEnterArena() {
    if (!generatedPaper) return;
    setPaper(generatedPaper);
    Analytics.paperGenerated({
      subject,
      grade,
      difficulty: "Olympiad",
      count: selectedPattern ? selectedPattern.sections.reduce((a, s) => a + s.questions, 0) : generatedPaper.questions.length,
      simulationMode: true,
      mistakesOnly: false
    });
  }

  async function handleSubmit(attempt: AttemptResult) {
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/tests/submit`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          paperId: attempt.paperId,
          answers: attempt.userAnswers,
          timeTakenSeconds: attempt.timeTakenSeconds,
        })
      });

      if (!res.ok) {
        const errData = await res.text();
        alert(errData || "Failed to submit test");
        return;
      }

      const data = await res.json();
      setResult({
        ...attempt,
        totalMarks: data.totalMarks,
        earnedMarks: data.earnedMarks
      });
      setPaper(null);

      Analytics.testCompleted({
        subject,
        grade,
        difficulty: "Olympiad",
        totalQuestions: attempt.questions.length,
        scorePct: Math.round((data.earnedMarks / data.totalMarks) * 100),
        timeTakenSeconds: attempt.timeTakenSeconds
      });
    } catch (err) {
      console.error(err);
      alert("Failed to submit exam. Please try again.");
    }
  }

  if (result && !paper) {
    return (
      <main className="flex min-h-screen flex-col bg-slate-50">
        <AppHeader />
        <div className="mx-auto w-full max-w-5xl px-4 py-8">
          <ResultsScreen result={result} onRestart={() => { setResult(null); setGeneratedPaper(null); }} />
        </div>
      </main>
    );
  }

  if (paper) {
    return (
      <main className="flex min-h-screen flex-col bg-slate-50">
        <TestArena
          config={{ subject, grade, difficulty: "Olympiad", count: paper.questions.length, olympiadLevel: level, olympiadId: selectedPattern?.id }}
          paper={paper}
          simulationMode={true}
          onSubmit={handleSubmit}
        />
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col bg-slate-50">
      <AppHeader />
      <AuthGate>
      <div className="mx-auto w-full max-w-5xl px-4 py-12">
        <div className="mb-10 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-brand-100 px-4 py-1.5 text-sm font-bold text-brand-800">
            <Award className="h-4 w-4" />
            Full Olympiad Simulator
          </div>
          <h1 className="text-4xl font-black tracking-tight text-slate-900 sm:text-5xl">
            Real Exam. <span className="text-brand-600">Real Pressure.</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
            Experience the exact pattern, scoring, and difficulty of official Olympiads. Your answers and analytics are recorded to predict your rank.
          </p>
        </div>

        {error && (
          <div
            ref={errorRef}
            className="mb-8 rounded-xl border-2 border-red-300 bg-red-50 p-5 flex items-start gap-3 text-red-800 shadow-md"
          >
            <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5 text-red-500" />
            <div className="flex-1">
              <p className="font-bold text-sm">{error}</p>
              {error.toLowerCase().includes("upgrade") && (
                <a
                  href="/dashboard"
                  className="mt-2 inline-flex items-center gap-1 text-xs font-semibold bg-red-600 text-white px-3 py-1.5 rounded-lg hover:bg-red-700 transition"
                >
                  View upgrade options →
                </a>
              )}
            </div>
          </div>
        )}

        <div className="grid gap-8 md:grid-cols-[1fr_400px]">
          {/* Configurator */}
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <FileText className="h-5 w-5 text-brand-500" /> Exam Setup
            </h2>

            {/* AI Callout Banner OR Animation OR Ready Card */}
            {!loading && !generatedPaper && (
              <div className="mb-6 rounded-2xl bg-gradient-to-r from-violet-600 via-indigo-600 to-brand-600 p-5 text-white shadow-md relative overflow-hidden">
                <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-10">
                  <Sparkles className="h-24 w-24" />
                </div>
                <div className="relative z-10 flex items-start gap-3.5">
                  <div className="rounded-lg bg-white/10 p-2 shrink-0">
                    <Sparkles className="h-5 w-5 text-yellow-300 animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-sm sm:text-base mb-1 tracking-tight">AI-Powered Adaptive Mock Exams</h3>
                    <p className="text-xs text-brand-100 leading-relaxed font-medium">
                      <span className="font-extrabold text-yellow-300">Free tier includes 1 full exam. Upgraded users get 7 fresh exams/week per subject.</span> Our advanced AI dynamically curates and generates high-fidelity questions tailored to your class, skills, and subjects. Practice with limitless fresh scenarios calibrated to official Olympiad syllabi!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {loading && (
              <div className="mb-6 w-full overflow-hidden rounded-2xl border border-brand-200/60 bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 shadow-xl p-6 min-h-[260px] flex flex-col items-center justify-center relative text-white animate-in fade-in duration-300">
                {/* Animated grid background */}
                <div className="absolute inset-0 opacity-10" style={{
                  backgroundImage: `linear-gradient(rgba(99,102,241,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.4) 1px, transparent 1px)`,
                  backgroundSize: "30px 30px"
                }} />

                {/* Glowing orb */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full bg-brand-600/10 blur-3xl pointer-events-none" />

                {/* Neural nodes animation */}
                <div className="relative flex items-center gap-2 mb-6">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="rounded-full bg-brand-400 animate-pulse"
                      style={{
                        width: i === 2 ? 12 : 7,
                        height: i === 2 ? 12 : 7,
                        opacity: loadingMsgIdx >= i ? 1 : 0.25,
                        boxShadow: loadingMsgIdx >= i ? '0 0 8px 2px rgba(99,102,241,0.7)' : 'none',
                        transition: 'all 0.5s ease',
                        animationDelay: `${i * 0.15}s`
                      }}
                    />
                  ))}
                </div>

                {/* AI Brain icon */}
                <div className="mb-4 relative">
                  <div className="h-14 w-14 rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center backdrop-blur-sm">
                    <Sparkles className="h-7 w-7 text-brand-300 animate-spin" style={{ animationDuration: '3s' }} />
                  </div>
                  <div className="absolute -top-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 flex items-center justify-center">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-300 animate-ping" />
                  </div>
                </div>

                {/* Message */}
                <p className="text-sm font-bold text-white mb-1 text-center tracking-tight transition-all duration-500">
                  {GENERATION_MESSAGES[loadingMsgIdx]}{loadingDots}
                </p>
                <p className="text-[10px] text-brand-300 mb-5 text-center">AI-powered · Olympiad-grade · Fresh syllabus mapping</p>

                {/* Progress bar */}
                <div className="w-full max-w-[200px]">
                  <div className="flex justify-between text-[9px] text-brand-400 mb-1 font-mono">
                    <span>Curating Paper</span>
                    <span>{loadingProgress}%</span>
                  </div>
                  <div className="h-1 w-full rounded-full bg-slate-700 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-brand-400 to-violet-400 transition-all duration-200"
                      style={{ width: `${loadingProgress}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {!loading && generatedPaper && (
              <div className="mb-6 rounded-2xl border-2 border-emerald-500 bg-emerald-50/60 backdrop-blur-md p-6 text-slate-800 shadow-lg relative overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-5">
                  <CheckCircle2 className="h-32 w-32 text-emerald-600" />
                </div>
                <div className="relative z-10 flex items-start gap-4">
                  <div className="rounded-xl bg-emerald-100 p-2.5 shrink-0 border border-emerald-200">
                    <CheckCircle2 className="h-6 w-6 text-emerald-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-black text-emerald-950 text-base mb-1 tracking-tight flex items-center gap-1.5">
                      Olympiad Simulator Ready!
                    </h3>
                    <p className="text-xs text-emerald-800 leading-relaxed font-semibold">
                      Your syllabus-calibrated exam is fully generated and ready. The timer will start immediately once you enter the arena. Make sure you have a distraction-free environment!
                    </p>

                    <div className="mt-4 grid grid-cols-2 gap-2 text-xs border-t border-emerald-200/50 pt-4">
                      <div className="flex items-center gap-1.5 font-semibold text-emerald-950">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        Class/Grade: <span className="font-extrabold">{grade}</span>
                      </div>
                      <div className="flex items-center gap-1.5 font-semibold text-emerald-950">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        Subject: <span className="font-extrabold">{subject}</span>
                      </div>
                      <div className="flex items-center gap-1.5 font-semibold text-emerald-950">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        Questions: <span className="font-extrabold">{generatedPaper.questions.length}</span>
                      </div>
                      <div className="flex items-center gap-1.5 font-semibold text-emerald-950">
                        <span className="h-2 w-2 rounded-full bg-emerald-500" />
                        Time Limit: <span className="font-extrabold">{selectedPattern?.totalTimeMinutes} Mins</span>
                      </div>
                    </div>

                    <button
                      onClick={handleEnterArena}
                      className="mt-5 w-full rounded-xl bg-emerald-600 py-3.5 font-bold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-700 transition hover:scale-[1.02] flex items-center justify-center gap-2"
                    >
                      <Award className="h-5 w-5" /> Enter Exam Arena &amp; Start Timer
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-6">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Select Subject</label>
                <select
                  value={subject}
                  onChange={(e) => handleSubjectChange(e.target.value as Subject)}
                  className="w-full rounded-xl border-slate-300 bg-slate-50 px-4 py-3 font-medium text-slate-800 focus:border-brand-500 focus:ring-brand-500"
                >
                  {Object.keys(SUBJECT_GRADE_MAP).map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Class / Grade</label>
                  <select
                    value={grade}
                    onChange={(e) => {
                      setGrade(parseInt(e.target.value));
                      setGeneratedPaper(null);
                    }}
                    className="w-full rounded-xl border-slate-300 bg-slate-50 px-4 py-3 font-medium text-slate-800 focus:border-brand-500 focus:ring-brand-500"
                  >
                    {gradeOptions.map((g) => (
                      <option key={g} value={g}>Class {g}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-semibold text-slate-700">Level</label>
                  <select
                    value={level}
                    onChange={(e) => {
                      setLevel(e.target.value as OlympiadLevel);
                      setGeneratedPaper(null);
                    }}
                    className="w-full rounded-xl border-slate-300 bg-slate-50 px-4 py-3 font-medium text-slate-800 focus:border-brand-500 focus:ring-brand-500"
                  >
                    <option value="L1">Level 1 (School)</option>
                    <option value="L2">Level 2 (National)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Complexity
                  <span className="ml-2 text-xs font-normal text-slate-500">Controls difficulty mix of questions</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(["Foundation", "Advanced", "Olympiad"] as const).map((c) => {
                    const meta = {
                      Foundation: { label: "Foundation", sub: "Easy questions", color: "emerald" },
                      Advanced:   { label: "Advanced",   sub: "Balanced mix",  color: "brand"   },
                      Olympiad:   { label: "Olympiad",   sub: "Hardest level", color: "violet"  },
                    }[c];
                    const isSelected = complexity === c;
                    const colorMap: Record<string, string> = {
                      emerald: isSelected ? "border-emerald-500 bg-emerald-50 text-emerald-800" : "border-slate-200 bg-slate-50 text-slate-600 hover:border-emerald-300",
                      brand:   isSelected ? "border-brand-500 bg-brand-50 text-brand-800"     : "border-slate-200 bg-slate-50 text-slate-600 hover:border-brand-300",
                      violet:  isSelected ? "border-violet-500 bg-violet-50 text-violet-800"   : "border-slate-200 bg-slate-50 text-slate-600 hover:border-violet-300",
                    };
                    return (
                      <button
                        key={c}
                        type="button"
                        onClick={() => { setComplexity(c); setGeneratedPaper(null); }}
                        className={`rounded-xl border-2 px-3 py-2.5 text-center transition ${colorMap[meta.color]}`}
                      >
                        <p className="text-xs font-bold">{meta.label}</p>
                        <p className="text-[10px] opacity-70 mt-0.5">{meta.sub}</p>
                        {isSelected && <div className="mt-1 h-1 w-4 mx-auto rounded-full bg-current opacity-50" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Pattern Preview */}
          <div>
            {selectedPattern ? (
              <div className="rounded-3xl border-2 border-brand-200 bg-brand-50/50 p-8 h-full flex flex-col justify-between">
                <div>
                  <h3 className="font-black text-brand-900 text-lg mb-2">{selectedPattern.name}</h3>
                  <div className="flex items-center gap-4 text-sm font-semibold text-brand-700 mb-6">
                    <span className="flex items-center gap-1"><Clock className="h-4 w-4" /> {selectedPattern.totalTimeMinutes} Minutes</span>
                    <span className="flex items-center gap-1"><FileText className="h-4 w-4" /> {selectedPattern.sections.reduce((a, s) => a + s.questions, 0)} Questions</span>
                  </div>

                  <div className="space-y-4 mb-8">
                    {selectedPattern.sections.map((sec, i) => (
                      <div key={i} className="rounded-xl bg-white p-4 shadow-sm border border-brand-100">
                        <p className="font-bold text-slate-800 mb-1">{sec.name}</p>
                        <div className="flex justify-between text-sm text-slate-500 font-medium">
                          <span>{sec.questions} Questions</span>
                          <span>{sec.marksPerQuestion} Mark{sec.marksPerQuestion > 1 ? "s" : ""} Each</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {generatedPaper ? (
                  <button
                    onClick={handleEnterArena}
                    className="w-full rounded-2xl bg-emerald-600 py-4 font-bold text-white shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-700 hover:shadow-emerald-500/40 flex items-center justify-center gap-2"
                  >
                    <Award className="h-5 w-5" /> Enter Exam Arena
                  </button>
                ) : (
                  <button
                    onClick={startMockExam}
                    disabled={loading}
                    className="w-full rounded-2xl bg-brand-600 py-4 font-bold text-white shadow-lg shadow-brand-500/30 transition hover:bg-brand-700 hover:shadow-brand-500/40 disabled:opacity-50 flex items-center justify-center gap-2 animate-in fade-in"
                  >
                     {loading ? <><Loader2 className="h-5 w-5 animate-spin" /> Generating Exam...</> : <><Award className="h-5 w-5" /> Start Exam</>}
                  </button>
                )}
              </div>
            ) : (
              <div className="rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
                <AlertTriangle className="h-10 w-10 text-slate-400 mb-4" />
                <h3 className="font-bold text-slate-700">No Pattern Found</h3>
                <p className="text-sm text-slate-500 mt-2">
                  We don't have an official Mock Exam pattern for {subject} Class {grade} {level}. Try a different selection.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-12 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 font-bold text-slate-900 text-lg">
            <Star className="h-5 w-5 text-brand-500 animate-pulse" />
            Frequently Asked Questions
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              {
                q: "How do Mock Exams differ from regular practice tests?",
                a: "Practice tests focus on single masteries and are customizable. Mock Exams perfectly replicate official Olympiad patterns (SOF IMO, NSO, NSTSE, etc.), matching exact section layouts, time limits, scoring schemes, and question counts.",
              },
              {
                q: "What are the limits for Free vs. Upgraded users?",
                a: "Free tier accounts get 1 free Mock Exam globally across any subject to test the high-fidelity simulator. Upgraded users (Pro/Modular) unlock 7 fresh Mock Exam generations every single week per subject, resetting every Monday!",
              },
              {
                q: "Are the questions in Mock Exams fresh or repeated?",
                a: "Every single mock generation is fully fresh and custom curated. Our hybrid AI engine gathers syllabus-calibrated questions and generates new ones dynamically so you always get a completely unique test paper.",
              },
              {
                q: "How are the final scores and rankings calculated?",
                a: "Mock Exams follow the official scoring rules (including section weightages). After completion, we evaluate your section-wise accuracy, total marks, and completion speed to compute advanced predictive percentiles and ranks.",
              },
              {
                q: "Can I pause the Mock Exam once I start?",
                a: "No. To recreate the real pressure of the official exam hall, the timer runs continuously once you enter the Arena. Make sure you are in a quiet, distraction-free environment with a stable connection before entering!",
              },
              {
                q: "How does the hybrid AI engine benefit my preparation?",
                a: "Our advanced hybrid AI calibrates the difficult 'Achievers Section' dynamically to push your logical thinking. It guarantees smart preparation tailored to your exact learning curves and official syllabi.",
              },
            ].map(({ q, a }) => (
              <div key={q} className="rounded-xl bg-slate-50 p-4 hover:bg-slate-100/50 transition">
                <p className="mb-1 text-sm font-semibold text-slate-800">{q}</p>
                <p className="text-xs leading-relaxed text-slate-600">{a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      </AuthGate>
    </main>
  );
}
