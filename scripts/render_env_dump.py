"""Открывает Environment у сервиса и сохраняет список переменных."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(m): print(f'[env] {m}', flush=True)


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
            page.get_by_role('link', name='Environment').first.click()
            time.sleep(6)
            page.screenshot(path='env_dump.png', full_page=True)
            Path('env_dump.txt').write_text(
                page.locator('main, body').first.inner_text(timeout=10_000),
                encoding='utf-8',
            )
            log(f'URL: {page.url}')
            log('Готово env_dump.{png,txt}')
            time.sleep(2)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
