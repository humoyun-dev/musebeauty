# Production deploy qo'llanmasi

2 CPU / 2GB VPS (Ubuntu) uchun bosqichma-bosqich. Buyruqlarning ko'pi uchun
`make` qisqartmalari bor (`Makefile` ga qarang).

> **Arxitektura:** Docker faqat backend'ni yuritadi (`api`, `bot`, `postgres`,
> `redis`, `backup`) va frontend statikni build qiladi. **nginx Docker ichida
> EMAS** — uni serverga (host) o'zingiz o'rnatasiz: u statik fayllarni beradi,
> `/api` ni Docker'dagi API portiga (`127.0.0.1:8000`) proxy qiladi va SSL'ni
> bajaradi. Rasmlar Cloudflare R2'da (`STORAGE_BACKEND=s3`).

---

## 1. Server tayyorlash

```bash
# Docker + compose
curl -fsSL https://get.docker.com | sh

# nginx + certbot (host darajasida — Docker tashqarisida)
sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx

# SWAP (build OOM bo'lmasligi uchun — SHART)
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Domen A-record'larini shu serverga yo'naltiring: `musebeauty.uz`,
`www.musebeauty.uz`, `admin.musebeauty.uz`.

---

## 2. Kod va sozlama

```bash
git clone <repo> && cd musebeauty
cp .env.example .env
nano .env          # BOT_TOKEN, ADMIN_TELEGRAM_IDS, DB_PASSWORD, JWT_SECRET,
                   # PAYMENT_CARD_*, domenlar, S3_* (R2) — to'ldiring
```

`JWT_SECRET` uchun: `openssl rand -hex 32`.

---

## 3. Backend'ni ishga tushirish

```bash
make up            # build + docker compose up -d (api+bot+postgres+redis+backup)
make logs          # migratsiya va api loglarini ko'rish
make seed          # (ixtiyoriy) minimal: tumanlar + namuna katalog
# YOKI to'liq demo (katalog + admin/Admin12345 + promo + buyurtmalar):
make demo
make admin U=admin P='KuchliParol123' R=superadmin   # o'z admin'ingiz
```

API faqat host'ga ochiladi: `http://127.0.0.1:8000` (internetga to'g'ridan
emas). Tekshirish: `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`.

> **Servislar:** `api`, `bot`, `postgres`, `redis`, `backup`, va 2 ta bir
> martalik statik-build servisi — **`website`** (Next.js → `./static/website`)
> va **`admin-panel`** (Vite → `./static/admin`). Bu ikkisi statikni build qilib
> host papkaga ko'chiradi va to'xtaydi (runtime'da ishlamaydi — RAM yemaydi).
> Frontendni qayta build qilish: `make front`.
>
> **Build eslatmasi:** 2 ta frontend (Vite + Next.js) build bo'ladi — 2GB'da
> tig'iz. **Swap shart.** Tig'iz bo'lsa ketma-ket: `docker compose build website`
> keyin `docker compose build admin-panel`. Yoki CI/kuchliroq mashinada build
> qilib serverga ko'chiring.

---

## 4. nginx (host) — statik + API proxy

Frontend statik build qilingach (`make front` → `./static/website`,
`./static/admin`), serverdagi nginx'ni sozlang. Namuna
`/etc/nginx/sites-available/musebeauty`:

```nginx
# ── Website: musebeauty.uz ──
server {
    listen 80;
    server_name musebeauty.uz www.musebeauty.uz;
    root /path/musebeauty/static/website;   # ← repo yo'lini qo'ying
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    # Next.js statik export (trailingSlash: true)
    location / { try_files $uri $uri/ $uri.html /index.html; }
}

# ── Admin: admin.musebeauty.uz ──
server {
    listen 80;
    server_name admin.musebeauty.uz;
    root /path/musebeauty/static/admin;     # ← repo yo'lini qo'ying
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    # Vite SPA — yo'naltirish client-side
    location / { try_files $uri /index.html; }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/musebeauty /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

> Rasmlar R2'dan to'g'ridan (`https://pub-...r2.dev/...`) keladi — nginx
> `/media` ni berishi shart emas. Agar `STORAGE_BACKEND=disk` ishlatsangiz,
> `location /media/ { alias /path/musebeauty/media/; }` qo'shing va
> docker-compose'da `media` volume'ni host papkaga bind qiling.

---

## 5. SSL (Let's Encrypt — host certbot)

Domenlar serverga yo'naltirilgan va nginx ishlab turgach:

```bash
sudo certbot --nginx \
  -d musebeauty.uz -d www.musebeauty.uz -d admin.musebeauty.uz \
  --email siz@mail.uz --agree-tos --no-eff-email
```

certbot 443 server bloklarini va sertifikatni avtomatik qo'shadi. **Yangilash**
avtomatik (certbot systemd timer); tekshirish: `sudo certbot renew --dry-run`.

---

## 6. Backup

`backup` servisi avtomatik har 24 soatda `pg_dump` qiladi (`dbbackups` volume,
oxirgi 14 nusxa). Qo'lda:

```bash
make backup            # darhol backup
make restore-list      # nusxalar ro'yxati
# Tiklash:
docker compose exec -T backup sh /scripts/restore.sh /backups/musebeauty_YYYYMMDD_HHMMSS.sql.gz
```

> Tavsiya: backup'larni vaqti-vaqti bilan boshqa serverga/bulut'ga ko'chiring
> (yagona VPS — yagona nuqta).

---

## 7. Payme / Click (avtomatik to'lov)

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
To'lov muvaffaqiyatli bo'lsa buyurtma avtomatik **"to'landi"** ga o'tadi — qo'lda
tasdiq shart emas. (Qo'lda chek usuli ham ishlayveradi.)

---

## 8. Rasm yuklash (Cloudflare R2)

`STORAGE_BACKEND=s3` — admin panelda yuklangan rasm to'g'ridan R2'ga ketadi va
ommaviy URL (`S3_PUBLIC_URL/...`) qaytadi. Bu URL website, admin va Telegram
botda to'g'ridan ishlaydi. `.env` da `S3_*` to'ldirilgan bo'lishi kerak
(`core/storage.py`). Disk rejimi uchun `STORAGE_BACKEND=disk` (4-bo'limga qarang).

---

## 9. Monitoring

- `api` konteynerda healthcheck (`/health`) — `docker compose ps` da holat ko'rinadi.
- Disk/RAM: `df -h`, `free -m`, `docker stats`.
- Loglar: `make logs` yoki `docker compose logs -f bot`.
- nginx (host): `sudo tail -f /var/log/nginx/{access,error}.log`.
- APScheduler har kuni 21:00 da adminlarga kunlik hisobot yuboradi; "kam qoldi"
  09:00 da.

---

## Tez-tez buyruqlar

| Buyruq | Vazifa |
|--------|--------|
| `make up` / `make down` | ishga tushirish / to'xtatish |
| `make front` | frontend statikni `./static` ga qayta build |
| `make logs` / `make ps` | loglar / holat |
| `make admin U= P= R=` | admin yaratish |
| `make backup` | qo'lda backup |
