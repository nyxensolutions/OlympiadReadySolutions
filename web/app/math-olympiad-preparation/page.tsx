import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { LandingFooter } from "@/components/landing/LandingFooter";

const SITE_URL = "https://olympiadready.com";

export const metadata: Metadata = {
  title: "Math Olympiad Preparation — Complete IMO Guide",
  description:
    "Complete math olympiad preparation guide for the IMO. Covers class-wise syllabus, exam pattern, Level 1 vs Level 2 strategy, practice routine, and common weak areas for Classes 1–12.",
  keywords: [
    "math olympiad preparation",
    "IMO preparation",
    "maths olympiad preparation India",
    "how to prepare for IMO",
    "International Mathematics Olympiad guide",
    "IMO study tips",
    "math olympiad tips for students",
  ],
  alternates: { canonical: "/math-olympiad-preparation" },
  openGraph: {
    title: "Math Olympiad Preparation — Complete IMO Guide | OlympiadReady",
    description:
      "Step-by-step math olympiad preparation for the IMO. Class-wise syllabus, Level 1 and Level 2 strategies, practice routines for Classes 1–12.",
    url: `${SITE_URL}/math-olympiad-preparation`,
    type: "article",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Math Olympiad Preparation Guide" }],
  },
};

const faqs = [
  {
    q: "What is the IMO exam pattern?",
    a: "The SOF IMO has three sections: Mathematical Reasoning (10–15 questions), Everyday Mathematics (10–15 questions), and Achievers Section (5 questions worth 3–4 marks each). Total: 35–40 questions in 60 minutes. There is no negative marking.",
  },
  {
    q: "Is the IMO syllabus the same as the school syllabus?",
    a: "Yes, the IMO syllabus is based entirely on the CBSE/NCERT school curriculum for each class. Olympiad questions are harder in how they are asked — they test deeper application and reasoning — but the underlying topics are the same.",
  },
  {
    q: "How do I qualify for IMO Level 2?",
    a: "Roughly the top 5% of students per class per zone qualify for Level 2 (national round). To qualify, aim for near-perfect accuracy on Sections 1 and 2, and attempt at least 3 out of 5 Achievers questions correctly.",
  },
  {
    q: "What topics should I focus on most for the IMO?",
    a: "For Classes 1–5: Number systems, arithmetic operations, patterns, and basic geometry. For Classes 6–8: Algebra, rational numbers, mensuration, and data handling. For Classes 9–12: Real numbers, polynomials, coordinate geometry, and probability are consistently high-weight topics.",
  },
  {
    q: "How many mock tests should I take before the IMO?",
    a: "Take at least 4–5 full-length timed mock tests in the 6 weeks before the exam. Your first mock establishes a baseline; use the results to guide focused practice, then re-test to measure improvement.",
  },
];

const articleJsonLd = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: "Math Olympiad Preparation — Complete IMO Guide for Classes 1–12",
  description:
    "Complete math olympiad preparation guide for the IMO. Covers class-wise syllabus, exam pattern, Level 1 vs Level 2 strategy, and practice routine.",
  author: { "@type": "Organization", name: "OlympiadReady", url: SITE_URL },
  publisher: {
    "@type": "Organization",
    name: "OlympiadReady",
    logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` },
  },
  mainEntityOfPage: { "@type": "WebPage", "@id": `${SITE_URL}/math-olympiad-preparation` },
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
    { "@type": "ListItem", position: 3, name: "Math Olympiad Preparation", item: `${SITE_URL}/math-olympiad-preparation` },
  ],
};

export default function MathOlympiadPreparationPage() {
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
          <span className="text-slate-700">Math Olympiad</span>
        </nav>

        <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">
          Mathematics
        </span>

        <h1 className="mt-4 text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl">
          Math Olympiad Preparation — Complete IMO Guide for Classes 1–12
        </h1>

        <p className="mt-5 text-lg leading-8 text-slate-600">
          The International Mathematics Olympiad (IMO) run by the Science Olympiad Foundation is the most popular
          school olympiad in India, with over 5 million participants annually. This guide covers everything you need
          for effective math olympiad preparation — the exam pattern, class-wise syllabus priorities, study strategy,
          and how to tackle the high-value Achievers section.
        </p>

        {/* Exam pattern overview */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          IMO exam pattern at a glance
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          The SOF IMO is a 60-minute multiple-choice paper taken inside school. There is no negative marking, so
          students should attempt every question. The paper has three sections:
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
                <td className="px-4 py-2.5 font-medium">Mathematical Reasoning</td>
                <td className="px-4 py-2.5">15</td>
                <td className="px-4 py-2.5">1</td>
                <td className="px-4 py-2.5">Concepts, calculation</td>
              </tr>
              <tr className="bg-slate-50/50">
                <td className="px-4 py-2.5 font-medium">Everyday Mathematics</td>
                <td className="px-4 py-2.5">15</td>
                <td className="px-4 py-2.5">1</td>
                <td className="px-4 py-2.5">Word problems, application</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 font-medium text-amber-700">Achievers Section</td>
                <td className="px-4 py-2.5">5</td>
                <td className="px-4 py-2.5">3</td>
                <td className="px-4 py-2.5">Higher order thinking</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <span className="font-semibold">Note on the Achievers section:</span> Those 5 questions are worth 15 marks
          out of a typical 45-mark paper. Students who score full marks on Achievers separate themselves from students
          who only focus on the first two sections. Dedicating 30% of your practice time to higher-order questions
          pays off disproportionately.
        </div>

        {/* Syllabus */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          IMO syllabus priorities by class group
        </h2>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 1–3: Number sense and basic operations</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          The focus at this level is understanding numbers up to 1000, place value, addition and subtraction
          with and without regrouping, multiplication tables, basic fractions, and simple shapes. Students
          who can solve picture-based word problems confidently are well-prepared for Classes 1–3 IMO.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 4–6: Fractions, decimals, and geometry</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          This is where many students start to find the IMO genuinely challenging. Fractions and their
          operations, decimal representation, percentage and ratio, perimeter and area, and introduction to
          negative numbers are the key topics. Data interpretation (bar graphs, pie charts) also starts
          appearing in Class 5–6 papers with increased weight.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 7–9: Algebra and coordinate geometry</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Linear equations, algebraic expressions, exponents, Pythagoras theorem, construction and properties
          of triangles, and basic probability are the backbone of Classes 7–9 IMO. Students who struggle here
          typically have gaps in fraction arithmetic from earlier classes — fix those first before tackling
          algebra.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 10–12: Calculus concepts and statistics</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          At Classes 10–12, the IMO closely tracks the board syllabus. Real numbers and polynomials, quadratic
          equations, trigonometry, arithmetic and geometric progressions, coordinate geometry, and probability
          are the most frequently tested areas. Level 2 papers at this stage are significantly harder and
          require problem-solving speed along with conceptual depth.
        </p>

        {/* Strategy */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          5-step math olympiad preparation strategy
        </h2>

        <div className="mt-6 space-y-5">
          {[
            {
              n: "1",
              h: "Map your gaps against the syllabus",
              b: "Download the IMO syllabus for your class. Go through each topic and rate yourself honestly: strong, shaky, or not covered. Prioritise the shaky topics — not the ones you are already good at.",
            },
            {
              n: "2",
              h: "Practise every topic before attempting full papers",
              b: "Topic-wise practice builds accuracy. Do at least 30–40 questions per topic before moving to full mock papers. This is especially important for topics like algebraic identities, mensuration, and data interpretation which require pattern recognition.",
            },
            {
              n: "3",
              h: "Master the Achievers section separately",
              b: "The Achievers questions are not just harder versions of the regular questions — they often require combining two or three concepts in a single problem. Practise these as a distinct exercise, not as an afterthought.",
            },
            {
              n: "4",
              h: "Time yourself from week one",
              b: "The IMO gives roughly 1.5 minutes per question. Students who practise without timing often discover they cannot finish the paper on exam day. Use a timer on every practice session — even topic-wise practice.",
            },
            {
              n: "5",
              h: "Review every wrong answer in full",
              b: "For every question you get wrong, write down the correct approach in your own words. This active recall step is far more effective than just reading the solution. Students who do this consistently see the largest score improvements.",
            },
          ].map(({ n, h, b }) => (
            <div key={n} className="flex gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {n}
              </div>
              <div>
                <p className="font-semibold text-slate-900">{h}</p>
                <p className="mt-1 text-[16px] leading-7 text-slate-700">{b}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Level 1 vs 2 */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Level 1 vs Level 2: different preparation
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Level 1 rewards speed and accuracy across the full syllabus. Level 2 (national round) rewards deep
          problem-solving — questions are fewer, longer, and require multi-step reasoning. Students who qualify
          for Level 2 should shift from broad coverage to intense practice on the top 5–6 topic areas, focusing
          specifically on Achievers-style problems and non-routine application questions.
        </p>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          For Level 2 preparation, working through SOF Level 2 past papers is non-negotiable. The difficulty
          jump from Level 1 to Level 2 is significant — students who only practise Level 1 style questions
          are rarely well-prepared for the national round.
        </p>

        {/* CTA */}
        <div className="mt-10 rounded-2xl bg-brand-600 p-6 text-white">
          <p className="text-lg font-bold">Practice IMO questions by topic and class</p>
          <p className="mt-1 text-sm text-white/80">
            AI-generated questions calibrated to your class and olympiad level — with instant step-by-step
            explanations for every answer.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/mock-exams"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-700 hover:bg-slate-100 transition"
            >
              Take a mock exam →
            </Link>
            <Link
              href="/practice-papers"
              className="inline-flex items-center gap-2 rounded-xl border border-white/30 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/20 transition"
            >
              Practice papers →
            </Link>
          </div>
        </div>

        {/* Common weak areas */}
        <h2 className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Common weak areas in math olympiad preparation
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Across thousands of practice sessions, these are the topics where students most consistently lose marks:
        </p>
        <ul className="mt-4 space-y-3 text-[17px] leading-8 text-slate-700">
          {[
            "Word problems involving percentage change (often misread or set up incorrectly)",
            "Geometry: identifying which property applies to a given figure (requires visual practice, not just memorisation)",
            "Data interpretation: reading the question correctly before calculating (students rush and use the wrong row/column)",
            "Achievers section: combining two concepts in one step — practise these question types explicitly",
            "Fraction arithmetic with unlike denominators — errors here cascade into wrong answers across multiple topics",
          ].map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
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
            <Link href="/science-olympiad-preparation" className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md">
              <span className="text-xs font-semibold text-slate-500">Science</span>
              <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">Science Olympiad Preparation — NSO Guide →</h3>
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
