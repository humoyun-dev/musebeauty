"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Category, type Product } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import { Reveal } from "@/components/Reveal";
import { BrandEmblem } from "@/components/BrandEmblem";
import {
  ArrowRight,
  Shield,
  Truck,
  Leaf,
  Heart,
  Sprig,
  Spark,
  Star,
  Quote,
  Check,
} from "@/components/Icons";

const FALLBACK_CATS = [
  "Yuz parvarishi",
  "Niqoblar",
  "Makiyaj",
  "Tozalash",
  "Quyoshdan himoya",
  "Lab parvarishi",
  "Ko'z parvarishi",
];

const HERO_PILLS = ["Yuz parvarishi", "Niqoblar", "Makiyaj", "Quyoshdan himoya", "Lab parvarishi"];

const TILE_BG = [
  "from-rose-200/80 via-rose-100 to-shell", // featured
  "from-rose-50 to-shell",
  "from-shell to-rose-50",
  "from-rose-100/70 to-shell",
  "from-shell to-rose-100/60",
  "from-rose-50 via-shell to-porcelain",
];

const PROMISES = [
  { icon: Shield, title: "100% Original", text: "Koreyadan rasmiy import" },
  { icon: Truck, title: "Tez yetkazish", text: "Toshkent bo'ylab 24 soatda" },
  { icon: Leaf, title: "Sof tarkib", text: "Tabiiy, isbotlangan formula" },
  { icon: Heart, title: "Sevimli brendlar", text: "Keng va saralangan tanlov" },
];

const VALUES = [
  { icon: Shield, title: "100% Original", text: "Faqat rasmiy, asl Koreya mahsulotlari." },
  { icon: Leaf, title: "Sof, mehribon tarkib", text: "Teri uchun sinovdan o'tgan formulalar." },
  { icon: Heart, title: "Keng tanlov", text: "Mashhur K-beauty brendlari bir joyda." },
];

const REVIEWS = [
  { text: "Terim hech qachon bunchalik silliq bo'lmagan. Endi faqat shu yerdan olaman.", name: "Malika", city: "Toshkent" },
  { text: "Buyurtma ertasiga yetib keldi, qadoqlash juda chiroyli. Original ekaniga ishonchim komil.", name: "Dilnoza", city: "Chilonzor" },
  { text: "Maslahatchilar terim turini so'rab, to'g'ri mahsulot tanlashga yordam berishdi.", name: "Sevara", city: "Yunusobod" },
];

export default function Home() {
  const [cats, setCats] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [c, p] = await Promise.all([
          api.categories(),
          api.products({ in_stock: true }),
        ]);
        setCats(c);
        setProducts(p.slice(0, 8));
      } catch {
        /* backend ulanmagan bo'lishi mumkin */
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const catTiles = (
    cats.length
      ? cats.slice(0, 7).map((c) => ({ name: c.name, href: `/catalog/?cat=${c.id}` }))
      : FALLBACK_CATS.map((name) => ({ name, href: "/catalog/" }))
  ).slice(0, 7);

  return (
    <div>
      {/* ───────────────────────── HERO (markazlashgan) ───────────────────────── */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-0 h-[34rem] w-[44rem] -translate-x-1/2 rounded-full bg-rose-100/50 blur-3xl" />
          <div className="absolute -bottom-40 left-1/4 h-[26rem] w-[26rem] rounded-full bg-gold-light/25 blur-3xl" />
        </div>
        {/* burchak botanikasi */}
        <Sprig aria-hidden className="pointer-events-none absolute -left-8 top-16 hidden h-56 w-56 -rotate-[18deg] text-rose-200 lg:block" />
        <Sprig aria-hidden className="pointer-events-none absolute -right-8 top-24 hidden h-48 w-48 rotate-[160deg] text-rose-200 lg:block" />

        <div className="container-page relative flex flex-col items-center py-16 text-center md:py-24 lg:py-28">
          <div className="animate-fade-up" style={{ animationDelay: "40ms" }}>
            <BrandEmblem className="h-20 w-20 shadow-soft" />
          </div>
          <p className="eyebrow mt-7 animate-fade-up justify-center" style={{ animationDelay: "140ms" }}>
            <Spark className="h-3.5 w-3.5" /> Korean Skincare &amp; Beauty
          </p>
          <h1
            className="display mt-5 max-w-4xl animate-fade-up text-[2.9rem] leading-[1.04] sm:text-6xl lg:text-[4.6rem]"
            style={{ animationDelay: "230ms" }}
          >
            Go'zalligingiz —
            <span className="block italic text-rose">bizning ilhomimiz.</span>
          </h1>
          <p
            className="mt-7 max-w-xl animate-fade-up text-[15px] leading-relaxed text-ink-soft sm:text-base"
            style={{ animationDelay: "340ms" }}
          >
            Koreyaning eng sevimli brendlaridan original parvarish, makiyaj va niqoblar —
            hammasi bir joyda. Toshkent bo'ylab tez va ishonchli yetkazib berish.
          </p>
          <div
            className="mt-9 flex animate-fade-up flex-wrap items-center justify-center gap-3"
            style={{ animationDelay: "450ms" }}
          >
            <Link href="/catalog/" className="btn-primary group">
              Mahsulotlarni ko'rish
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link href="/promotions/" className="btn-outline">
              Aksiyalar
            </Link>
          </div>
          <div
            className="mt-10 flex animate-fade-up flex-wrap justify-center gap-2.5"
            style={{ animationDelay: "560ms" }}
          >
            {HERO_PILLS.map((p) => (
              <Link
                key={p}
                href="/catalog/"
                className="rounded-full border border-line bg-shell/70 px-4 py-2 text-xs font-medium text-ink-soft transition-colors hover:border-rose hover:text-rose"
              >
                {p}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ──────────────────── BREND VA'DALARI ──────────────────── */}
      <section className="border-y border-line bg-shell">
        <div className="container-page grid grid-cols-2 divide-line lg:grid-cols-4 lg:divide-x">
          {PROMISES.map(({ icon: Icon, title, text }, i) => (
            <div
              key={title}
              className={`flex items-center gap-4 py-7 lg:px-8 ${
                i < 2 ? "border-b border-line lg:border-b-0" : ""
              } ${i % 2 === 0 ? "pr-4 lg:pr-8" : "pl-4 lg:pl-8"}`}
            >
              <Icon className="h-6 w-6 shrink-0 text-rose" />
              <div>
                <p className="text-sm font-semibold text-ink">{title}</p>
                <p className="text-xs text-ink-soft">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ──────────────────── KATEGORIYALAR — BENTO MOZAIKA ──────────────────── */}
      <section id="categories" className="container-page py-20 lg:py-24">
        <Reveal className="mb-12 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Assortiment</p>
            <h2 className="display mt-4 text-4xl sm:text-5xl">Nimadan boshlaymiz?</h2>
          </div>
          <Link href="/catalog/" className="group link-arrow">
            Barcha mahsulotlar
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Reveal>

        <div className="grid auto-rows-[168px] grid-cols-2 gap-4 sm:gap-5 lg:auto-rows-[210px] lg:grid-cols-4">
          {catTiles.map((c, i) => {
            const featured = i === 0;
            const bg = featured ? TILE_BG[0] : TILE_BG[((i - 1) % (TILE_BG.length - 1)) + 1];
            return (
              <Reveal
                key={c.name + i}
                delay={(i % 4) * 60}
                className={featured ? "col-span-2 row-span-2" : ""}
              >
                <Link
                  href={c.href}
                  className={`group relative flex h-full flex-col justify-end overflow-hidden rounded-lg border border-line bg-gradient-to-br ${bg} p-5 transition-all duration-500 hover:-translate-y-1 hover:shadow-lift sm:p-6`}
                >
                  <Sprig
                    className={`absolute -right-2 -top-2 rotate-12 text-rose-300/60 transition-transform duration-700 group-hover:rotate-3 group-hover:scale-110 ${
                      featured ? "h-36 w-36" : "h-20 w-20"
                    }`}
                  />
                  {featured && (
                    <span className="relative mb-3 inline-flex w-fit items-center gap-1.5 rounded-full bg-rose/15 px-3 py-1 text-[10px] font-semibold uppercase tracking-wider2 text-rose-700">
                      <Spark className="h-3 w-3" /> Eng ommabop
                    </span>
                  )}
                  <h3 className={`relative font-serif text-ink ${featured ? "text-2xl sm:text-4xl" : "text-lg sm:text-xl"}`}>
                    {c.name}
                  </h3>
                  <span className="relative mt-1.5 inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider2 text-rose">
                    Ko'rish
                    <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                  </span>
                </Link>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* ──────────────────── OMMABOP MAHSULOTLAR ──────────────────── */}
      <section className="container-page pb-20 lg:pb-24">
        <Reveal className="mb-12 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Eng ko'p tanlangan</p>
            <h2 className="display mt-4 text-4xl sm:text-5xl">Ommabop mahsulotlar</h2>
          </div>
          <Link href="/catalog/" className="group link-arrow">
            Hammasi
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Reveal>

        {loading ? (
          <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i}>
                <div className="shimmer aspect-[4/5] rounded-md bg-rose-50" />
                <div className="shimmer mt-4 h-4 w-3/4 rounded bg-rose-50" />
                <div className="shimmer mt-2 h-4 w-1/3 rounded bg-rose-50" />
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="rounded-lg border border-dashed border-line bg-shell py-16 text-center">
            <div className="relative mx-auto h-14 w-14 text-rose-300">
              <Sprig className="h-14 w-14" />
              <Spark className="absolute left-[58%] top-[30%] h-3 w-3 text-gold" />
            </div>
            <p className="mt-4 text-ink-soft">Tez orada yangi mahsulotlar qo'shamiz.</p>
            <Link href="/catalog/" className="btn-outline mt-6">
              Katalogga o'tish
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-x-5 gap-y-10 sm:grid-cols-3 lg:grid-cols-4">
            {products.map((p, i) => (
              <Reveal key={p.id} delay={(i % 4) * 70}>
                <ProductCard product={p} />
              </Reveal>
            ))}
          </div>
        )}
      </section>

      {/* ──────────────────── BREND (Glow your muse) ──────────────────── */}
      <section id="brend" className="relative overflow-hidden bg-shell">
        <Sprig aria-hidden className="pointer-events-none absolute -left-10 top-1/2 hidden h-80 w-80 -translate-y-1/2 -rotate-12 text-rose-100 lg:block" />
        <Sprig aria-hidden className="pointer-events-none absolute -right-10 top-10 hidden h-64 w-64 rotate-[150deg] text-rose-100 lg:block" />
        <div className="container-page relative py-20 text-center lg:py-28">
          <Reveal className="mx-auto max-w-2xl">
            <BrandEmblem className="mx-auto h-16 w-16" />
            <p className="eyebrow mt-6 no-rule justify-center">Glow your muse</p>
            <h2 className="display mt-4 text-4xl sm:text-5xl">
              Sof tarkib, <span className="italic text-rose">asl go'zallik</span>
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-ink-soft">
              MUSE BEAUTY — Koreyaning ishonchli go'zallik uylaridan tanlangan original
              mahsulotlar. Har bir formula teringizga g'amxo'rlik bilan tanlangan.
            </p>
          </Reveal>

          <div className="mx-auto mt-14 grid max-w-4xl gap-5 sm:grid-cols-3">
            {VALUES.map(({ icon: Icon, title, text }, i) => (
              <Reveal key={title} delay={i * 90}>
                <div className="h-full rounded-lg border border-line bg-porcelain p-7">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-5 font-serif text-lg text-ink">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink-soft">{text}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ──────────────────── MIJOZLAR FIKRI ──────────────────── */}
      <section className="container-page py-20 lg:py-24">
        <Reveal className="mb-14 text-center">
          <p className="eyebrow no-rule justify-center">Mijozlar fikri</p>
          <h2 className="display mt-4 text-4xl sm:text-5xl">Sevib tanlangan</h2>
        </Reveal>
        <div className="grid gap-6 lg:grid-cols-3">
          {REVIEWS.map((r, i) => (
            <Reveal key={r.name} delay={i * 90}>
              <figure className="flex h-full flex-col rounded-lg border border-line bg-shell p-8">
                <Quote className="h-8 w-8 text-rose-200" />
                <div className="mt-3 flex gap-0.5 text-gold">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star key={j} filled className="h-4 w-4" />
                  ))}
                </div>
                <blockquote className="mt-5 flex-1 text-[15px] leading-relaxed text-ink/90">
                  {r.text}
                </blockquote>
                <figcaption className="mt-6 border-t border-line pt-5 text-sm">
                  <span className="font-semibold text-ink">{r.name}</span>
                  <span className="text-ink-soft"> · {r.city}</span>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ──────────────────── YETKAZISH / CTA ──────────────────── */}
      <section id="delivery" className="container-page pb-20 lg:pb-28">
        <Reveal>
          <div className="grid items-center gap-10 overflow-hidden rounded-lg border border-line bg-gradient-to-br from-rose-50 to-shell p-10 sm:p-14 lg:grid-cols-2">
            <div>
              <p className="eyebrow">Toshkent bo'ylab</p>
              <h2 className="display mt-4 text-3xl sm:text-4xl">Ishonchli va tez yetkazib berish</h2>
              <p className="mt-5 max-w-md text-ink-soft">
                Buyurtmangiz ehtiyotkorlik bilan qadoqlanib, kuryer orqali tez yetkaziladi.
                To'lovni qulay usulda — karta yoki Payme orqali amalga oshiring.
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <span className="chip"><Truck className="h-4 w-4 text-rose" /> Kuryer yetkazish</span>
                <span className="chip"><Shield className="h-4 w-4 text-rose" /> Xavfsiz to'lov</span>
                <span className="chip"><Spark className="h-4 w-4 text-rose" /> Original kafolat</span>
              </div>
            </div>
            <div className="lg:pl-8">
              <Link href="/catalog/" className="btn-primary group w-full sm:w-auto">
                Hoziroq buyurtma berish
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <p className="mt-4 text-sm text-ink-soft">
                Yoki bizning{" "}
                <a href="https://t.me/" className="font-medium text-rose underline-offset-2 hover:underline">
                  Telegram bot
                </a>{" "}
                orqali ham buyurtma berishingiz mumkin.
              </p>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
