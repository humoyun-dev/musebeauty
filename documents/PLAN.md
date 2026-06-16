# MUSE BEAUTY — Ish Rejasi (PLAN)

> Loyiha: **musebeauty** · Koreya (K-beauty) go'zallik vositalari onlayn savdosi

Bu hujjat arxitekturani amalga oshirish tartibini belgilaydi: nimani qaysi
ketma-ketlikda qurish, har bosqich nima bilan tugashi va o'zaro bog'liqliklar.

> Jadval (kun/hafta) qo'yilmagan — ketma-ketlik va "tugadi" mezoni muhimroq.
> Sizning vaqtingizga qarab har bosqichni rejalashtirasiz.

---

## 0-bosqich — Boshlang'ich qarorlar va tayyorgarlik

Kod yozishdan oldin shularni hal qiling:

- [ ] **Tannarx hisobi:** FIFO (har partiya alohida narx) yoki o'rtacha tannarx?
      → Tavsiya: boshida **o'rtacha** (sodda), keyin kerak bo'lsa FIFO'ga o'tasiz.
- [ ] **Chegirma + promokod:** ustma-ust (stack) yoki bittasi?
      → Tavsiya: **bittasi** (mijozga foydaliroq bo'lgani) — zararга ketmaslik uchun.
- [ ] **Domen** olingan (`musebeauty.uz`, `admin.musebeauty.uz`)
- [ ] **VPS** (2 CPU / 2GB) tayyor, swap yoqilgan
- [ ] **Telegram bot** BotFather'da yaratilgan, token olingan
- [ ] **Admin Telegram ID'lari** aniqlangan
- [ ] **To'lov kartasi** (Humo/Uzcard) — chek qabul qilish uchun
- [ ] **Toshkent tumanlari** ro'yxati + har biriga yetkazib berish narxi

**Tugadi:** barcha qarorlar qabul qilingan, VPS va domen tayyor.

---

## 1-bosqich — Poydevor (infra + ma'lumotlar bazasi)

**Maqsad:** bo'sh, lekin to'liq ishlaydigan skelet.

- [x] Repo tuzilmasi: `backend/`, `admin-panel/`, `website/`, `static/` (nginx Docker ichida emas — host darajasida)
- [x] Docker setup (tayyor — `docker-compose.yml`, Dockerfile'lar, `.env.example`)
- [x] `core/`: config (pydantic-settings), database (async engine), security (JWT), redis
- [x] **Barcha SQLAlchemy modellari** (14 jadval, audit_log ham qo'shildi):
      categories, products, customers, districts, orders, order_items,
      payments, supply_batches, batch_items, discounts, promo_codes,
      promo_redemptions, admins, audit_log
- [x] Alembic sozlash + birinchi migratsiya (async env.py)
- [x] `app/main.py` — FastAPI + `/health` (baza tekshiruvi bilan)
- [x] `app/bot/` — aiogram bot (/start + ro'yxatdan o'tish)

**Tugadi ✅** (2026-06-16, Docker python:3.11 da tasdiqlangan): migratsiya 14 jadval
yaratadi, importlar yuklanadi, `/health` ishlaydi.

---

## 2-bosqich — MVP backend + bot (sotuv ishlaydi)

**Maqsad:** mijoz bot orqali haqiqiy buyurtma bera oladi.

Servislar (`services/`):
- [x] `catalog` — kategoriya/mahsulot ro'yxati, qidiruv
- [x] `cart` — savat (Redis'da)
- [x] `inventory` — qoldiq qulflab kamaytirish/oshirish (oversell yo'q)
- [x] `pricing` — asosiy narx hisobi (chegirmasiz, yetkazib berish bilan)
- [x] `order` — buyurtma yaratish (atomik), holat zanjiri
- [x] `payment` — chek qabul qilish (is_confirmed=false) + tasdiqlash
- [x] `notify` — admin'ga va mijozga bildirishnoma (httpx → Telegram)

Bot handlerlari:
- [x] start / ro'yxatdan o'tish (telefon)
- [x] katalog ko'rish (kategoriya → mahsulot → tafsilot)
- [x] savat (qo'shish, miqdor +/−, o'chirish, tozalash)
- [x] checkout FSM (tuman → manzil → tasdiq)
- [x] chek yuborish (rasm)
- [x] qo'shimcha: buyurtmalarim, aloqa

API (`api/public`): [x] catalog, [x] cart, [x] order endpointlari.

Qo'shimcha: `app/seed.py` — Toshkent tumanlari + namuna katalog (sinov uchun).

**Tugadi ✅** (2026-06-16, uchidan-uchiga oqim Docker'da tasdiqlangan): savat →
buyurtma → qoldiq avtomatik kamaydi → chek → admin tasdiq → 'tolandi'; bekor
qilinganда qoldiq qaytadi. Narx snapshot to'g'ri (290 000 + 30 000 = 320 000).

---

## 3-bosqich — Admin panel (alohida React ilova)

**Maqsad:** admin brauzerда hammasini boshqaradi (bot komandalari emas).

Backend (`api/admin`):
- [x] auth (login → JWT), role tekshiruvi (`require_role`, superadmin har doim o'tadi)
- [x] products CRUD (+ kategoriya CRUD)
- [x] orders ro'yxati + holat o'zgartirish (zanjir tekshiruvi)
- [x] inventory + supply_batches (partiya kiritish → o'rtacha tannarx qayta hisob)
- [x] payment tasdiqlash (→ buyurtma 'tolandi')
- [x] customers ro'yxati + `create_admin` CLI + CORS

Admin panel (React + Refine + Ant Design):
- [x] login sahifasi (JWT saqlash, authProvider)
- [x] mahsulotlar (qo'shish/tahrirlash, kategoriya tanlash, rasm URL)
- [x] buyurtmalar (ro'yxat + tafsilot + holat zanjiri tugmalari)
- [x] to'lov tasdiqlash (chek file_id → bir tugma bilan tasdiq)
- [x] ombor (partiya qo'shish — dinamik mahsulot qatorlari)
- [x] mijozlar ro'yxati
- [x] kategoriyalar CRUD

> Bu bosqichni 2-bosqich tugagach **parallel** qilish mumkin
> (backend API tayyor bo'lsa, frontend alohida ishlanadi).

**Tugadi ✅** (2026-06-16): backend `api/admin` uchidan-uchiga tasdiqlangan
(login → CRUD → to'lov tasdiq → holat o'tishlari → partiya/o'rtacha tannarx 84 000);
admin panel `npm run build` muvaffaqiyatli (4073 modul, dist tayyor). Bot ichidagi
admin komandalar endi shart emas.

---

## 4-bosqich — Marketing va hisobot

**Maqsad:** chegirma/promokod ishlaydi, foyda ko'rinadi.

- [x] `pricing` to'liq: auto-chegirma vs promokod — BITTASI (mijozga foydaliroq), stack emas
- [x] `promo` servis: kod validatsiyasi (muddat, limit, min summa, per-user, first_order, scope)
- [x] bot checkout'da promokod kiritish (ixtiyoriy bosqich + "kodsiz davom etish")
- [x] admin: chegirma va promokod sahifalari (CRUD)
- [x] `report` servis: kunlik savdo, foyda (subtotal − discount − tannarx), top mahsulotlar
- [x] admin dashboard (bugun/oy daromad-foyda, kam qoldi, kutilayotgan to'lov)
- [x] APScheduler ishlari: promo muddati (soatlik), "kam qoldi" (09:00), kunlik hisobot (21:00)

**Tugadi ✅** (2026-06-16, Docker'da tasdiqlangan): promokod 20% (auto 10% dan
katta) g'olib bo'ldi — USTMA-UST EMAS; `promo_redemptions` ga yozildi, `used_count`
oshdi; foyda hisobi to'g'ri (200 000 − 40 000 − 120 000 = 40 000). Admin panel
`npm run build` muvaffaqiyatli (4076 modul, dashboard/chegirma/promo sahifalari).

---

## 5-bosqich — Production va kengayish

**Maqsad:** barqaror, xavfsiz, onlayn.

- [x] SSL: serverdagi (host) nginx orqali `sudo certbot --nginx -d ...` (Let's Encrypt)
- [x] PostgreSQL avtomatik backup (kunlik `pg_dump`, `backup` servis + 14 nusxa rotatsiya)
- [~] Yandex yetkazib berish — hozircha qo'lда (dizayn bo'yicha; API keyin `DeliveryService`)
- [x] Payme/Click integratsiyasi (avtomatik to'lov tasdiq — Payme JSON-RPC, Click imzo)
- [x] **Website (Next.js)** — `api/public` ustida (statik eksport → `./static/website`, host nginx beradi)
- [x] Rasm saqlash: Cloudflare R2 (`STORAGE_BACKEND=s3`, to'g'ridan `pub-...r2.dev` public URL) + S3-mos interfeys (disk rejimi ham mavjud)
- [x] Monitoring: api healthcheck (`/health`), `make logs`/`ps`, scheduler hisobotlari

**Tugadi ✅** (2026-06-16, Docker'da tasdiqlangan): rasm yuklash (Cloudflare R2,
to'g'ridan public URL), Payme (CheckPerform→Create→Perform → buyurtma avtomatik
'tolandi', auth/summa xatolari, idempotent), Click (prepare/complete imzo
tekshiruvi), **Website** (Next.js storefront: katalog→savat→checkout→web-order,
9 sahifa statik build → `./static/website`). SSL host nginx + certbot orqali,
backup + restore tayyor.
Qoldi: Yandex Delivery API, MinIO/S3 — ixtiyoriy keyingi yaxshilashlar.

---

## Production checklist (chiqishdan oldin)

- [x] `.env` maxfiy, git'da yo'q (`.gitignore`)
- [ ] Admin parollari kuchli, JWT_SECRET tasodifiy va uzun *(deploy'da to'ldiriladi)*
- [x] DB backup avtomatik (`backup` servis) — tiklash skripti bor (`scripts/restore.sh`)
- [ ] Swap yoqilgan (build OOM bo'lmasligi uchun) *(server tayyorlashda — DEPLOY.md)*
- [x] Healthcheck'lar ishlayapti (api `/health`)
- [x] Barcha narx/chegirma hisobi serverда (mijoz tomonda emas)
- [x] Eski/to'lanmagan buyurtmalar avtomatik bekor bo'ladi (`cancel_stale_orders`, 24 soat)

---

## Risklar va e'tibor

- **2GB build OOM** → swap qo'shing yoki CI'da build qiling.
- **Bitta VPS = yagona nuqta** → backup hayotiy muhim. Kengaysangiz
  bazani alohida/managed Postgres'ga ko'chiring.
- **Qo'lda to'lov → soxta chek xavfi** → admin har chekni diqqat bilan
  tasdiqlasin; buyurtma faqat tasdiqdan keyin "to'landi" bo'ladi.
- **Ombor noaniqligi** → har sotuv va har partiya qoldiqni avtomatik
  yangilashi shart (qo'lda tahrir minimal bo'lsin).

---

## Parallel ishlash imkoniyati

- 1-bosqich tugagach, **backend (2-bosqich)** va **admin panel (3-bosqich)**
  ni parallel olib borish mumkin — API shartnomasi (endpoint'lar) kelishilgan bo'lsa.
- Website (5-bosqich) butunlay alohida — istalgan vaqt qo'shiladi.
