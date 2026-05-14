export type Question = {
  q: string;
  options: string[];
  answer: string;
  explanation: string;
  topic?: string;
};

export type DashboardSummary = {
  subscription: {
    tier: "Free" | "Pro";
    used: number;
    limit: number;
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
};

export type PreviewRequest = {
  subject: string;
  grade: number;
  difficulty: string;
  count: number;
};

export type GeneratedPaper = {
  paperId: string;
  title: string;
  subject: string;
  grade: number;
  difficulty: string;
  questions: Question[];
  cached?: boolean;
};

export type AttemptResult = {
  paperId: string;
  questions: Question[];
  userAnswers: (string | null)[];
  flagged: boolean[];
  timeTakenSeconds: number;
  config: PreviewRequest;
};

export type SubscriptionStatus = {
  tier: "Free" | "Pro";
  used: number;
  limit: number;
  allowed: boolean;
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
  "Math",
  "Science",
  "English",
  "Hindi",
  "General Knowledge",
  "Logical Reasoning",
  "Computers",
  "AI"
] as const;

export type Subject = (typeof SUBJECTS)[number];

export const SUBJECT_GRADE_MAP: Record<Subject, { min: number; max: number }> = {
  Math:                 { min: 1,  max: 12 },
  Science:              { min: 1,  max: 12 },
  English:              { min: 1,  max: 12 },
  "Logical Reasoning":  { min: 1,  max: 12 },
  Computers:            { min: 1,  max: 10 },
  AI:                   { min: 1,  max: 10 },
  "General Knowledge":  { min: 1,  max: 10 },
  Hindi:                { min: 3,  max: 10 },
};

export function isSubjectAvailable(subject: Subject, grade: number): boolean {
  const range = SUBJECT_GRADE_MAP[subject];
  return grade >= range.min && grade <= range.max;
}

export const DIFFICULTIES = ["Foundation", "Advanced", "Olympiad"] as const;
export const QUANTITIES = [5, 10, 20, 35] as const;
export const SECONDS_PER_QUESTION = 90;
