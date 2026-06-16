# MUSE BEAUTY — Website (Next.js)

Mijozlar uchun do'kon (storefront). Backendning `api/public` endpointlariga
ulanadi. **Statik eksport** — production'da serverdagi (host) nginx beradi (Node serveri yo'q, RAM tejaladi).

## Sahifalar

- `/` — bosh sahifa (hero, kategoriyalar, ommabop mahsulotlar)
- `/catalog` — katalog (kategoriya filtri + qidiruv)
- `/product?id=N` — mahsulot tafsiloti + savatga qo'shish
- `/cart` — savat (localStorage)
- `/checkout` — buyurtma (ism, telefon, tuman, manzil, promokod + jonli narx)
- `/order` — buyurtma tasdiqlandi (to'lov ko'rsatmasi / Payme tugmasi)

## Mahalliy dev

```bash
cp .env.example .env       # NEXT_PUBLIC_API_URL ni backend manziliga moslang
npm install
npm run dev                # http://localhost:3000
```

Backend ishlab turishi kerak (`docker compose up`), `make seed` bilan ma'lumot.

## Production build

```bash
npm run build              # out/ — statik fayllar (host nginx beradi)
```

Odatda qo'lда qilinmaydi: Docker'dagi bir-martalik `website` build servisi shu
papkani build qilib, natijani host papka `./static/website` ga chiqaradi.
Serverdagi (host) nginx esa uni `musebeauty.uz` da to'g'ridan beradi
(`make front` bilan qayta build qilinadi).

## Texnologiya

- Next.js 14 (App Router, `output: export`)
- Tailwind CSS (K-beauty estetikasi)
- Savat — React Context + localStorage (server yo'q)
- Buyurtma — `api/public/orders/web` (Telegram'siz, telefon orqali mijoz)
