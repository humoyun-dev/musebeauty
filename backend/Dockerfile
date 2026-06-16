# Backend image — api va bot shu bitta image'dan ishlaydi (faqat command farqli).
FROM python:3.11-slim

# Python: .pyc yozmaydi, stdout/stderr bufersiz (log darhol ko'rinadi)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Avval faqat requirements — Docker layer cache uchun (kod o'zgarsa qayta build emas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keyin qolgan kod
COPY . .

# alembic shu yerdan upgrade qiladi, uvicorn app.main:app ni ishga tushiradi
EXPOSE 8000

# Default command docker-compose'da override qilinadi (api / bot uchun alohida)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
