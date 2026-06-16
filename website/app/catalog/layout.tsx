import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Katalog — barcha go'zallik vositalari",
  description:
    "Koreadan original parvarish, makiyaj, niqob va go'zallik vositalari katalogi. Kategoriya bo'yicha tanlang — Toshkent bo'ylab yetkazib berish.",
  alternates: { canonical: "/catalog/" },
};

export default function CatalogLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
