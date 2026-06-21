import type { Metadata } from "next";
import TopicsClient from "./TopicsClient";

export const metadata: Metadata = {
  title: "Olympiad Topic Map — Topic-wise Practice, Classes 1–12",
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
      <TopicsClient />
    </>
  );
}
