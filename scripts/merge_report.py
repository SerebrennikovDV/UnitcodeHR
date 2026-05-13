"""Склеивает 7 частей отчёта в единый файл Серебренников_ПД_Отчет.docx.

Запуск:
    .\\venv\\Scripts\\python.exe scripts\\merge_report.py

ВАЖНО. Титульный лист со штрих-кодом студент вставляет вручную на
первую страницу через Word: ЭУ Витте → выгрузить титульник → вставить
картинкой. Запрещено распознавать титульник или брать чужой и
перебивать ФИО (требование методички, см. Оформление.txt п. 6).

После склейки также вручную:
- собрать автособираемое оглавление (Word: Ссылки → Оглавление);
- проверить сквозную нумерацию страниц и рисунков;
- переработать текст своими словами (антиплагиат).
"""
from pathlib import Path

from docx import Document
from docxcompose.composer import Composer


REPORT_DIR = Path(__file__).resolve().parent.parent.parent  # ~/Desktop/Учеба
PARTS = [
    'Серебренников_ПД_Отчет_часть1.docx',
    'Серебренников_ПД_Отчет_часть2.docx',
    'Серебренников_ПД_Отчет_часть3.docx',
    'Серебренников_ПД_Отчет_часть4.docx',
    'Серебренников_ПД_Отчет_часть5.docx',
    'Серебренников_ПД_Отчет_часть6.docx',
    'Серебренников_ПД_Отчет_часть7.docx',
]
OUT_PATH = REPORT_DIR / 'Серебренников_ПД_Отчет.docx'


def merge():
    paths = [REPORT_DIR / name for name in PARTS]
    for p in paths:
        if not p.exists():
            raise SystemExit(f'Отсутствует часть отчёта: {p.name}')

    base = Document(str(paths[0]))
    composer = Composer(base)
    for p in paths[1:]:
        print(f'  + добавляю {p.name}')
        composer.append(Document(str(p)))

    composer.save(str(OUT_PATH))
    size = OUT_PATH.stat().st_size
    print(f'\nГотово: {OUT_PATH}')
    print(f'Размер: {size:,} байт ({size / 1024 / 1024:.2f} МБ)')


if __name__ == '__main__':
    merge()
