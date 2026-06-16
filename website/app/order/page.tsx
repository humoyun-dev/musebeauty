"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { type WebOrderResult } from "@/lib/api";
import { money } from "@/lib/format";
import { Check, ArrowRight, Shield } from "@/components/Icons";

export default function OrderPage() {
  const [order, setOrder] = useState<WebOrderResult | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("muse_last_order");
      if (raw) setOrder(JSON.parse(raw));
    } catch {
      /* ignore */
    }
    setLoaded(true);
  }, []);

  if (!loaded) return <p className="container-page py-28 text-center text-ink-soft">Yuklanmoqda…</p>;

  if (!order) {
    return (
      <div className="container-page py-28 text-center">
        <p className="text-ink-soft">Buyurtma topilmadi.</p>
        <Link href="/catalog/" className="btn-primary mt-6">
          Katalogga o'tish
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="container-page py-16 lg:py-24">
      <div className="mx-auto max-w-lg text-center">
        <div className="mx-auto flex h-16 w-16 animate-fade-up items-center justify-center rounded-full bg-rose text-white">
          <Check className="h-8 w-8" />
        </div>
        <p className="eyebrow mt-7 justify-center">Buyurtma qabul qilindi</p>
        <h1 className="display mt-4 text-3xl sm:text-4xl">Rahmat! Buyurtmangiz qabul qilindi</h1>
        <p className="mt-3 text-ink-soft">
          Buyurtma raqami: <span className="font-semibold text-ink">#{order.order_id}</span>
        </p>

        {/* To'lov kartasi */}
        <div className="mt-9 overflow-hidden rounded-lg border border-line bg-shell text-left">
          <div className="border-b border-line bg-rose-50/60 px-7 py-5">
            <p className="text-xs uppercase tracking-wider2 text-ink-mute">To'lov uchun summa</p>
            <p className="mt-1 font-serif text-3xl text-rose">{money(order.total)}</p>
          </div>
          <div className="space-y-4 px-7 py-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink-soft">Karta raqami</span>
              <span className="font-mono text-base font-medium tracking-wider text-ink">
                {order.payment_card_number}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink-soft">Karta egasi</span>
              <span className="text-base text-ink">{order.payment_card_holder}</span>
            </div>
          </div>
        </div>

        {order.payme_url ? (
          <a
            href={order.payme_url}
            className="btn-primary mt-7 w-full"
            target="_blank"
            rel="noreferrer"
          >
            Payme orqali to'lash
            <ArrowRight className="h-4 w-4" />
          </a>
        ) : (
          <p className="mt-7 inline-flex items-start gap-2 rounded-[4px] border border-line bg-shell px-5 py-4 text-left text-sm text-ink-soft">
            <Shield className="mt-0.5 h-5 w-5 shrink-0 text-rose" />
            To'lovni amalga oshiring — operator tez orada siz bilan bog'lanib, buyurtmani
            tasdiqlaydi.
          </p>
        )}

        <Link
          href="/catalog/"
          className="mt-8 inline-flex items-center gap-2 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
        >
          Xaridni davom ettirish
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
