import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { LandingFooter } from "@/components/landing/LandingFooter";

const SITE_URL = "https://olympiadready.com";

export const metadata: Metadata = {
  title: "Science Olympiad Preparation — Complete NSO Guide",
  description:
    "Complete NSO preparation guide for Indian students. Covers class-wise science olympiad syllabus, exam pattern, study strategy, and practice tips for the National Science Olympiad, Classes 1–12.",
  keywords: [
    "science olympiad preparation",
    "NSO preparation",
    "national science olympiad preparation",
    "how to prepare for NSO",
    "NSO study tips",
    "science olympiad guide India",
    "NSO syllabus guide",
  ],
  alternates: { canonical: "/science-olympiad-preparation" },
  openGraph: {
    title: "Science Olympiad Preparation — Complete NSO Guide | OlympiadReady",
    description:
      "Step-by-step NSO preparation guide. Class-wise syllabus, exam pattern, Achievers section strategy, and practice tips for the National Science Olympiad.",
    url: `${SITE_URL}/science-olympiad-preparation`,
    type: "article",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Science Olympiad Preparation Guide" }],
  },
};

const faqs = [
  {
    q: "What is the NSO exam pattern?",
    a: "The SOF NSO has three sections: Science (15 questions, 1 mark each), Achievers Section (5 questions, 3 marks each), and Logical Reasoning (10 questions, 1 mark each). The total time is 60 minutes and there is no negative marking.",
  },
  {
    q: "Is the NSO syllabus the same as the CBSE science syllabus?",
    a: "Yes, the NSO follows the CBSE/NCERT school science curriculum for each class. The questions test the same topics but with higher application depth — especially in the Achievers section which tests reasoning and multi-concept understanding.",
  },
  {
    q: "Which topics carry the most weight in the NSO?",
    a: "For Classes 1–5: Plants, animals, and human body. For Classes 6–8: Cell biology, light and sound, and matter. For Classes 9–10: Chemical reactions, life processes, electricity, and natural resources. These topics appear consistently across SOF NSO papers.",
  },
  {
    q: "How is NSO different from NTSE science?",
    a: "NSO is purely objective (MCQ) and based on the current class syllabus, while NTSE tests cumulative science knowledge up to Class 10 with a separate mental ability component. NSO is ideal preparation for students in Classes 1–10 before attempting NTSE in Class 10.",
  },
  {
    q: "How many mock tests should I take before the NSO?",
    a: "Take at least 4 full-length NSO mock tests in the 6 weeks before the exam. Focus on the Science and Achievers sections — these together determine your rank. Logical Reasoning is important but the Science section carries the highest overall weight.",
  },
];

const articleJsonLd = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: "Science Olympiad Preparation — Complete NSO Guide for Classes 1–12",
  description:
    "Complete NSO preparation guide. Covers class-wise science olympiad syllabus, exam pattern, study strategy, and practice tips for the National Science Olympiad.",
  author: { "@type": "Organization", name: "OlympiadReady", url: SITE_URL },
  publisher: {
    "@type": "Organization",
    name: "OlympiadReady",
    logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` },
  },
  mainEntityOfPage: { "@type": "WebPage", "@id": `${SITE_URL}/science-olympiad-preparation` },
  image: `${SITE_URL}/og-image.png`,
};

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.map((f) => ({
    "@type": "Question",
    name: f.q,
    acceptedAnswer: { "@type": "Answer", text: f.a },
  })),
};

const breadcrumbJsonLd = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
    { "@type": "ListItem", position: 2, name: "Olympiad Preparation", item: `${SITE_URL}/olympiad-preparation` },
    { "@type": "ListItem", position: 3, name: "Science Olympiad Preparation", item: `${SITE_URL}/science-olympiad-preparation` },
  ],
};

export default function ScienceOlympiadPreparationPage() {
  return (
    <div className="min-h-screen bg-white">
      <AppHeader />

      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      <article className="mx-auto max-w-3xl px-4 py-12">
        {/* Breadcrumb */}
        <nav className="mb-6 flex items-center gap-2 text-sm text-slate-500">
          <Link href="/" className="hover:text-brand-600">Home</Link>
          <span>/</span>
          <Link href="/olympiad-preparation" className="hover:text-brand-600">Olympiad Preparation</Link>
          <span>/</span>
          <span className="text-slate-700">Science Olympiad</span>
        </nav>

        <span className="inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
          Science
        </span>

        <h1 className="mt-4 text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl">
          Science Olympiad Preparation — Complete NSO Guide for Classes 1–12
        </h1>

        <p className="mt-5 text-lg leading-8 text-slate-600">
          The National Science Olympiad (NSO) by the Science Olympiad Foundation is one of India&apos;s most
          widely taken school olympiads, testing science knowledge alongside logical reasoning for Classes 1–12.
          This guide covers everything for NSO preparation — exam pattern, class-wise syllabus priorities, how
          to handle application-based questions, and a practical practice routine.
        </p>

        {/* Exam pattern */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          NSO exam pattern at a glance
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          The NSO is a 60-minute multiple-choice paper conducted inside school. No negative marking applies,
          so students should attempt all questions. The three sections are:
        </p>

        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Section</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Questions</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Marks each</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Focus</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              <tr>
                <td className="px-4 py-2.5 font-medium">Logical Reasoning</td>
                <td className="px-4 py-2.5">10</td>
                <td className="px-4 py-2.5">1</td>
                <td className="px-4 py-2.5">Patterns, analogies, series</td>
              </tr>
              <tr className="bg-slate-50/50">
                <td className="px-4 py-2.5 font-medium">Science</td>
                <td className="px-4 py-2.5">20</td>
                <td className="px-4 py-2.5">1</td>
                <td className="px-4 py-2.5">Concepts and application</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-medium text-amber-700">Achievers Section</td>
                <td className="px-4 py-2.5">5</td>
                <td className="px-4 py-2.5">3</td>
                <td className="px-4 py-2.5">Higher order reasoning</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <span className="font-semibold">Achievers section weight:</span> Those 5 questions are worth 15 marks.
          A student who scores full marks on Achievers has a significant rank advantage even with a few errors in
          the main Science section. Prioritise this section in your practice.
        </div>

        {/* Syllabus by class */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          NSO syllabus priorities by class group
        </h2>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 1–3: Living things and the natural world</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          At this level, NSO questions focus on plants and animals, the human body (five senses, body parts),
          food and nutrition, weather and seasons, materials (hard/soft, rough/smooth), and simple observations
          about nature. Questions are picture-based and straightforward — building vocabulary for science terms
          is the most useful preparation strategy.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 4–6: Systems and properties of matter</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          The syllabus expands significantly here: digestive, respiratory, and circulatory systems, properties
          of solids/liquids/gases, simple machines, force and motion, light and shadow, and the water cycle.
          Students who understand the <em>why</em> behind these phenomena (not just their names) handle NSO
          application questions much better than those who memorise facts.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 7–9: Chemistry, physics, and biology depth</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          This is where NSO preparation becomes genuinely demanding. Cell biology (structure, organelles,
          division), chemical reactions and equations (for Classes 8–9), laws of motion, electricity and
          circuits, and heredity and reproduction are the high-weight topics. Students who scored well at
          Class 6–7 level but find Class 8–9 NSO difficult typically have gaps in their understanding of
          chemical equations — address these early.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 10–12: Integration across all science streams</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          At this level, the NSO tests across Physics, Chemistry, and Biology. Chemical bonding and reactions,
          life processes, electricity and magnetism, carbon compounds, and genetics are consistently
          high-scoring topics in Class 10. For Classes 11–12, the paper aligns closely with the board syllabus
          — students preparing for JEE/NEET will find NSO preparation naturally complementary.
        </p>

        {/* Strategy */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          5-step NSO preparation strategy
        </h2>

        <div className="mt-6 space-y-5">
          {[
            {
              n: "1",
              h: "Understand concepts before memorising facts",
              b: "NSO questions are designed to test whether you understand a concept, not just whether you remember a textbook line. Students who understand why plants need sunlight for photosynthesis can answer novel application questions; students who memorised the definition of photosynthesis cannot.",
            },
            {
              n: "2",
              h: "Split preparation by section",
              b: "Treat the Science section and Logical Reasoning section as separate preparation tasks. Science requires conceptual understanding and factual recall. Logical Reasoning requires pattern recognition and is best improved through dedicated daily puzzles — not science study.",
            },
            {
              n: "3",
              h: "Practise application and experiment-based questions explicitly",
              b: "The NSO frequently presents questions based on a described experiment or observation ('A student adds vinegar to baking soda and observes bubbles forming — what gas is produced?'). These look different from textbook questions. Practise at least 15–20 such questions per topic.",
            },
            {
              n: "4",
              h: "Use diagrams actively in practice",
              b: "Biology and physics diagrams appear heavily in NSO papers — labelling, identifying parts, or explaining what would happen if a component were removed. Practise drawing and labelling key diagrams (human digestive system, plant cell, circuit diagrams) from memory.",
            },
            {
              n: "5",
              h: "Take 4–5 full mock tests in the final 6 weeks",
              b: "Full mock tests build the stamina to switch between Logical Reasoning and Science rapidly within the same 60-minute window. Students who only do topic-wise practice are often surprised by how different it feels in the actual exam.",
            },
          ].map(({ n, h, b }) => (
            <div key={n} className="flex gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white">
                {n}
              </div>
              <div>
                <p className="font-semibold text-slate-900">{h}</p>
                <p className="mt-1 text-[16px] leading-7 text-slate-700">{b}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-10 rounded-2xl bg-emerald-600 p-6 text-white">
          <p className="text-lg font-bold">Practice NSO questions topic by topic</p>
          <p className="mt-1 text-sm text-white/80">
            AI-generated science questions calibrated to your class — with instant explanations that explain
            the concept, not just the answer.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/mock-exams"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-emerald-700 hover:bg-slate-100 transition"
            >
              Take a science mock exam →
            </Link>
            <Link
              href="/topics"
              className="inline-flex items-center gap-2 rounded-xl border border-white/30 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/20 transition"
            >
              Browse NSO topics →
            </Link>
          </div>
        </div>

        {/* Common weak areas */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Common weak areas in NSO preparation
        </h2>
        <ul className="mt-4 space-y-3 text-[17px] leading-8 text-slate-700">
          {[
            "Logical Reasoning — many students under-prepare this section assuming science knowledge is enough; it is worth 10 marks",
            "Experiment-based questions — students who only read textbooks haven't practised the 'observation → conclusion' format",
            "Diagram labelling — requires active recall, not passive recognition; must be practised by drawing, not just looking at diagrams",
            "Chemical equations (Classes 8–9) — balancing and identifying reaction types is a consistent source of errors",
            "Achievers questions — typically involve combining two biology or chemistry concepts; must be explicitly practised",
          ].map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
              <span>{item}</span>
            </li>
          ))}
        </ul>

        {/* Related guides */}
        <div className="mt-14">
          <h2 className="text-xl font-extrabold tracking-tight text-slate-900">Related guides</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <Link href="/olympiad-preparation" className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md">
              <span className="text-xs font-semibold text-slate-500">Overview</span>
              <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">Complete Olympiad Preparation Guide →</h3>
            </Link>
            <Link href="/math-olympiad-preparation" className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md">
              <span className="text-xs font-semibold text-slate-500">Mathematics</span>
              <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">Math Olympiad Preparation — IMO Guide →</h3>
            </Link>
          </div>
        </div>

        {/* FAQ */}
        <section className="mt-14">
          <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Frequently asked questions</h2>
          <div className="mt-6 space-y-4">
            {faqs.map((f) => (
              <div key={f.q} className="rounded-2xl border border-slate-200 p-5">
                <h3 className="font-bold text-slate-900">{f.q}</h3>
                <p className="mt-2 text-[16px] leading-7 text-slate-700">{f.a}</p>
              </div>
            ))}
          </div>
        </section>
      </article>

      <LandingFooter />
    </div>
  );
}
