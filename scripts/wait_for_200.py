"""Опрашивает https://unitcode-hr.onrender.com/ пока не вернёт 200 (или 25 минут).

Пишет статус в wait_for_200.log."""
from pathlib import Path
import sys, time, datetime
import requests

URL = 'https://unitcode-hr.onrender.com/'
LOG = Path('wait_for_200.log')
MAX = 60 * 25  # 25 минут
STEP = 30


def log(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.open('a', encoding='utf-8').write(line + '\n')


def main():
    LOG.write_text('', encoding='utf-8')
    start = time.time()
    while time.time() - start < MAX:
        try:
            r = requests.get(URL, timeout=45)
            log(f'status={r.status_code} len={len(r.text)}')
            if r.status_code == 200 and len(r.text) > 500:
                log('READY!')
                return 0
        except Exception as e:
            log(f'err: {e!r}')
        time.sleep(STEP)
    log('TIMEOUT')
    return 1


if __name__ == '__main__':
    sys.exit(main())
