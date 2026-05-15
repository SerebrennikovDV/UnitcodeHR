"""Открывает в Events ссылку «deploy logs» рядом с failed 3b14add."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'
TARGET = '3b14add'


def log(m): print(f'[failed-logs] {m}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1400, 'height': 1000},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto('https://dashboard.render.com/services', wait_until='domcontentloaded')
            time.sleep(4)
            page.get_by_role('link', name='unitcode-hr').first.click()
            time.sleep(4)
            page.get_by_role('link', name='Events').first.click()
            time.sleep(4)

            log('Ищу ссылку «deploy logs» в записи failed 3b14add')
            # В тексте записи: «Check your deploy logs for more information.» — это ссылка
            link = page.get_by_role('link', name='deploy logs').first
            link.wait_for(state='visible', timeout=10_000)
            link.click()
            time.sleep(8)

            for _ in range(8):
                page.mouse.wheel(0, 4000)
                time.sleep(0.5)

            page.screenshot(path='failed_logs.png', full_page=True)
            Path('failed_logs.txt').write_text(
                page.locator('main, body').first.inner_text(timeout=10_000),
                encoding='utf-8',
            )
            log(f'URL: {page.url}')
            log('Готово, failed_logs.{png,txt}')
            time.sleep(2)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
