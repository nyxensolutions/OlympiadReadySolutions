import type { MetadataRoute } from "next";

const SITE_URL = "https://olympiadready.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/dashboard", "/admin", "/sign-in", "/sign-up", "/parent", "/invoice"]
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL
  };
}
