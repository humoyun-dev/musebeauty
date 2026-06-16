import type { MetadataRoute } from "next";

export const dynamic = "force-static";

const SITE = "https://musebeauty.uz";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/cart/", "/checkout/", "/order/"],
    },
    sitemap: `${SITE}/sitemap.xml`,
    host: SITE,
  };
}
