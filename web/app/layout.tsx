import type { Metadata } from "next";
import Script from "next/script";
import { ClerkProvider } from "@clerk/nextjs";
import { WhatsAppFloat } from "@/components/WhatsAppFloat";
import "./globals.css";

const SITE_URL = "https://olympiadready.com";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "OlympiadReady — India's First AI Olympiad Prep Platform",
    template: "%s | OlympiadReady"
  },
  description:
    "India's first AI-powered Olympiad preparation platform. Infinite AI-generated practice papers, full mock exams, instant explanations and topic mastery tracking for IMO, NSO, IEO, IGKO & every major school Olympiad. Classes 1–12. Free to start.",
  keywords: [
    "Olympiad preparation",
    "AI Olympiad practice",
    "IMO practice papers",
    "NSO mock test",
    "IEO preparation",
    "SOF Olympiad",
    "Olympiad mock exam",
    "Olympiad practice online India",
    "class 1 to 12 Olympiad"
  ],
  authors: [{ name: "OlympiadReady" }],
  creator: "OlympiadReady",
  publisher: "OlympiadReady",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: SITE_URL,
    siteName: "OlympiadReady",
    title: "OlympiadReady — India's First AI Olympiad Prep Platform",
    description:
      "AI-generated practice papers, mock exams & mastery tracking for IMO, NSO, IEO & every major school Olympiad. Classes 1–12. Free to start.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "OlympiadReady — India's first AI Olympiad prep platform"
      }
    ]
  },
  twitter: {
    card: "summary_large_image",
    title: "OlympiadReady — India's First AI Olympiad Prep Platform",
    description:
      "AI-generated practice papers, mock exams & mastery tracking for IMO, NSO, IEO & more. Classes 1–12. Free to start.",
    images: ["/og-image.png"]
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" }
  },
  icons: {
    icon: "/logo.png",
    apple: "/apple-touch-icon.png"
  }
};

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "OlympiadReady",
  url: SITE_URL,
  logo: `${SITE_URL}/logo.png`,
  description:
    "India's first AI-powered Olympiad preparation platform for school students in Classes 1–12.",
  areaServed: "IN",
  sameAs: [] as string[]
};

const websiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "OlympiadReady",
  url: SITE_URL,
  potentialAction: {
    "@type": "SearchAction",
    target: `${SITE_URL}/topics?q={search_term_string}`,
    "query-input": "required name=search_term_string"
  }
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className="min-h-screen bg-slate-50 text-slate-900">
          {/* SEO: structured data for Google */}
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
          />
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteJsonLd) }}
          />
          {children}
          <WhatsAppFloat />

          {/* Razorpay checkout */}
          <Script
            src="https://checkout.razorpay.com/v1/checkout.js"
            strategy="afterInteractive"
          />

          {/* Umami — privacy-first analytics (no cookies, no banner needed) */}
          {process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID && (
            <Script
              defer
              src="https://cloud.umami.is/script.js"
              data-website-id={process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID}
              strategy="afterInteractive"
            />
          )}
        </body>
      </html>
    </ClerkProvider>
  );
}
