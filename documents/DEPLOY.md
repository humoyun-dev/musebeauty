# Production deploy qo'llanmasi (5-bosqich)

2 CPU / 2GB VPS (Ubuntu) uchun bosqichma-bosqich. Buyruqlarning ko'pi uchun
`make` qisqartmalari bor (`Makefile` ga qarang).

---

## 1. Server tayyorlash

```bash
# Docker + compose
curl -fsSL https://get.docker.com | sh

# SWAP (build OOM bo'lmasligi uchun — SHART)
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Domen A-record'larini shu serverga yo'naltiring: `musebeauty.uz`, `www.musebeauty.uz`, `admin.musebeauty.uz`.

---

## 2. Kod va sozlama

```bash
git clone <repo> && cd musebeauty
cp .env.example .env
nano .env          # BOT_TOKEN, ADMIN_TELEGRAM_IDS, DB_PASSWORD, JWT_SECRET,
                   # PAYMENT_CARD_*, domenlar — to'ldiring
```

`JWT_SECRET` uchun: `openssl rand -hex 32`.

---

## 3. Ishga tushirish (SSL'siz, 80-portda)

```bash
make up            # build + docker compose up -d
make logs          # migratsiya va api loglarini ko'rish
make seed          # (ixtiyoriy) minimal: tumanlar + namuna katalog
# YOKI to'liq demo (katalog + admin/Admin12345 + promo + buyurtmalar):
make demo
make admin U=admin P='KuchliParol123' R=superadmin   # o'z admin'ingiz
```

Tekshirish: `http://<server-ip>/` → website (do'kon) ochiladi; bot `/start` ga
javob beradi. (Admin: `admin.<domen>`; website: `<domen>`.)

> **Servislar:** `api`, `bot`, `postgres`, `redis`, `nginx`, `backup`, va
> 2 ta statik-build servisi — **`website`** (musebeauty.uz) va **`admin-panel`**
> (admin.musebeauty.uz). Bu ikkisi bir martalik: statikni build qilib umumiy
> volume'ga ko'chiradi va to'xtaydi (runtime'da ishlamaydi — RAM yemaydi).
> nginx ularni shu volume'lardan beradi.
>
> **Build eslatmasi:** 2 ta frontend (Vite + Next.js) build bo'ladi — 2GB'da tig'iz.
> **Swap shart**. Tig'iz bo'lsa ketma-ket build qiling:
> `docker compose build website && docker compose build admin-panel && docker compose build`
> yoki image'larni CI/kuchliroq mashinada build qilib serverga `push` qiling.

---

## 4. SSL (Let's Encrypt)

Domenlar serverga yo'naltirilgach:

```bash
make ssl D="musebeauty.uz www.musebeauty.uz admin.musebeauty.uz" E=siz@mail.uz
```

Bu certbot orqali sertifikat oladi, `nginx/certs/` ga qo'yadi va nginx'ni qayta
ishga tushiradi (HTTPS avtomatik yoqiladi). **Yangilash** (90 kunda bir) — shu
buyruqni qayta ishga tushiring yoki cron'ga qo'ying:

```cron
0 3 1 */2 * cd /path/musebeauty && CERTBOT_EMAIL=siz@mail.uz ./scripts/init-ssl.sh musebeauty.uz www.musebeauty.uz admin.musebeauty.uz
```

---

## 5. Backup

`backup` servisi avtomatik har 24 soatda `pg_dump` qiladi (`dbbackups` volume,
oxirgi 14 nusxa). Qo'lда:

```bash
make backup            # darhol backup
make restore-list      # nusxalar ro'yxati
# Tiklash:
docker compose exec -T backup sh /scripts/restore.sh /backups/musebeauty_YYYYMMDD_HHMMSS.sql.gz
```

> Tavsiya: backup'larni vaqti-vaqti bilan boshqa serverga/bulut'ga ko'chiring
> (yagona VPS — yagona nuqta).

---

## 6. Payme / Click (avtomatik to'lov)

1. Payme/Click kabinetida merchant yarating, webhook URL bering:
   - Payme:  `https://musebeauty.uz/api/public/payme`
   - Click:  `https://musebeauty.uz/api/public/click/prepare` va `.../complete`
2. `.env` ga kalitlarni qo'ying va yoqing:
   ```
   PAYME_ENABLED=true
   PAYME_KEY=<kassa kaliti>
   CLICK_ENABLED=true
   CLICK_SERVICE_ID=...  CLICK_SECRET_KEY=...
   ```
3. `make restart`.

Payme uchun account maydoni **`order_id`** bo'lishi kerak (kabinetda sozlanadi).
To'lov muvaffaqiyatli bo'lsa buyurtma avtomatik **"to'landi"** ga o'tadi — qo'lда
tasdiq shart emas. (Qo'lда chek usuli ham ishlayveradi.)

---

## 7. Rasm yuklash

Admin panelда mahsulot tahrirlashda "Rasm yuklash" — fayl `media` volume'ga
saqlanadi, nginx `/media/` orqali beradi. Hozir **disk**; kelajakda MinIO/S3
(`STORAGE_BACKEND=s3`, `core/storage.py` da `_save_s3` to'ldiriladi).

---

## 8. Monitoring

- `api` konteynerда healthcheck (`/health`) — `docker compose ps` da holat ko'rinadi.
- Disk/RAM: `df -h`, `free -m`, `docker stats`.
- Loglar: `make logs` yoki `docker compose logs -f bot`.
- APScheduler har kuni 21:00 da adminlarga kunlik hisobot yuboradi; "kam qoldi"
  09:00 da.

---

## Tez-tez buyruqlar

| Buyruq | Vazifa |
|--------|--------|
| `make up` / `make down` | ishga tushirish / to'xtatish |
| `make logs` / `make ps` | loglar / holat |
| `make admin U= P= R=` | admin yaratish |
| `make backup` | qo'lда backup |
| `make ssl D= E=` | SSL sertifikat |
