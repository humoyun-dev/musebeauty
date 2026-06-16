"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, type District, type Quote } from "@/lib/api";
import { useCart } from "@/lib/cart";
import { money } from "@/lib/format";
import { MapPin, Check, ArrowRight } from "@/components/Icons";

export default function CheckoutPage() {
  const router = useRouter();
  const { items, ready, count, clear } = useCart();

  const [districts, setDistricts] = useState<District[]>([]);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [districtId, setDistrictId] = useState<number | "">("");
  const [address, setAddress] = useState("");
  const [promo, setPromo] = useState("");
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [mapLink, setMapLink] = useState("");
  const [locInfo, setLocInfo] = useState<string | null>(null);
  const [locOk, setLocOk] = useState(false);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const detectLocation = () => {
    if (!navigator.geolocation) {
      setLocInfo("Brauzer joylashuvni qo'llab-quvvatlamaydi");
      return;
    }
    setLocInfo("Aniqlanmoqda…");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLng(pos.coords.longitude);
        setLocOk(true);
        setLocInfo("Joylashuv aniqlandi");
      },
      () => {
        setLocOk(false);
        setLocInfo("Joylashuvga ruxsat berilmadi");
      },
    );
  };

  const itemList = Object.entries(items).map(([id, qty]) => ({
    product_id: Number(id),
    qty,
  }));

  useEffect(() => {
    api.districts().then(setDistricts).catch(() => {});
  }, []);

  useEffect(() => {
    if (!ready || itemList.length === 0) return;
    api
      .quote({
        items: itemList,
        district_id: districtId || null,
        promo_code: promo || null,
        phone: phone || null,
      })
      .then(setQuote)
      .catch(() => setQuote(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(items), districtId, promo, phone, ready]);

  if (ready && count === 0) {
    return (
      <div className="container-page py-28 text-center">
        <p className="text-ink-soft">Savatingiz bo'sh.</p>
        <Link href="/catalog/" className="btn-primary mt-6">
          Katalogga o'tish
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (phone.trim().length < 7) {
      setError("Telefon raqamini to'g'ri kiriting");
      return;
    }
    setSubmitting(true);
    try {
      const result = await api.createWebOrder({
        name: name || null,
        phone,
        items: itemList,
        district_id: districtId || null,
        address: address || null,
        promo_code: promo || null,
        latitude: lat,
        longitude: lng,
        map_link: mapLink || null,
      });
      sessionStorage.setItem("muse_last_order", JSON.stringify(result));
      clear();
      router.push("/order/");
    } catch (err: any) {
      setError(err?.message ?? "Buyurtma berib bo'lmadi");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container-page py-14 lg:py-20">
      <header className="mb-10 border-b border-line pb-8">
        <p className="eyebrow">Yakuniy qadam</p>
        <h1 className="display mt-4 text-4xl sm:text-5xl">Buyurtma berish</h1>
      </header>

      <div className="grid gap-10 lg:grid-cols-[1fr_360px]">
        {/* Forma */}
        <form onSubmit={submit} className="space-y-7">
          <fieldset className="space-y-5">
            <legend className="mb-2 text-[11px] font-semibold uppercase tracking-eyebrow text-ink-mute">
              Aloqa ma'lumotlari
            </legend>
            <Field label="Ism">
              <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Ismingiz" />
            </Field>
            <Field label="Telefon raqami *">
              <input
                className="input"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+998 90 123 45 67"
                required
              />
            </Field>
          </fieldset>

          <fieldset className="space-y-5">
            <legend className="mb-2 text-[11px] font-semibold uppercase tracking-eyebrow text-ink-mute">
              Yetkazib berish
            </legend>
            <Field label="Tuman">
              <select
                className="input"
                value={districtId}
                onChange={(e) => setDistrictId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">Tanlang…</option>
                {districts.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} — {money(d.delivery_fee)}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Manzil">
              <textarea
                className="input"
                rows={2}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Ko'cha, uy, kvartira, mo'ljal"
              />
            </Field>
            <Field label="Aniq joylashuv (ixtiyoriy)">
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={detectLocation}
                  className="inline-flex items-center gap-2 rounded-[4px] border border-line bg-shell px-4 py-2.5 text-sm font-medium text-ink transition-colors hover:border-ink/30"
                >
                  <MapPin className="h-4 w-4 text-rose" />
                  Joylashuvni aniqlash
                </button>
                {locInfo && (
                  <span
                    className={`inline-flex items-center gap-1.5 text-sm ${
                      locOk ? "text-rose" : "text-ink-soft"
                    }`}
                  >
                    {locOk && <Check className="h-4 w-4" />}
                    {locInfo}
                  </span>
                )}
              </div>
              <input
                className="input mt-3"
                value={mapLink}
                onChange={(e) => setMapLink(e.target.value)}
                placeholder="yoki Google / Yandex map havolasini joylang"
              />
            </Field>
          </fieldset>

          <fieldset className="space-y-3">
            <legend className="mb-2 text-[11px] font-semibold uppercase tracking-eyebrow text-ink-mute">
              Promokod
            </legend>
            <input
              className="input uppercase"
              value={promo}
              onChange={(e) => setPromo(e.target.value)}
              placeholder="BAHOR2026"
            />
            {quote?.promo_error && <p className="text-sm text-rose">{quote.promo_error}</p>}
          </fieldset>

          {error && (
            <p className="rounded-[4px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </p>
          )}

          <button className="btn-primary w-full lg:hidden" disabled={submitting}>
            {submitting ? "Yuborilmoqda…" : "Buyurtmani tasdiqlash"}
          </button>
        </form>

        {/* Narx xulosasi */}
        <div className="h-fit lg:sticky lg:top-28">
          <div className="card border border-line p-7">
            <h2 className="font-serif text-xl text-ink">Xulosa</h2>
            <div className="mt-5 space-y-3">
              {quote ? (
                <>
                  <Row label="Mahsulotlar" value={money(quote.subtotal)} />
                  {Number(quote.discount_amount) > 0 && (
                    <Row label="Chegirma" value={`−${money(quote.discount_amount)}`} accent />
                  )}
                  <Row
                    label="Yetkazib berish"
                    value={quote.free_delivery ? "Bepul" : money(quote.delivery_fee)}
                    accent={quote.free_delivery}
                  />
                  <div className="mt-2 border-t border-line pt-4">
                    <Row label="Jami" value={money(quote.total)} bold />
                  </div>
                </>
              ) : (
                <p className="text-sm text-ink-mute">Tumanni tanlang — narx hisoblanadi.</p>
              )}
            </div>
            <button
              onClick={submit}
              className="btn-primary mt-6 hidden w-full lg:flex"
              disabled={submitting}
            >
              {submitting ? "Yuborilmoqda…" : "Buyurtmani tasdiqlash"}
            </button>
            <p className="mt-4 hidden items-center justify-center gap-1.5 text-xs text-ink-mute lg:flex">
              <Check className="h-3.5 w-3.5 text-rose" /> Xavfsiz va ishonchli to'lov
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      {children}
    </label>
  );
}

function Row({
  label,
  value,
  bold,
  accent,
}: {
  label: string;
  value: string;
  bold?: boolean;
  accent?: boolean;
}) {
  return (
    <div className={`flex justify-between ${bold ? "text-lg font-semibold text-ink" : "text-sm text-ink-soft"}`}>
      <span>{label}</span>
      <span className={accent ? "font-medium text-rose" : bold ? "font-serif" : "text-ink"}>{value}</span>
    </div>
  );
}
