# MUSE BEAUTY — To'liq Arxitektura

> Loyiha: **musebeauty** · Koreya (K-beauty) go'zallik vositalari onlayn savdosi

**Loyiha:** Koreadan keltiriladigan go'zalik vositalari onlayn savdosi
**Hudud:** Toshkent shahri (boshlang'ich bosqich)
**Kanallar:** Telegram bot + Website
**To'lov:** Qo'lda (keyin Payme/Click)
**Yetkazib berish:** Yandex

---

## 1. Umumiy ko'rinish

Tizimning markazida **bitta backend va bitta ma'lumotlar bazasi** turadi. Bot, website va admin panel — bularning hammasi shu yagona "miya"ga ulanadi. Hech qaysi ma'lumot ikki joyda takrorlanmaydi.

```
                    ┌──────────────────────────────────┐
                    │          BACKEND (API)            │
                    │      FastAPI (async, Py3.11)      │
                    │                                   │
                    │  ┌────────────┐  ┌────────────┐   │
                    │  │ api/public │  │ api/admin  │   │
                    │  │ (bot+web)  │  │ (auth bilan)│  │
                    │  └─────┬──────┘  └──────┬─────┘   │
                    │        └────────┬───────┘         │
                    │         ┌───────┴────────┐        │
                    │         │ Servis qatlami  │        │
                    │         │ (business logic)│        │
                    │         └───────┬────────┘        │
                    │         ┌───────┴────────┐        │
                    │         │ ORM (SQLAlchemy)│        │
                    │         └───────┬────────┘        │
                    └─────────────────┼─────────────────┘
                                      │
                             ┌────────┴────────┐
                             │   PostgreSQL    │
                             └─────────────────┘

   Kirish kanallari (har biri ALOHIDA ilova, alohida deploy):
   ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐
   │ Telegram bot │  │   Website    │  │   Admin / ERP      │
   │  (aiogram 3) │  │  (Next.js)   │  │  panel (React)     │
   │              │  │              │  │  admin.musebeauty.uz      │
   └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘
          │ api/public      │ api/public          │ api/admin
          └─────────────────┴─────────────────────┘
                  (hammasi bitta backendga ulanadi)

   Tashqi xizmatlar:
   ┌──────────┐  ┌──────────────┐  ┌──────────────┐
   │  Redis   │  │ Yandex Yetk. │  │ Payme/Click  │
   │ (FSM/keш)│  │  (keyinroq)  │  │  (keyinroq)  │
   └──────────┘  └──────────────┘  └──────────────┘
```

**Admin panel — alohida ilova:** o'z subdomain'ida (`admin.musebeauty.uz`), o'z deploy'ida, faqat himoyalangan `api/admin/*` orqali backendga ulanadi. Biznes mantiq baribir bitta `services/` qatlamida — takrorlanmaydi (DRY).

---

## 2. Texnologik stack

| Qatlam | Texnologiya | Izoh |
|--------|-------------|------|
| Til | Python 3.11 | |
| Backend API | FastAPI (async) | Website va admin uchun |
| Bot | aiogram 3 | |
| ORM | SQLAlchemy 2 (async) | |
| Migratsiya | Alembic | Sxema o'zgarishlarini boshqarish |
| Baza (prod) | PostgreSQL | |
| Baza (dev) | SQLite | Mahalliy ishlash uchun |
| Kesh / FSM | Redis | Bot holatlari, savat, sessiya |
| Rejalashtiruvchi | APScheduler | Eslatma, promo muddati, "kam qoldi" |
| Admin panel | React + Refine (yoki React-Admin) | **Alohida ilova**, `api/admin` ga ulanadi |
| — muqobil | Tooljet / Appsmith (low-code) | Eng tez yo'l, kam kod |
| Website | Next.js | 2-bosqichda |
| Rasm saqlash | Cloudflare R2 (S3-mos) | Mahsulot rasmlari, to'g'ridan public URL |
| Reverse proxy | Nginx (host darajasida, Docker tashqarisida) | API'ni `127.0.0.1:8000` ga proxy + SSL |
| Deployment | Docker + docker-compose | nginx Docker ichida emas |

---

## 3. Loyiha tuzilmasi (papkalar)

Endi tizim **ikkita alohida loyihadan** iborat: `backend/` (umumiy miya) va `admin-panel/` (alohida admin ilovasi).

### Backend (bitta, hammaga xizmat qiladi)
```
backend/
├── app/
│   ├── core/             # config, db ulanish, xavfsizlik
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py   # admin auth (JWT), role
│   ├── models/           # SQLAlchemy modellari
│   ├── schemas/          # Pydantic (validatsiya)
│   ├── services/         # BIZNES MANTIQ (bitta, umumiy)
│   │   ├── catalog.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── pricing.py    # chegirma + promokod
│   │   ├── inventory.py  # ombor kirim/chiqim
│   │   ├── payment.py
│   │   ├── delivery.py
│   │   ├── promo.py
│   │   ├── report.py     # ERP hisobotlar
│   │   └── notify.py     # bildirishnomalar
│   ├── api/
│   │   ├── public/       # bot + website uchun (auth yo'q yoki yengil)
│   │   │   ├── catalog.py
│   │   │   ├── cart.py
│   │   │   └── order.py
│   │   └── admin/        # ADMIN/ERP uchun (auth majburiy)
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── orders.py
│   │       ├── inventory.py
│   │       ├── promo.py
│   │       └── reports.py
│   ├── bot/              # aiogram handler va FSM
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── states.py
│   └── tasks/            # APScheduler ishlari
├── alembic/
├── docker-compose.yml
├── Dockerfile
└── .env
```

### Admin panel (alohida ilova, alohida repo)
```
admin-panel/             # React + Refine
├── src/
│   ├── pages/
│   │   ├── products/     # mahsulot CRUD
│   │   ├── orders/       # buyurtmalar, holat o'zgartirish
│   │   ├── inventory/    # ombor, partiyalar
│   │   ├── promo/        # chegirma, promokod
│   │   ├── customers/    # mijozlar
│   │   └── reports/      # moliya, analitika
│   ├── api/             # backendning api/admin ga so'rovlar
│   ├── auth/            # login, JWT saqlash
│   └── components/
├── Dockerfile
└── package.json
```

**Asosiy tamoyil:** barcha biznes mantiq backendning `services/` ichida bitta nusxada. Bot, `api/public`, `api/admin` — hammasi shu servislarni chaqiradi. Admin panel mustaqil ilova bo'lsa-da, hech qanday mantiqni takrorlamaydi — faqat `api/admin` orqali so'rov yuboradi.

---

## 4. Ma'lumotlar bazasi (to'liq sxema)

### Katalog va ombor
```
categories
  id, name, slug, is_active

products
  id, category_id, name, description, image_url,
  price,            # joriy sotuv narxi
  cost_price,       # tannarx (foyda hisobi uchun)
  stock_qty,        # ombor qoldig'i
  is_active, created_at

supply_batches            # Koreadan kelgan partiyalar
  id, supplier, arrival_date, total_cost, note

batch_items               # partiya ichidagi mahsulotlar
  id, batch_id, product_id, qty, unit_cost
```

### Mijozlar va buyurtmalar
```
customers
  id, telegram_id, name, phone, created_at

districts                 # Toshkent tumanlari
  id, name, delivery_fee

orders
  id, customer_id, status, payment_status,
  district_id, address, phone,
  subtotal,         # chegirmasiz jami
  discount_amount,  # qo'llanilgan chegirma (snapshot)
  promo_code_id,    # ishlatilgan promokod (agar bor)
  delivery_fee,
  total,            # = subtotal − discount + delivery
  created_at

order_items
  id, order_id, product_id, qty,
  unit_price,       # sotilgan paytdagi narx (snapshot)
  cost_price        # o'sha paytdagi tannarx (snapshot)
```

### To'lov
```
payments
  id, order_id, amount, method,
  screenshot_url,   # qo'lda to'lov cheki
  is_confirmed, confirmed_by, confirmed_at
```

### Chegirma, aksiya, promokod
```
discounts                 # kodsiz chegirma/aksiya
  id, name, type,         # percent / fixed
  value, scope,           # all / category / product
  target_id,
  valid_from, valid_until, is_active

promo_codes               # kod bilan
  id, code, type,         # percent / fixed / free_delivery
  value, min_order_amount, max_discount,
  usage_limit, used_count,
  per_user_limit, first_order_only,
  scope, target_id,
  valid_from, valid_until, is_active

promo_redemptions         # kim qachon ishlatdi
  id, promo_code_id, customer_id, order_id,
  discount_amount, used_at
```

### Admin
```
admins
  id, username, password_hash, role, is_active

audit_log                 # kim nimani o'zgartirdi (ixtiyoriy)
  id, admin_id, action, entity, entity_id, created_at
```

**Snapshot tamoyili:** buyurtmaga narx, tannarx, chegirma — hammasi o'sha paytdagi qiymat bilan yoziladi. Keyinchalik mahsulot narxi yoki promokod o'zgarsa, eski buyurtma hisobi buzilmaydi.

---

## 5. Buyurtma oqimi (checkout)

```
1. Mijoz savatga mahsulot qo'shadi          → CartService
2. Manzil + tuman + telefon kiritadi
3. Promokod kiritsa → tekshiriladi          → PromoService
4. Narx hisoblanadi:                         → PricingService
      a) mahsulot chegirmasi qo'llanadi
      b) promokod subtotal'ga qo'llanadi
      c) tuman bo'yicha yetkazib berish narxi
5. Buyurtma yaratiladi (status: yangi)       → OrderService
6. Ombordan zaxiralanadi (stock kamayadi)    → InventoryService
7. To'lov ko'rsatmasi (karta raqami) beriladi
8. Admin'ga bildirishnoma yuboriladi         → NotifyService
```

### Buyurtma holatlari
```
yangi → to'landi → tayyorlandi → jo'natildi → yetkazildi
                 ↘ bekor qilindi   ↘ qaytarildi
```

---

## 6. To'lov oqimi (qo'lda)

```
1. Mijozga karta raqami (Humo/Uzcard) ko'rsatiladi
2. Mijoz to'laydi va chek/screenshot yuboradi
3. Screenshot `payments` jadvaliga saqlanadi (is_confirmed=false)
4. Admin panelda admin tasdiqlaydi:
      payment_status → to'landi
      order.status   → to'landi
5. Mijozga "to'lov qabul qilindi" bildirishnomasi
```

**Keyingi bosqich:** Payme/Click integratsiyasi. `payments.method` allaqachon bor — faqat avtomatik tasdiqlash qo'shiladi, qolgan mantiq o'zgarmaydi.

---

## 7. Yetkazib berish (Yandex)

**Hozircha (qo'lda):** buyurtma "tayyorlandi" bo'lганda, admin Yandex Go / Yandex Delivery ilovasi orqali kuryer chaqiradi. Tuman bo'yicha narx `districts.delivery_fee` dan olinadi.

**Keyin (API):** `DeliveryService` Yandex Delivery API'ga ulanadi — avtomatik kuryer chaqirish, narx hisobi, kuzatish. Mantiq bitta servisda izolyatsiyalangan, shuning uchun qolgan tizimga ta'sir qilmaydi.

---

## 8. Bot arxitekturasi (aiogram 3)

```
bot/
├── filters.py           # IsAdmin / IsNotAdmin — admin va mijozni ajratish
├── handlers/
│   ├── start.py         # /start, ro'yxatdan o'tish        ┐
│   ├── catalog.py       # kategoriya, mahsulot ko'rish      │ MIJOZ
│   ├── cart.py          # savat                              │ (IsNotAdmin)
│   ├── checkout.py      # buyurtma berish (FSM) + promokod   │
│   ├── payment.py       # chek yuborish                      │
│   ├── misc.py          # buyurtmalarim, aksiyalar, aloqa   ┘
│   └── admin_bot.py     # ADMIN bot (IsAdmin) — boshqaruv
├── keyboards/           # inline/reply tugmalar (admin alohida)
└── states.py            # FSM holatlari
```

**Admin va mijoz ajratilgan:** `ADMIN_TELEGRAM_IDS` dagi foydalanuvchilar
e-commerce (katalog/savat/checkout) ni **ko'rmaydi** — ularga **admin bot**
ishlaydi. Router darajasidagi filtr buni ta'minlaydi:

- Admin bot router → `IsAdmin` (birinchi ulanadi)
- Barcha mijoz routerlari → `IsNotAdmin`

**Admin bot imkoniyatlari** (Telegram orqali tezkor boshqaruv):
buyurtmalar + holatni o'zgartirish (inline tugmalar), to'lov cheklarini
tasdiqlash (mijozga avtomatik xabar), kam qoldi, kunlik/oylik hisobot.
To'liq boshqaruv esa — alohida admin saytida (brauzer).

- **FSM holati** Redis'da saqlanadi (checkout bosqichlari: tuman → manzil → promo → tasdiq).
- **Savat** ham Redis'da (tez, sessiyaga bog'liq).
- Bot (ham mijoz, ham admin) faqat `services/` ni chaqiradi — alohida mantiq yozilmaydi.

---

## 9. Rejalashtirilgan ishlar (APScheduler)

- Promokod muddati tugaganda `is_active=false`
- "Kam qoldi" ogohlantirishi (`stock_qty < N` bo'lsa admin'ga)
- Kunlik savdo hisoboti (admin'ga avtomatik)
- To'lanmagan buyurtmalarni eslatish/bekor qilish

---

## 10. Xavfsizlik

- Admin panel — JWT yoki sessiya autentifikatsiyasi, parol hash (bcrypt)
- Bot — Telegram `telegram_id` orqali, admin ID'lar `.env` da
- `.env` da: DB parol, bot token, kalit so'zlar (kodga yozilmaydi)
- To'lov cheklari — faqat admin ko'ra oladigan saqlovda
- Barcha narx/chegirma hisobi **serverda** (mijoz tomonda emas)
- SQL injection — ORM orqali himoyalangan; input Pydantic bilan validatsiya

---

## 11. Deployment (2 CPU / 2GB RAM uchun)

```
docker-compose (nginx Docker ichida EMAS):
  ├── api          (FastAPI — api/public + api/admin), faqat 127.0.0.1:8000 ga ochiq
  ├── bot          (aiogram, long polling)        ← api bilan bir xil image
  ├── postgres     (past resursga sozlangan)
  ├── redis        (maxmemory 96mb)
  ├── backup       (kunlik pg_dump)
  ├── website      (Next.js → statik build → ./static/website) ← bir martalik
  └── admin-panel  (React/Vite → statik build → ./static/admin)  ← bir martalik

host nginx (Docker tashqarisida, serverga qo'lda o'rnatiladi):
  ├── musebeauty.uz        → ./static/website (statik) + /api → 127.0.0.1:8000
  └── admin.musebeauty.uz  → ./static/admin   (statik) + /api → 127.0.0.1:8000
```

`website` va `admin-panel` — **bir martalik build servislari**: statikni host
papkalarga (`./static/website`, `./static/admin`) bind-mount orqali ko'chirib
to'xtaydi (runtime'da Node ishlamaydi). Serverdagi (host) nginx shu papkalarni
to'g'ridan beradi. API esa faqat `127.0.0.1:8000` ga ochiladi (internetga
to'g'ridan emas) — host nginx unga `/api` ni proxy qiladi.

**Admin panel — alohida ilova, samarali serviring.** Admin o'z repo'sida, o'z React build'i bilan mustaqil ishlanadi (alohida deploy qilinadi). Lekin 2GB RAM cheklovi tufayli production'da Node serveri ishlamaydi — `npm run build` natijasi (statik fayllar) `./static/admin` ga chiqadi va host nginx orqali beriladi. Shunday qilib admin ham alohida bo'ladi, ham deyarli RAM yemaydi.

**Bot — long polling.** Webhook va undagi HTTPS shartini chetlab o'tadi; sozlash sodda. SSL faqat admin/website uchun kerak.

**Resurslar — erkinlik, lekin minimal iz.** Tamoyil: RAM va CPU ga **to'liq
erkinlik** — `mem_limit`/`cpus` (va hatto soft `mem_reservation`) qo'yilmaydi.
Ular servislarning bo'sh RAM/CPU ga "burst" qilishini to'sadi, qattiq `mem_limit`
esa host'da bo'sh RAM bo'lsa ham konteynerni OOM bilan o'ldiradi. Erkinlik kam
resursni ham qoplaydi: bo'sh joy bo'lsa tez, kam bo'lsa ham ishlayveradi.

Minimalni cgroup emas, **ilova darajasida** ta'minlaymiz:

| Servis | Ilova darajasidagi sozlama (minimal iz) |
|--------|------------------------------------------|
| postgres | shared_buffers=96MB, max_connections=30, parallel query o'chiq, WAL cheklangan |
| redis | --maxmemory 96mb (o'zini cheklaydi, diskka yozmaydi) |
| api | uvicorn 1 worker; SQLAlchemy pool kichik (≈5+5) |

Real ishlatish ~500–800M. Mo'ljal 2 CPU / 2GB, ammo **swap** bilan ~1 CPU / 1GB
da ham erkin ishlaydi. Bo'sh RAM/CPU bo'lsa — avtomatik foydalanadi (cheklov yo'q).

- Migratsiya: faqat `api` konteyner bajaradi (`alembic upgrade head`)
- SSL: serverdagi (host) nginx orqali `sudo certbot --nginx -d ...` (Let's Encrypt) yoki Cloudflare Origin sertifikat
- Backup: PostgreSQL kunlik `pg_dump` (cron)
- **Build ogohlantirishi:** React build 2GB'da tig'iz bo'lishi mumkin → swap qo'shing yoki image'ni CI/kuchliroq mashinada build qiling. Runtime 2GB'da bemalol.

---

## 12. Bosqichma-bosqich yo'l xaritasi

### 1-bosqich — MVP (eng tez ishga tushadigan)
- Telegram bot: katalog, savat, buyurtma
- Qo'lda to'lov (chek yuborish + admin tasdiq)
- **Alohida admin panel** (React + Refine): mahsulot, buyurtma, ombor boshqaruvi
- Backend: `api/public` + `api/admin` + admin auth (JWT)
- Yandex qo'lda (admin kuryer chaqiradi)
- Asosiy ERP: ombor, buyurtma, ta'minot partiyalari

### 2-bosqich — Marketing va kengayish
- Chegirma, aksiya, promokod (admin panelda boshqariladi)
- Moliya hisobotlari (foyda, eng ko'p sotilgan)
- Mijozlar bazasi (CRM-lite)
- "Kam qoldi" va kunlik hisobot avtomatikasi

### 3-bosqich — To'liq onlayn
- Website (Next.js)
- Payme/Click integratsiyasi
- Yandex Delivery API
- Admin panelni kengaytirish (rollar, audit log, dashboard)
- MinIO/S3 rasm saqlash

### 4-bosqich — O'sish
- Ko'p ombor / boshqa shaharlar
- Sodiqlik dasturi (ballar)
- Avtomatik qaytarish
- Analitika dashboard

---

## Eslatma: ochiq qarorlar

Tizimni qurishdan oldin shu ikki qarorni belgilash kerak:

1. **Tannarx hisobi:** har partiya alohida narxda kuzatiladimi (FIFO), yoki har mahsulotga bitta o'rtacha tannarq yetarlimi? — Ombor modelining murakkabligini belgilaydi.
2. **Chegirma + promokod ustma-ust (stack) bo'ladimi**, yoki bittasi qo'llanadimi? — Zararga ketmaslik uchun bittasi (mijozga foydaliroq) tavsiya etiladi.
