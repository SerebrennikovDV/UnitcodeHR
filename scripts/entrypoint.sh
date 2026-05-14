#!/usr/bin/env bash
# Стартовая инициализация контейнера на Render:
#   1. migrate          — создать таблицы при первом запуске
#   2. collectstatic    — собрать статику в /app/staticfiles
#   3. loaddata         — справочники (роли, отделы, должности и т.д.)
#   4. seed_demo        — демо-вакансия и 4 тестовых кандидата
#   5. createsuperuser  — admin/admin12345 (на первом запуске)
#   6. gunicorn         — запуск веб-сервера
#
# Каждая под-команда идёт под "|| true", чтобы повторный деплой не падал,
# если данные уже загружены. Миграции и gunicorn — без || true.

set -e

echo '== migrate =='
python manage.py migrate --noinput

echo '== collectstatic =='
python manage.py collectstatic --noinput || true

echo '== loaddata directories =='
python manage.py loaddata \
    fixtures/01_roles.json \
    fixtures/02_departments.json \
    fixtures/03_positions.json \
    fixtures/04_sources.json \
    fixtures/05_stages.json \
    fixtures/06_skills.json || true

echo '== seed_demo =='
python manage.py seed_demo --reset || true

echo '== createsuperuser =='
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}" \
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@unitcode.local}" \
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin12345}" \
python manage.py createsuperuser --noinput || echo '(already exists)'

echo '== gunicorn =='
exec gunicorn unitcode_hr.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
