import Link from "next/link";
import { ArrowRight, Clock } from "lucide-react";
import { getAllPosts, formatDate } from "@/lib/blog";

export function BlogTeaserSection() {
  const posts = getAllPosts().slice(0, 3);
  if (posts.length === 0) return null;

  return (
    <section className="bg-slate-50 px-4 py-16 sm:py-20">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-600">From the blog</p>
            <h2 className="mt-2 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
              Olympiad prep guides &amp; tips
            </h2>
            <p className="mt-2 max-w-2xl text-slate-600">
              Practical advice on IMO, NSO, IEO and more — written for Indian parents and students, Classes 1–12.
            </p>
          </div>
          <Link
            href="/blog"
            className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700 transition hover:bg-brand-100"
          >
            View all posts <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((post) => (
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
      </div>
    </section>
  );
}
