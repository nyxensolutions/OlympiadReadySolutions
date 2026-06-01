import type { Metadata } from "next";
import MockExamsClient from "./MockExamsClient";

export const metadata: Metadata = {
  title: "AI Mock Exams for Olympiads — Adaptive Practice Tests",
  description:
    "Take AI-powered adaptive mock exams for SOF Olympiads (IMO, NSO, IEO) for Classes 1–12. Timed, exam-pattern tests with instant scoring and detailed explanations.",
  keywords: [
    "olympiad mock test",
    "IMO mock exam",
    "NSO mock test",
    "online olympiad practice test",
    "adaptive mock exam",
    "olympiad exam preparation"
  ],
  alternates: { canonical: "/mock-exams" },
  openGraph: {
    title: "AI Mock Exams for Olympiads — Adaptive Practice Tests | OlympiadReady",
    description:
      "AI-powered adaptive mock exams for IMO, NSO, IEO — Classes 1–12. Timed, exam-pattern tests with instant scoring.",
    url: "https://olympiadready.com/mock-exams",
    type: "website"
  }
};

export default function Page() {
  return <MockExamsClient />;
}
