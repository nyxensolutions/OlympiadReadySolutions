import type { Metadata } from "next";
import Link from "next/link";
import { Clock, ArrowRight } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { getAllPosts, formatDate } from "@/lib/blog";

export const metadata: Metadata = {
  title: "Olympiad Prep Blog — Tips & Exam Strategy",
  description:
    "Practical guides and tips on Olympiad preparation for Indian students — IMO, NSO, IEO and more. Class-by-class strategy, study plans and free practice advice.",
  alternates: { canonical: "/blog" },
  openGraph: {
    title: "Olympiad Prep Blog — Tips, Guides & Exam Strategy | OlympiadReady",
    description:
      "Practical guides and tips on Olympiad preparation for Indian students — IMO, NSO, IEO and more.",
    url: "https://olympiadready.com/blog",
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "OlympiadReady Blog" }]
  }
};

export default function BlogIndexPage() {
  const allPosts = getAllPosts();
  const [featured, ...rest] = allPosts;

  return (
    <div className="min-h-screen bg-white">
      <AppHeader active="blog" />

      {/* Hero */}
      <section className="bg-gradient-hero px-4 py-14 text-white">
        <div className="mx-auto max-w-5xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-200">OlympiadReady Blog</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">
            Olympiad preparation, made clear.
          </h1>
          <p className="mt-3 max-w-2xl text-brand-100">
            Guides, tips and exam strategy for IMO, NSO, IEO and every major school Olympiad — written for Indian
            parents and students, Classes 1–12.
          </p>
        </div>
      </section>

      <main className="mx-auto max-w-5xl px-4 py-12">
        {/* Featured */}
        {featured && (
          <Link
            href={`/blog/${featured.slug}`}
            className="group block rounded-3xl border border-slate-200 bg-slate-50 p-8 transition hover:border-brand-200 hover:bg-brand-50/40 hover:shadow-md"
          >
            <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">
              {featured.tag}
            </span>
            <h2 className="mt-4 text-2xl font-extrabold tracking-tight text-slate-900 group-hover:text-brand-700 sm:text-3xl">
              {featured.title}
            </h2>
            <p className="mt-3 max-w-3xl text-[17px] leading-7 text-slate-600">{featured.excerpt}</p>
            <div className="mt-5 flex items-center gap-4 text-sm text-slate-500">
              <span>{formatDate(featured.date)}</span>
              <span className="inline-flex items-center gap-1">
                <Clock className="h-4 w-4" /> {featured.readingMinutes} min read
              </span>
              <span className="inline-flex items-center gap-1 font-semibold text-brand-700">
                Read <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </span>
            </div>
          </Link>
        )}

        {/* Grid */}
        <div className="mt-8 grid gap-6 sm:grid-cols-2">
          {rest.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition hover:border-brand-200 hover:shadow-md"
            >
              <span className="inline-flex w-fit items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
                {post.tag}
              </span>
              <h3 className="mt-3 text-lg font-bold text-slate-900 group-hover:text-brand-700">{post.title}</h3>
              <p className="mt-2 flex-1 text-[15px] leading-6 text-slate-600">{post.excerpt}</p>
              <div className="mt-4 flex items-center gap-3 text-xs text-slate-500">
                <span>{formatDate(post.date)}</span>
                <span className="inline-flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" /> {post.readingMinutes} min
                </span>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
