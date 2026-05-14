"""Автоматический Blueprint-деплой UnitcodeHR на Render через Public Git URL.

Не требует подключения GitHub-аккаунта — Render умеет деплоить публичные
репозитории напрямую по URL.

Запуск:
    .\venv\Scripts\python.exe scripts\render_deploy_public.py
"""
from pathlib import Path
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


PROFILE_DIR = Path.home() / '.unitcode-render-profile'
REPO_URL = 'https://github.com/SerebrennikovDV/UnitcodeHR'


def log(msg: str) -> None:
    print(f'[render-public] {msg}', flush=True)


def fill_public_url(page) -> None:
    log('Перехожу на Blueprint-select')
    page.goto('https://dashboard.render.com/select-repo?type=blueprint',
              wait_until='domcontentloaded')
    time.sleep(3)
    page.screenshot(path='pub_step1.png', full_page=True)

    log(f'Заполняю Public Git Repository: {REPO_URL}')
    inp = page.locator('input[placeholder*="github.com"]').first
    inp.wait_for(state='visible', timeout=15_000)
    inp.click()
    inp.fill(REPO_URL)
    time.sleep(1)
    page.screenshot(path='pub_step2_filled.png', full_page=True)

    log('Жму Continue')
    cont = page.get_by_role('button', name='Continue').first
    cont.wait_for(state='visible', timeout=10_000)
    cont.click()
    time.sleep(5)
    page.screenshot(path='pub_step3_after_continue.png', full_page=True)


def fill_blueprint_name(page, name: str = 'unitcode-hr') -> None:
    log(f'Заполняю Blueprint Name: {name}')
    # Поле сразу после метки "Blueprint Name"
    candidates = [
        'input[name="name"]',
        'input[placeholder*="name" i]',
        'label:has-text("Blueprint Name") + input',
        'text=Blueprint Name >> xpath=../..//input',
    ]
    for sel in candidates:
        try:
            inp = page.locator(sel).first
            inp.wait_for(state='visible', timeout=4_000)
            inp.click()
            inp.fill(name)
            log(f'Заполнено через селектор: {sel}')
            time.sleep(1)
            return
        except PWTimeout:
            continue
    # Fallback — первое видимое пустое текстовое поле на странице
    inp = page.locator('input[type="text"]:visible').first
    inp.click()
    inp.fill(name)
    log('Заполнено через fallback input[type=text]')
    time.sleep(1)


def apply_blueprint(page) -> None:
    fill_blueprint_name(page)
    page.screenshot(path='pub_step4a_name_filled.png', full_page=True)

    log('Ищу финальную кнопку Deploy Blueprint / Apply')
    for label in ('Deploy Blueprint', 'Apply', 'Create New Resources',
                  'Create resources', 'Create Service', 'Create', 'Deploy'):
        try:
            btn = page.get_by_role('button', name=label).first
            btn.wait_for(state='visible', timeout=6_000)
            btn.click()
            log(f'Нажата кнопка: {label}')
            time.sleep(6)
            page.screenshot(path='pub_step5_after_deploy.png', full_page=True)
            return
        except PWTimeout:
            continue
    log('Не нашёл финальную кнопку. Скрин — pub_step5_manual.png')
    page.screenshot(path='pub_step5_manual.png', full_page=True)


def wait_for_service_url(page) -> str | None:
    log('Жду URL сервиса (до 15 мин)…')
    deadline = time.time() + 900
    while time.time() < deadline:
        try:
            anchors = page.locator('a').all_text_contents()
            for a in anchors:
                if '.onrender.com' in a:
                    return a.strip()
        except Exception:
            pass
        time.sleep(8)
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
            fill_public_url(page)
            apply_blueprint(page)
            url = wait_for_service_url(page)
            if url:
                log(f'СЕРВИС: {url}')
                Path('render_service_url.txt').write_text(url, encoding='utf-8')
            else:
                log('URL не получен — смотри pub_step*.png и dashboard')
            time.sleep(30)
        except Exception as exc:
            log(f'Ошибка: {exc!r}')
            try:
                page.screenshot(path='pub_error.png', full_page=True)
            except Exception:
                pass
            raise
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
