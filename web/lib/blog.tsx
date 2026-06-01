import type { ReactNode } from "react";
import Link from "next/link";

/* ─────────────────────────────────────────────────────────────
   Lightweight typographic building blocks (no prose plugin needed)
   ───────────────────────────────────────────────────────────── */
export const H2 = ({ children, id }: { children: ReactNode; id?: string }) => (
  <h2 id={id} className="mt-12 scroll-mt-24 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
    {children}
  </h2>
);
export const H3 = ({ children }: { children: ReactNode }) => (
  <h3 className="mt-8 text-xl font-bold text-slate-900">{children}</h3>
);
export const P = ({ children }: { children: ReactNode }) => (
  <p className="mt-4 text-[17px] leading-8 text-slate-700">{children}</p>
);
export const UL = ({ children }: { children: ReactNode }) => (
  <ul className="mt-4 space-y-2 text-[17px] leading-8 text-slate-700">{children}</ul>
);
export const OL = ({ children }: { children: ReactNode }) => (
  <ol className="mt-4 list-decimal space-y-2 pl-6 text-[17px] leading-8 text-slate-700 marker:font-semibold marker:text-brand-600">
    {children}
  </ol>
);
export const LI = ({ children }: { children: ReactNode }) => (
  <li className="flex gap-3">
    <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
    <span>{children}</span>
  </li>
);
export const LIo = ({ children }: { children: ReactNode }) => <li className="pl-1">{children}</li>;
export const B = ({ children }: { children: ReactNode }) => (
  <strong className="font-semibold text-slate-900">{children}</strong>
);
export const Callout = ({ children }: { children: ReactNode }) => (
  <div className="mt-6 rounded-2xl border border-brand-100 bg-brand-50 p-5 text-[16px] leading-7 text-slate-700">
    {children}
  </div>
);
export const CTA = ({ children, href = "/" }: { children: ReactNode; href?: string }) => (
  <div className="mt-10 rounded-2xl bg-gradient-hero p-6 text-white sm:p-8">
    <p className="text-lg font-bold sm:text-xl">{children}</p>
    <Link
      href={href}
      className="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-700 transition hover:bg-slate-100"
    >
      Try 5 questions free →
    </Link>
  </div>
);

export type FAQ = { q: string; a: string };

export type BlogPost = {
  slug: string;
  title: string;
  description: string;
  date: string; // ISO
  updated?: string; // ISO
  tag: string;
  readingMinutes: number;
  keywords: string[];
  /** Short plain-text summary used on the listing card */
  excerpt: string;
  content: ReactNode;
  faqs?: FAQ[];
};

/* ─────────────────────────────────────────────────────────────
   POSTS
   ───────────────────────────────────────────────────────────── */
export const posts: BlogPost[] = [
  /* 1 ───────────────────────────────────────────────────────── */
  {
    slug: "imo-nso-ieo-explained-parents-guide-to-sof-olympiads",
    title: "IMO, NSO & IEO Explained: A Parent's Guide to SOF Olympiads",
    description:
      "What are the IMO, NSO and IEO? A clear, jargon-free guide for Indian parents to SOF Olympiads — levels, syllabus, eligibility, dates and how to prepare.",
    date: "2026-05-20",
    tag: "Guides",
    readingMinutes: 7,
    keywords: ["SOF Olympiad", "IMO", "NSO", "IEO", "Olympiad for kids", "Indian Olympiad exams"],
    excerpt:
      "Confused by all the Olympiad acronyms? Here's a plain-English guide to the IMO, NSO, IEO and other SOF exams — what they test, who can appear, and how the two levels work.",
    content: (
      <>
        <P>
          If your child has come home with a school circular about an &ldquo;Olympiad&rdquo;, you are not alone in
          feeling a little lost. Between the IMO, NSO, IEO, IGKO and a dozen other abbreviations, it is hard to know
          what actually matters. This guide breaks it down in plain language.
        </P>

        <H2 id="what-are-olympiads">What exactly is an Olympiad?</H2>
        <P>
          School Olympiads are competitive exams that test conceptual understanding and reasoning &mdash; not rote
          memorisation. They are taken alongside regular school studies, usually once a year, and rank students at the
          school, state, zonal and national level. The goal is to reward deep thinking and give strong students a
          national benchmark.
        </P>
        <P>
          The most widely taken Olympiads in India are run by the <B>Science Olympiad Foundation (SOF)</B>. Other
          reputable bodies include Silverzone, Unified Council, CREST and the HBCSE (which runs the senior, route-to-
          international Olympiads).
        </P>

        <H2 id="the-main-sof-exams">The main SOF Olympiads</H2>
        <UL>
          <LI>
            <B>IMO &mdash; International Mathematics Olympiad.</B> Tests mathematical reasoning, logic and
            problem-solving for Classes 1&ndash;12.
          </LI>
          <LI>
            <B>NSO &mdash; National Science Olympiad.</B> Covers science concepts, application and reasoning.
          </LI>
          <LI>
            <B>IEO &mdash; International English Olympiad.</B> Grammar, vocabulary, comprehension and everyday English.
          </LI>
          <LI>
            <B>IGKO &mdash; International General Knowledge Olympiad.</B> Current affairs, life skills and GK.
          </LI>
          <LI>
            <B>ISSO &amp; others.</B> Social studies and subject-specific Olympiads round out the list.
          </LI>
        </UL>

        <H2 id="levels">How the two levels work</H2>
        <P>
          Most SOF Olympiads have two rounds. <B>Level 1</B> is held in school and is open to all registered students.
          Students who clear the Level 1 cut-off (top performers, plus class and zone toppers) qualify for{" "}
          <B>Level 2</B>, a tougher national round. For Classes 1&ndash;2, there is usually only a single level.
        </P>
        <Callout>
          <B>Parent tip:</B> Level 1 questions follow a predictable pattern &mdash; a section of logical reasoning, a
          subject section, and a high-weight &ldquo;Achievers&rdquo; section with harder questions. Practising in that
          exact format matters more than doing random worksheets.
        </Callout>

        <H2 id="eligibility-dates">Eligibility, fees and dates</H2>
        <P>
          Any student in Classes 1&ndash;12 can appear &mdash; you register through your school, which receives the
          forms from SOF. Registration windows typically open between July and September, with Level 1 exams held
          between November and January, depending on the subject. Because exact dates shift each year, always confirm
          against the official schedule.
        </P>
        <P>
          We maintain a continuously updated calendar of registration windows and exam dates across all major boards on
          our <Link href="/olympiad-dates" className="font-semibold text-brand-700 underline">Olympiad Dates</Link>{" "}
          page.
        </P>

        <H2 id="how-to-prepare">How should my child prepare?</H2>
        <OL>
          <LIo>Start with the official syllabus for your child&rsquo;s class and subject.</LIo>
          <LIo>Practise in the real exam pattern, including the Achievers section.</LIo>
          <LIo>Review mistakes &mdash; understanding <em>why</em> an answer is wrong is where learning happens.</LIo>
          <LIo>Sit at least one full timed mock exam before the real thing.</LIo>
        </OL>
        <P>
          You don&rsquo;t need expensive coaching to do this well. A structured set of pattern-aligned questions, a way
          to track weak topics, and consistent short practice sessions will take most students a very long way.
        </P>

        <CTA>Give your child SOF-pattern practice for IMO, NSO, IEO and more &mdash; free to start.</CTA>
      </>
    ),
    faqs: [
      {
        q: "What is the difference between IMO Level 1 and Level 2?",
        a: "Level 1 is held in school and is open to all registered students. Level 2 is a tougher national-level round for students who clear the Level 1 cut-off, such as class toppers, zone toppers and top percentile scorers."
      },
      {
        q: "Which class can start appearing for SOF Olympiads?",
        a: "Students from Class 1 right up to Class 12 can appear. For Classes 1 and 2 there is generally a single level, while higher classes have both Level 1 and Level 2 rounds."
      },
      {
        q: "How do I register my child for an Olympiad?",
        a: "Registration is done through your child's school, which receives forms from the Olympiad body (such as SOF). Watch for the school circular, usually between July and September."
      }
    ]
  },

  /* 2 ───────────────────────────────────────────────────────── */
  {
    slug: "how-to-prepare-for-the-maths-olympiad-imo",
    title: "How to Prepare for the Maths Olympiad (IMO): A Step-by-Step Guide",
    description:
      "A practical, class-by-class plan to prepare for the International Mathematics Olympiad (IMO) — syllabus, study schedule, the Achievers section, and free practice tips.",
    date: "2026-05-24",
    tag: "Maths",
    readingMinutes: 8,
    keywords: ["IMO preparation", "maths olympiad", "how to prepare for IMO", "IMO syllabus", "Olympiad maths practice"],
    excerpt:
      "A clear, no-coaching-required plan to prepare for the IMO — from understanding the syllabus to mastering the high-scoring Achievers section.",
    content: (
      <>
        <P>
          The International Mathematics Olympiad rewards <B>reasoning</B>, not memorisation. That is good news: with the
          right structure, almost any motivated student can improve dramatically. Here is a step-by-step plan you can
          follow without expensive coaching.
        </P>

        <H2 id="understand-the-pattern">Step 1: Understand the exam pattern</H2>
        <P>A typical IMO Level 1 paper is split into clear sections:</P>
        <UL>
          <LI><B>Logical Reasoning</B> &mdash; patterns, series, analogies, spatial reasoning.</LI>
          <LI><B>Mathematical Reasoning</B> &mdash; core concepts from your class syllabus.</LI>
          <LI><B>Everyday Mathematics</B> &mdash; applying maths to real situations.</LI>
          <LI><B>Achievers Section</B> &mdash; fewer questions, but each carries more marks. This section decides ranks.</LI>
        </UL>
        <Callout>
          Most students lose ranks not because the maths is too hard, but because they never practised the{" "}
          <B>Achievers section</B> format. Treat it as a separate skill.
        </Callout>

        <H2 id="map-the-syllabus">Step 2: Map the syllabus to your class</H2>
        <P>
          The IMO syllabus closely tracks your school maths syllabus, one or two notches deeper. List every chapter for
          your class, and rate your confidence in each from 1 to 5. This single exercise tells you exactly where to
          spend your time.
        </P>

        <H2 id="build-a-schedule">Step 3: Build a realistic schedule</H2>
        <P>
          Consistency beats intensity. Twenty focused minutes a day for three months will outperform last-minute
          cramming every single time. A simple weekly rhythm that works:
        </P>
        <OL>
          <LIo>3 days of topic practice (your weakest chapters first).</LIo>
          <LIo>1 day of logical reasoning drills.</LIo>
          <LIo>1 day reviewing mistakes from earlier in the week.</LIo>
          <LIo>1 timed mini-test; rest on the seventh day.</LIo>
        </OL>

        <H2 id="master-mistakes">Step 4: Learn from every mistake</H2>
        <P>
          Keep a &ldquo;mistake log&rdquo;. For each wrong answer, write one line on <em>why</em> it went wrong &mdash;
          careless error, concept gap, or misread question. Patterns appear within a week, and fixing them is the
          fastest way to gain marks.
        </P>

        <H2 id="mock-exams">Step 5: Take full timed mock exams</H2>
        <P>
          In the final month, sit at least two or three full-length, timed mock papers. This builds exam stamina,
          improves time management, and removes surprises on the big day. A good mock also predicts your likely rank so
          you know where you stand.
        </P>

        <H2 id="free-resources">Free ways to practise</H2>
        <UL>
          <LI>Previous years&rsquo; sample papers from the official Olympiad body.</LI>
          <LI>Class textbook exercises &mdash; attempt the starred/optional problems.</LI>
          <LI>Pattern-aligned online practice that tracks your weak topics automatically.</LI>
        </UL>
        <P>
          The key is <B>quality and pattern-fit</B>, not volume. A hundred random sums help less than thirty
          well-chosen, exam-style questions reviewed properly.
        </P>

        <CTA href="/?subject=Math">Practise unlimited IMO-pattern questions at your child&rsquo;s exact level.</CTA>
      </>
    ),
    faqs: [
      {
        q: "How early should we start preparing for the IMO?",
        a: "Two to three months of consistent, short daily practice is ideal for Level 1. Starting earlier helps, but regularity matters far more than the total number of hours."
      },
      {
        q: "Is coaching necessary to do well in the Maths Olympiad?",
        a: "No. A structured plan, pattern-aligned practice, a mistake log and a few timed mock exams are enough for most students to perform well without paid coaching."
      },
      {
        q: "What is the Achievers section in the IMO?",
        a: "It is a section with fewer but higher-mark questions that are more challenging. Because each question carries more weight, it heavily influences final ranks and deserves dedicated practice."
      }
    ]
  },

  /* 3 ───────────────────────────────────────────────────────── */
  {
    slug: "olympiad-preparation-tips-at-home",
    title: "12 Practical Olympiad Preparation Tips You Can Start at Home",
    description:
      "Twelve simple, proven Olympiad preparation tips for parents and students — build a routine, practise smart, manage exam stress, and improve without burnout.",
    date: "2026-05-28",
    tag: "Tips",
    readingMinutes: 6,
    keywords: ["Olympiad preparation tips", "study tips for kids", "Olympiad at home", "exam preparation India"],
    excerpt:
      "Twelve practical, low-stress tips to help your child prepare for any Olympiad at home — no expensive coaching required.",
    content: (
      <>
        <P>
          Great Olympiad preparation is less about doing more and more about doing the right things consistently. Here
          are twelve practical tips you can put into action this week.
        </P>

        <H2 id="routine">Build the routine</H2>
        <OL>
          <LIo><B>Short and daily wins.</B> 20&ndash;30 focused minutes a day beats a three-hour weekend marathon.</LIo>
          <LIo><B>Same time, same place.</B> A fixed study slot removes daily negotiation and builds habit.</LIo>
          <LIo><B>Start with the weakest topic</B> while energy is highest, not the easiest one.</LIo>
          <LIo><B>End on a small win</B> &mdash; one question your child can solve confidently, to stay motivated.</LIo>
        </OL>

        <H2 id="practise-smart">Practise smart</H2>
        <OL>
          <LIo><B>Match the exam pattern.</B> Practise in the real section format, including reasoning and Achievers.</LIo>
          <LIo><B>Keep a mistake log.</B> One line on why each error happened reveals fixable patterns fast.</LIo>
          <LIo><B>Quality over quantity.</B> Thirty well-chosen questions, reviewed, beat a hundred skimmed ones.</LIo>
          <LIo><B>Time some sessions.</B> Occasional timed practice builds speed and exam composure.</LIo>
        </OL>

        <H2 id="mindset">Mindset and stress</H2>
        <OL>
          <LIo><B>Praise effort, not just marks.</B> It keeps children willing to attempt hard problems.</LIo>
          <LIo><B>Normalise mistakes.</B> Treat every wrong answer as information, not failure.</LIo>
          <LIo><B>Protect sleep and play.</B> A rested brain learns maths far better than a tired one.</LIo>
          <LIo><B>Do one full mock</B> before the exam so the format feels familiar and calm on the day.</LIo>
        </OL>

        <Callout>
          <B>The one habit that matters most:</B> reviewing mistakes. Students who spend even five minutes a day
          understanding their errors improve noticeably faster than those who only attempt new questions.
        </Callout>

        <CTA>Track weak topics automatically and practise smarter &mdash; start free today.</CTA>
      </>
    ),
    faqs: [
      {
        q: "How much time per day should a child spend on Olympiad preparation?",
        a: "Around 20 to 30 minutes of focused daily practice is ideal for most students. Consistency over several weeks matters far more than long, occasional study sessions."
      },
      {
        q: "How can I reduce my child's exam stress?",
        a: "Praise effort over marks, treat mistakes as information rather than failure, protect sleep and play time, and complete at least one full mock exam so the format feels familiar."
      }
    ]
  },

  /* 4 ───────────────────────────────────────────────────────── */
  {
    slug: "how-ai-is-transforming-olympiad-preparation",
    title: "How AI Is Transforming Olympiad Preparation for Indian Students",
    description:
      "From adaptive question generation to instant explanations and rank prediction, here is how AI is making high-quality Olympiad preparation affordable and accessible in India.",
    date: "2026-05-30",
    tag: "AI & Learning",
    readingMinutes: 6,
    keywords: ["AI olympiad preparation", "adaptive learning India", "AI tutor", "personalised learning", "edtech India"],
    excerpt:
      "Adaptive practice, instant explanations and rank prediction were once luxuries. Here's how AI is putting them within every Indian student's reach.",
    content: (
      <>
        <P>
          For years, the best Olympiad preparation meant expensive coaching and a tutor who could tailor questions to a
          child&rsquo;s exact level. Artificial intelligence is quietly changing that &mdash; making personalised,
          high-quality practice available to any student with a phone or laptop.
        </P>

        <H2 id="adaptive">1. Practice that adapts to the child</H2>
        <P>
          A good human tutor notices when a student has mastered a topic and raises the difficulty. AI does the same at
          scale: it generates fresh questions calibrated to the student&rsquo;s class, subject and demonstrated skill,
          so practice is never too easy or discouragingly hard.
        </P>

        <H2 id="infinite">2. An endless supply of fresh questions</H2>
        <P>
          Printed workbooks run out, and children often memorise answers rather than methods. AI can generate
          effectively limitless, pattern-aligned questions, so every practice session is genuinely new &mdash; testing
          understanding instead of recall.
        </P>

        <H2 id="explanations">3. Instant, step-by-step explanations</H2>
        <P>
          The moment a student gets stuck is the moment they learn most &mdash; if help is available. AI can explain the{" "}
          <em>why</em> behind each answer immediately, turning a wrong attempt into an understood concept rather than a
          source of frustration.
        </P>

        <H2 id="analytics">4. Knowing exactly what to fix</H2>
        <P>
          AI-driven analytics show which topics are weak, how accuracy is trending, and where time is being lost. Some
          platforms even predict a likely rank from full mock exams, so families know where they stand well before the
          real thing.
        </P>

        <H2 id="access">5. Affordable access, beyond the metros</H2>
        <P>
          Perhaps the biggest shift is access. Personalised preparation that once required a premium tutor is now
          available at the cost of a few printed papers &mdash; reaching students in towns and cities far from
          established coaching hubs.
        </P>

        <Callout>
          AI does not replace effort, teachers or good habits. It removes the friction &mdash; the cost, the waiting,
          the guesswork &mdash; so a motivated student can spend their energy on what actually matters: solving
          problems and understanding why.
        </Callout>

        <CTA>Experience adaptive, AI-powered Olympiad practice &mdash; free to start.</CTA>
      </>
    ),
    faqs: [
      {
        q: "Can AI really help my child prepare for Olympiads?",
        a: "Yes. AI can generate fresh, pattern-aligned questions at the right difficulty, give instant explanations, and highlight weak topics — closely mirroring what a good personal tutor does, at a fraction of the cost."
      },
      {
        q: "Does AI-based practice replace teachers and coaching?",
        a: "No. It complements them. AI removes cost and friction from practice and feedback, while teachers, mentors and good study habits remain essential to a child's progress."
      }
    ]
  }
];

/* ─────────────────────────────────────────────────────────────
   Helpers
   ───────────────────────────────────────────────────────────── */
export function getAllPosts(): BlogPost[] {
  return [...posts].sort((a, b) => +new Date(b.date) - +new Date(a.date));
}
export function getPostBySlug(slug: string): BlogPost | undefined {
  return posts.find((p) => p.slug === slug);
}
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });
}
