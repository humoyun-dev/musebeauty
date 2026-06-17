#!/usr/bin/env bash
# Production deploy — GitHub Actions buni server'da ishga tushiradi:
#   ssh ... 'bash -s' < scripts/ci-deploy.sh
#
# Docker faqat backend'ni yuritadi va frontend statikni build qiladi; nginx
# (host) statikni beradi va /api ni 127.0.0.1:8000 ga proxy qiladi.
# Untracked fayllar (.env, docker-compose.override.yml, static/) saqlanadi —
# `git reset --hard` faqat kuzatilgan fayllarga tegadi, `git clean` ishlatilmaydi.
set -euo pipefail

cd /var/www/musebeauty

# docker guruhi yo'q sessiyada sudo'ga tushamiz (ikkisida ham ishlaydi)
SUDO=""
docker info >/dev/null 2>&1 || SUDO="sudo"
DC="$SUDO docker compose"

echo "==> Kodni origin/main ga moslash"
git fetch origin main
git reset --hard origin/main

echo "==> Image'larni build qilish"
$DC build

echo "==> Backend servislar (api startda alembic upgrade head bajaradi)"
$DC up -d postgres redis api bot backup

echo "==> Frontend statik (admin + website — one-shot, ./static ga ko'chiradi)"
$DC up admin-panel website

echo "==> Eski (dangling) image'larni tozalash"
$SUDO docker image prune -f || true

echo "==> Health tekshiruvi"
for i in $(seq 1 12); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "OK — API sog'lom"
    exit 0
  fi
  sleep 3
done
echo "::error:: API /health 36s ichida javob bermadi"
exit 1
