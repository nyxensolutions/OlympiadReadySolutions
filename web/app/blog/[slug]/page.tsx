import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Clock } from "lucide-react";
import { AppHeader } from "@/components/AppHeader";
import { getAllPosts, getPostBySlug, formatDate } from "@/lib/blog";

const SITE_URL = "https://olympiadready.com";

export function generateStaticParams() {
  return getAllPosts().map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const post = getPostBySlug(params.slug);
  if (!post) return { title: "Post not found" };
  const url = `${SITE_URL}/blog/${post.slug}`;
  return {
    title: post.title,
    description: post.description,
    keywords: post.keywords,
    alternates: { canonical: `/blog/${post.slug}` },
    openGraph: {
      type: "article",
      url,
      title: post.title,
      description: post.description,
      publishedTime: post.date,
      modifiedTime: post.updated ?? post.date,
      authors: ["OlympiadReady"],
      tags: post.keywords
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.description
    }
  };
}

export default function BlogPostPage({ params }: { params: { slug: string } }) {
  const post = getPostBySlug(params.slug);
  if (!post) notFound();

  const url = `${SITE_URL}/blog/${post.slug}`;
  const related = getAllPosts().filter((p) => p.slug !== post.slug).slice(0, 2);

  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    dateModified: post.updated ?? post.date,
    author: { "@type": "Organization", name: "OlympiadReady", url: SITE_URL },
    publisher: {
      "@type": "Organization",
      name: "OlympiadReady",
      logo: { "@type": "ImageObject", url: `${SITE_URL}/logo.png` }
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    image: `${SITE_URL}/og-image.png`,
    keywords: post.keywords.join(", ")
  };

  const faqJsonLd = post.faqs?.length
    ? {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: post.faqs.map((f) => ({
          "@type": "Question",
          name: f.q,
          acceptedAnswer: { "@type": "Answer", text: f.a }
        }))
      }
    : null;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "Blog", item: `${SITE_URL}/blog` },
      { "@type": "ListItem", position: 3, name: post.title, item: url }
    ]
  };

  return (
    <div className="min-h-screen bg-white">
      <AppHeader active="blog" />

      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />
      {faqJsonLd && (
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }} />
      )}

      <article className="mx-auto max-w-3xl px-4 py-12">
        <Link href="/blog" className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:underline">
          <ArrowLeft className="h-4 w-4" /> All posts
        </Link>

        <div className="mt-6">
          <span className="inline-flex items-center rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">
            {post.tag}
          </span>
          <h1 className="mt-4 text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl">
            {post.title}
          </h1>
          <div className="mt-4 flex items-center gap-4 text-sm text-slate-500">
            <span>{formatDate(post.date)}</span>
            <span className="inline-flex items-center gap-1">
              <Clock className="h-4 w-4" /> {post.readingMinutes} min read
            </span>
          </div>
        </div>

        <hr className="my-8 border-slate-200" />

        {/* Body */}
        <div>{post.content}</div>

        {/* FAQs */}
        {post.faqs?.length ? (
          <section className="mt-14">
            <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Frequently asked questions</h2>
            <div className="mt-6 space-y-4">
              {post.faqs.map((f) => (
                <div key={f.q} className="rounded-2xl border border-slate-200 p-5">
                  <h3 className="font-bold text-slate-900">{f.q}</h3>
                  <p className="mt-2 text-[16px] leading-7 text-slate-700">{f.a}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {/* Related */}
        {related.length > 0 && (
          <section className="mt-16">
            <h2 className="text-xl font-extrabold tracking-tight text-slate-900">Keep reading</h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {related.map((r) => (
                <Link
                  key={r.slug}
                  href={`/blog/${r.slug}`}
                  className="group rounded-2xl border border-slate-200 p-5 transition hover:border-brand-200 hover:shadow-md"
                >
                  <span className="text-xs font-semibold text-slate-500">{r.tag}</span>
                  <h3 className="mt-1 font-bold text-slate-900 group-hover:text-brand-700">{r.title}</h3>
                </Link>
              ))}
            </div>
          </section>
        )}
      </article>
    </div>
  );
}
