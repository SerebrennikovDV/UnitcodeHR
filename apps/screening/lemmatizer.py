"""Лемматизация русского текста через pymorphy3."""
import re
from functools import lru_cache

try:
    import pymorphy3
    _morph = pymorphy3.MorphAnalyzer()
except ImportError:  # pragma: no cover
    _morph = None


_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё0-9\+\-_\.#]*", re.UNICODE)


@lru_cache(maxsize=50_000)
def lemmatize_word(word: str) -> str:
    """Возвращает нормальную (словарную) форму слова. Кэшируется LRU.

    Для англоязычных слов и аббревиатур возвращается lowercase без изменений
    (pymorphy3 для них не нужен).
    """
    if not word:
        return ''
    if _morph is None or not re.search(r'[А-Яа-яЁё]', word):
        return word.lower()
    parsed = _morph.parse(word)
    if parsed:
        return parsed[0].normal_form
    return word.lower()


def tokenize(text: str) -> list[str]:
    """Разбивает текст на токены — алфавитно-цифровые последовательности."""
    return _TOKEN_RE.findall(text or '')


def lemmatize_text(text: str) -> str:
    """Возвращает строку нормализованных токенов через пробел."""
    return ' '.join(lemmatize_word(t) for t in tokenize(text))


def lemmatize_keywords(keywords: list[str]) -> list[str]:
    """Лемматизирует список ключевых слов / фраз."""
    out = []
    for kw in keywords:
        out.append(' '.join(lemmatize_word(t) for t in tokenize(kw)))
    return out
