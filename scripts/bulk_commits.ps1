# Скрипт массового коммита по docs/GIT_COMMITS_GUIDE.md.

$ErrorActionPreference = 'Continue'
Set-Location $PSScriptRoot\..

# CRLF-предупреждения от git подавляем глобально.
git config --local core.autocrlf true | Out-Null

function Do-Commit {
    param([string]$Message, [string[]]$Files)
    $valid = @()
    foreach ($f in $Files) {
        $items = Get-ChildItem -Path $f -ErrorAction SilentlyContinue
        if ($items) { $valid += $items.FullName }
    }
    if (-not $valid) {
        Write-Host "  SKIP $Message - no matching files"
        return
    }
    $null = git add -- $valid 2>&1
    $st = git status --porcelain | Where-Object { $_ -match '^[AM]' }
    if (-not $st) {
        Write-Host "  SKIP $Message - nothing staged"
        return
    }
    $out = git commit -m $Message 2>&1
    $code = $LASTEXITCODE
    if ($code -eq 0) {
        Write-Host "  OK   $Message"
    } else {
        Write-Host "  FAIL $Message (exit $code)"
        Write-Host ($out -join "`n")
    }
}

$commits = @(
    @{ msg = 'chore: initial gitignore and env example'; files = @('.gitignore', '.env.example') }
    @{ msg = 'chore: pin Python dependencies in requirements.txt'; files = @('requirements.txt') }
    @{ msg = 'chore(deploy): Dockerfile and render.yaml for deployment'; files = @('Dockerfile', 'render.yaml') }
    @{ msg = 'chore: main.py wrapper and Django manage.py'; files = @('main.py', 'manage.py') }
    @{ msg = 'docs: project README with overview and install instructions'; files = @('README.md') }
    @{ msg = 'feat(config): WSGI/ASGI entrypoints'; files = @('unitcode_hr/__init__.py', 'unitcode_hr/wsgi.py', 'unitcode_hr/asgi.py') }
    @{ msg = 'feat(config): base settings with apps, middleware, templates, db'; files = @('unitcode_hr/settings.py') }
    @{ msg = 'feat(config): root URL routing'; files = @('unitcode_hr/urls.py') }
    @{ msg = 'feat(core): core app skeleton with admin branding'; files = @('apps/__init__.py', 'apps/core/__init__.py', 'apps/core/apps.py', 'apps/core/admin.py') }
    @{ msg = 'feat(core): models for core app'; files = @('apps/core/models.py') }
    @{ msg = 'feat(core): home, healthz, about, help and dashboard views'; files = @('apps/core/views.py', 'apps/core/urls_dashboard.py') }
    @{ msg = 'feat(core): site_info global context processor'; files = @('apps/core/context_processors.py') }
    @{ msg = 'feat(core): template tag get_item for dict lookups'; files = @('apps/core/templatetags/__init__.py', 'apps/core/templatetags/dict_extras.py') }
    @{ msg = 'feat(core): Bootstrap 5 base template, home, dashboard, help, about'; files = @('templates/base.html', 'templates/core') }
    @{ msg = 'feat(accounts): create accounts app'; files = @('apps/accounts/__init__.py', 'apps/accounts/apps.py') }
    @{ msg = 'feat(accounts): Role and custom User models'; files = @('apps/accounts/models.py') }
    @{ msg = 'feat(accounts): admin for User and Role with extra fields'; files = @('apps/accounts/admin.py') }
    @{ msg = 'feat(accounts): LoginForm and ProfileForm'; files = @('apps/accounts/forms.py') }
    @{ msg = 'feat(accounts): login, logout, profile views and URLs'; files = @('apps/accounts/views.py', 'apps/accounts/urls.py') }
    @{ msg = 'feat(accounts): role_required decorator and login/profile templates'; files = @('apps/accounts/decorators.py', 'templates/accounts') }
    @{ msg = 'feat(catalog): create catalog app'; files = @('apps/catalog/__init__.py', 'apps/catalog/apps.py') }
    @{ msg = 'feat(catalog): Department, Position, Source, Stage, Skill models'; files = @('apps/catalog/models.py') }
    @{ msg = 'feat(catalog): admin for all reference models'; files = @('apps/catalog/admin.py') }
    @{ msg = 'feat(catalog): list views for skills and departments'; files = @('apps/catalog/views.py', 'apps/catalog/urls.py') }
    @{ msg = 'feat(catalog): templates for skill and department lists'; files = @('templates/catalog') }
    @{ msg = 'feat(vacancies): create vacancies app'; files = @('apps/vacancies/__init__.py', 'apps/vacancies/apps.py') }
    @{ msg = 'feat(vacancies): HiringRequest, Vacancy, VacancySkill models'; files = @('apps/vacancies/models.py') }
    @{ msg = 'feat(vacancies): admin with publish/archive bulk actions'; files = @('apps/vacancies/admin.py') }
    @{ msg = 'feat(vacancies): CRUD views for hiring requests and vacancies'; files = @('apps/vacancies/forms.py', 'apps/vacancies/views.py', 'apps/vacancies/urls.py') }
    @{ msg = 'feat(vacancies): templates incl. public vacancy page'; files = @('templates/vacancies') }
    @{ msg = 'feat(candidates): create candidates app'; files = @('apps/candidates/__init__.py', 'apps/candidates/apps.py') }
    @{ msg = 'feat(candidates): Candidate, Resume, CandidateSkill models'; files = @('apps/candidates/models.py') }
    @{ msg = 'feat(candidates): admin with archive_inactive action'; files = @('apps/candidates/admin.py') }
    @{ msg = 'feat(candidates): public application form with dedup logic'; files = @('apps/candidates/forms.py', 'apps/candidates/views.py', 'apps/candidates/urls.py') }
    @{ msg = 'feat(candidates): templates for list, detail and public apply form'; files = @('templates/candidates') }
    @{ msg = 'feat(pipeline): create pipeline app'; files = @('apps/pipeline/__init__.py', 'apps/pipeline/apps.py') }
    @{ msg = 'feat(pipeline): Application, StageHistory, Interview models'; files = @('apps/pipeline/models.py') }
    @{ msg = 'feat(pipeline): admin for applications, history and interviews'; files = @('apps/pipeline/admin.py') }
    @{ msg = 'feat(pipeline): signals fix stage history and trigger screening'; files = @('apps/pipeline/signals.py') }
    @{ msg = 'feat(pipeline): kanban board, application detail, restore, interview schedule'; files = @('apps/pipeline/views.py', 'apps/pipeline/urls.py', 'templates/pipeline') }
    @{ msg = 'feat(offers): create offers app'; files = @('apps/offers/__init__.py', 'apps/offers/apps.py') }
    @{ msg = 'feat(offers): Offer and Hire models with admin actions'; files = @('apps/offers/models.py', 'apps/offers/admin.py') }
    @{ msg = 'feat(offers): generate_offer_docx service via python-docx'; files = @('apps/offers/services.py') }
    @{ msg = 'feat(offers): list, detail, download and regenerate docx views'; files = @('apps/offers/views.py', 'apps/offers/urls.py', 'templates/offers') }
    @{ msg = 'feat(screening): create screening app'; files = @('apps/screening/__init__.py', 'apps/screening/apps.py') }
    @{ msg = 'feat(screening): ResumeParse, Match, ExternalVacancy models'; files = @('apps/screening/models.py', 'apps/screening/admin.py') }
    @{ msg = 'feat(screening): resume parser with experience extraction'; files = @('apps/screening/parser.py') }
    @{ msg = 'feat(screening): Russian lemmatizer wrapper over pymorphy3'; files = @('apps/screening/lemmatizer.py') }
    @{ msg = 'feat(screening): score calculator with TF-IDF + experience bonus'; files = @('apps/screening/scorer.py') }
    @{ msg = 'feat(screening): orchestrator services (parse, score, enrich)'; files = @('apps/screening/services.py') }
    @{ msg = 'feat(screening): match_list, recalculate and enrich views'; files = @('apps/screening/views.py', 'apps/screening/urls.py', 'templates/screening') }
    @{ msg = 'feat(connectors): BaseVacancyConnector and HH/SJ/Avito mock implementations'; files = @('connectors') }
    @{ msg = 'feat(analytics): create analytics app skeleton'; files = @('apps/analytics/__init__.py', 'apps/analytics/apps.py', 'apps/analytics/models.py', 'apps/analytics/admin.py') }
    @{ msg = 'feat(analytics): time_to_hire, source_of_hire, funnel, cost_per_hire metrics'; files = @('apps/analytics/services.py') }
    @{ msg = 'feat(analytics): dashboard with Chart.js and xlsx export'; files = @('apps/analytics/views.py', 'apps/analytics/urls.py', 'templates/analytics') }
    @{ msg = 'feat(feedback): feedback form for public visitors with admin moderation'; files = @('apps/feedback/__init__.py', 'apps/feedback/apps.py', 'apps/feedback/models.py', 'apps/feedback/admin.py', 'apps/feedback/forms.py', 'apps/feedback/views.py', 'apps/feedback/urls.py', 'templates/feedback') }
    @{ msg = 'feat(audit): ActionLog model and middleware for HTTP-level auditing'; files = @('apps/audit/__init__.py', 'apps/audit/apps.py', 'apps/audit/models.py', 'apps/audit/admin.py', 'apps/audit/middleware.py') }
    @{ msg = 'feat(ui): corporate CSS and JS'; files = @('static/css', 'static/js') }
    @{ msg = 'feat(fixtures): roles and departments seed data'; files = @('fixtures/01_roles.json', 'fixtures/02_departments.json') }
    @{ msg = 'feat(fixtures): positions, sources, stages seed data'; files = @('fixtures/03_positions.json', 'fixtures/04_sources.json', 'fixtures/05_stages.json') }
    @{ msg = 'feat(fixtures): 25 IT-skills with aliases'; files = @('fixtures/06_skills.json') }
    @{ msg = 'feat(fixtures): demo users template and seed instructions'; files = @('fixtures/07_demo_users.json', 'fixtures/README.md') }
    @{ msg = 'docs: git commit guide'; files = @('docs/GIT_COMMITS_GUIDE.md') }
    @{ msg = 'chore(db): initial migrations for accounts and catalog'; files = @('apps/accounts/migrations', 'apps/catalog/migrations') }
    @{ msg = 'chore(db): initial migrations for vacancies and candidates'; files = @('apps/vacancies/migrations', 'apps/candidates/migrations') }
    @{ msg = 'chore(db): initial migrations for pipeline, offers, screening'; files = @('apps/pipeline/migrations', 'apps/offers/migrations', 'apps/screening/migrations') }
    @{ msg = 'chore(db): initial migrations for feedback, audit, analytics'; files = @('apps/feedback/migrations', 'apps/audit/migrations', 'apps/analytics/migrations') }
    @{ msg = 'chore(db): empty core migrations folder'; files = @('apps/core/migrations') }
    @{ msg = 'fix(pipeline): load dict_extras and clean kanban board template'; files = @('templates/pipeline/board.html') }
    @{ msg = 'feat(core): seed_demo management command for vacancy and 4 test candidates'; files = @('apps/core/management/__init__.py', 'apps/core/management/commands/__init__.py', 'apps/core/management/commands/seed_demo.py') }
    @{ msg = 'feat(core): take_screenshots management command via Playwright'; files = @('apps/core/management/commands/take_screenshots.py') }
    @{ msg = 'docs: UI screenshots collected during practice (12 PNG)'; files = @('docs/screenshots') }
    @{ msg = 'chore: report generators (parts 6, 7, merge) for graduation practice'; files = @('scripts/make_part6.py', 'scripts/make_part7.py', 'scripts/merge_report.py') }
)

foreach ($c in $commits) {
    Do-Commit -Message $c.msg -Files $c.files
}

Write-Host ""
$count = (git log --oneline | Measure-Object).Count
Write-Host "Всего коммитов: $count"
