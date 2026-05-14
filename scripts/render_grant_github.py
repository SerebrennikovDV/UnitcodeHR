"""Открывает окно Chromium с сохранённым профилем Render и ведёт прямо
на страницу настройки GitHub-permissions, чтобы дать Render доступ к
репозиторию UnitcodeHR. Окно остаётся открытым 10 минут — действуй вручную,
скрипт ничего не кликает.

Запуск:
    .\venv\Scripts\python.exe scripts\render_grant_github.py
"""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright


PROFILE_DIR = Path.home() / '.unitcode-render-profile'


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
            print('[grant-github] Открываю Render Account → GitHub permissions')
            page.goto('https://dashboard.render.com/account/settings',
                      wait_until='domcontentloaded')
            print('[grant-github] Окно открыто. Сделай вручную:')
            print('  1. Найди раздел "GitHub" / "Connected Accounts"')
            print('  2. Нажми "Configure" или "Manage Permissions"')
            print('  3. В открывшемся GitHub: Repository access → выбери UnitcodeHR')
            print('  4. Save')
            print('[grant-github] Жду 10 минут — потом окно закроется.')
            time.sleep(600)
        finally:
            ctx.close()


if __name__ == '__main__':
    main()
