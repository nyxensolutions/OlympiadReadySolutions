"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  BookOpen, CheckCircle2, ChevronRight, Loader2,
  Lock, MicVocal, Star, Trophy, XCircle
} from "lucide-react";
import { SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type SpellWord = {
  word: string;
  definition: string;
  usageSentence: string;
  pronunciation: string | null;
  memoryTip: string | null;
  origin: string | null;
  category: string;
  difficulty: string;
  grade: number;
};

type RoundState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "practice"; words: SpellWord[]; idx: number; input: string; revealed: boolean; score: number; results: { word: string; correct: boolean; typed: string }[] }
  | { kind: "finished"; score: number; total: number; results: { word: string; correct: boolean; typed: string }[] };

const DIFFICULTIES = ["Easy", "Medium", "Hard"] as const;

export default function SpellBeePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="spell-bee" />
      <div className="bg-gradient-to-br from-violet-700 via-purple-600 to-indigo-600 px-4 py-12 text-white">
        <div className="mx-auto max-w-4xl">
          <div className="flex items-center gap-3 mb-3">
            <div className="rounded-xl bg-white/10 p-2.5">
              <MicVocal className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-violet-200">Spell Bee</p>
              <h1 className="text-2xl font-extrabold sm:text-3xl">Hummingbird Spell Bee Prep</h1>
            </div>
          </div>
          <p className="max-w-xl text-sm text-violet-100">
            Practice spelling for the Hummingbird Spell Bee competition.
            Words are organised by grade and difficulty — from easy vocabulary to challenging spellings.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {["Grade 1–8", "Easy → Hard", "Definitions & Examples", "Memory Tips"].map((f) => (
              <span key={f} className="inline-flex items-center gap-1 rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white">
                <CheckCircle2 className="h-3 w-3 text-emerald-300" />
                {f}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-8">
        <SignedOut>
          <div className="rounded-2xl border border-violet-100 bg-violet-50 p-8 text-center">
            <Lock className="mx-auto h-10 w-10 text-violet-300 mb-3" />
            <h2 className="text-lg font-bold text-slate-800">Sign in to practise</h2>
            <p className="mt-2 text-sm text-slate-500">Create a free account to access spelling practice.</p>
            <Link
              href="/sign-in"
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-violet-600 px-6 py-3 text-sm font-bold text-white transition hover:bg-violet-700"
            >
              Sign in <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </SignedOut>
        <SignedIn>
          <SpellBeeBody />
        </SignedIn>
      </div>
    </div>
  );
}

function SpellBeeBody() {
  const { getToken } = useAuth();

  const [grade, setGrade] = useState(3);
  const [difficulty, setDifficulty] = useState<typeof DIFFICULTIES[number]>("Easy");
  const [round, setRound] = useState<RoundState>({ kind: "idle" });
  const [tier, setTier] = useState<"Free" | "Pro">("Free");

  async function startRound() {
    setRound({ kind: "loading" });
    try {
      const token = await getToken();
      const res = await fetch(
        `${API_URL}/api/spell-bee/words?grade=${grade}&difficulty=${difficulty}&count=10`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (res.status === 503) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { message?: string }).message ?? "No words available.");
      }
      if (!res.ok) throw new Error(`Failed to load words (${res.status})`);

      const data = await res.json();
      setTier(data.tier);
      if (data.words.length === 0) throw new Error("No words found for this selection.");

      setRound({
        kind: "practice",
        words: data.words,
        idx: 0,
        input: "",
        revealed: false,
        score: 0,
        results: [],
      });
    } catch (e) {
      alert(e instanceof Error ? e.message : "Something went wrong.");
      setRound({ kind: "idle" });
    }
  }

  function handleInput(value: string) {
    if (round.kind !== "practice") return;
    setRound({ ...round, input: value });
  }

  function checkAnswer() {
    if (round.kind !== "practice") return;
    const { words, idx, input, score, results } = round;
    const current = words[idx];
    const correct = input.trim().toLowerCase() === current.word.toLowerCase();
    const newResults = [...results, { word: current.word, correct, typed: input.trim() }];

    if (idx + 1 >= words.length) {
      setRound({ kind: "finished", score: score + (correct ? 1 : 0), total: words.length, results: newResults });
    } else {
      setRound({ ...round, idx: idx + 1, input: "", revealed: false, score: score + (correct ? 1 : 0), results: newResults });
    }
  }

  function reveal() {
    if (round.kind !== "practice") return;
    setRound({ ...round, revealed: true });
  }

  function restart() { setRound({ kind: "idle" }); }

  if (round.kind === "finished") {
    return <Results score={round.score} total={round.total} results={round.results} onRestart={restart} />;
  }

  if (round.kind === "practice") {
    const { words, idx, input, revealed, score } = round;
    const current = words[idx];
    return (
      <PracticeCard
        word={current}
        idx={idx}
        total={words.length}
        score={score}
        input={input}
        revealed={revealed}
        onInput={handleInput}
        onCheck={checkAnswer}
        onReveal={reveal}
        onSkip={() => {
          const newResults = [...round.results, { word: current.word, correct: false, typed: "(skipped)" }];
          if (idx + 1 >= words.length) {
            setRound({ kind: "finished", score: round.score, total: words.length, results: newResults });
          } else {
            setRound({ ...round, idx: idx + 1, input: "", revealed: false, results: newResults });
          }
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {tier === "Free" && (
        <div className="rounded-xl border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-800">
          <span className="font-semibold">Free plan:</span> 5 words per round.{" "}
          <Link href="/" className="underline font-medium">Upgrade to Pro</Link> for 20 words per round + advanced categories.
        </div>
      )}

      {/* Config panel */}
      <div className="rounded-2xl border border-white/40 bg-white/70 backdrop-blur-md shadow-xl p-6">
        <h2 className="text-base font-bold text-slate-900 mb-5">Configure your practice round</h2>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Grade</label>
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 8 }, (_, i) => i + 1).map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGrade(g)}
                  className={`rounded-lg border px-3.5 py-1.5 text-sm font-semibold transition ${
                    grade === g
                      ? "border-violet-600 bg-violet-600 text-white shadow"
                      : "border-slate-300 bg-white text-slate-700 hover:border-violet-300 hover:bg-violet-50"
                  }`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Difficulty</label>
            <div className="flex gap-2">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setDifficulty(d)}
                  className={`flex-1 rounded-xl border px-3 py-2 text-sm font-semibold transition ${
                    difficulty === d
                      ? "border-violet-600 bg-violet-50 text-violet-700"
                      : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
            <p className="mt-1.5 text-xs text-slate-500">
              Easy: common words · Medium: challenging vocabulary · Hard: competition-level spellings
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={startRound}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-violet-600/30 transition hover:bg-violet-700 hover:scale-[1.02]"
        >
          <MicVocal className="h-5 w-5" />
          Start Spell Bee Practice
        </button>
      </div>

      {/* Info section */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h3 className="font-bold text-slate-900 flex items-center gap-2 mb-4">
          <Star className="h-4 w-4 text-amber-500" />
          About Hummingbird Spell Bee
        </h3>
        <div className="grid gap-4 sm:grid-cols-2">
          {[
            { q: "What is Hummingbird Spell Bee?", a: "Hummingbird Spelling Competition is a popular national-level spell bee contest for school students. It tests spelling, vocabulary, and language skills." },
            { q: "Which grades can participate?", a: "Students from Grade 1 to Grade 8 can participate. Each grade has an age-appropriate word list." },
            { q: "How does the practice work?", a: "You see the definition and a usage sentence for a word. You type the spelling. Hints like pronunciation and memory tips are available to help you learn." },
            { q: "What is the free vs. Pro difference?", a: "Free users get 5 words per practice round. Pro users get 20 words per round plus access to advanced word categories and full word-bank search." },
          ].map(({ q, a }) => (
            <div key={q} className="rounded-xl bg-slate-50 p-4">
              <p className="mb-1 text-sm font-semibold text-slate-800">{q}</p>
              <p className="text-xs leading-relaxed text-slate-600">{a}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 rounded-xl border border-amber-100 bg-amber-50 p-3 text-xs text-amber-700">
          <span className="font-semibold">Coming soon:</span> Audio pronunciation, word-list downloads, leaderboard, and full syllabus word lists for all grades.
        </div>
      </div>
    </div>
  );
}

function PracticeCard({
  word, idx, total, score, input, revealed,
  onInput, onCheck, onReveal, onSkip
}: {
  word: SpellWord;
  idx: number; total: number; score: number;
  input: string; revealed: boolean;
  onInput: (v: string) => void;
  onCheck: () => void;
  onReveal: () => void;
  onSkip: () => void;
}) {
  return (
    <div className="rounded-2xl border border-violet-200 bg-white shadow-lg overflow-hidden">
      {/* Progress */}
      <div className="bg-violet-600 px-6 py-4 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-violet-200">
            Word {idx + 1} of {total}
          </span>
          <span className="text-xs font-semibold text-violet-200">Score: {score}</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-violet-500">
          <div className="h-full rounded-full bg-white transition-all" style={{ width: `${((idx) / total) * 100}%` }} />
        </div>
      </div>

      <div className="p-6">
        <div className="rounded-xl border border-violet-100 bg-violet-50 p-4 mb-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-violet-500 mb-1">Definition</p>
          <p className="text-sm text-slate-800 font-medium">{word.definition}</p>
          <p className="mt-2 text-xs text-slate-500 italic">"{word.usageSentence}"</p>

          <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
            {word.pronunciation && (
              <span className="rounded-full bg-violet-100 px-2.5 py-1 text-violet-700">
                🔊 {word.pronunciation}
              </span>
            )}
            {word.origin && (
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
                Origin: {word.origin}
              </span>
            )}
            <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-emerald-700">
              {word.category}
            </span>
          </div>

          {word.memoryTip && (
            <div className="mt-3 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2 text-xs text-amber-700">
              💡 <span className="font-semibold">Tip:</span> {word.memoryTip}
            </div>
          )}
        </div>

        <label className="block text-sm font-semibold text-slate-700 mb-2">Type the spelling:</label>
        <input
          type="text"
          autoFocus
          value={revealed ? word.word : input}
          readOnly={revealed}
          onChange={(e) => onInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !revealed) onCheck(); }}
          placeholder="Type the word here…"
          className={`w-full rounded-xl border px-4 py-3 text-base font-mono tracking-widest transition focus:outline-none focus:ring-2 ${
            revealed
              ? "border-violet-300 bg-violet-50 text-violet-700 focus:ring-violet-300"
              : "border-slate-300 bg-white focus:border-violet-500 focus:ring-violet-500/20"
          }`}
        />

        <div className="mt-4 flex flex-wrap gap-2">
          {!revealed ? (
            <>
              <button
                type="button"
                onClick={onCheck}
                className="flex-1 rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-bold text-white shadow transition hover:bg-violet-700"
              >
                Check Answer
              </button>
              <button
                type="button"
                onClick={onReveal}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Show answer
              </button>
              <button
                type="button"
                onClick={onSkip}
                className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-500 transition hover:bg-slate-100"
              >
                Skip
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={onSkip}
              className="flex-1 rounded-xl bg-slate-800 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-slate-700"
            >
              Next word →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Results({
  score, total, results, onRestart
}: {
  score: number; total: number;
  results: { word: string; correct: boolean; typed: string }[];
  onRestart: () => void;
}) {
  const pct = Math.round((score / total) * 100);
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-violet-200 bg-gradient-to-br from-violet-50 to-white p-6 text-center shadow-sm">
        <Trophy className="mx-auto h-10 w-10 text-amber-500 mb-2" />
        <h2 className="text-2xl font-extrabold text-slate-900">{pct}%</h2>
        <p className="text-slate-600 text-sm mt-1">
          {score} out of {total} words spelled correctly
        </p>
        <p className="mt-3 text-sm font-medium text-slate-700">
          {pct >= 90 ? "Outstanding! You're ready for the competition. 🏆" :
           pct >= 70 ? "Great effort! Keep practising the ones you missed." :
           "Good start — review the words below and try again."}
        </p>
        <div className="mt-4 flex gap-3 justify-center">
          <button
            type="button"
            onClick={onRestart}
            className="rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-violet-700"
          >
            Practise again
          </button>
          <Link
            href="/dashboard"
            className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Dashboard
          </Link>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-100 px-6 py-4 flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-slate-500" />
          <h3 className="font-semibold text-slate-900">Review</h3>
        </div>
        <div className="divide-y divide-slate-50">
          {results.map((r, i) => (
            <div key={i} className={`flex items-center gap-4 px-6 py-3 ${r.correct ? "bg-emerald-50/40" : "bg-red-50/40"}`}>
              {r.correct
                ? <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
                : <XCircle className="h-4 w-4 shrink-0 text-red-500" />
              }
              <span className="font-mono font-semibold text-sm text-slate-800">{r.word}</span>
              {!r.correct && r.typed !== "(skipped)" && (
                <span className="text-xs text-red-500">You typed: <span className="font-mono">{r.typed}</span></span>
              )}
              {r.typed === "(skipped)" && <span className="text-xs text-slate-400">Skipped</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
