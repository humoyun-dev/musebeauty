import "./globals.css";
import type { Metadata } from "next";
import { CartProvider } from "@/lib/cart";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

const SITE = "https://musebeauty.uz";
const DESC =
  "Koreadan keltirilgan original parvarish, makiyaj va go'zallik vositalari. K-beauty mahsulotlari — Toshkent bo'ylab tez va ishonchli yetkazib berish.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: {
    default: "MUSE BEAUTY — Koreya go'zallik vositalari · Toshkent",
    template: "%s · MUSE BEAUTY",
  },
  description: DESC,
  applicationName: "MUSE BEAUTY",
  category: "shopping",
  keywords: [
    "MUSE BEAUTY",
    "Koreya kosmetika",
    "K-beauty",
    "Korean skincare",
    "go'zallik vositalari",
    "parvarish",
    "makiyaj",
    "niqob",
    "yuz parvarishi",
    "original kosmetika Toshkent",
    "kosmetika yetkazib berish",
  ],
  authors: [{ name: "MUSE BEAUTY" }],
  creator: "MUSE BEAUTY",
  publisher: "MUSE BEAUTY",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "uz_UZ",
    url: SITE,
    siteName: "MUSE BEAUTY",
    title: "MUSE BEAUTY — Koreya go'zallik vositalari",
    description: DESC,
  },
  twitter: {
    card: "summary_large_image",
    title: "MUSE BEAUTY — Koreya go'zallik vositalari",
    description: DESC,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Store",
      "@id": `${SITE}/#store`,
      name: "MUSE BEAUTY",
      alternateName: "MUSE BEAUTY — Korean Skincare & Beauty",
      image: `${SITE}/logo.jpg`,
      logo: `${SITE}/logo.jpg`,
      url: SITE,
      description: DESC,
      slogan: "Glow your muse",
      address: {
        "@type": "PostalAddress",
        addressLocality: "Toshkent",
        addressCountry: "UZ",
      },
      areaServed: { "@type": "City", name: "Toshkent" },
      sameAs: ["https://t.me/", "https://instagram.com/"],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE}/#website`,
      url: SITE,
      name: "MUSE BEAUTY",
      inLanguage: "uz",
      publisher: { "@id": `${SITE}/#store` },
      potentialAction: {
        "@type": "SearchAction",
        target: `${SITE}/catalog/?q={search_term_string}`,
        "query-input": "required name=search_term_string",
      },
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..500&family=Hanken+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <meta name="theme-color" content="#F8EEE9" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>
        <CartProvider>
          <Header />
          <main className="min-h-[70vh]">{children}</main>
          <Footer />
        </CartProvider>

        {/* Atmosfera uchun yengil film-grain qatlami */}
        <div
          aria-hidden="true"
          className="grain-overlay pointer-events-none fixed inset-0 z-[60] opacity-[0.04] mix-blend-multiply"
        />
      </body>
    </html>
  );
}
