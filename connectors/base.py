"""Абстрактный базовый коннектор к внешним источникам вакансий.

Все реализации (HHConnector, SuperJobConnector, AvitoConnector) наследуют
этот класс и реализуют метод _real_search для боевого режима. Метод search
управляет режимом (mock / real) и кешированием результатов в БД.
"""
from __future__ import annotations

import abc
import json
import logging
from pathlib import Path
from typing import Iterable

from django.conf import settings

logger = logging.getLogger(__name__)


class BaseVacancyConnector(abc.ABC):
    """Базовый класс коннекторов внешних источников вакансий."""

    #: Короткое имя источника, например 'hh', 'superjob', 'avito'.
    source: str = ''
    #: Человекочитаемое название, например 'hh.ru'.
    display_name: str = ''
    #: Имя файла с mock-ответом в connectors/fixtures/
    mock_filename: str = ''

    def __init__(self) -> None:
        self.fixtures_path: Path = settings.CONNECTORS['FIXTURES_PATH']
        self.mock_mode: bool = settings.CONNECTORS['MOCK_MODE']

    # --- Публичный API ---

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Возвращает список вакансий по поисковому запросу.

        Каждый элемент — словарь с ключами:
            - external_id: ID на внешнем источнике
            - title: заголовок вакансии
            - description: текстовое описание
            - keywords: список извлечённых ключевых слов
            - url: ссылка на оригинал
            - salary_from, salary_to: вилка ЗП (если есть)
        """
        if self.mock_mode:
            return self._mock_search(query, limit)
        return self._real_search(query, limit)

    def cache_to_db(self, vacancies: Iterable[dict], query: str) -> int:
        """Сохраняет полученные вакансии в screening_externalvacancy."""
        from apps.screening.models import ExternalVacancy
        saved = 0
        for v in vacancies:
            ExternalVacancy.objects.update_or_create(
                source=self.source,
                external_id=str(v.get('external_id', '')),
                defaults={
                    'query': query,
                    'title': v.get('title', '')[:200],
                    'description': v.get('description', ''),
                    'raw_payload': v,
                    'extracted_keywords': v.get('keywords', []),
                },
            )
            saved += 1
        return saved

    # --- Реализация по умолчанию ---

    def _mock_search(self, query: str, limit: int) -> list[dict]:
        """Загружает фейковые данные из connectors/fixtures/<mock_filename>."""
        if not self.mock_filename:
            return []
        path = self.fixtures_path / self.mock_filename
        if not path.exists():
            logger.warning('Mock-файл не найден: %s', path)
            return []
        try:
            with open(path, encoding='utf-8') as fh:
                items = json.load(fh)
        except Exception as exc:
            logger.error('Ошибка чтения mock-файла %s: %s', path, exc)
            return []
        # Фильтр по запросу — простой поиск подстроки в заголовке/описании
        ql = query.lower()
        filtered = [
            it for it in items
            if ql in (it.get('title', '') + ' ' + it.get('description', '')).lower()
        ]
        return (filtered or items)[:limit]

    @abc.abstractmethod
    def _real_search(self, query: str, limit: int) -> list[dict]:
        """Боевой запрос к внешнему API. Реализуется в наследниках."""
        raise NotImplementedError
