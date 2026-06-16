"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Product } from "@/lib/api";
import { useCart } from "@/lib/cart";
import { useQueryParam } from "@/lib/useQuery";
import { money } from "@/lib/format";
import {
  ArrowLeft,
  Plus,
  Minus,
  Check,
  Shield,
  Truck,
  Chat,
  Sprig,
} from "@/components/Icons";

export default function ProductPage() {
  const idParam = useQueryParam("id");
  const { add } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [qty, setQty] = useState(1);
  const [loading, setLoading] = useState(true);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!idParam) return;
    setLoading(true);
    api
      .product(Number(idParam))
      .then(setProduct)
      .catch(() => setProduct(null))
      .finally(() => setLoading(false));
  }, [idParam]);

  if (loading)
    return (
      <div className="container-page grid gap-12 py-14 md:grid-cols-2 lg:py-20">
        <div className="shimmer aspect-[4/5] rounded-lg bg-rose-50" />
        <div className="space-y-5 py-6">
          <div className="shimmer h-9 w-3/4 rounded bg-rose-50" />
          <div className="shimmer h-7 w-1/3 rounded bg-rose-50" />
          <div className="shimmer h-24 w-full rounded bg-rose-50" />
          <div className="shimmer h-14 w-full rounded bg-rose-50" />
        </div>
      </div>
    );

  if (!product)
    return (
      <div className="container-page py-28 text-center">
        <Sprig className="mx-auto h-16 w-16 text-rose-200" />
        <p className="mt-4 text-ink-soft">Mahsulot topilmadi.</p>
        <Link href="/catalog/" className="btn-outline mt-6">
          <ArrowLeft className="h-4 w-4" /> Katalogga qaytish
        </Link>
      </div>
    );

  const out = product.stock_qty <= 0;

  return (
    <div className="container-page py-10 lg:py-16">
      <nav className="mb-8 flex items-center gap-2 text-sm text-ink-soft">
        <Link href="/catalog/" className="transition-colors hover:text-ink">
          Katalog
        </Link>
        <span className="text-line">/</span>
        <span className="truncate text-ink">{product.name}</span>
      </nav>

      <div className="grid gap-10 md:grid-cols-2 lg:gap-16">
        {/* Rasm */}
        <div className="md:sticky md:top-28 md:h-fit">
          <div className="relative aspect-[4/5] overflow-hidden rounded-lg border border-line bg-gradient-to-br from-rose-50 to-shell">
            {product.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={product.image_url}
                alt={product.name}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-rose-300">
                <Sprig className="h-28 w-28" />
              </div>
            )}
            {out && (
              <span className="absolute left-4 top-4 rounded-[3px] bg-ink/85 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-porcelain">
                Tugadi
              </span>
            )}
          </div>
        </div>

        {/* Ma'lumot */}
        <div className="py-2">
          <p className="eyebrow">Koreya · Original</p>
          <h1 className="display mt-4 text-3xl sm:text-4xl lg:text-[2.6rem]">{product.name}</h1>
          <p className="mt-5 font-serif text-3xl text-rose">{money(product.price)}</p>

          <p
            className={`mt-4 inline-flex items-center gap-2 text-sm ${
              out ? "text-ink-soft" : "text-rose"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${out ? "bg-ink-mute" : "bg-rose"}`}
            />
            {out ? "Hozircha tugagan" : `Mavjud — ${product.stock_qty} dona`}
          </p>

          {product.description && (
            <p className="mt-6 max-w-prose leading-relaxed text-ink-soft">
              {product.description}
            </p>
          )}

          {!out && (
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <div className="flex items-center rounded-[4px] border border-line bg-shell">
                <button
                  className="flex h-12 w-12 items-center justify-center text-ink-soft transition-colors hover:text-ink"
                  onClick={() => setQty((q) => Math.max(1, q - 1))}
                  aria-label="Kamaytirish"
                >
                  <Minus className="h-4 w-4" />
                </button>
                <span className="w-10 text-center font-medium">{qty}</span>
                <button
                  className="flex h-12 w-12 items-center justify-center text-ink-soft transition-colors hover:text-ink"
                  onClick={() => setQty((q) => Math.min(product.stock_qty, q + 1))}
                  aria-label="Ko'paytirish"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
              <button
                className="btn-primary flex-1"
                onClick={() => {
                  add(product.id, qty);
                  setAdded(true);
                  setTimeout(() => setAdded(false), 2000);
                }}
              >
                {added ? (
                  <>
                    <Check className="h-4 w-4" /> Savatga qo'shildi
                  </>
                ) : (
                  "Savatga qo'shish"
                )}
              </button>
            </div>
          )}

          <Link
            href="/cart/"
            className="mt-4 inline-flex text-sm font-medium text-rose hover:underline"
          >
            Savatga o'tish →
          </Link>

          {/* Ishonch belgilari */}
          <ul className="mt-10 space-y-4 border-t border-line pt-8">
            {[
              { icon: Shield, t: "Original kafolati", d: "Koreyadan rasmiy import qilingan" },
              { icon: Truck, t: "Tez yetkazib berish", d: "Toshkent bo'ylab 24 soat ichida" },
              { icon: Chat, t: "Maslahat", d: "Telegram orqali bepul yordam" },
            ].map(({ icon: Icon, t, d }) => (
              <li key={t} className="flex items-start gap-4">
                <Icon className="mt-0.5 h-5 w-5 shrink-0 text-rose" />
                <div>
                  <p className="text-sm font-medium text-ink">{t}</p>
                  <p className="text-sm text-ink-soft">{d}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
