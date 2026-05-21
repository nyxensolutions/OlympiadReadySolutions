"use client";

import { useState } from "react";
import { Crown } from "lucide-react";
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

  function openUpgrade(reason?: string) {
    setUpgradeReason(reason);
    setShowUpgrade(true);
  }

  function handleQuotaExceeded(info: QuotaError) {
    openUpgrade(info.message);
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
          {status?.tier === "Free" && (
            <button
              type="button"
              onClick={() => openUpgrade()}
              className="inline-flex items-center gap-1.5 rounded-full bg-achiever-50 px-3 py-1 text-xs font-semibold text-achiever-700 ring-1 ring-achiever-600/20 hover:bg-achiever-100"
            >
              <Crown className="h-3 w-3" />
              Upgrade to Pro
            </button>
          )}
        </div>
      )}

      <div className="flex justify-center">
        {phase.kind === "config" && (
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
      />
    </div>
  );
}
