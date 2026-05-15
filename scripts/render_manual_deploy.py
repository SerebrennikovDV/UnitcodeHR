"""Нажимает Manual Deploy → Deploy latest commit на странице сервиса."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(m): print(f'[manual] {m}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1400, 'height': 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            log('Открываю unitcode-hr')
            page.goto('https://dashboard.render.com/services', wait_until='domcontentloaded')
            time.sleep(4)
            page.get_by_role('link', name='unitcode-hr').first.click()
            time.sleep(5)
            page.screenshot(path='manual_before.png', full_page=True)

            log('Кликаю Manual Deploy')
            # На Render обычно кнопка "Manual Deploy" открывает выпадающий список
            btn = page.get_by_role('button', name='Manual Deploy').first
            btn.wait_for(state='visible', timeout=10_000)
            btn.click()
            time.sleep(2)
            page.screenshot(path='manual_dropdown.png', full_page=True)

            # Выбираем "Deploy latest commit"
            for label in ('Deploy latest commit', 'Deploy latest', 'Clear build cache & deploy'):
                try:
                    item = page.get_by_role('menuitem', name=label).first
                    item.wait_for(state='visible', timeout=4_000)
                    item.click()
                    log(f'Выбрано: {label}')
                    break
                except Exception:
                    try:
                        item = page.locator(f'text={label}').first
                        item.wait_for(state='visible', timeout=2_000)
                        item.click()
                        log(f'Выбрано (text): {label}')
                        break
                    except Exception:
                        continue
            time.sleep(5)
            page.screenshot(path='manual_after.png', full_page=True)
            log('Готово, deploy запущен')
            time.sleep(5)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
