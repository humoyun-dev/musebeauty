import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Buyurtma qabul qilindi",
  description: "Buyurtmangiz qabul qilindi — MUSE BEAUTY.",
  robots: { index: false, follow: false },
};

export default function OrderLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
