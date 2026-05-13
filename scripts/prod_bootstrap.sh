#!/usr/bin/env bash
# Команды для первой инициализации прод-БД на Render.
# Открыть на Render: Service -> Shell -> вставить этот блок целиком.
#
# Учётка прод-администратора создаётся через DJANGO_SUPERUSER_*-переменные
# окружения, чтобы пароль не оставался в истории shell.
# Замени admin12345 на сложный пароль перед запуском!

set -e

echo '=== 1/3 Применение миграций ==='
python manage.py migrate --noinput

echo
echo '=== 2/3 Загрузка фикстур-справочников ==='
python manage.py loaddata \
    fixtures/01_roles.json \
    fixtures/02_departments.json \
    fixtures/03_positions.json \
    fixtures/04_sources.json \
    fixtures/05_stages.json \
    fixtures/06_skills.json

echo
echo '=== 3/3 Создание суперпользователя ==='
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@unitcode.local \
DJANGO_SUPERUSER_PASSWORD='ChangeMe-Pr0d-2026!' \
python manage.py createsuperuser --noinput || echo '(уже существует — пропускаем)'

echo
echo '=== Готово ==='
echo 'Открой <твой-URL>.onrender.com/admin/ и войди как admin / ChangeMe-Pr0d-2026!'
echo 'СРАЗУ ПОСЛЕ ВХОДА — смени пароль через /admin/accounts/user/1/password/'
