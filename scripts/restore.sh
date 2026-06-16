#!/bin/sh
# Backup'dan tiklash. Hostда ishga tushiriladi:
#   docker compose exec -T backup sh /scripts/restore.sh /backups/musebeauty_YYYYMMDD_HHMMSS.sql.gz
# DIQQAT: joriy ma'lumotlar ustiga yoziladi.
set -e

FILE="$1"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    echo "Foydalanish: restore.sh <backup_fayl.sql.gz>"
    echo "Mavjud nusxalar:"
    ls -1t /backups/musebeauty_*.sql.gz 2>/dev/null || echo "  (yo'q)"
    exit 1
fi

echo "[restore] tiklanmoqda: $FILE"
gunzip -c "$FILE" | PGPASSWORD="$DB_PASSWORD" psql -h "${DB_HOST:-postgres}" -U "$DB_USER" -d "$DB_NAME"
echo "[restore] tayyor"
