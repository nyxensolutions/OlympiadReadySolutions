"use client";

import { useState } from "react";
import { Award, Clock, FileText, ChevronRight, CheckCircle2, AlertTriangle, Loader2, Sparkles } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { OLYMPIAD_PATTERNS, getAvailableOlympiads, type OlympiadLevel } from "@/lib/olympiadPatterns";
import { SUBJECT_GRADE_MAP, type Subject, type GeneratedPaper, type AttemptResult } from "@/lib/types";
import { TestArena } from "@/components/TestArena";
import { ResultsScreen } from "@/components/ResultsScreen";
import { useAuth } from "@clerk/nextjs";
import { Analytics } from "@/lib/analytics";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export default function MockExamsPage() {
  const { isSignedIn, getToken } = useAuth();
  const [subject, setSubject] = useState<Subject>("Mathematics");
  const [grade, setGrade] = useState<number>(6);
  const [level, setLevel] = useState<OlympiadLevel>("L1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [paper, setPaper] = useState<GeneratedPaper | null>(null);
  const [result, setResult] = useState<AttemptResult | null>(null);

  const availablePatterns = getAvailableOlympiads(subject, grade, level);
  const selectedPattern = availablePatterns.length > 0 ? availablePatterns[0] : null;

  const gradeRange = SUBJECT_GRADE_MAP[subject];
  const gradeOptions = [];
  for (let g = gradeRange.min; g <= gradeRange.max; g++) {
    gradeOptions.push(g);
  }

  const handleSubjectChange = (newSubject: Subject) => {
    setSubject(newSubject);
    const range = SUBJECT_GRADE_MAP[newSubject];
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
          olympiadId: selectedPattern.id,
          totalTimeMinutes: selectedPattern.totalTimeMinutes,
          sections: selectedPattern.sections
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || "Failed to generate mock exam");
      }

      const paperData = await res.json();
      setPaper(paperData);
      Analytics.paperGenerated({
        subject,
        grade,
        difficulty: "Olympiad",
        count: selectedPattern.sections.reduce((a, s) => a + s.questions, 0),
        simulationMode: true,
        mistakesOnly: false
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
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
          {/* Using existing ResultsScreen, but it might not show Earned Marks. It's fine for now. */}
          <ResultsScreen result={result} onRestart={() => setResult(null)} />
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
          <div className="mb-8 rounded-xl bg-red-50 p-4 border border-red-200 flex items-center gap-3 text-red-800">
            <AlertTriangle className="h-5 w-5 shrink-0" />
            <p className="font-semibold">{error}</p>
          </div>
        )}

        <div className="grid gap-8 md:grid-cols-[1fr_400px]">
          {/* Configurator */}
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
              <FileText className="h-5 w-5 text-brand-500" /> Exam Setup
            </h2>

            {/* AI Callout Banner */}
            <div className="mb-6 rounded-2xl bg-gradient-to-r from-violet-600 via-indigo-600 to-brand-600 p-6 text-white shadow-md relative overflow-hidden">
              <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-10">
                <Sparkles className="h-32 w-32" />
              </div>
              <div className="relative z-10 flex items-start gap-4">
                <div className="rounded-xl bg-white/10 p-2.5 shrink-0">
                  <Sparkles className="h-6 w-6 text-yellow-300 animate-pulse" />
                </div>
                <div>
                  <h3 className="font-extrabold text-base mb-1 tracking-tight">AI-Powered Adaptive Mock Exams</h3>
                  <p className="text-xs text-brand-100 leading-relaxed font-medium">
                    Our advanced AI dynamically curates and generates high-fidelity questions tailored precisely to your class grade, specific learning skills, and selected subjects. Practice with limitless fresh scenarios calibrated precisely to official Olympiad syllabi!
                  </p>
                </div>
              </div>
            </div>

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
                    onChange={(e) => setGrade(parseInt(e.target.value))}
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
                    onChange={(e) => setLevel(e.target.value as OlympiadLevel)}
                    className="w-full rounded-xl border-slate-300 bg-slate-50 px-4 py-3 font-medium text-slate-800 focus:border-brand-500 focus:ring-brand-500"
                  >
                    <option value="L1">Level 1 (School)</option>
                    <option value="L2">Level 2 (National)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Pattern Preview */}
          <div>
            {selectedPattern ? (
              <div className="rounded-3xl border-2 border-brand-200 bg-brand-50/50 p-8">
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

                <button
                  onClick={startMockExam}
                  disabled={loading}
                  className="w-full rounded-2xl bg-brand-600 py-4 font-bold text-white shadow-lg shadow-brand-500/30 transition hover:bg-brand-700 hover:shadow-brand-500/40 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                   {loading ? <><Loader2 className="h-5 w-5 animate-spin" /> Generating Exam...</> : <><Award className="h-5 w-5" /> Start Exam</>}
                </button>
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
      </div>
    </main>
  );
}
