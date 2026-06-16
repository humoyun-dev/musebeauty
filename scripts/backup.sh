#!/bin/sh
# PostgreSQL backup — pg_dump | gzip. docker-compose 'backup' servisi har kuni chaqiradi.
# Oxirgi 14 nusxa saqlanadi (eskilari o'chiriladi).
set -e

TS=$(date +%Y%m%d_%H%M%S)
OUT="/backups/musebeauty_${TS}.sql.gz"

PGPASSWORD="$DB_PASSWORD" pg_dump -h "${DB_HOST:-postgres}" -U "$DB_USER" -d "$DB_NAME" | gzip > "$OUT"
echo "[backup] tayyor: $OUT ($(du -h "$OUT" | cut -f1))"

# Rotatsiya: 14 tadan ortig'ini o'chiramiz
ls -1t /backups/musebeauty_*.sql.gz 2>/dev/null | tail -n +15 | xargs -r rm -f
