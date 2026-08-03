"use client";

import { useEffect, useRef, useState } from "react";
import { Crown, Sparkles, CheckCircle, ArrowRight } from "lucide-react";
import type {
  AttemptResult,
  GeneratedPaper,
  PreviewRequest,
  QuotaError
} from "@/lib/types";
import { recommendNextDifficulty } from "@/lib/types";
import { useSubscription } from "@/lib/useSubscription";
import { ConfigForm } from "./ConfigForm";
import { TestArena } from "./TestArena";
import { ResultsScreen } from "./ResultsScreen";
import { SubscriptionBadge } from "./SubscriptionBadge";
import { UpgradeModal } from "./UpgradeModal";

type Phase =
  | { kind: "config"; suggestedConfig?: Partial<PreviewRequest>; adaptiveMessage?: string }
  | { kind: "arena"; config: PreviewRequest; paper: GeneratedPaper; simulationMode: boolean }
  | { kind: "results"; result: AttemptResult; simulationMode: boolean };

export function GeneratorFlow({ initialConfig, autoStart, olympiadId }: { initialConfig?: Partial<PreviewRequest>, autoStart?: boolean, olympiadId?: string } = {}) {
  const [phase, setPhase] = useState<Phase>({ kind: "config", suggestedConfig: initialConfig });
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [upgradeReason, setUpgradeReason] = useState<string | undefined>(undefined);
  const { status, refresh } = useSubscription();

  const [upgradeGrade, setUpgradeGrade] = useState<number | undefined>(undefined);
  const [upgradeSubject, setUpgradeSubject] = useState<string | undefined>(undefined);
  const softNudgeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Soft upgrade nudge: after 3rd paper completed, show upgrade modal 2.5s into results screen
  useEffect(() => {
    if (
      phase.kind === "results" &&
      status?.tier === "Free" &&
      typeof status.used === "number" &&
      status.used >= 3 &&
      status.used < (status.limit ?? 5)
    ) {
      softNudgeTimer.current = setTimeout(() => {
        openUpgrade(`You've completed ${status.used} of ${status.limit ?? 5} free papers — unlock unlimited practice for ₹77/month (August offer).`);
      }, 2500);
    }
    return () => {
      if (softNudgeTimer.current) clearTimeout(softNudgeTimer.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase.kind]);

  function openUpgrade(reason?: string, grade?: number, subject?: string) {
    setUpgradeReason(reason);
    setUpgradeGrade(grade);
    setUpgradeSubject(subject);
    setShowUpgrade(true);
  }

  function handleQuotaExceeded(info: QuotaError, grade: number, subject: string) {
    openUpgrade(info.message, grade, subject);
  }

  function handleRestart(result: AttemptResult) {
    const score = result.questions.reduce(
      (acc, q, i) => acc + (result.userAnswers[i] === q.answer ? 1 : 0),
      0
    );
    const pct = result.questions.length > 0 ? (score / result.questions.length) * 100 : 0;
    const rec = recommendNextDifficulty(pct, result.config.difficulty);
    setPhase({
      kind: "config",
      suggestedConfig: rec ? { ...result.config, difficulty: rec.difficulty } : result.config,
      adaptiveMessage: rec?.reason,
    });
  }

  return (
    <div className="w-full max-w-6xl">
      {phase.kind === "config" && (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <SubscriptionBadge status={status} />
          {status?.tier !== "Pro" && status?.tier !== "School" && (
            <button
              type="button"
              onClick={() => openUpgrade()}
              className="inline-flex items-center gap-1.5 rounded-full bg-achiever-50 px-3 py-1 text-xs font-semibold text-achiever-700 ring-1 ring-achiever-600/20 hover:bg-achiever-100"
            >
              <Crown className="h-3 w-3" />
              {status?.tier === "Modular" ? "Unlock More Subjects" : "Upgrade to Pro"}
            </button>
          )}
        </div>
      )}

      <div className="flex justify-center">
        {phase.kind === "config" && status?.tier === "Free" && typeof status.used === "number" && status.used >= (status.limit ?? 5) ? (
          <div className="w-full max-w-lg rounded-2xl border border-achiever-200 bg-gradient-to-b from-achiever-50 to-white p-8 shadow-sm text-center">
            <div className="mb-4 inline-flex items-center justify-center w-14 h-14 rounded-full bg-achiever-100">
              <Sparkles className="h-7 w-7 text-achiever-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">
              You&apos;ve used all {status.limit} free papers
            </h2>
            <p className="text-sm text-gray-500 mb-6">
              Unlock unlimited AI-generated practice papers for any subject and grade.
            </p>
            <ul className="text-left space-y-2 mb-7">
              {[
                "Unlimited AI-generated papers per subject",
                "Olympiad, Standard & Speed difficulty levels",
                "Instant detailed explanations for every answer",
                "Track your progress over time",
              ].map((feat) => (
                <li key={feat} className="flex items-start gap-2 text-sm text-gray-700">
                  <CheckCircle className="h-4 w-4 text-achiever-500 mt-0.5 shrink-0" />
                  {feat}
                </li>
              ))}
            </ul>
            <div className="mb-2 inline-block rounded-full bg-orange-100 px-3 py-0.5 text-[10px] font-bold uppercase tracking-wide text-orange-700">
              🎉 August Offer — 40% Off
            </div>
            <div className="mb-3 text-xs text-gray-400 font-medium uppercase tracking-wide mt-2">Starting from</div>
            <div className="mb-6 flex items-baseline justify-center gap-2">
              <span className="text-base font-medium text-gray-400 line-through">₹129</span>
              <span className="text-3xl font-extrabold text-gray-900">₹77</span>
              <span className="text-sm text-gray-500">/ subject / month</span>
            </div>
            <button
              type="button"
              onClick={() => openUpgrade(`You've used all ${status.limit} free papers. Upgrade to continue practising.`)}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-achiever-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-achiever-700 transition-colors"
            >
              Upgrade to Pro <ArrowRight className="h-4 w-4" />
            </button>
            <p className="mt-3 text-xs text-gray-400">
              Cancel anytime. No hidden fees.
            </p>
          </div>
        ) : phase.kind === "config" && (
          <ConfigForm
            initialConfig={phase.suggestedConfig}
            adaptiveMessage={phase.adaptiveMessage}
            autoStart={autoStart}
            olympiadId={olympiadId}
            onGenerated={(config, paper, simulationMode) => {
              setPhase({ kind: "arena", config, paper, simulationMode });
              void refresh();
            }}
            onQuotaExceeded={handleQuotaExceeded}
            onRequiresUpgrade={() => openUpgrade("Level 2 practice requires a Pro subscription.")}
            status={status}
          />
        )}
        {phase.kind === "arena" && (
          <TestArena
            config={phase.config}
            paper={phase.paper}
            simulationMode={phase.simulationMode}
            onSubmit={(result) => setPhase({ kind: "results", result, simulationMode: phase.simulationMode })}
          />
        )}
        {phase.kind === "results" && (
          <ResultsScreen
            result={phase.result}
            simulationMode={phase.simulationMode}
            onRestart={() => handleRestart(phase.result)}
          />
        )}
      </div>

      <UpgradeModal
        open={showUpgrade}
        onClose={() => setShowUpgrade(false)}
        onUpgraded={() => void refresh()}
        reason={upgradeReason}
        initialGrade={upgradeGrade}
        initialSubject={upgradeSubject}
      />
    </div>
  );
}
