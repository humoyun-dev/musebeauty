"use client";

import { useState } from "react";
import Link from "next/link";
import { useCart } from "@/lib/cart";
import { money } from "@/lib/format";
import type { Product } from "@/lib/api";
import { Heart, Plus, Check, Sprig, Spark } from "@/components/Icons";

export function ProductCard({ product }: { product: Product }) {
  const { add } = useCart();
  const out = product.stock_qty <= 0;
  const [fav, setFav] = useState(false);
  const [added, setAdded] = useState(false);

  const onAdd = () => {
    add(product.id, 1);
    setAdded(true);
    setTimeout(() => setAdded(false), 1400);
  };

  return (
    <article className="group relative flex flex-col">
      <div className="relative overflow-hidden rounded-md border border-line bg-gradient-to-br from-rose-50 to-shell">
        <Link href={`/product/?id=${product.id}`} className="block aspect-[4/5]">
          {product.image_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={product.image_url}
              alt={product.name}
              loading="lazy"
              className="h-full w-full object-cover transition-transform duration-[1.2s] ease-out group-hover:scale-105"
            />
          ) : (
            <div className="relative flex h-full w-full items-center justify-center text-rose-300">
              <Sprig className="h-16 w-16 transition-transform duration-700 group-hover:scale-110" />
              <Spark className="absolute left-[58%] top-[32%] h-3.5 w-3.5 text-gold" />
            </div>
          )}
        </Link>

        {/* Sevimlilar */}
        <button
          onClick={() => setFav((v) => !v)}
          aria-label="Sevimlilarga qo'shish"
          className={`absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full backdrop-blur-md transition-all ${
            fav
              ? "bg-rose text-white"
              : "bg-shell/80 text-ink/60 hover:text-rose"
          }`}
        >
          <Heart filled={fav} className="h-4 w-4" />
        </button>

        {out && (
          <span className="absolute left-3 top-3 rounded-[3px] bg-ink/85 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-porcelain">
            Tugadi
          </span>
        )}

        {/* Savatga — desktopда hoverда ko'tariladi */}
        <div className="absolute inset-x-3 bottom-3 hidden translate-y-3 opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100 sm:block">
          <button
            onClick={onAdd}
            disabled={out}
            className="w-full rounded-[4px] bg-ink/90 py-3 text-xs font-medium uppercase tracking-wider2 text-porcelain backdrop-blur-md transition-colors hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {out ? "Tugagan" : added ? "✓ Qo'shildi" : "Savatga qo'shish"}
          </button>
        </div>
      </div>

      {/* Matn */}
      <div className="flex flex-1 flex-col pt-4">
        <Link href={`/product/?id=${product.id}`}>
          <h3 className="line-clamp-2 min-h-[2.6rem] text-[14px] leading-snug text-ink transition-colors hover:text-rose">
            {product.name}
          </h3>
        </Link>
        <div className="mt-2 flex items-center justify-between gap-3">
          <span className="font-serif text-lg text-ink">{money(product.price)}</span>
          {/* Mobil uchun doimiy tugma */}
          <button
            onClick={onAdd}
            disabled={out}
            aria-label="Savatga qo'shish"
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-ink/20 text-ink transition-all hover:border-ink hover:bg-ink hover:text-porcelain disabled:cursor-not-allowed disabled:opacity-40 sm:hidden"
          >
            {added ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </article>
  );
}
