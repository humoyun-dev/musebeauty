"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Telegram, Instagram, Check, Spark, Sprig } from "@/components/Icons";

const COLUMNS = [
  {
    title: "Do'kon",
    links: [
      { label: "Barcha mahsulotlar", href: "/catalog/" },
      { label: "Yangi kelganlar", href: "/catalog/" },
      { label: "Aksiyalar", href: "/promotions/" },
      { label: "Kategoriyalar", href: "/#categories" },
    ],
  },
  {
    title: "Yordam",
    links: [
      { label: "Yetkazib berish", href: "/#delivery" },
      { label: "To'lov usullari", href: "/#delivery" },
      { label: "Original kafolati", href: "/#brend" },
      { label: "Savat", href: "/cart/" },
    ],
  },
];

function Newsletter() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (email.includes("@")) setDone(true);
      }}
      className="mt-6"
    >
      {done ? (
        <p className="inline-flex items-center gap-2 text-sm text-gold-light">
          <Check className="h-4 w-4" />
          Rahmat! Tez orada yangiliklar yuboramiz.
        </p>
      ) : (
        <div className="flex max-w-sm items-center gap-0 border-b border-porcelain/25 focus-within:border-gold-light">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email manzilingiz"
            className="w-full bg-transparent py-3 text-sm text-porcelain placeholder:text-porcelain/40 outline-none"
          />
          <button
            type="submit"
            aria-label="Obuna bo'lish"
            className="shrink-0 p-2 text-porcelain/70 transition-colors hover:text-gold-light"
          >
            <ArrowRight />
          </button>
        </div>
      )}
    </form>
  );
}

export function Footer() {
  return (
    <footer className="relative mt-28 overflow-hidden bg-ink text-porcelain">
      {/* nozik issiq nur + botanik vodaznak */}
      <div
        aria-hidden
        className="pointer-events-none absolute -left-40 top-0 h-96 w-96 rounded-full bg-rose-500/15 blur-3xl"
      />
      <Sprig
        aria-hidden
        className="pointer-events-none absolute -right-4 bottom-8 hidden h-72 w-72 rotate-12 text-porcelain/[0.05] lg:block"
      />
      <div className="container-page relative grid gap-12 py-16 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr] lg:py-20">
        {/* Brend */}
        <div>
          <div className="flex items-center gap-3.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.jpg"
              alt="MUSE BEAUTY logotipi"
              className="h-14 w-14 shrink-0 rounded-full object-cover ring-1 ring-porcelain/20"
            />
            <div>
              <Link
                href="/"
                className="inline-flex items-start font-serif text-2xl font-medium uppercase leading-none tracking-[0.28em]"
              >
                Muse<span className="text-rose-300">Beauty</span>
                <Spark className="ml-1 mt-1 h-2.5 w-2.5 text-gold-light" />
              </Link>
              <p className="mt-2 text-[10px] font-semibold uppercase tracking-eyebrow text-gold-light">
                Glow your muse
              </p>
            </div>
          </div>
          <p className="mt-5 max-w-xs text-sm leading-relaxed text-porcelain/60">
            Koreadan original parvarish, makiyaj va go'zallik vositalari — keng tanlov,
            Toshkent bo'ylab ishonch bilan yetkaziladi.
          </p>
          <div className="mt-6 flex items-center gap-3">
            <a
              href="https://t.me/"
              target="_blank"
              rel="noreferrer"
              aria-label="Telegram"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-porcelain/20 text-porcelain/80 transition-colors hover:border-gold-light hover:text-gold-light"
            >
              <Telegram className="h-[18px] w-[18px]" />
            </a>
            <a
              href="https://instagram.com/"
              target="_blank"
              rel="noreferrer"
              aria-label="Instagram"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-porcelain/20 text-porcelain/80 transition-colors hover:border-gold-light hover:text-gold-light"
            >
              <Instagram className="h-[18px] w-[18px]" />
            </a>
          </div>
        </div>

        {/* Havolalar */}
        {COLUMNS.map((col) => (
          <div key={col.title}>
            <h3 className="text-[11px] font-semibold uppercase tracking-eyebrow text-gold-light">
              {col.title}
            </h3>
            <ul className="mt-5 space-y-3">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link
                    href={l.href}
                    className="text-sm text-porcelain/65 transition-colors hover:text-porcelain"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}

        {/* Newsletter */}
        <div>
          <h3 className="text-[11px] font-semibold uppercase tracking-eyebrow text-gold-light">
            Go'zallik xati
          </h3>
          <p className="mt-5 text-sm leading-relaxed text-porcelain/60">
            Yangi mahsulotlar, marosim maslahatlari va maxsus takliflardan birinchi
            bo'lib xabardor bo'ling.
          </p>
          <Newsletter />
        </div>
      </div>

      {/* Pastki chiziq */}
      <div className="border-t border-porcelain/10">
        <div className="container-page flex flex-col items-center justify-between gap-4 py-6 text-xs text-porcelain/50 sm:flex-row">
          <p>© 2026 MUSE BEAUTY · Korean Skincare &amp; Beauty · Toshkent</p>
          <div className="flex items-center gap-2">
            {["Payme", "Uzcard", "Humo", "Visa"].map((p) => (
              <span
                key={p}
                className="rounded-[3px] border border-porcelain/15 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider text-porcelain/60"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
