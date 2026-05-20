/**
 * Umami analytics — lightweight custom event tracker.
 * window.umami is injected by the Umami script in layout.tsx.
 * Safe to call on the server (no-ops when window is undefined).
 */
declare global {
  interface Window {
    umami?: {
      track: (eventName: string, data?: Record<string, unknown>) => void;
    };
  }
}

export function trackEvent(
  eventName: string,
  data?: Record<string, unknown>
): void {
  if (typeof window === "undefined") return;
  if (!window.umami) return;
  window.umami.track(eventName, data);
}

// ─── Typed event helpers ──────────────────────────────────────────────────────

export const Analytics = {
  /** User clicked Generate & Start Test */
  paperGenerated(opts: {
    subject: string;
    grade: number;
    difficulty: string;
    count: number;
    simulationMode: boolean;
    mistakesOnly: boolean;
  }) {
    trackEvent("paper_generated", {
      subject: opts.subject,
      grade: opts.grade,
      difficulty: opts.difficulty,
      count: opts.count,
      simulation_mode: opts.simulationMode,
      mistakes_only: opts.mistakesOnly,
    });
  },

  /** User exhausted quota — upgrade prompt shown */
  quotaExceeded(subject: string, grade: number) {
    trackEvent("quota_exceeded", { subject, grade });
  },

  /** ResultsScreen mounted — test was completed */
  testCompleted(opts: {
    subject: string;
    grade: number;
    difficulty: string;
    totalQuestions: number;
    scorePct: number;
    timeTakenSeconds: number;
  }) {
    trackEvent("test_completed", {
      subject: opts.subject,
      grade: opts.grade,
      difficulty: opts.difficulty,
      total_questions: opts.totalQuestions,
      score_pct: opts.scorePct,
      time_taken_seconds: opts.timeTakenSeconds,
    });
  },

  /** User downloaded a PDF */
  pdfDownloaded(subject: string, grade: number, difficulty: string) {
    trackEvent("pdf_downloaded", { subject, grade, difficulty });
  },

  /** Upgrade modal was opened */
  upgradeModalOpened(reason?: string) {
    trackEvent("upgrade_modal_opened", { reason: reason ?? "unknown" });
  },

  /** User successfully upgraded to Pro */
  upgradeCompleted() {
    trackEvent("upgrade_completed");
  },

  /** User opened the challenge/share link */
  challengeShared(subject: string, grade: number) {
    trackEvent("challenge_shared", { subject, grade });
  },

  /** User shared result to parent via WhatsApp */
  sharedToParent(scorePct: number) {
    trackEvent("shared_to_parent", { score_pct: scorePct });
  },
};
