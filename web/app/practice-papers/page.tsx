import type { Metadata } from "next";
import PracticePapersClient from "./PracticePapersClient";

export const metadata: Metadata = {
  title: "Olympiad Practice Papers & Sample Question Papers (PDF)",
  description:
    "Download Olympiad practice question papers for IMO, NSO, IEO and more — Classes 1–12. AI-generated, exam-pattern PDFs with answer keys, from just ₹29.",
  keywords: [
    "olympiad practice papers",
    "olympiad sample papers",
    "IMO question paper",
    "NSO previous year papers",
    "olympiad question papers pdf",
    "olympiad sample question paper class 5"
  ],
  alternates: { canonical: "/practice-papers" },
  openGraph: {
    title: "Olympiad Practice Papers & Sample Question Papers | OlympiadReady",
    description:
      "Download exam-pattern Olympiad practice papers (IMO, NSO, IEO) for Classes 1–12 with answer keys, from just ₹29.",
    url: "https://olympiadready.com/practice-papers",
    type: "website"
  }
};

export default function Page() {
  return <PracticePapersClient />;
}
