# Website (Next.js) — STATIK eksport build.
# Natija host papkaga (./static/website) ko'chiriladi; server'dagi nginx shuni
# beradi (runtime'da Node yo'q — RAM tejaladi).
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY . .
RUN npm run build      # → /app/out (output: export)

# Yengil ko'chiruvchi: ishga tushganda out'ni /output (host papka) ga ko'chiradi va tugaydi.
FROM alpine:3.20
COPY --from=build /app/out /out
CMD ["sh", "-c", "rm -rf /output/* 2>/dev/null; cp -r /out/. /output/ && echo '✅ website statik tayyor'"]
