"use client";

import { useState } from "react";
import { Crown } from "lucide-react";
import type {
  AttemptResult,
  GeneratedPaper,
  PreviewRequest,
  QuotaError
} from "@/lib/types";
import { useSubscription } from "@/lib/useSubscription";
import { ConfigForm } from "./ConfigForm";
import { TestArena } from "./TestArena";
import { ResultsScreen } from "./ResultsScreen";
import { SubscriptionBadge } from "./SubscriptionBadge";
import { UpgradeModal } from "./UpgradeModal";

type Phase =
  | { kind: "config" }
  | { kind: "arena"; config: PreviewRequest; paper: GeneratedPaper }
  | { kind: "results"; result: AttemptResult };

export function GeneratorFlow() {
  const [phase, setPhase] = useState<Phase>({ kind: "config" });
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
            onGenerated={(config, paper) => {
              setPhase({ kind: "arena", config, paper });
              void refresh();
            }}
            onQuotaExceeded={handleQuotaExceeded}
          />
        )}
        {phase.kind === "arena" && (
          <TestArena
            config={phase.config}
            paper={phase.paper}
            onSubmit={(result) => setPhase({ kind: "results", result })}
          />
        )}
        {phase.kind === "results" && (
          <ResultsScreen
            result={phase.result}
            onRestart={() => setPhase({ kind: "config" })}
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
