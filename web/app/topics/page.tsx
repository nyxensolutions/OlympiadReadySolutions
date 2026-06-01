import type { Metadata } from "next";
import TopicsClient from "./TopicsClient";

export const metadata: Metadata = {
  title: "Olympiad Syllabus Map — Topic-wise Practice for Classes 1–12",
  description:
    "Explore the complete Olympiad syllabus map for Maths, Science and English (IMO, NSO, IEO). Practise topic by topic, track mastery and find your weak areas, Classes 1–12.",
  keywords: [
    "olympiad syllabus",
    "IMO syllabus",
    "NSO syllabus",
    "olympiad topics class wise",
    "olympiad maths topics",
    "olympiad preparation topics"
  ],
  alternates: { canonical: "/topics" },
  openGraph: {
    title: "Olympiad Syllabus Map — Topic-wise Practice | OlympiadReady",
    description:
      "Complete Olympiad syllabus map for Maths, Science and English. Practise topic by topic and track mastery, Classes 1–12.",
    url: "https://olympiadready.com/topics",
    type: "website"
  }
};

export default function Page() {
  return <TopicsClient />;
}
