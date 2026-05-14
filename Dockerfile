# Образ для развёртывания UnitcodeHR на Render.com и в Docker-средах
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Системные зависимости (pdfplumber требует libmagic, pymorphy3 — gcc для сборки расширений)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh

EXPOSE 8000

# entrypoint.sh при старте делает migrate, collectstatic, loaddata, seed_demo,
# createsuperuser и затем запускает gunicorn. См. scripts/entrypoint.sh.
CMD ["scripts/entrypoint.sh"]
