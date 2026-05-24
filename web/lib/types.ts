export type Question = {
  q: string;
  imageUrl?: string;
  options: string[];
  answer: string;
  explanation: string;
  topic?: string;
  sectionName?: string;
  marks?: number;
};

export type DashboardSummary = {
  subscription: {
    tier: "Free" | "Pro" | "Modular";
    used: number;
    limit: number;
    activeUnlocks?: Array<{
      grade: number;
      subject: string;
      aiGenerationsUsed: number;
      endDate: string;
    }>;
  };
  papers: Array<{
    paperId: string;
    title: string;
    subject: string;
    grade: number;
    difficulty: string;
    createdAt: string;
  }>;
  results: Array<{
    resultId: string;
    paperId: string;
    paperTitle: string;
    subject: string;
    score: number;
    totalQuestions: number;
    timeTakenSeconds: number;
    completedAt: string;
  }>;
  mastery: Array<{
    subject: string;
    topic: string;
    masteryScore: number;
    lastUpdated: string;
  }>;
  mistakeCount: number;
};

export type OlympiadLevel = "L1" | "L2";

export type PreviewRequest = {
  subject: string;
  grade: number;
  difficulty: string;
  count: number;
  topic?: string;
  mistakesOnly?: boolean;
  olympiadLevel?: OlympiadLevel;
  /** The specific olympiad the student is targeting (e.g. "sof_imo", "hbcse", "silverzone_math"). */
  olympiadId?: string;
};

export type GeneratedPaper = {
  paperId: string;
  title: string;
  subject: string;
  grade: number;
  difficulty: string;
  questions: Question[];
  isMockExam?: boolean;
  patternId?: string;
};

export type AttemptResult = {
  paperId: string;
  questions: Question[];
  userAnswers: (string | null)[];
  flagged: boolean[];
  timeTakenSeconds: number;
  config: PreviewRequest;
  isMockExam?: boolean;
  totalMarks?: number;
  earnedMarks?: number;
};

export function recommendNextDifficulty(
  scorePct: number,
  currentDifficulty: string
): { difficulty: string; reason: string } | null {
  const order = ["Foundation", "Advanced", "Olympiad"];
  const idx = order.indexOf(currentDifficulty);
  if (idx === -1) return null;

  if (scorePct >= 80 && idx < order.length - 1) {
    return {
      difficulty: order[idx + 1],
      reason: `Great score (${Math.round(scorePct)}%)! You're ready to step up.`,
    };
  }
  if (scorePct < 45 && idx > 0) {
    return {
      difficulty: order[idx - 1],
      reason: `Score was ${Math.round(scorePct)}%. Build confidence at a lower level first.`,
    };
  }
  return null;
}

export type SubscriptionStatus = {
  tier: "Free" | "Pro" | "Modular";
  used: number;
  limit: number;
  allowed: boolean;
  activeUnlocks?: Array<{
    grade: number;
    subject: string;
    aiGenerationsUsed: number;
    endDate: string;
  }>;
};

export type CheckoutResponse = {
  orderId: string;
  keyId: string;
  amount: number;
  currency: string;
  planName: string;
  planDisplayName: string;
};

export type QuotaError = {
  code: "QUOTA_EXCEEDED";
  message: string;
  tier: "Free" | "Pro";
  used: number;
  limit: number;
  upgrade: boolean;
};

export const SUBJECTS = [
  "Mathematics",
  "Science",
  "English",
  "Hindi",
  "Social Studies",
  "General Knowledge",
  "Logical Reasoning",
  "Computer Science",
  "AI",
  "Spell Bee",
  "Commerce"
] as const;

export type Subject = (typeof SUBJECTS)[number];

export const SUBJECT_GRADE_MAP: Record<Subject, { min: number; max: number }> = {
  Mathematics:          { min: 1,  max: 12 },
  Science:              { min: 1,  max: 12 },
  English:              { min: 1,  max: 12 },
  "Logical Reasoning":  { min: 1,  max: 12 },
  "Computer Science":   { min: 1,  max: 10 },
  AI:                   { min: 1,  max: 10 },
  "General Knowledge":  { min: 1,  max: 10 },
  "Social Studies":     { min: 3,  max: 10 },
  Hindi:                { min: 3,  max: 10 },
  "Spell Bee":          { min: 1,  max: 12 },
  Commerce:             { min: 11, max: 12 },
};

export function isSubjectAvailable(subject: Subject, grade: number): boolean {
  const range = SUBJECT_GRADE_MAP[subject];
  return grade >= range.min && grade <= range.max;
}

export const DIFFICULTIES = ["Foundation", "Advanced", "Olympiad"] as const;
export const QUANTITIES = [5, 10, 20, 35] as const;
export const SECONDS_PER_QUESTION = 90;

export type LeaderboardEntry = {
  rank: number;
  displayName: string;
  bestScorePct: number;
  medal: "Gold" | "Silver" | "Bronze" | "None";
};

export type DailyQuizQuestion = {
  questionId: string;
  questionText: string;
  imageUrl?: string;
  options: string[];
  subject: string;
  topic: string;
  difficulty: string;
};

export type DailyQuizAnswer = {
  correctAnswer: string;
  isCorrect: boolean;
  explanation: string;
};
