import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Buyurtma berish",
  description: "Buyurtmangizni rasmiylashtiring — MUSE BEAUTY, Toshkent bo'ylab yetkazib berish.",
  robots: { index: false, follow: false },
};

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
