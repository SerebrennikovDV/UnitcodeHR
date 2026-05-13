"""Извлечение текста из файлов резюме (.pdf, .docx, .txt)."""
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(file_path: str) -> str:
    """Возвращает чистый текст файла резюме.

    Поддерживаемые форматы — PDF, DOCX, TXT. При невозможности извлечения
    возвращается пустая строка (вызывающий код помещает в реасоны причину).
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning('Файл не найден: %s', file_path)
        return ''

    ext = path.suffix.lower()
    try:
        if ext == '.pdf':
            return _extract_pdf(path)
        elif ext == '.docx':
            return _extract_docx(path)
        elif ext == '.txt':
            return path.read_text(encoding='utf-8', errors='ignore')
        else:
            logger.warning('Неподдерживаемый формат: %s', ext)
            return ''
    except Exception as exc:
        logger.error('Ошибка извлечения текста из %s: %s', file_path, exc)
        return ''


def _extract_pdf(path: Path) -> str:
    """Извлекает текст из PDF через pdfplumber."""
    import pdfplumber
    parts = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or '')
    return '\n'.join(parts)


def _extract_docx(path: Path) -> str:
    """Извлекает текст из DOCX через python-docx."""
    from docx import Document
    doc = Document(str(path))
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())


def extract_experience_years(text: str) -> float | None:
    """Извлекает общий стаж работы из текста резюме.

    Применяются разные паттерны типичных формулировок на русском языке:
        «опыт работы 5 лет», «5 лет опыта», «более 3 лет», «стаж — 7+ лет»,
        «work experience: 4 years» и т.п. При наличии нескольких упоминаний
        берётся максимальное значение.
    """
    if not text:
        return None
    lowered = text.lower().replace('ё', 'е')
    candidates = []

    patterns = [
        r'опыт\s+работы[^0-9]{0,30}(\d{1,2})\+?\s*(?:год|лет|года)',
        r'(\d{1,2})\+?\s*(?:год|лет|года)\s+опыта',
        r'стаж[^0-9]{0,20}(\d{1,2})\+?\s*(?:год|лет|года)',
        r'более\s+(\d{1,2})\s*(?:год|лет|года)',
        r'опыт[^0-9]{0,30}(\d{1,2})\s*\+?\s*(?:год|лет|года)',
        r'(\d{1,2})\+?\s*year[s]?\s+(?:of\s+)?experience',
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, lowered):
            try:
                val = float(m.group(1))
                if 0 < val < 60:
                    candidates.append(val)
            except (ValueError, IndexError):
                continue

    # Альтернативный путь — суммирование периодов «с 2019 по 2024» / «2020-2024»
    for m in re.finditer(r'(\d{4})\s*[-–—]\s*(\d{4}|по\s+(?:наст|сегодн|тек))', lowered):
        from datetime import date
        start = int(m.group(1))
        end_raw = m.group(2)
        end = int(end_raw) if end_raw.isdigit() else date.today().year
        diff = end - start
        if 0 < diff < 60:
            candidates.append(float(diff))

    return max(candidates) if candidates else None
