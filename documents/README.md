# Docker — ishga tushirish (2 CPU / 2GB RAM)

## Kutilgan papka tuzilmasi

`docker-compose.yml` shu tuzilmani kutadi:

```
docker/
├── docker-compose.yml
├── .env                 # .env.example dan nusxa
├── backend/             # FastAPI + bot kodi (api va bot shu yerdan)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── main.py      # FastAPI ilovasi (api uchun)
│       ├── bot.py       # `python -m app.bot` (bot uchun)
│       └── ...
├── admin-panel/         # React (Vite) admin — nginx build qiladi
│   ├── package.json
│   └── src/
└── nginx/
    ├── Dockerfile
    ├── default.conf
    └── certs/           # fullchain.pem va privkey.pem shu yerda
```

> `backend/app/` va `admin-panel/src/` ichidagi kod hali yozilmagan —
> bu fayllar shu kod uchun infratuzilma. Keyingi qadamda kodni yozamiz.

## Ishga tushirish

```bash
cp .env.example .env        # va qiymatlarni to'ldiring
docker compose build
docker compose up -d
docker compose logs -f api  # migratsiya va api loglarini ko'rish
```

To'xtatish / qayta ishga tushirish:
```bash
docker compose down         # to'xtatadi (ma'lumot saqlanadi)
docker compose up -d --build
```

## SSL sertifikat (bot polling bo'lгани uchun shart emas, lekin admin/website uchun kerak)

Eng oson ikki yo'l:

1. **Certbot (standalone)** — bir marta sertifikat oling, natijani
   `nginx/certs/` ga `fullchain.pem` va `privkey.pem` nomi bilan qo'ying.
2. **Cloudflare** — domenni Cloudflare orqali yo'naltirib, Origin
   sertifikatdan foydalaning (eng kam ovoragarchilik).

Sertifikatsiz sinab ko'rmoqchi bo'lsangiz, `default.conf` dagi `443` ssl
bloklarini vaqtincha `80` ga o'tkazib turing.

## Muhim: kam RAM'da build

React admin'ni build qilish (`npm run build`) build vaqtida bir necha yuz MB
RAM talab qiladi. 2GB serverda ba'zan tig'iz bo'lishi mumkin. Yechimlar:

- **Swap qo'shing** (eng oson, tavsiya etiladi):
  ```bash
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile && sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  ```
- Yoki image'ni kuchliroq mashinada / CI'da build qilib, serverga `push` qiling.

**Ishlash (runtime)** 2GB'da bemalol — yuqoridagi cheklov faqat build paytida.

## Resurslar — erkinlik, lekin minimal iz

Tamoyil: RAM va CPU ga **to'liq erkinlik** beriladi (qattiq `mem_limit`/`cpus`
yo'q), **ammo** har servis minimal iz egallaydi — shuning uchun kam resursli
mashinada ham erkin ishlaydi. Mo'ljal 2 CPU / 2GB, lekin **swap** bilan
~1 CPU / 1GB da ham yuradi.

Nega qattiq cheklov yo'q — bitta ilovali kichik serverda foydadan ko'ra zarar:

- `cpus` cheklovi bo'sh yadroga "burst" qilishni to'sadi — scheduler
  o'zi adolatli taqsimlaydi, cheklov shart emas.
- `mem_limit` qattiq chegara: host'da bo'sh RAM bo'lsa ham konteynerni
  OOM bilan o'ldiradi. Servislar bo'sh RAM ga chiqa olishi kerak.

Minimalni **ilova darajasida** ta'minlaymiz (cgroup emas, dasturning o'zini moslash):

- postgres — `shared_buffers=96MB`, `max_connections=30`, parallel query o'chiq,
  WAL cheklangan (kichik disk uchun)
- redis — `--maxmemory 96mb` (o'zini cheklaydi, diskka yozmaydi)
- uvicorn — 1 worker; SQLAlchemy pool kichik (≈5+5)

Real ishlatish ~500–800M. Bo'sh RAM/CPU bo'lsa — avtomatik foydalanadi.
Zaxira sifatida hostда **swap** yoqing.

> Agar kelajakda memory leak'dan xavotirlansangiz, faqat `api` konteynerga
> **kengroq** `mem_limit` (masalan 512m) qo'shsangiz bo'ladi — leak butun
> mashinani muzlatmasligi uchun. Lekin boshida shart emas.
