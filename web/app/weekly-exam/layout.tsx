import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Weekly Olympiad Exam — Practice Challenge",
  description:
    "Take the weekly Olympiad exam — a timed, full-length practice test covering Maths, Science and English for Classes 1–12. Free to attempt every week.",
  alternates: { canonical: "/weekly-exam" }
};

export default function WeeklyExamLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
