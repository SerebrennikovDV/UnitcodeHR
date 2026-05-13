"""Снимает скриншоты ключевых экранов системы UnitcodeHR через Playwright.

Использование:
    1. Запустить runserver в отдельном терминале:
       python manage.py runserver 127.0.0.1:8000 --noreload
    2. В другом терминале выполнить:
       python manage.py take_screenshots

Скриншоты сохраняются в docs/screenshots/ как PNG, viewport 1366x900,
формат полностраничный (full_page=True) — захватывает прокрутку до низа.
"""
from pathlib import Path
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


SCREENSHOTS = [
    # (имя_файла, путь, требует_авторизации, описание)
    ('01_home_public.png',          '/',                          False, 'Главная — открытые вакансии'),
    ('02_login.png',                '/accounts/login/',           False, 'Страница входа'),
    ('03_feedback_public.png',      '/feedback/',                 False, 'Публичная форма обратной связи'),
    ('04_dashboard.png',            '/dashboard/',                True,  'Дашборд HR-аналитики'),
    ('05_vacancies_manage.png',     '/vacancies/',                True,  'Управление вакансиями'),
    ('06_pipeline_board.png',       '/pipeline/',                 True,  'Канбан-доска воронки подбора'),
    ('07_candidates_list.png',      '/candidates/',               True,  'Список кандидатов'),
    ('08_screening_matches.png',    '/screening/matches/',        True,  'Список результатов скрининга'),
    ('09_offers_list.png',          '/offers/',                   True,  'Реестр офферов'),
    ('10_admin_index.png',          '/admin/',                    True,  'Главная страница админ-панели'),
    ('11_admin_skills.png',         '/admin/catalog/skill/',      True,  'Справочник навыков в админке'),
    ('12_admin_users.png',          '/admin/accounts/user/',      True,  'Пользователи в админке'),
]


class Command(BaseCommand):
    help = 'Снимает скриншоты ключевых экранов UnitcodeHR через Playwright.'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', default='http://127.0.0.1:8000',
                              help='Базовый URL запущенного dev-сервера.')
        parser.add_argument('--username', default='admin',
                              help='Логин для авторизованных страниц.')
        parser.add_argument('--password', default='admin12345',
                              help='Пароль для авторизованных страниц.')
        parser.add_argument('--out', default=None,
                              help='Каталог для сохранения скриншотов (по умолчанию docs/screenshots/).')

    def handle(self, *args, **options):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CommandError('Установите playwright: pip install playwright && playwright install chromium') from exc

        base_url = options['base_url'].rstrip('/')
        out_dir = Path(options['out']) if options['out'] else Path(settings.BASE_DIR) / 'docs' / 'screenshots'
        out_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f'Скриншоты будут сохранены в {out_dir}'))

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(viewport={'width': 1366, 'height': 900},
                                            locale='ru-RU')
                page = ctx.new_page()

                self._login(page, base_url, options['username'], options['password'])

                for filename, path, auth_required, description in SCREENSHOTS:
                    url = f'{base_url}{path}'
                    self.stdout.write(f'  -> {filename}: {description} ({url})')
                    try:
                        page.goto(url, wait_until='networkidle', timeout=20000)
                    except Exception as exc:
                        self.stderr.write(self.style.WARNING(
                            f'     Таймаут при загрузке {url}: {exc}'
                        ))
                        continue
                    # Дополнительная задержка для дорисовки Chart.js на дашборде
                    if 'dashboard' in path:
                        time.sleep(1.5)
                    page.screenshot(path=str(out_dir / filename), full_page=True)
            finally:
                browser.close()

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Сохранено {len(SCREENSHOTS)} скриншотов в {out_dir}'
        ))

    def _login(self, page, base_url: str, username: str, password: str) -> None:
        """Программно логинится через форму /accounts/login/, после чего сессия
        сохраняется в контексте и используется для всех последующих переходов."""
        page.goto(f'{base_url}/accounts/login/', wait_until='networkidle')
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
