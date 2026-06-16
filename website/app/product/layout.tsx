import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mahsulot",
  description:
    "Original Koreya go'zallik vositasi — tarkibi, narxi va mavjudligi. MUSE BEAUTY, Toshkent bo'ylab yetkazib berish.",
};

export default function ProductLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
