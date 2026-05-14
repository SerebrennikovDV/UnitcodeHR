"""Открывает страницу сервиса unitcode-hr на Render и забирает логи."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(m): print(f'[logs] {m}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1400, 'height': 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            log('Перехожу на services')
            page.goto('https://dashboard.render.com/services', wait_until='domcontentloaded')
            time.sleep(4)

            log('Открываю unitcode-hr')
            link = page.get_by_role('link', name='unitcode-hr').first
            link.wait_for(state='visible', timeout=15_000)
            link.click()
            time.sleep(5)

            log('Перехожу в Logs')
            try:
                logs_link = page.get_by_role('link', name='Logs').first
                logs_link.wait_for(state='visible', timeout=10_000)
                logs_link.click()
            except Exception:
                # Если боковая навигация другая — пробуем по URL
                url = page.url.rstrip('/')
                page.goto(url + '/logs', wait_until='domcontentloaded')
            time.sleep(8)
            page.screenshot(path='render_logs.png', full_page=True)
            log('Скрин: render_logs.png')

            # Дамп текста логов
            try:
                body = page.locator('main, [role="main"], body').first.inner_text(timeout=8_000)
            except Exception:
                body = page.content()
            Path('render_logs_dump.txt').write_text(body, encoding='utf-8')
            log('Логи сохранены в render_logs_dump.txt')
            time.sleep(3)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
