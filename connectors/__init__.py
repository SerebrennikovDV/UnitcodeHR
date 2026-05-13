"""Пакет коннекторов к внешним источникам вакансий.

Содержит единый интерфейс BaseVacancyConnector и реализации для hh.ru,
SuperJob и Avito. По умолчанию все коннекторы работают в режиме mock —
возвращают предзаписанные ответы из connectors/fixtures/. Переключение
в реальный режим выполняется через переменную окружения CONNECTORS_MOCK_MODE.
"""
from typing import Type

from .base import BaseVacancyConnector
from .hh import HHConnector
from .superjob import SuperJobConnector
from .avito import AvitoConnector


_REGISTRY: dict[str, Type[BaseVacancyConnector]] = {
    'hh': HHConnector,
    'superjob': SuperJobConnector,
    'avito': AvitoConnector,
}


def get_connector(name: str) -> BaseVacancyConnector:
    """Возвращает экземпляр коннектора по короткому имени источника."""
    if name not in _REGISTRY:
        raise ValueError(f'Неизвестный источник: {name}. Доступные: {list(_REGISTRY)}')
    return _REGISTRY[name]()


__all__ = [
    'BaseVacancyConnector',
    'HHConnector',
    'SuperJobConnector',
    'AvitoConnector',
    'get_connector',
]
