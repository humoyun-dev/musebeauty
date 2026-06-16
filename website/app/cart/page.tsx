"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Product } from "@/lib/api";
import { useCart } from "@/lib/cart";
import { money } from "@/lib/format";
import { Plus, Minus, Close, Bag, ArrowRight, Sprig } from "@/components/Icons";

export default function CartPage() {
  const { items, setQty, remove, ready, count } = useCart();
  const [products, setProducts] = useState<Record<number, Product>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ready) return;
    const ids = Object.keys(items).map(Number);
    if (ids.length === 0) {
      setProducts({});
      setLoading(false);
      return;
    }
    setLoading(true);
    Promise.all(ids.map((id) => api.product(id).catch(() => null)))
      .then((list) => {
        const map: Record<number, Product> = {};
        list.forEach((p) => {
          if (p) map[p.id] = p;
        });
        setProducts(map);
      })
      .finally(() => setLoading(false));
  }, [items, ready]);

  const lines = Object.entries(items)
    .map(([id, qty]) => ({ product: products[Number(id)], qty }))
    .filter((l) => l.product);
  const subtotal = lines.reduce((s, l) => s + Number(l.product!.price) * l.qty, 0);

  if (!ready || loading)
    return <p className="container-page py-28 text-center text-ink-soft">Yuklanmoqda…</p>;

  if (count === 0) {
    return (
      <div className="container-page py-28 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border border-line bg-shell text-ink/40">
          <Bag className="h-8 w-8" />
        </div>
        <h1 className="display mt-6 text-3xl">Savatingiz bo'sh</h1>
        <p className="mt-3 text-ink-soft">Go'zallik marosimini boshlash uchun mahsulot tanlang.</p>
        <Link href="/catalog/" className="btn-primary mt-8">
          Xaridni boshlash
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="container-page py-14 lg:py-20">
      <header className="mb-10 border-b border-line pb-8">
        <p className="eyebrow">{count} ta mahsulot</p>
        <h1 className="display mt-4 text-4xl sm:text-5xl">Savat</h1>
      </header>

      <div className="grid gap-10 lg:grid-cols-[1fr_360px]">
        {/* Qatorlar */}
        <div className="divide-y divide-line border-y border-line">
          {lines.map(({ product, qty }) => (
            <div key={product!.id} className="flex items-center gap-4 py-5 sm:gap-6">
              <Link
                href={`/product/?id=${product!.id}`}
                className="h-24 w-20 shrink-0 overflow-hidden rounded-md border border-line bg-gradient-to-br from-rose-50 to-shell"
              >
                {product!.image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={product!.image_url} alt="" className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-rose-300">
                    <Sprig className="h-8 w-8" />
                  </div>
                )}
              </Link>

              <div className="min-w-0 flex-1">
                <Link
                  href={`/product/?id=${product!.id}`}
                  className="line-clamp-2 text-sm font-medium text-ink transition-colors hover:text-rose sm:text-[15px]"
                >
                  {product!.name}
                </Link>
                <p className="mt-1 font-serif text-lg text-rose">{money(product!.price)}</p>

                <div className="mt-3 flex items-center gap-4">
                  <div className="flex items-center rounded-[4px] border border-line">
                    <button
                      className="flex h-9 w-9 items-center justify-center text-ink-soft hover:text-ink"
                      onClick={() => setQty(product!.id, qty - 1)}
                      aria-label="Kamaytirish"
                    >
                      <Minus className="h-3.5 w-3.5" />
                    </button>
                    <span className="w-8 text-center text-sm">{qty}</span>
                    <button
                      className="flex h-9 w-9 items-center justify-center text-ink-soft hover:text-ink"
                      onClick={() => setQty(product!.id, Math.min(product!.stock_qty, qty + 1))}
                      aria-label="Ko'paytirish"
                    >
                      <Plus className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <button
                    className="inline-flex items-center gap-1.5 text-xs text-ink-mute transition-colors hover:text-rose"
                    onClick={() => remove(product!.id)}
                  >
                    <Close className="h-3.5 w-3.5" /> O'chirish
                  </button>
                </div>
              </div>

              <p className="hidden shrink-0 font-serif text-lg text-ink sm:block">
                {money(Number(product!.price) * qty)}
              </p>
            </div>
          ))}
        </div>

        {/* Xulosa */}
        <div className="h-fit lg:sticky lg:top-28">
          <div className="card border border-line p-7">
            <h2 className="font-serif text-xl text-ink">Buyurtma xulosasi</h2>
            <div className="mt-5 flex justify-between text-sm text-ink-soft">
              <span>Mahsulotlar ({count})</span>
              <span className="text-ink">{money(subtotal)}</span>
            </div>
            <p className="mt-4 border-t border-line pt-4 text-xs text-ink-mute">
              Chegirma va yetkazib berish to'lovi keyingi qadamda hisoblanadi.
            </p>
            <Link href="/checkout/" className="btn-primary mt-6 w-full">
              Buyurtma berish
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/catalog/"
              className="mt-3 block text-center text-sm text-ink-soft transition-colors hover:text-ink"
            >
              Xaridni davom ettirish
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
