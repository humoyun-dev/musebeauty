import type { MetadataRoute } from "next";

export const dynamic = "force-static";

const SITE = "https://musebeauty.uz";
const LAST = "2026-06-17";

export default function sitemap(): MetadataRoute.Sitemap {
  const pages: Array<{
    path: string;
    priority: number;
    freq: "daily" | "weekly" | "monthly";
  }> = [
    { path: "/", priority: 1.0, freq: "daily" },
    { path: "/catalog/", priority: 0.9, freq: "daily" },
    { path: "/promotions/", priority: 0.7, freq: "weekly" },
  ];

  return pages.map((p) => ({
    url: `${SITE}${p.path}`,
    lastModified: LAST,
    changeFrequency: p.freq,
    priority: p.priority,
  }));
}
