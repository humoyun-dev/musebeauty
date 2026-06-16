# MUSE BEAUTY — keng tarqalgan amallar uchun qisqa buyruqlar.
# Foydalanish:  make <buyruq>   (masalan: make up, make logs)

.PHONY: help build up down restart logs ps migrate seed admin backup restore-list shell-api shell-db front

help:
	@echo "Buyruqlar:"
	@echo "  make up         - build qilib ishga tushirish (detached)"
	@echo "  make front      - website + admin statikni ./static ga qayta build qilish"
	@echo "  make down       - to'xtatish (ma'lumot saqlanadi)"
	@echo "  make restart    - qayta ishga tushirish"
	@echo "  make logs       - api loglari (migratsiya + so'rovlar)"
	@echo "  make ps         - servislar holati"
	@echo "  make seed       - minimal ma'lumot (tumanlar + katalog)"
	@echo "  make demo       - to'liq demo (katalog+admin+promo+buyurtmalar)"
	@echo "  make admin U=.. P=.. - admin yaratish (R=role ixtiyoriy)"
	@echo "  make backup     - darhol qo'lda backup"
	@echo "  make restore-list - mavjud backup nusxalari"

build:
	docker compose build

# Frontendlarni (website + admin) qayta build qilib statikni ./static ga ko'chiradi.
# Serverdagi nginx shu papkalarni beradi. 2GB'da tig'iz bo'lsa ketma-ket build.
front:
	docker compose build website admin-panel
	docker compose up website admin-panel

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f api

ps:
	docker compose ps

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m app.seed

# To'liq demo (katalog, admin admin/Admin12345, promo, mijoz, buyurtmalar)
demo:
	docker compose exec api python -m app.demo

# make admin U=admin P=Parol123 R=superadmin
admin:
	docker compose exec api python -m app.create_admin "$(U)" "$(P)" "$(R)"

backup:
	docker compose exec backup /scripts/backup.sh

restore-list:
	docker compose exec backup sh -c "ls -1t /backups/kbeauty_*.sql.gz 2>/dev/null || echo 'backup yo''q'"

shell-api:
	docker compose exec api sh

shell-db:
	docker compose exec postgres psql -U $${DB_USER} -d $${DB_NAME}
