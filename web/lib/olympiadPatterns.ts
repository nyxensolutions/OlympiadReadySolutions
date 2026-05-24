import type { Subject } from "./types";

export type OlympiadLevel = "L1" | "L2";

export type OlympiadSection = {
  name: string;
  questions: number;
  marksPerQuestion: number;
  difficulty: "Foundation" | "Advanced" | "Olympiad";
  topics?: string[]; // If specific topics are enforced, otherwise random from subject
};

export type OlympiadPattern = {
  id: string;
  name: string;
  org: string;
  subject: Subject;
  grades: { min: number; max: number };
  level: OlympiadLevel;
  totalTimeMinutes: number;
  sections: OlympiadSection[];
};

// Patterns based on standard SOF, SilverZone, and other major olympiads
export const OLYMPIAD_PATTERNS: OlympiadPattern[] = [
  // --- SOF IMO (Math) ---
  {
    id: "sof_imo_l1_1_4",
    name: "IMO - International Mathematics Olympiad (Level 1)",
    org: "SOF",
    subject: "Mathematics",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Mathematical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Everyday Mathematics", questions: 10, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_imo_l1_5_12",
    name: "IMO - International Mathematics Olympiad (Level 1)",
    org: "SOF",
    subject: "Mathematics",
    grades: { min: 5, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Mathematical Reasoning", questions: 20, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Everyday Mathematics", questions: 10, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- SOF NSO (Science) ---
  {
    id: "sof_nso_l1_1_4",
    name: "NSO - National Science Olympiad (Level 1)",
    org: "SOF",
    subject: "Science",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 5, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Science", questions: 25, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_nso_l1_5_12",
    name: "NSO - National Science Olympiad (Level 1)",
    org: "SOF",
    subject: "Science",
    grades: { min: 5, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Science", questions: 35, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- SOF IEO (English) ---
  {
    id: "sof_ieo_l1_1_4",
    name: "IEO - International English Olympiad (Level 1)",
    org: "SOF",
    subject: "English",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Word and Structure Knowledge", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Reading", questions: 10, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Spoken and Written Expression", questions: 5, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_ieo_l1_5_12",
    name: "IEO - International English Olympiad (Level 1)",
    org: "SOF",
    subject: "English",
    grades: { min: 5, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Word and Structure Knowledge", questions: 25, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Reading", questions: 10, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Spoken and Written Expression", questions: 10, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Generic Level 2 Pattern ---
  {
    id: "generic_l2_5_12",
    name: "Generic Level 2 Olympiad",
    org: "Generic",
    subject: "Mathematics",
    grades: { min: 5, max: 12 },
    level: "L2",
    totalTimeMinutes: 60,
    sections: [
      { name: "Subject Knowledge", questions: 40, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 10, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Logical Reasoning ---
  {
    id: "sof_lr_l1_1_4",
    name: "IRAO - Logical Reasoning Olympiad (Level 1)",
    org: "SOF",
    subject: "Logical Reasoning",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Verbal Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Non-Verbal Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_lr_l1_5_12",
    name: "IRAO - Logical Reasoning Olympiad (Level 1)",
    org: "SOF",
    subject: "Logical Reasoning",
    grades: { min: 5, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Verbal Reasoning", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Non-Verbal Reasoning", questions: 20, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Computers & Cyber ---
  {
    id: "sof_nco_l1_1_4",
    name: "NCO - National Cyber Olympiad (Level 1)",
    org: "SOF",
    subject: "Computer Science",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 5, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Computers & IT", questions: 25, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_nco_l1_5_10",
    name: "NCO - National Cyber Olympiad (Level 1)",
    org: "SOF",
    subject: "Computer Science",
    grades: { min: 5, max: 10 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Logical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Computers & IT", questions: 35, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- AI ---
  {
    id: "sof_ai_l1_1_4",
    name: "IAIO - International AI Olympiad (Level 1)",
    org: "SOF",
    subject: "AI",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Core AI Concepts", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Logical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_ai_l1_5_10",
    name: "IAIO - International AI Olympiad (Level 1)",
    org: "SOF",
    subject: "AI",
    grades: { min: 5, max: 10 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Core AI Concepts", questions: 25, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Logical Reasoning", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- General Knowledge ---
  {
    id: "sof_igko_l1_1_4",
    name: "IGKO - International General Knowledge Olympiad (Level 1)",
    org: "SOF",
    subject: "General Knowledge",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "General Awareness", questions: 20, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Current Affairs", questions: 5, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Life Skills", questions: 5, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_igko_l1_5_10",
    name: "IGKO - International General Knowledge Olympiad (Level 1)",
    org: "SOF",
    subject: "General Knowledge",
    grades: { min: 5, max: 10 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "General Awareness", questions: 30, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Current Affairs", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Life Skills", questions: 5, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Social Studies ---
  {
    id: "sof_isso_l1_3_4",
    name: "ISSO - International Social Studies Olympiad (Level 1)",
    org: "SOF",
    subject: "Social Studies",
    grades: { min: 3, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "History", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Geography", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Civics", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_isso_l1_5_10",
    name: "ISSO - International Social Studies Olympiad (Level 1)",
    org: "SOF",
    subject: "Social Studies",
    grades: { min: 5, max: 10 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "History", questions: 15, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Geography", questions: 15, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Civics", questions: 15, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Hindi ---
  {
    id: "sof_iho_l1_3_4",
    name: "IHO - International Hindi Olympiad (Level 1)",
    org: "SOF",
    subject: "Hindi",
    grades: { min: 3, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Vyakaran (Grammar)", questions: 20, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Sahitya (Literature)", questions: 10, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_iho_l1_5_10",
    name: "IHO - International Hindi Olympiad (Level 1)",
    org: "SOF",
    subject: "Hindi",
    grades: { min: 5, max: 10 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Vyakaran (Grammar)", questions: 30, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Sahitya (Literature)", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Spell Bee ---
  {
    id: "sof_spellbee_l1_1_4",
    name: "IBSB - International Spelling Bee Olympiad (Level 1)",
    org: "SOF",
    subject: "Spell Bee",
    grades: { min: 1, max: 4 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Spellings & Vocabulary", questions: 30, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 2, difficulty: "Olympiad", topics: [] }
    ]
  },
  {
    id: "sof_spellbee_l1_5_12",
    name: "IBSB - International Spelling Bee Olympiad (Level 1)",
    org: "SOF",
    subject: "Spell Bee",
    grades: { min: 5, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Spellings & Vocabulary", questions: 45, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  },
  // --- Commerce (ICO) ---
  {
    id: "sof_ico_l1_11_12",
    name: "ICO - International Commerce Olympiad (Level 1)",
    org: "SOF",
    subject: "Commerce",
    grades: { min: 11, max: 12 },
    level: "L1",
    totalTimeMinutes: 60,
    sections: [
      { name: "Accountancy", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Business Studies", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Economics", questions: 15, marksPerQuestion: 1, difficulty: "Foundation", topics: [] },
      { name: "Achievers Section", questions: 5, marksPerQuestion: 3, difficulty: "Olympiad", topics: [] }
    ]
  }
];

export function getAvailableOlympiads(subject: Subject, grade: number, level: OlympiadLevel): OlympiadPattern[] {
  const patterns = OLYMPIAD_PATTERNS.filter(
    (p) => p.subject === subject && grade >= p.grades.min && grade <= p.grades.max && p.level === level
  );
  if (patterns.length > 0) return patterns;

  // Highly robust Level 2 fallback generation so that any subject chosen in L2 has an official pattern layout.
  if (level === "L2") {
    return [
      {
        id: `generic_l2_${subject.toLowerCase()}`,
        name: `${subject} Olympiad - Level 2 (National)`,
        org: "Generic",
        subject: subject,
        grades: { min: 1, max: 12 },
        level: "L2",
        totalTimeMinutes: 60,
        sections: [
          { name: "Subject Knowledge", questions: grade >= 5 ? 40 : 30, marksPerQuestion: 1, difficulty: "Advanced", topics: [] },
          { name: "Achievers Section", questions: 5, marksPerQuestion: grade >= 5 ? 3 : 2, difficulty: "Olympiad", topics: [] }
        ]
      }
    ];
  }
  return [];
}
