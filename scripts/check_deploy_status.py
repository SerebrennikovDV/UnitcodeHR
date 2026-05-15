"""Заходит на страницу сервиса, проверяет последний деплой и забирает свежие логи."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(m): print(f'[check] {m}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1400, 'height': 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            log('Открываю services')
            page.goto('https://dashboard.render.com/services', wait_until='domcontentloaded')
            time.sleep(4)
            link = page.get_by_role('link', name='unitcode-hr').first
            link.wait_for(state='visible', timeout=15_000)
            link.click()
            time.sleep(5)
            page.screenshot(path='deploy_status.png', full_page=True)

            # Events page
            try:
                events = page.get_by_role('link', name='Events').first
                events.wait_for(state='visible', timeout=5_000)
                events.click()
                time.sleep(4)
                page.screenshot(path='deploy_events.png', full_page=True)
                events_text = page.locator('main, body').first.inner_text(timeout=8_000)
                Path('deploy_events.txt').write_text(events_text, encoding='utf-8')
                log('Events сохранены в deploy_events.txt')
            except Exception as e:
                log(f'Events: {e!r}')

            # Logs
            try:
                logs_link = page.get_by_role('link', name='Logs').first
                logs_link.wait_for(state='visible', timeout=5_000)
                logs_link.click()
                time.sleep(8)
                page.screenshot(path='deploy_logs.png', full_page=True)
                logs_text = page.locator('main, body').first.inner_text(timeout=8_000)
                Path('deploy_logs.txt').write_text(logs_text, encoding='utf-8')
                log('Логи сохранены в deploy_logs.txt')
            except Exception as e:
                log(f'Logs: {e!r}')

            time.sleep(2)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
