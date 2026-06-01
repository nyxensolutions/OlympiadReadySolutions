import type { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/blog";

const SITE_URL = "https://olympiadready.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();

  // Public, indexable routes (logged-in/admin routes are intentionally excluded)
  const routes: { path: string; priority: number; changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"] }[] = [
    { path: "/", priority: 1.0, changeFrequency: "weekly" },
    { path: "/blog", priority: 0.8, changeFrequency: "weekly" },
    { path: "/mock-exams", priority: 0.9, changeFrequency: "weekly" },
    { path: "/practice-papers", priority: 0.9, changeFrequency: "weekly" },
    { path: "/topics", priority: 0.8, changeFrequency: "weekly" },
    { path: "/spell-bee", priority: 0.8, changeFrequency: "weekly" },
    { path: "/weekly-exam", priority: 0.7, changeFrequency: "weekly" },
    { path: "/challenge", priority: 0.6, changeFrequency: "monthly" },
    { path: "/olympiad-dates", priority: 0.6, changeFrequency: "monthly" },
    { path: "/contact", priority: 0.4, changeFrequency: "yearly" },
    { path: "/privacy", priority: 0.2, changeFrequency: "yearly" },
    { path: "/terms", priority: 0.2, changeFrequency: "yearly" },
    { path: "/refund", priority: 0.2, changeFrequency: "yearly" },
    { path: "/cookies", priority: 0.2, changeFrequency: "yearly" }
  ];

  const staticEntries: MetadataRoute.Sitemap = routes.map((r) => ({
    url: `${SITE_URL}${r.path}`,
    lastModified: now,
    changeFrequency: r.changeFrequency,
    priority: r.priority
  }));

  const blogEntries: MetadataRoute.Sitemap = getAllPosts().map((post) => ({
    url: `${SITE_URL}/blog/${post.slug}`,
    lastModified: new Date(post.updated ?? post.date),
    changeFrequency: "monthly",
    priority: 0.7
  }));

  return [...staticEntries, ...blogEntries];
}
