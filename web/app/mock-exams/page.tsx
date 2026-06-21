import type { Metadata } from "next";
import MockExamsClient from "./MockExamsClient";

export const metadata: Metadata = {
  title: "Olympiad Mock Exams — AI Adaptive Practice Tests",
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
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "OlympiadReady Mock Exams" }]
  }
};

const breadcrumb = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://olympiadready.com" },
    { "@type": "ListItem", position: 2, name: "Mock Exams", item: "https://olympiadready.com/mock-exams" }
  ]
};

export default function Page() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <h1 className="sr-only">Olympiad Mock Exams — AI-Powered Adaptive Practice Tests for Classes 1–12</h1>
      <MockExamsClient />
    </>
  );
}
