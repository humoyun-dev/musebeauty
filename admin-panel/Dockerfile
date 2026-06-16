# Admin panel (React + Vite) — STATIK build.
# Natija host papkaga (./static/admin) ko'chiriladi; server'dagi nginx shuni
# beradi (runtime'da Node yo'q — RAM tejaladi).
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY . .
RUN npm run build      # → /app/dist

# Yengil ko'chiruvchi: ishga tushganda dist'ni /output (host papka) ga ko'chiradi va tugaydi.
FROM alpine:3.20
COPY --from=build /app/dist /dist
CMD ["sh", "-c", "rm -rf /output/* 2>/dev/null; cp -r /dist/. /output/ && echo '✅ admin statik tayyor'"]
