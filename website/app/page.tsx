"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Category, type Product } from "@/lib/api";
import { ProductCard } from "@/components/ProductCard";
import { Reveal } from "@/components/Reveal";
import {
  ArrowRight,
  Shield,
  Truck,
  Leaf,
  Chat,
  Spark,
  Sprig,
  Star,
  Quote,
  Check,
  Heart,
} from "@/components/Icons";

const FALLBACK_CATS = [
  "Yuz parvarishi",
  "Niqoblar",
  "Makiyaj",
  "Tozalash",
  "Quyoshdan himoya",
  "Lab parvarishi",
  "Ko'z parvarishi",
  "To'plamlar",
];

const PROMISES = [
  { icon: Shield, title: "Original kafolati", text: "Koreyadan rasmiy mahsulot" },
  { icon: Truck, title: "Tez yetkazish", text: "Toshkent bo'ylab 24 soatda" },
  { icon: Leaf, title: "Sof tarkib", text: "Tabiiy, isbotlangan formula" },
  { icon: Chat, title: "Qo'llab-quvvatlash", text: "Telegram orqali maslahat" },
];

const VALUES = [
  {
    icon: Shield,
    title: "100% Original",
    text: "Faqat rasmiy import qilingan, asl Koreya mahsulotlari.",
  },
  {
    icon: Leaf,
    title: "Sof, isbotlangan tarkib",
    text: "Teri uchun mehribon, sinovdan o'tgan formulalar.",
  },
  {
    icon: Heart,
    title: "Sevimli K-beauty brendlar",
    text: "Mashhur va yangi brendlardan keng tanlov — bir joyda.",
  },
];

const REVIEWS = [
  {
    text: "Terim hech qachon bunchalik silliq bo'lmagan. Mahsulotlar haqiqatan ham ishlaydi — endi faqat shu yerdan olaman.",
    name: "Malika",
    city: "Toshkent",
  },
  {
    text: "Buyurtma ertasiga yetib keldi, qadoqlash juda chiroyli. Original ekanligiga ishonchim komil.",
    name: "Dilnoza",
    city: "Chilonzor",
  },
  {
    text: "Maslahatchilar terim turini so'rab, to'g'ri mahsulot tanlashga yordam berishdi. Bunday e'tibor kamdan-kam.",
    name: "Sevara",
    city: "Yunusobod",
  },
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

  const catTiles = cats.length
    ? cats.slice(0, 8).map((c) => ({ name: c.name, href: `/catalog/?cat=${c.id}` }))
    : FALLBACK_CATS.map((name) => ({ name, href: "/catalog/" }));

  return (
    <div>
      {/* ───────────────────────── HERO ───────────────────────── */}
      <section className="relative overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <div className="absolute -right-24 -top-32 h-[30rem] w-[30rem] rounded-full bg-rose-200/40 blur-3xl" />
          <div className="absolute -bottom-32 left-1/4 h-[26rem] w-[26rem] rounded-full bg-gold-light/30 blur-3xl" />
        </div>

        <div className="container-page relative grid items-center gap-12 py-14 md:grid-cols-2 md:py-20 lg:py-24">
          {/* Matn */}
          <div className="max-w-xl">
            <p className="eyebrow animate-fade-up" style={{ animationDelay: "60ms" }}>
              <Spark className="h-3.5 w-3.5" /> Korean Skincare &amp; Beauty
            </p>
            <h1
              className="display mt-6 animate-fade-up text-[2.7rem] leading-[1.05] sm:text-5xl lg:text-[3.9rem]"
              style={{ animationDelay: "150ms" }}
            >
              Koreyacha go'zallik,
              <span className="block italic text-rose">har kuningizda.</span>
            </h1>
            <p
              className="mt-6 max-w-md animate-fade-up text-[15px] leading-relaxed text-ink-soft sm:text-base"
              style={{ animationDelay: "260ms" }}
            >
              Parvarish, makiyaj, niqob va yana ko'plab original K-beauty mahsulotlari —
              hammasi bir joyda. Toshkent bo'ylab tez va ishonchli yetkazib berish.
            </p>
            <div
              className="mt-8 flex animate-fade-up flex-wrap items-center gap-3"
              style={{ animationDelay: "370ms" }}
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
              className="mt-8 flex animate-fade-up flex-wrap items-center gap-x-6 gap-y-2 text-[13px] text-ink-soft"
              style={{ animationDelay: "480ms" }}
            >
              {["100% Original", "Tez yetkazish", "Qulay narx"].map((t) => (
                <span key={t} className="inline-flex items-center gap-2">
                  <Check className="h-4 w-4 text-rose" /> {t}
                </span>
              ))}
            </div>
          </div>

          {/* Vizual — brend emblemi + botanika + kategoriya chiplari */}
          <div
            className="relative mx-auto hidden aspect-square w-full max-w-md animate-fade-in md:block"
            style={{ animationDelay: "250ms" }}
          >
            <Sprig
              aria-hidden
              className="absolute -left-4 top-4 h-44 w-44 -rotate-12 origin-bottom animate-sway text-rose-200"
            />
            <Sprig
              aria-hidden
              className="absolute -right-2 bottom-2 h-36 w-36 rotate-[165deg] origin-top animate-sway text-rose-200"
              style={{ animationDelay: "1.5s" }}
            />

            <div className="absolute inset-8 overflow-hidden rounded-full bg-shell shadow-lift ring-1 ring-rose-200/70">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/logo.jpg"
                alt="MUSE BEAUTY — Korean Skincare & Beauty"
                className="h-full w-full scale-[1.04] object-cover"
              />
            </div>

            <div
              className="absolute left-0 top-14 animate-float rounded-full border border-line bg-shell/90 px-4 py-2 text-xs font-medium text-ink shadow-soft backdrop-blur"
              style={{ animationDelay: "0.3s" }}
            >
              Parvarish
            </div>
            <div
              className="absolute -right-1 top-1/3 animate-float rounded-full border border-line bg-shell/90 px-4 py-2 text-xs font-medium text-ink shadow-soft backdrop-blur"
              style={{ animationDelay: "1.0s" }}
            >
              Makiyaj
            </div>
            <div
              className="absolute bottom-10 left-6 animate-float rounded-full border border-line bg-shell/90 px-4 py-2 text-xs font-medium text-ink shadow-soft backdrop-blur"
              style={{ animationDelay: "0.7s" }}
            >
              Niqoblar
            </div>
            <Spark className="absolute right-10 top-8 h-5 w-5 text-gold" />
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

      {/* ──────────────────── KATEGORIYALAR (assortiment) ──────────────────── */}
      <section id="categories" className="container-page py-20 lg:py-24">
        <Reveal className="mb-12 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Assortiment</p>
            <h2 className="display mt-4 text-4xl sm:text-5xl">Har xil ehtiyoj uchun</h2>
          </div>
          <Link href="/catalog/" className="group link-arrow">
            Barcha mahsulotlar
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Reveal>

        <div className="grid grid-cols-2 gap-4 sm:gap-5 lg:grid-cols-4">
          {catTiles.map((c, i) => (
            <Reveal key={c.name + i} delay={(i % 4) * 70}>
              <Link
                href={c.href}
                className="group relative flex h-40 flex-col justify-end overflow-hidden rounded-md border border-line bg-gradient-to-br from-rose-50 via-shell to-porcelain p-5 transition-all duration-500 hover:-translate-y-1 hover:shadow-lift"
              >
                <Sprig className="absolute -right-3 -top-3 h-24 w-24 rotate-12 text-rose-200/70 transition-transform duration-500 group-hover:rotate-6" />
                <h3 className="relative font-serif text-lg text-ink sm:text-xl">{c.name}</h3>
                <span className="relative mt-1.5 inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider2 text-rose">
                  Ko'rish
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            </Reveal>
          ))}
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
          <div className="rounded-md border border-dashed border-line bg-shell py-16 text-center">
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

      {/* ──────────────────── BREND (Glow your muse) — yengil ──────────────────── */}
      <section id="brend" className="relative overflow-hidden bg-shell">
        <Sprig
          aria-hidden
          className="pointer-events-none absolute -left-10 top-1/2 hidden h-80 w-80 -translate-y-1/2 -rotate-12 text-rose-100 lg:block"
        />
        <Sprig
          aria-hidden
          className="pointer-events-none absolute -right-10 top-10 hidden h-64 w-64 rotate-[150deg] text-rose-100 lg:block"
        />
        <div className="container-page relative py-20 lg:py-28">
          <Reveal className="mx-auto max-w-2xl text-center">
            <p className="eyebrow no-rule justify-center">Glow your muse</p>
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
                <div className="h-full rounded-md border border-line bg-porcelain p-7 text-center">
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose">
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="mt-5 font-serif text-lg text-ink">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-ink-soft">{text}</p>
                </div>
              </Reveal>
            ))}
          </div>

          <Reveal className="mt-12 text-center">
            <Link href="/catalog/" className="btn-primary group">
              Kolleksiyani ko'rish
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Reveal>
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
              <figure className="flex h-full flex-col rounded-md border border-line bg-shell p-8">
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

      {/* ──────────────────── YETKAZISH / NEWSLETTER ──────────────────── */}
      <section id="delivery" className="container-page pb-20 lg:pb-28">
        <Reveal>
          <div className="grid items-center gap-10 overflow-hidden rounded-lg border border-line bg-gradient-to-br from-rose-50 to-shell p-10 sm:p-14 lg:grid-cols-2">
            <div>
              <p className="eyebrow">Toshkent bo'ylab</p>
              <h2 className="display mt-4 text-3xl sm:text-4xl">
                Ishonchli va tez yetkazib berish
              </h2>
              <p className="mt-5 max-w-md text-ink-soft">
                Buyurtmangiz ehtiyotkorlik bilan qadoqlanib, kuryer orqali tez
                yetkaziladi. To'lovni qulay usulda — karta yoki Payme orqali amalga
                oshiring.
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
