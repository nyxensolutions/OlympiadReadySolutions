import type { Metadata } from "next";
import TopicsClient from "./TopicsClient";

export const metadata: Metadata = {
  title: "Olympiad Syllabus Map — Topic-wise Practice",
  description:
    "Explore the Olympiad syllabus for Maths, Science & English (IMO, NSO, IEO). Practise topic by topic, track mastery and find weak areas. Classes 1–12.",
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
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "OlympiadReady Topic Map" }]
  }
};

const breadcrumb = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://olympiadready.com" },
    { "@type": "ListItem", position: 2, name: "Olympiad Syllabus Map", item: "https://olympiadready.com/topics" }
  ]
};

export default function Page() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <h1 className="sr-only">Olympiad Syllabus Map — Topic-wise Practice for Classes 1–12</h1>
      <TopicsClient />
    </>
  );
}
