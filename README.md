# MuseBeauty.uz

Go'zallik mahsulotlari uchun onlayn do'kon platformasi: **Telegram bot** (xarid),
**admin panel** (boshqaruv) va **sayt** — bitta backend ustida.

## Imkoniyatlar

- 🛍 **Telegram bot** — katalog, mahsulot albomi (bir nechta rasm), savat,
  buyurtma, qo'lda to'lov (chek yuborish), buyurtma tarixi
- 🧑‍💼 **Admin panel** — mahsulot/kategoriya CRUD, ko'p rasm yuklash, ombor,
  buyurtmalar, aksiyalar va promokodlar, foyda hisobi
- 🌐 **Sayt** — vitrina (editorial K-beauty luxe dizayn)
- 💳 **To'lov** — qo'lda (karta + chek), Payme/Click (ulanishga tayyor)
- 🗂 **Rasm saqlash** — disk (volume) yoki Cloudflare R2 (S3-mos)

## Texnologiyalar

| Qatlam | Stack |
|--------|-------|
| Backend / API | FastAPI, SQLAlchemy (async), Alembic, Pydantic |
| Bot | aiogram 3 (FSM — Redis) |
| Baza / kesh | PostgreSQL (asyncpg), Redis |
| Admin panel | React, Vite, Refine, Ant Design |
| Rejalashtirish | APScheduler |
| Saqlash | disk / Cloudflare R2 (boto3) |
| Infratuzilma | Docker Compose (nginx server'da, Docker tashqarisida) |

## Tuzilma

```
backend/          FastAPI + aiogram bot (app/), Alembic migratsiyalari
admin-panel/      React (Vite + Refine + AntD) admin
website/          Vitrina sayt
static/           Frontend statik build chiqishi (server'dagi nginx beradi)
scripts/          backup / restore
documents/        Arxitektura, deploy, reja
docker-compose.yml
```

## Ishga tushirish

```bash
cp .env.example .env     # qiymatlarni to'ldiring (bot token, DB, R2 ...)
make build               # image'larni quradi
make migrate             # alembic upgrade head
make up                  # barcha servislarni ko'taradi
make logs                # loglar
```

Batafsil: [`documents/DEPLOY.md`](documents/DEPLOY.md) va
[`documents/arxitektura.md`](documents/arxitektura.md).

## Sozlash (.env)

Barcha sozlamalar `.env` orqali — namuna va izohlar [`.env.example`](.env.example) da.
Maxfiy qiymatlar (token, parol, kalitlar) repozitoriyga **kiritilmaydi**.

## Litsenziya

Xususiy loyiha. Barcha huquqlar himoyalangan.
