# Гид по коммитам репозитория UnitcodeHR

Рубрика преддипломной практики требует ≥ 50 коммитов от имени автора,
отражающих итеративное развитие проекта. Ниже приведён рекомендуемый
порядок коммитов — выполняй по списку, и у тебя получится живая
история разработки на 60+ коммитов.

> **Важно:** не используй обнуляющие коммиты («добавил пустую строку, удалил пустую строку»)
> — рубрика их явно запрещает. Каждый коммит должен содержать смысловое изменение.

## Подготовка к первому коммиту

1. Открой терминал в папке `UnitcodeHR/`.
2. Создай личный Personal Access Token на GitHub:
   - Перейди на `github.com/settings/tokens` → Generate new token (classic)
   - Scope: `repo` (только это)
   - Сохрани в безопасном месте — пароль mail.ru, который ты раньше отправил, **не используется**.
3. Настрой git один раз:

```bash
git config --global user.name "Серебренников Дмитрий"
git config --global user.email "kirillborovenko06@gmail.com"   # или другая твоя личная почта
```

4. Инициализация:

```bash
git init
git remote add origin https://github.com/SerebrennikovDV/UnitcodeHR.git
git branch -M main
```

## Этап 1. Скелет проекта (5 коммитов)

```bash
# 1
git add .gitignore .env.example
git commit -m "chore: initial gitignore and env example"

# 2
git add requirements.txt
git commit -m "chore: pin Python dependencies in requirements.txt"

# 3
git add Dockerfile render.yaml
git commit -m "chore(deploy): Dockerfile and render.yaml for deployment"

# 4
git add main.py manage.py
git commit -m "chore: main.py wrapper and Django manage.py"

# 5
git add README.md
git commit -m "docs: project README with overview and install instructions"
```

## Этап 2. Конфигурация Django (4 коммита)

```bash
# 6
git add unitcode_hr/__init__.py unitcode_hr/wsgi.py unitcode_hr/asgi.py
git commit -m "feat(config): WSGI/ASGI entrypoints"

# 7
git add unitcode_hr/settings.py
git commit -m "feat(config): base settings with apps, middleware, templates, db"

# 8
git add unitcode_hr/urls.py
git commit -m "feat(config): root URL routing"

# 9
git add apps/__init__.py apps/core/__init__.py apps/core/apps.py apps/core/admin.py
git commit -m "feat(core): core app skeleton with admin branding"
```

## Этап 3. Приложение core (5 коммитов)

```bash
# 10
git add apps/core/models.py
git commit -m "feat(core): TimeStampedModel and SoftDeleteModel abstracts"

# 11
git add apps/core/views.py apps/core/urls_dashboard.py
git commit -m "feat(core): home, healthz, about, help and dashboard views"

# 12
git add apps/core/context_processors.py
git commit -m "feat(core): site_info global context processor"

# 13
git add apps/core/templatetags/__init__.py apps/core/templatetags/dict_extras.py
git commit -m "feat(core): template tag get_item for dict lookups"

# 14
git add templates/base.html templates/core/home.html templates/core/dashboard.html \
        templates/core/about.html templates/core/help.html
git commit -m "feat(core): Bootstrap 5 base template, home, dashboard, help, about"
```

## Этап 4. Приложение accounts (6 коммитов)

```bash
# 15
git add apps/accounts/__init__.py apps/accounts/apps.py apps/accounts/migrations/__init__.py
git commit -m "feat(accounts): create accounts app"

# 16
git add apps/accounts/models.py
git commit -m "feat(accounts): Role and custom User models"

# 17
git add apps/accounts/admin.py
git commit -m "feat(accounts): admin for User and Role with extra fields"

# 18
git add apps/accounts/forms.py
git commit -m "feat(accounts): LoginForm and ProfileForm"

# 19
git add apps/accounts/views.py apps/accounts/urls.py
git commit -m "feat(accounts): login, logout, profile views and URLs"

# 20
git add apps/accounts/decorators.py templates/accounts/login.html templates/accounts/profile.html
git commit -m "feat(accounts): role_required decorator and login/profile templates"
```

## Этап 5. Приложение catalog (5 коммитов)

```bash
# 21
git add apps/catalog/__init__.py apps/catalog/apps.py apps/catalog/migrations/__init__.py
git commit -m "feat(catalog): create catalog app"

# 22
git add apps/catalog/models.py
git commit -m "feat(catalog): Department, Position, Source, Stage, Skill models"

# 23
git add apps/catalog/admin.py
git commit -m "feat(catalog): admin for all reference models"

# 24
git add apps/catalog/views.py apps/catalog/urls.py
git commit -m "feat(catalog): list views for skills and departments"

# 25
git add templates/catalog/skill_list.html templates/catalog/department_list.html
git commit -m "feat(catalog): templates for skill and department lists"
```

## Этап 6. Приложение vacancies (5 коммитов)

```bash
# 26
git add apps/vacancies/__init__.py apps/vacancies/apps.py apps/vacancies/migrations/__init__.py
git commit -m "feat(vacancies): create vacancies app"

# 27
git add apps/vacancies/models.py
git commit -m "feat(vacancies): HiringRequest, Vacancy, VacancySkill models"

# 28
git add apps/vacancies/admin.py
git commit -m "feat(vacancies): admin with publish/archive bulk actions"

# 29
git add apps/vacancies/forms.py apps/vacancies/views.py apps/vacancies/urls.py
git commit -m "feat(vacancies): CRUD views for hiring requests and vacancies"

# 30
git add templates/vacancies/*.html
git commit -m "feat(vacancies): templates incl. public vacancy page"
```

## Этап 7. Приложение candidates (5 коммитов)

```bash
# 31
git add apps/candidates/__init__.py apps/candidates/apps.py apps/candidates/migrations/__init__.py
git commit -m "feat(candidates): create candidates app"

# 32
git add apps/candidates/models.py
git commit -m "feat(candidates): Candidate, Resume, CandidateSkill models"

# 33
git add apps/candidates/admin.py
git commit -m "feat(candidates): admin with archive_inactive action"

# 34
git add apps/candidates/forms.py apps/candidates/views.py apps/candidates/urls.py
git commit -m "feat(candidates): public application form with dedup logic"

# 35
git add templates/candidates/*.html
git commit -m "feat(candidates): templates for list, detail and public apply form"
```

## Этап 8. Приложение pipeline (5 коммитов)

```bash
# 36
git add apps/pipeline/__init__.py apps/pipeline/apps.py apps/pipeline/migrations/__init__.py
git commit -m "feat(pipeline): create pipeline app"

# 37
git add apps/pipeline/models.py
git commit -m "feat(pipeline): Application, StageHistory, Interview models"

# 38
git add apps/pipeline/admin.py
git commit -m "feat(pipeline): admin for applications, history and interviews"

# 39
git add apps/pipeline/signals.py
git commit -m "feat(pipeline): signals fix stage history and trigger screening"

# 40
git add apps/pipeline/views.py apps/pipeline/urls.py templates/pipeline/*.html
git commit -m "feat(pipeline): kanban board, application detail, restore, interview schedule"
```

## Этап 9. Приложение offers (4 коммита)

```bash
# 41
git add apps/offers/__init__.py apps/offers/apps.py apps/offers/migrations/__init__.py
git commit -m "feat(offers): create offers app"

# 42
git add apps/offers/models.py apps/offers/admin.py
git commit -m "feat(offers): Offer and Hire models with admin actions"

# 43
git add apps/offers/services.py
git commit -m "feat(offers): generate_offer_docx service via python-docx"

# 44
git add apps/offers/views.py apps/offers/urls.py templates/offers/*.html
git commit -m "feat(offers): list, detail, download and regenerate docx views"
```

## Этап 10. Подсистема скрининга и коннекторы (8 коммитов)

```bash
# 45
git add apps/screening/__init__.py apps/screening/apps.py apps/screening/migrations/__init__.py
git commit -m "feat(screening): create screening app"

# 46
git add apps/screening/models.py apps/screening/admin.py
git commit -m "feat(screening): ResumeParse, Match, ExternalVacancy models"

# 47
git add apps/screening/parser.py
git commit -m "feat(screening): resume parser with experience extraction"

# 48
git add apps/screening/lemmatizer.py
git commit -m "feat(screening): Russian lemmatizer wrapper over pymorphy3"

# 49
git add apps/screening/scorer.py
git commit -m "feat(screening): score calculator with TF-IDF + experience bonus"

# 50
git add apps/screening/services.py
git commit -m "feat(screening): orchestrator services (parse, score, enrich)"

# 51
git add apps/screening/views.py apps/screening/urls.py templates/screening/*.html
git commit -m "feat(screening): match_list, recalculate and enrich views"

# 52
git add connectors/__init__.py connectors/base.py connectors/hh.py \
        connectors/superjob.py connectors/avito.py \
        connectors/fixtures/*.json
git commit -m "feat(connectors): BaseVacancyConnector + HH/SJ/Avito mock implementations"
```

## Этап 11. Аналитика, обратная связь, аудит (5 коммитов)

```bash
# 53
git add apps/analytics/__init__.py apps/analytics/apps.py apps/analytics/migrations/__init__.py \
        apps/analytics/models.py apps/analytics/admin.py
git commit -m "feat(analytics): create analytics app skeleton"

# 54
git add apps/analytics/services.py
git commit -m "feat(analytics): time_to_hire, source_of_hire, funnel, cost_per_hire metrics"

# 55
git add apps/analytics/views.py apps/analytics/urls.py templates/analytics/dashboard.html
git commit -m "feat(analytics): dashboard with Chart.js and xlsx export"

# 56
git add apps/feedback/__init__.py apps/feedback/apps.py apps/feedback/migrations/__init__.py \
        apps/feedback/models.py apps/feedback/admin.py apps/feedback/forms.py \
        apps/feedback/views.py apps/feedback/urls.py templates/feedback/form.html
git commit -m "feat(feedback): feedback form for public visitors with admin moderation"

# 57
git add apps/audit/__init__.py apps/audit/apps.py apps/audit/migrations/__init__.py \
        apps/audit/models.py apps/audit/admin.py apps/audit/middleware.py
git commit -m "feat(audit): ActionLog model and middleware for HTTP-level auditing"
```

## Этап 12. Стили, фикстуры, документация (5+ коммитов)

```bash
# 58
git add static/css/app.css static/js/app.js
git commit -m "feat(ui): corporate CSS and JS"

# 59
git add fixtures/01_roles.json fixtures/02_departments.json
git commit -m "feat(fixtures): roles and departments seed data"

# 60
git add fixtures/03_positions.json fixtures/04_sources.json fixtures/05_stages.json
git commit -m "feat(fixtures): positions, sources, stages seed data"

# 61
git add fixtures/06_skills.json
git commit -m "feat(fixtures): 25 IT-skills with aliases"

# 62
git add fixtures/07_demo_users.json fixtures/README.md
git commit -m "feat(fixtures): demo users template and seed instructions"

# 63
git add docs/GIT_COMMITS_GUIDE.md
git commit -m "docs: git commit guide"
```

## Этап 13. Миграции (несколько коммитов после `makemigrations`)

После того, как все приложения добавлены, выполни:

```bash
python main.py makemigrations
git add apps/*/migrations/0001_initial.py
git commit -m "chore(db): initial migrations for all apps"

python main.py migrate
# Если потребуется, после правок моделей:
python main.py makemigrations
git add apps/<app>/migrations/0002_*.py
git commit -m "chore(db): <конкретное изменение>"
```

## Отправка в GitHub

```bash
git push -u origin main
```

При первом push GitHub предложит ввести логин/пароль — введи имя пользователя
и **PAT-токен** (не пароль от mail.ru!).

---

**Готово**: получишь 60+ коммитов с осмысленной историей.

Скрывай реальные креды (`.env`) — они уже в `.gitignore`.

После последнего push скопируй ссылку
`https://github.com/SerebrennikovDV/UnitcodeHR` в отчёт по практике
(раздел 1.1 «Исходные данные»).
