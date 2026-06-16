"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useCart } from "@/lib/cart";
import { Bag, Search, Menu, Close } from "@/components/Icons";

const NAV = [
  { href: "/catalog/", label: "Katalog" },
  { href: "/promotions/", label: "Aksiyalar" },
  { href: "/#categories", label: "Kategoriyalar" },
  { href: "/#brend", label: "Brend" },
];

export function Header() {
  const { count } = useCart();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Menyu ochiqligida scroll'ni bloklash
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      {/* E'lon chizig'i */}
      <div className="bg-ink text-porcelain">
        <div className="container-page flex h-9 items-center justify-center gap-3 text-[11px] font-medium uppercase tracking-wider2">
          <span className="text-gold-light">Bepul yetkazish</span>
          <span className="hidden text-porcelain/70 sm:inline">300 000 so'mdan yuqori xaridlarga</span>
          <span aria-hidden className="text-gold/60">·</span>
          <span className="text-porcelain/70">100% Original</span>
        </div>
      </div>

      <header
        className={`sticky top-0 z-50 transition-all duration-500 ${
          scrolled
            ? "border-b border-line bg-porcelain/85 backdrop-blur-md"
            : "border-b border-transparent bg-porcelain/0"
        }`}
      >
        <div className="container-page grid h-[72px] grid-cols-[1fr_auto_1fr] items-center">
          {/* Chap: navigatsiya / mobil menyu tugmasi */}
          <div className="flex items-center">
            <button
              className="icon-btn -ml-2 md:hidden"
              onClick={() => setOpen(true)}
              aria-label="Menyu"
            >
              <Menu />
            </button>
            <nav className="hidden items-center gap-8 md:flex">
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className="nav-link text-ink/80 hover:text-ink">
                  {n.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Markaz: logotip — emblem (logo rasmi) + wordmark */}
          <Link href="/" className="group inline-flex select-none items-center justify-center gap-2.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.jpg"
              alt="MUSE BEAUTY logotipi"
              className="h-9 w-9 shrink-0 rounded-full object-cover shadow-soft ring-1 ring-rose-200/70 transition-transform duration-500 group-hover:scale-105 sm:h-11 sm:w-11"
            />
            <span className="leading-none">
              <span className="block font-serif text-[16px] font-medium uppercase leading-none tracking-[0.22em] text-ink sm:text-[19px]">
                <span className="ml-[0.22em]">Muse</span>
                <span className="text-rose">Beauty</span>
              </span>
              <span className="mt-1 hidden text-[8px] font-semibold uppercase tracking-[0.32em] text-ink-soft sm:block">
                Korean Skincare &amp; Beauty
              </span>
            </span>
          </Link>

          {/* O'ng: amallar */}
          <div className="flex items-center justify-end gap-1">
            <Link href="/catalog/" className="icon-btn" aria-label="Qidiruv">
              <Search />
            </Link>
            <Link href="/cart/" className="icon-btn relative" aria-label="Savat">
              <Bag />
              {count > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-rose px-1 text-[10px] font-bold text-white">
                  {count}
                </span>
              )}
            </Link>
          </div>
        </div>
      </header>

      {/* Mobil menyu */}
      <div
        className={`fixed inset-0 z-[70] md:hidden ${open ? "" : "pointer-events-none"}`}
        aria-hidden={!open}
      >
        <div
          className={`absolute inset-0 bg-ink/30 backdrop-blur-sm transition-opacity duration-300 ${
            open ? "opacity-100" : "opacity-0"
          }`}
          onClick={() => setOpen(false)}
        />
        <nav
          className={`absolute left-0 top-0 h-full w-[82%] max-w-sm bg-porcelain px-7 py-6 shadow-lift transition-transform duration-400 ease-out ${
            open ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-serif text-lg uppercase tracking-[0.3em] text-ink">Menyu</span>
            <button className="icon-btn -mr-2" onClick={() => setOpen(false)} aria-label="Yopish">
              <Close />
            </button>
          </div>
          <div className="mt-10 flex flex-col gap-1">
            {NAV.map((n, i) => (
              <Link
                key={n.href}
                href={n.href}
                onClick={() => setOpen(false)}
                className="border-b border-line/70 py-4 font-serif text-2xl text-ink transition-colors hover:text-rose"
                style={{ transitionDelay: `${i * 20}ms` }}
              >
                {n.label}
              </Link>
            ))}
          </div>
          <Link
            href="/cart/"
            onClick={() => setOpen(false)}
            className="btn-primary mt-10 w-full"
          >
            <Bag className="h-4 w-4" />
            Savat{count > 0 ? ` · ${count}` : ""}
          </Link>
        </nav>
      </div>
    </>
  );
}
