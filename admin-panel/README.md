# MUSE BEAUTY — Admin panel

React + Refine + Ant Design. Backendning `api/admin` endpointlariga ulanadi.
Alohida ilova — production'da Nginx statik fayllarni beradi (Node serveri yo'q).

## Mahalliy dev

```bash
cp .env.example .env       # VITE_API_URL ni backend manziliga moslang
npm install
npm run dev                # http://localhost:5173
```

Backend `docker compose up` bilan ishlab turishi va admin yaratilgan bo'lishi kerak:

```bash
docker compose exec api python -m app.create_admin admin "Parol123" superadmin
```

## Production build

```bash
npm run build              # dist/ — statik fayllar
```

Bu odatda qo'lда qilinmaydi: `nginx/Dockerfile` build bosqichida shu papkani
o'zi build qilib, natijani Nginx orqali `admin.musebeauty.uz` da beradi.

## Tuzilma

- `src/providers/` — `apiClient` (fetch + JWT), `authProvider` (login), `dataProvider` (REST)
- `src/pages/` — orders, payments, products, categories, supply, customers, login
- `src/lib/format.ts` — pul va holat yorliqlari
