"use client";

import { useEffect, useState } from "react";
import { api, type Category, type Product } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import { Reveal } from "@/components/Reveal";
import { useQueryParam } from "@/lib/useQuery";
import { Search, Sprig } from "@/components/Icons";

export default function CatalogPage() {
  const catParam = useQueryParam("cat");
  const [cats, setCats] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [active, setActive] = useState<number | null>(null);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (catParam) setActive(Number(catParam));
  }, [catParam]);

  useEffect(() => {
    api.categories().then(setCats).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .products({ category_id: active ?? undefined, q: q || undefined })
      .then(setProducts)
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, [active, q]);

  const activeName = active ? cats.find((c) => c.id === active)?.name : null;

  return (
    <div className="container-page py-14 lg:py-20">
      {/* Sarlavha */}
      <header className="mb-10 border-b border-line pb-10">
        <p className="eyebrow">Kolleksiya</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
          <h1 className="display text-4xl sm:text-5xl">{activeName ?? "Katalog"}</h1>
          {!loading && (
            <p className="text-sm text-ink-soft">
              {products.length} ta mahsulot
            </p>
          )}
        </div>
      </header>

      <div className="grid gap-10 lg:grid-cols-[230px_1fr]">
        {/* Yon panel */}
        <aside className="lg:sticky lg:top-28 lg:h-fit">
          <div className="relative mb-8">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-ink-mute" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Mahsulot qidirish…"
              className="input pl-11"
            />
          </div>

          <p className="mb-3 text-[11px] font-semibold uppercase tracking-eyebrow text-ink-mute">
            Kategoriyalar
          </p>
          {/* Mobil: gorizontal chiplar / Desktop: ro'yxat */}
          <div className="flex flex-wrap gap-2 lg:flex-col lg:gap-1">
            <FilterItem active={active === null} onClick={() => setActive(null)}>
              Barchasi
            </FilterItem>
            {cats.map((c) => (
              <FilterItem key={c.id} active={active === c.id} onClick={() => setActive(c.id)}>
                {c.name}
              </FilterItem>
            ))}
          </div>
        </aside>

        {/* Mahsulotlar */}
        <div>
          {loading ? (
            <div className="grid grid-cols-2 gap-x-5 gap-y-10 sm:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i}>
                  <div className="shimmer aspect-[4/5] rounded-md bg-rose-50" />
                  <div className="shimmer mt-4 h-4 w-3/4 rounded bg-rose-50" />
                  <div className="shimmer mt-2 h-4 w-1/3 rounded bg-rose-50" />
                </div>
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="rounded-md border border-dashed border-line bg-shell py-24 text-center">
              <Sprig className="mx-auto h-14 w-14 text-rose-200" />
              <p className="mt-4 text-ink-soft">Mahsulot topilmadi.</p>
              {(q || active) && (
                <button
                  onClick={() => {
                    setQ("");
                    setActive(null);
                  }}
                  className="btn-outline mt-6"
                >
                  Filtrlarni tozalash
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-x-5 gap-y-10 sm:grid-cols-3">
              {products.map((p, i) => (
                <Reveal key={p.id} delay={(i % 3) * 60}>
                  <ProductCard product={p} />
                </Reveal>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FilterItem({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-[4px] px-4 py-2.5 text-left text-sm font-medium transition-colors lg:w-full ${
        active
          ? "bg-ink text-porcelain"
          : "border border-line bg-shell text-ink-soft hover:border-ink/30 hover:text-ink lg:border-transparent lg:bg-transparent"
      }`}
    >
      {children}
    </button>
  );
}
