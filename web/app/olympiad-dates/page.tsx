import type { Metadata } from "next";
import OlympiadDatesClient from "./OlympiadDatesClient";

export const metadata: Metadata = {
  title: "Olympiad Exam Dates 2026 — IMO, NSO, IEO",
  description:
    "Check the latest Olympiad exam dates and registration schedule for SOF IMO, NSO, IEO and other major Olympiads. Stay updated on important dates for Classes 1–12.",
  keywords: [
    "olympiad exam dates",
    "IMO exam date 2026",
    "NSO exam date",
    "SOF olympiad schedule",
    "olympiad registration dates",
    "olympiad exam calendar"
  ],
  alternates: { canonical: "/olympiad-dates" },
  openGraph: {
    title: "Olympiad Exam Dates 2026 — IMO, NSO, IEO Schedule | OlympiadReady",
    description:
      "Latest Olympiad exam dates and registration schedule for SOF IMO, NSO, IEO and more, Classes 1–12.",
    url: "https://olympiadready.com/olympiad-dates",
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Olympiad Exam Dates 2026" }]
  }
};

const breadcrumb = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: "https://olympiadready.com" },
    { "@type": "ListItem", position: 2, name: "Olympiad Exam Dates 2026", item: "https://olympiadready.com/olympiad-dates" }
  ]
};

export default function Page() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <OlympiadDatesClient />
    </>
  );
}
