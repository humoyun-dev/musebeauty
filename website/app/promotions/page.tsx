"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Promotions, type PublicDiscount, type PublicPromo } from "@/lib/api";
import { money } from "@/lib/format";
import { Reveal } from "@/components/Reveal";
import { Tag, Copy, Check, Spark, Sprig, ArrowRight } from "@/components/Icons";

function discountLabel(d: PublicDiscount): string {
  const v = d.type === "percent" ? `${Number(d.value)}%` : money(d.value);
  const scope =
    d.scope === "all"
      ? "barcha mahsulotlarga"
      : d.scope === "category"
        ? "tanlangan kategoriyaga"
        : "tanlangan mahsulotga";
  return `${v} chegirma — ${scope}`;
}

function promoLabel(p: PublicPromo): string {
  if (p.type === "free_delivery") return "Bepul yetkazib berish";
  const v = p.type === "percent" ? `${Number(p.value)}%` : money(p.value);
  let s = `${v} chegirma`;
  if (Number(p.min_order_amount) > 0) s += ` · ${money(p.min_order_amount)} dan`;
  if (p.first_order_only) s += " · faqat birinchi buyurtma";
  return s;
}

export default function PromotionsPage() {
  const [data, setData] = useState<Promotions | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    api
      .promotions()
      .then(setData)
      .catch(() => setData({ discounts: [], promo_codes: [] }))
      .finally(() => setLoading(false));
  }, []);

  const copy = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(code);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      /* ignore */
    }
  };

  const empty = !loading && data && data.discounts.length === 0 && data.promo_codes.length === 0;

  return (
    <div className="container-page py-14 lg:py-20">
      {/* Sarlavha */}
      <header className="relative mb-14 overflow-hidden rounded-lg border border-line bg-gradient-to-br from-rose-100 via-porcelain to-shell px-8 py-14 text-center sm:py-16">
        <Sprig
          aria-hidden
          className="pointer-events-none absolute -left-6 top-1/2 hidden h-48 w-48 -translate-y-1/2 -rotate-12 text-rose-200 sm:block"
        />
        <Sprig
          aria-hidden
          className="pointer-events-none absolute -right-6 top-4 hidden h-40 w-40 rotate-[150deg] text-rose-200 sm:block"
        />
        <p className="eyebrow relative justify-center">
          <Spark className="h-4 w-4" /> Maxsus takliflar
        </p>
        <h1 className="display relative mt-4 text-4xl sm:text-5xl">Aksiyalar</h1>
        <p className="relative mt-3 text-ink-soft">Joriy chegirmalar va promokodlar</p>
      </header>

      {loading ? (
        <p className="py-16 text-center text-ink-soft">Yuklanmoqda…</p>
      ) : empty ? (
        <div className="rounded-lg border border-dashed border-line bg-shell py-24 text-center">
          <Tag className="mx-auto h-14 w-14 text-rose-200" />
          <p className="mt-4 text-ink-soft">Hozircha faol aksiya yo'q. Tez orada qaytib keling!</p>
          <Link href="/catalog/" className="btn-outline mt-6">
            Katalogga o'tish
          </Link>
        </div>
      ) : (
        <div className="space-y-16">
          {/* Avtomatik chegirmalar */}
          {data!.discounts.length > 0 && (
            <section>
              <div className="mb-6 flex items-center justify-between">
                <h2 className="display text-2xl sm:text-3xl">Chegirmalar</h2>
                <p className="text-xs text-ink-mute">Avtomatik qo'llanadi</p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                {data!.discounts.map((d, i) => (
                  <Reveal key={d.id} delay={i * 60}>
                    <div className="card flex items-center gap-5 border border-line p-6">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-rose-50 text-rose">
                        <Tag className="h-6 w-6" />
                      </div>
                      <div>
                        <p className="font-medium text-ink">{d.name}</p>
                        <p className="mt-0.5 text-sm text-rose">{discountLabel(d)}</p>
                      </div>
                    </div>
                  </Reveal>
                ))}
              </div>
            </section>
          )}

          {/* Promokodlar */}
          {data!.promo_codes.length > 0 && (
            <section>
              <div className="mb-6 flex items-center justify-between">
                <h2 className="display text-2xl sm:text-3xl">Promokodlar</h2>
                <p className="text-xs text-ink-mute">Buyurtmada kiriting</p>
              </div>
              <div className="grid gap-5 sm:grid-cols-2">
                {data!.promo_codes.map((p, i) => (
                  <Reveal key={p.code} delay={i * 60}>
                    <div className="relative flex items-center justify-between gap-4 overflow-hidden rounded-md border border-dashed border-rose-300 bg-shell p-6">
                      {/* chekka 'ticket' o'yiqlari */}
                      <span className="absolute -left-2.5 top-1/2 h-5 w-5 -translate-y-1/2 rounded-full bg-porcelain" />
                      <span className="absolute -right-2.5 top-1/2 h-5 w-5 -translate-y-1/2 rounded-full bg-porcelain" />
                      <div className="min-w-0">
                        <p className="font-serif text-2xl font-medium tracking-wide text-rose">
                          {p.code}
                        </p>
                        <p className="mt-1 text-sm text-ink-soft">{promoLabel(p)}</p>
                      </div>
                      <button
                        onClick={() => copy(p.code)}
                        className="inline-flex shrink-0 items-center gap-1.5 rounded-[4px] border border-line bg-porcelain px-4 py-2.5 text-sm font-medium text-ink transition-colors hover:border-ink/30"
                      >
                        {copied === p.code ? (
                          <>
                            <Check className="h-4 w-4 text-rose" /> Olindi
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4" /> Nusxa
                          </>
                        )}
                      </button>
                    </div>
                  </Reveal>
                ))}
              </div>
              <p className="mt-4 text-xs text-ink-mute">
                Faqat bitta promokod qo'llanadi — tizim eng foydalisini tanlaydi.
              </p>
            </section>
          )}

          <div className="border-t border-line pt-12 text-center">
            <Link href="/catalog/" className="btn-primary">
              Xaridni boshlash
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
