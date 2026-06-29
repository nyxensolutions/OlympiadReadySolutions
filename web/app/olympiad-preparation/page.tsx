import type { Metadata } from "next";
import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { LandingFooter } from "@/components/landing/LandingFooter";

const SITE_URL = "https://olympiadready.com";

export const metadata: Metadata = {
  title: "Olympiad Preparation Guide — Classes 1–12",
  description:
    "Complete olympiad preparation guide for Indian students. Step-by-step strategies for IMO, NSO, IEO, IGKO — study plans, practice tips, and a clear roadmap for Classes 1–12.",
  keywords: [
    "olympiad preparation",
    "how to prepare for olympiads",
    "olympiad preparation guide",
    "online olympiad preparation",
    "olympiad study plan India",
    "olympiad preparation for students",
    "school olympiad preparation",
  ],
  alternates: { canonical: "/olympiad-preparation" },
  openGraph: {
    title: "Olympiad Preparation Guide — Classes 1–12 | OlympiadReady",
    description:
      "Complete olympiad preparation guide for Indian students. Step-by-step strategies for IMO, NSO, IEO, IGKO for Classes 1–12.",
    url: `${SITE_URL}/olympiad-preparation`,
    type: "article",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Olympiad Preparation Guide" }],
  },
};

const faqs = [
  {
    q: "When should I start olympiad preparation?",
    a: "Ideally 3–4 months before the exam, which is typically held in November–December. Starting in August gives you enough time to cover all topics, take mock tests, and review weak areas without pressure.",
  },
  {
    q: "How many hours a day should I study for olympiads?",
    a: "For Classes 1–5, 20–30 minutes of focused practice daily is enough. For Classes 6–10, aim for 45–60 minutes. For Classes 11–12, 60–90 minutes dedicated specifically to olympiad topics (separate from board exam study).",
  },
  {
    q: "Can I prepare for multiple olympiads at the same time?",
    a: "Yes — IMO, NSO, and IEO share a significant portion of their syllabus with the school curriculum. Students in Classes 3–8 often prepare for 2–3 olympiads simultaneously with only slightly more effort than preparing for one.",
  },
  {
    q: "Are olympiad questions harder than school exams?",
    a: "Olympiad questions test the same concepts but require deeper application and reasoning. You won't encounter topics outside your school syllabus, but questions are framed as puzzles or multi-step problems rather than direct recall.",
  },
  {
    q: "How do I qualify for Level 2 (national round)?",
    a: "In SOF olympiads, roughly the top 5% of students per class per zone qualify for Level 2. Focus on speed and accuracy — Level 1 rewards students who can answer all questions correctly within the time limit.",
  },
  {
    q: "Does OlympiadReady cover all olympiad subjects?",
    a: "Yes. OlympiadReady covers Maths (IMO), Science (NSO), English (IEO), General Knowledge (IGKO), Reasoning, and Spell Bee for Classes 1–12. Questions are aligned to SOF, Silverzone, and CREST Olympiad patterns.",
  },
];

const articleJsonLd = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: "Olympiad Preparation Guide — Everything You Need to Know",
  description:
    "Complete olympiad preparation guide for Indian students. Step-by-step strategies for IMO, NSO, IEO, IGKO — study plans, practice tips, and a clear roadmap for Classes 1–12.",
  author: { "@type": "Organization", name: "OlympiadReady", url: SITE_URL },
  publisher: {
    "@type": "Organization",
    name: "OlympiadReady",
    logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` },
  },
  mainEntityOfPage: { "@type": "WebPage", "@id": `${SITE_URL}/olympiad-preparation` },
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
    { "@type": "ListItem", position: 2, name: "Olympiad Preparation Guide", item: `${SITE_URL}/olympiad-preparation` },
  ],
};

export default function OlympiadPreparationPage() {
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
          <span className="text-slate-700">Olympiad Preparation Guide</span>
        </nav>

        <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">
          Complete Guide
        </span>

        <h1 className="mt-4 text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl">
          Olympiad Preparation Guide — Everything You Need to Know
        </h1>

        <p className="mt-5 text-lg leading-8 text-slate-600">
          School olympiads are one of the best opportunities for Indian students to challenge themselves beyond the
          regular syllabus, earn national recognition, and build problem-solving skills that last a lifetime. This guide
          covers exactly how to prepare for olympiads — from choosing the right exams to building a daily study routine
          — for students in Classes 1 through 12.
        </p>

        {/* Quick nav */}
        <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <p className="mb-3 text-sm font-semibold text-slate-700">In this guide</p>
          <ol className="space-y-1.5 text-sm text-brand-700">
            {[
              ["#which-olympiads", "Which olympiads should you target?"],
              ["#how-to-start", "How to start: 5 practical steps"],
              ["#by-class", "Preparation strategy by class group"],
              ["#study-routine", "Building a daily study routine"],
              ["#mock-tests", "The role of mock tests and practice papers"],
              ["#mistakes", "Common mistakes and how to avoid them"],
              ["#faq", "Frequently asked questions"],
            ].map(([href, label]) => (
              <li key={href}>
                <a href={href} className="hover:underline">{label}</a>
              </li>
            ))}
          </ol>
        </div>

        {/* Section 1 */}
        <h2 id="which-olympiads" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Which olympiads should you target?
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          India has several major school olympiad bodies. The Science Olympiad Foundation (SOF) is the largest,
          running the International Mathematics Olympiad (IMO), National Science Olympiad (NSO), International English
          Olympiad (IEO), and International General Knowledge Olympiad (IGKO). Silverzone and CREST are two other
          reputable bodies with strong national reach.
        </p>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          For most students, starting with the SOF olympiad in their strongest subject is the best first step.
          Students in Classes 3–8 can reasonably prepare for 2–3 olympiads in a single season because the IMO, NSO,
          and IEO all draw from the school curriculum. Adding a reasoning-based olympiad like IGKO requires minimal
          extra effort once the core subjects are covered.
        </p>

        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Olympiad</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Subject</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Classes</th>
                <th className="px-4 py-3 text-left font-semibold text-slate-700">Organiser</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[
                ["IMO", "Mathematics", "1–12", "SOF"],
                ["NSO", "Science", "1–12", "SOF"],
                ["IEO", "English", "1–12", "SOF"],
                ["IGKO", "General Knowledge", "1–10", "SOF"],
                ["Spell Bee", "English Spelling", "1–12", "Various"],
                ["IMAS / RMO", "Advanced Maths", "6–12", "IMAS / HBCSE"],
              ].map(([name, subj, cls, org]) => (
                <tr key={name} className="even:bg-slate-50/50">
                  <td className="px-4 py-2.5 font-semibold text-brand-700">{name}</td>
                  <td className="px-4 py-2.5 text-slate-700">{subj}</td>
                  <td className="px-4 py-2.5 text-slate-600">{cls}</td>
                  <td className="px-4 py-2.5 text-slate-500">{org}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Section 2 */}
        <h2 id="how-to-start" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          How to start olympiad preparation: 5 practical steps
        </h2>

        <div className="mt-6 space-y-5">
          {[
            {
              step: "1",
              title: "Register before the deadline",
              body: "SOF olympiads close school registrations in September–October. Your school coordinator handles registration — confirm your school has registered and that you are on the list. Missing the registration deadline is the most common reason students miss the exam entirely.",
            },
            {
              step: "2",
              title: "Download the official syllabus",
              body: "The SOF publishes a detailed syllabus PDF for every class and subject on their website. This is your definitive guide to what can appear in the paper. Highlight the topics you already know well versus the ones you haven't covered yet.",
            },
            {
              step: "3",
              title: "Strengthen your school syllabus first",
              body: "Olympiad questions are based entirely on the school curriculum — they just go deeper. A student who understands their NCERT or CBSE textbook thoroughly has already covered 70–80% of what the olympiad tests. Don't start olympiad-specific preparation until your school concepts are solid.",
            },
            {
              step: "4",
              title: "Practise with past papers and topic-wise questions",
              body: "Past SOF papers from the last 3–5 years are the single most effective preparation resource. Work through them topic by topic — don't just solve papers end-to-end. Identify which question types appear repeatedly and focus your practice there.",
            },
            {
              step: "5",
              title: "Take full timed mock tests in the final 4 weeks",
              body: "In the last month before the exam, take at least 3–4 full-length timed mock tests under exam conditions. This builds the speed and focus required to finish the paper comfortably within the time limit. Review every wrong answer in detail.",
            },
          ].map(({ step, title, body }) => (
            <div key={step} className="flex gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {step}
              </div>
              <div>
                <p className="font-semibold text-slate-900">{title}</p>
                <p className="mt-1 text-[16px] leading-7 text-slate-700">{body}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA 1 */}
        <div className="mt-10 rounded-2xl bg-brand-600 p-6 text-white">
          <p className="text-lg font-bold">Start practising topic by topic</p>
          <p className="mt-1 text-sm text-white/80">
            OlympiadReady maps every olympiad topic to your class and subject — so you always know exactly what to
            practise next.
          </p>
          <Link
            href="/topics"
            className="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-700 hover:bg-slate-100 transition"
          >
            Browse the syllabus map →
          </Link>
        </div>

        {/* Section 3 */}
        <h2 id="by-class" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Preparation strategy by class group
        </h2>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 1–5: Build the habit, keep it fun</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          At this stage, the goal is not a high rank — it is building the habit of practising beyond the textbook and
          enjoying problem-solving. Parents should keep sessions short (15–25 minutes), use visually engaging practice
          questions, and focus on number sense, patterns, and basic reasoning. The exam itself is not stressful at
          this level — most Class 1–3 children finish in well under the time limit.
        </p>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Avoid rote practice. A child who understands why 3 × 4 = 12 will handle olympiad questions better than one
          who has memorised tables without understanding multiplication as repeated addition.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 6–8: Deepen and diversify</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          This is the sweet spot for olympiad preparation. The syllabus gets substantially harder (algebra, biology
          cells, tenses and grammar), and reasoning questions become genuinely challenging. Students who do well at
          this level often qualify for Level 2 national rounds. Aim for 45–60 minutes of olympiad practice daily,
          split across 2–3 subjects if targeting multiple olympiads.
        </p>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          For maths, focus on rational numbers, basic geometry proofs, and data interpretation — these are
          consistently high-weight topics across all Classes 6–8 IMO papers. For science, the Life Science section
          tends to have the steepest difficulty curve at this level.
        </p>

        <h3 className="mt-8 text-xl font-bold text-slate-900">Classes 9–12: Focus and depth over breadth</h3>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Board exam preparation naturally aligns with olympiad preparation at this stage — but the olympiad questions
          are significantly more application-heavy than boards. Students should not attempt 3–4 olympiads at Class 9+;
          pick 1–2 and go deep. The Achievers section in SOF olympiads carries higher marks and specifically tests
          application, so practising harder questions from this section is essential for a competitive rank.
        </p>

        {/* Section 4 */}
        <h2 id="study-routine" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Building a daily study routine
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Consistency beats intensity every time in olympiad preparation. A student who practises 30 minutes every
          day for 90 days will outperform a student who studies 5 hours on weekends alone. Build a simple structure:
        </p>
        <ul className="mt-4 space-y-2 text-[17px] leading-8 text-slate-700">
          {[
            "Weekdays: 20–45 minutes of topic-wise questions aligned to the current chapter in school",
            "Saturday: one timed section (e.g., 15 questions, 25 minutes) on a weaker topic",
            "Sunday: review the week's wrong answers — understand why each was wrong before moving on",
            "Final 4 weeks: replace topic practice with full mock tests; review every error",
          ].map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
              <span>{item}</span>
            </li>
          ))}
        </ul>

        {/* Section 5 */}
        <h2 id="mock-tests" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          The role of mock tests and practice papers
        </h2>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Many students make the mistake of doing only chapter-wise practice and skipping full-length mock tests.
          Mock tests do something that topic practice cannot: they train your brain to switch between topics rapidly,
          manage time pressure, and make decisions when you are unsure of an answer (should I skip or guess?).
        </p>
        <p className="mt-4 text-[17px] leading-8 text-slate-700">
          Take your first mock test 6–8 weeks before the exam, without any special preparation, to establish a
          baseline score. Identify the 3 weakest topics from the result and make those your priority for the next
          3–4 weeks. Then take another mock test to measure improvement. Repeat.
        </p>

        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-[16px] leading-7 text-slate-700">
          <span className="font-semibold text-amber-800">Pro tip:</span> After each mock test, spend at least as much
          time reviewing wrong answers as you spent taking the test. The review session is where the real learning
          happens.
        </div>

        {/* CTA 2 */}
        <div className="mt-8 rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 p-6 text-white">
          <p className="text-lg font-bold">Try an AI mock exam for free</p>
          <p className="mt-1 text-sm text-white/80">
            Adaptive, timed, and calibrated to your class and olympiad — with instant explanations for every answer.
          </p>
          <Link
            href="/mock-exams"
            className="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-violet-700 hover:bg-slate-100 transition"
          >
            Take a free mock exam →
          </Link>
        </div>

        {/* Section 6 */}
        <h2 id="mistakes" className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
          Common mistakes and how to avoid them
        </h2>

        <div className="mt-6 space-y-4">
          {[
            {
              mistake: "Starting too late",
              fix: "3–4 months is the minimum. Starting 6 weeks before the exam leaves no time for proper mock test review.",
            },
            {
              mistake: "Skipping the Achievers / High Order Thinking section",
              fix: "This section carries 3–4 marks per question versus 1 mark for standard questions. Ignoring it is a rank killer.",
            },
            {
              mistake: "Practising without a timer",
              fix: "The biggest cause of low scores is running out of time — not lack of knowledge. Always practise with a timer.",
            },
            {
              mistake: "Buying too many books",
              fix: "One good olympiad workbook per subject plus official past papers is enough. More books = less depth per book.",
            },
            {
              mistake: "Not reviewing wrong answers",
              fix: "Marking answers wrong without understanding why is the most expensive mistake in olympiad prep. Every wrong answer is a mini lesson.",
            },
          ].map(({ mistake, fix }) => (
            <div key={mistake} className="rounded-2xl border border-slate-200 p-5">
              <p className="font-bold text-rose-700">✗ {mistake}</p>
              <p className="mt-1.5 text-[15px] leading-6 text-slate-700">
                <span className="font-semibold text-emerald-700">Fix: </span>{fix}
              </p>
            </div>
          ))}
        </div>

        {/* Guide links */}
        <div className="mt-14">
          <h2 className="text-xl font-extrabold tracking-tight text-slate-900">Subject-specific preparation guides</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <Link
              href="/math-olympiad-preparation"
              className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md"
            >
              <span className="text-xs font-semibold text-slate-500">Mathematics</span>
              <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">
                Math Olympiad Preparation — IMO Guide →
              </h3>
            </Link>
            <Link
              href="/science-olympiad-preparation"
              className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md"
            >
              <span className="text-xs font-semibold text-slate-500">Science</span>
              <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">
                Science Olympiad Preparation — NSO Guide →
              </h3>
            </Link>
          </div>
        </div>

        {/* FAQ */}
        <section id="faq" className="mt-14 scroll-mt-24">
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
