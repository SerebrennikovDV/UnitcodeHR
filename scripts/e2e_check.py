"""E2E-проверка всех ключевых страниц UnitcodeHR на проде.

1. Ждёт пока главная не ответит 200.
2. Заходит как admin/admin12345.
3. Обходит все URL, на каждом фиксирует HTTP-код и наличие "500/Server Error".
4. Сохраняет скриншот каждой страницы и итоговый отчёт.

Запуск:
    .\\venv\\Scripts\\python.exe scripts\\e2e_check.py
"""
from pathlib import Path
import sys, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE = 'https://unitcode-hr.onrender.com'

GUEST_URLS = [
    ('/', 'home'),
    ('/about/', 'about'),
    ('/help/', 'help'),
    ('/feedback/', 'feedback'),
    ('/accounts/login/', 'login'),
]

AUTH_URLS = [
    ('/dashboard/', 'dashboard'),
    ('/vacancies/', 'vacancies_list'),
    ('/candidates/', 'candidates_list'),
    ('/pipeline/', 'pipeline_board'),
    ('/screening/matches/', 'screening_matches'),
    ('/analytics/', 'analytics'),
    ('/offers/', 'offers'),
    ('/accounts/profile/', 'profile'),
    ('/admin/', 'admin'),
    ('/catalog/skills/', 'catalog_skills'),
    ('/catalog/departments/', 'catalog_departments'),
]

LOGIN = ('admin', 'admin12345')
SCREENS = Path('e2e_screens')
SCREENS.mkdir(exist_ok=True)


def log(m): print(f'[e2e] {m}', flush=True)


def wait_until_live(page, timeout_s=900):
    log(f'Жду пока {BASE}/ ответит 200 (до {timeout_s} сек)')
    deadline = time.time() + timeout_s
    last_status = None
    while time.time() < deadline:
        try:
            r = page.request.get(BASE + '/', timeout=30_000)
            last_status = r.status
            if r.status == 200:
                log(f'LIVE: {r.status}')
                return True
            log(f'  status={r.status}')
        except Exception as e:
            log(f'  exc: {e!r}')
        time.sleep(15)
    log(f'Не ожил за {timeout_s}s, последний код={last_status}')
    return False


def login(page):
    log('Логин admin/admin12345')
    page.goto(BASE + '/accounts/login/', wait_until='domcontentloaded')
    time.sleep(2)
    cur = page.url
    if '/accounts/login' not in cur:
        log(f'Уже залогинен (persistent profile), URL={cur}')
        return True
    page.locator('input[name="username"]').first.fill(LOGIN[0])
    page.locator('input[name="password"]').first.fill(LOGIN[1])
    page.locator('button[type="submit"], input[type="submit"]').first.click()
    page.wait_for_load_state('domcontentloaded')
    time.sleep(3)
    cur = page.url
    log(f'После логина URL={cur}')
    return '/accounts/login' not in cur


def visit(page, path, name):
    url = BASE + path
    try:
        resp = page.goto(url, wait_until='domcontentloaded', timeout=45_000)
        time.sleep(1.5)
        code = resp.status if resp else 0
        title = (page.title() or '')[:80]
        body = page.content().lower()
        bad = any(s in body for s in ['server error (500)', 'internal server error',
                                       'something went wrong', 'traceback', 'exception value'])
        screenshot = SCREENS / f'{name}.png'
        page.screenshot(path=str(screenshot), full_page=True)
        flag = 'OK' if code < 400 and not bad else ('500' if bad else f'HTTP{code}')
        log(f'  [{flag:5}] {path:40} title={title!r}')
        return (path, name, code, bad, title)
    except Exception as e:
        log(f'  [EXC ] {path:40} {e!r}')
        return (path, name, -1, True, str(e)[:80])


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(Path.home() / '.unitcode-render-profile'),
            headless=False,
            viewport={'width': 1280, 'height': 820},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            if not wait_until_live(page, timeout_s=900):
                log('Сайт так и не поднялся, выхожу')
                return

            results = []
            log('--- GUEST PAGES ---')
            for path, name in GUEST_URLS:
                results.append(visit(page, path, 'guest_' + name))

            log('--- LOGIN ---')
            if not login(page):
                log('Логин не прошёл — пропускаю auth-страницы')
            else:
                log('--- AUTH PAGES ---')
                for path, name in AUTH_URLS:
                    results.append(visit(page, path, 'auth_' + name))

            # Сводка
            log('=== ИТОГ ===')
            ok = sum(1 for _, _, c, b, _ in results if c == 200 and not b)
            bad = [r for r in results if r[2] != 200 or r[3]]
            log(f'OK: {ok}/{len(results)}')
            if bad:
                log('Проблемные URL:')
                for path, name, code, bad_flag, title in bad:
                    log(f'  {path}  http={code}  bad={bad_flag}  title={title}')

            Path('e2e_results.txt').write_text(
                '\n'.join(f'{p}\t{n}\t{c}\t{b}\t{t}' for p, n, c, b, t in results),
                encoding='utf-8'
            )
            log('Результаты: e2e_results.txt, скрины: e2e_screens/')
            time.sleep(5)
        finally:
            ctx.close()


if __name__ == '__main__':
    sys.exit(main())
