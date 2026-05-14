"""Полуавтоматический Blueprint-деплой UnitcodeHR на Render через Playwright.

Откроет реальное окно Chromium с сохранённым профилем. Если ты ещё не
залогинен в Render — нажми «Sign in with GitHub» один раз, дальше скрипт
сам найдёт репозиторий и нажмёт Apply.

Запуск:
    .\venv\Scripts\python.exe scripts\render_deploy.py
"""
from pathlib import Path
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


PROFILE_DIR = Path.home() / '.unitcode-render-profile'
REPO_NAME = 'UnitcodeHR'


def log(msg: str) -> None:
    print(f'[render-deploy] {msg}', flush=True)


def wait_for_login(page) -> None:
    log('Открываю dashboard.render.com')
    page.goto('https://dashboard.render.com', wait_until='domcontentloaded')
    log('Жду, когда ты войдёшь через GitHub OAuth (максимум 5 мин)...')
    # Признак удачного логина: URL содержит /select, /workspaces, /home или /services
    page.wait_for_function(
        """() => {
            const p = location.pathname;
            return p.includes('/select') || p.includes('/services')
                || p.includes('/workspaces') || p.includes('/home')
                || p === '/' && !document.querySelector('input[type=password]');
        }""",
        timeout=300_000,
    )
    log(f'Залогинен. URL: {page.url}')


def open_blueprint_flow(page) -> None:
    log('Перехожу к Blueprint-flow…')
    page.goto('https://dashboard.render.com/select-repo?type=blueprint',
                wait_until='domcontentloaded')
    time.sleep(2)
    page.screenshot(path='render_step1_select_repo.png', full_page=True)
    log('Скрин: render_step1_select_repo.png')


def pick_repository(page) -> None:
    log(f'Ищу репозиторий {REPO_NAME}…')
    # Кнопки/строки с именем репо
    selectors = [
        f'text=/SerebrennikovDV/{REPO_NAME}/',
        f'text=/{REPO_NAME}/',
        f'role=button[name=/{REPO_NAME}/]',
        f'role=link[name=/{REPO_NAME}/]',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state='visible', timeout=8_000)
            loc.click()
            log(f'Кликнул по селектору: {sel}')
            return
        except PWTimeout:
            continue
    # Если репо не показано — возможно нужно настроить permissions
    log('Не нашёл UnitcodeHR в списке. Открой Configure GitHub и разреши доступ к репо.')
    page.screenshot(path='render_step2_no_repo.png', full_page=True)
    raise SystemExit(2)


def apply_blueprint(page) -> None:
    time.sleep(3)
    page.screenshot(path='render_step3_before_apply.png', full_page=True)
    log('Скрин: render_step3_before_apply.png')

    # Пробуем по очереди разные тексты кнопки.
    for label in ('Apply', 'Create New Resources', 'Create resources',
                   'Create Service', 'Connect', 'Deploy'):
        try:
            btn = page.get_by_role('button', name=label).first
            btn.wait_for(state='visible', timeout=4_000)
            btn.click()
            log(f'Нажата кнопка: {label}')
            time.sleep(5)
            page.screenshot(path='render_step4_after_apply.png', full_page=True)
            return
        except PWTimeout:
            continue
    log('Не нашёл кнопку Apply/Create. Покажу скрин — действуй вручную.')
    page.screenshot(path='render_step4_manual.png', full_page=True)


def wait_for_service_url(page) -> str | None:
    log('Жду, когда Render выдаст URL сервиса (до 10 мин)…')
    deadline = time.time() + 600
    while time.time() < deadline:
        # На странице сервиса есть ссылка вида https://<name>-XXXX.onrender.com
        anchors = page.locator('a').all_text_contents()
        for a in anchors:
            if '.onrender.com' in a:
                return a.strip()
        time.sleep(5)
        page.screenshot(path='render_waiting.png', full_page=True)
    return None


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1280, 'height': 820},
            args=['--start-maximized'],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            wait_for_login(page)
            open_blueprint_flow(page)
            pick_repository(page)
            apply_blueprint(page)
            url = wait_for_service_url(page)
            if url:
                log(f'СЕРВИС ПОДНЯТ: {url}')
                Path('render_service_url.txt').write_text(url, encoding='utf-8')
            else:
                log('URL не получен — проверь скрины и dashboard.render.com')
            log('Не закрываю окно браузера 60 секунд — успей всё рассмотреть.')
            time.sleep(60)
        except KeyboardInterrupt:
            log('Отмена пользователем.')
        except Exception as exc:
            log(f'Ошибка: {exc!r}')
            try:
                page.screenshot(path='render_error.png', full_page=True)
            except Exception:
                pass
            raise
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
