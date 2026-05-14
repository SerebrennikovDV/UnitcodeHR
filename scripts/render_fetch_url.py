"""Открывает dashboard.render.com → Services и забирает URL сервиса unitcode-hr."""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / '.unitcode-render-profile'


def log(msg): print(f'[fetch] {msg}', flush=True)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={'width': 1280, 'height': 820},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            log('Открываю dashboard.render.com')
            page.goto('https://dashboard.render.com/', wait_until='domcontentloaded')
            time.sleep(5)
            page.screenshot(path='fetch_dashboard.png', full_page=True)

            log('Перехожу на /services')
            page.goto('https://dashboard.render.com/services', wait_until='domcontentloaded')
            time.sleep(5)
            page.screenshot(path='fetch_services.png', full_page=True)

            log('Ищу unitcode-hr')
            link = page.get_by_role('link', name='unitcode-hr').first
            try:
                link.wait_for(state='visible', timeout=10_000)
                link.click()
                time.sleep(6)
                page.screenshot(path='fetch_service.png', full_page=True)
            except Exception:
                log('Не нашёл ссылку unitcode-hr — смотри fetch_services.png')
                return

            # Ищем .onrender.com
            log('Ищу onrender.com URL на странице сервиса')
            for _ in range(20):
                anchors = page.locator('a').all_text_contents()
                for a in anchors:
                    a = a.strip()
                    if '.onrender.com' in a:
                        log(f'НАЙДЕН URL: {a}')
                        Path('render_service_url.txt').write_text(a, encoding='utf-8')
                        return
                # Может URL в input/copy-кнопке
                spans = page.locator('span,div,code').all_text_contents()
                for s in spans:
                    s = s.strip()
                    if '.onrender.com' in s and 'http' in s:
                        log(f'НАЙДЕН URL (span): {s}')
                        Path('render_service_url.txt').write_text(s, encoding='utf-8')
                        return
                time.sleep(5)
            log('URL не найден за 100 сек — смотри fetch_service.png')
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
