"""Открывает список Databases и показывает значение DATABASE_URL у unitcode-hr."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(m): print(f'[db-check] {m}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1400, 'height': 1000},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            # 1) Databases list
            page.goto('https://dashboard.render.com/databases', wait_until='domcontentloaded')
            time.sleep(5)
            page.screenshot(path='db_list.png', full_page=True)
            Path('db_list.txt').write_text(
                page.locator('main, body').first.inner_text(timeout=10_000),
                encoding='utf-8',
            )
            log('db_list saved')

            # 2) Service Environment — раскрыть глазик у DATABASE_URL
            page.goto('https://dashboard.render.com/web/srv-d82s14jrjlhs73dqg1kg/env',
                      wait_until='domcontentloaded')
            time.sleep(6)

            # Найти строку с DATABASE_URL и кликнуть на eye-кнопку справа
            row = page.locator('text=DATABASE_URL').first
            row.wait_for(state='visible', timeout=10_000)
            # eye-кнопка — visually-hidden, лучше через ближайший button у того же ряда
            try:
                btn = page.locator('input[value="DATABASE_URL"]').first.locator('xpath=ancestor::tr|ancestor::div[1]').locator('button').last
                btn.click()
            except Exception:
                # fallback: жмём все «глазы»
                for b in page.locator('button[aria-label*="reveal" i], button[aria-label*="show" i], button[title*="reveal" i], button[title*="show" i]').all():
                    try: b.click(); time.sleep(0.3)
                    except Exception: pass
            time.sleep(3)
            page.screenshot(path='env_revealed.png', full_page=True)
            Path('env_revealed.txt').write_text(
                page.locator('main, body').first.inner_text(timeout=10_000),
                encoding='utf-8',
            )
            log('env_revealed saved')
            time.sleep(2)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
