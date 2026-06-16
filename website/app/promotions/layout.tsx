import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Aksiyalar va chegirmalar",
  description:
    "MUSE BEAUTY joriy chegirmalari va promokodlari. Sevimli K-beauty mahsulotlaringizga maxsus takliflar bilan tejab xarid qiling.",
  alternates: { canonical: "/promotions/" },
};

export default function PromotionsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
