"""Коннектор к SuperJob API.

Требует API-ключа (получается на api.superjob.ru). В режиме mock —
возвращает данные из connectors/fixtures/superjob_sample.json.
"""
import logging
import requests
from django.conf import settings

from .base import BaseVacancyConnector

logger = logging.getLogger(__name__)


class SuperJobConnector(BaseVacancyConnector):
    source = 'superjob'
    display_name = 'SuperJob'
    mock_filename = 'superjob_sample.json'

    def _real_search(self, query: str, limit: int) -> list[dict]:
        api_key = settings.CONNECTORS['SUPERJOB_API_KEY']
        if not api_key:
            logger.warning('SUPERJOB_API_KEY не задан — пропускаем источник')
            return []
        url = 'https://api.superjob.ru/2.0/vacancies/'
        try:
            response = requests.get(
                url, params={'keyword': query, 'count': min(limit, 100)},
                headers={'X-Api-App-Id': api_key,
                         'User-Agent': 'UnitcodeHR/1.0'},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning('SuperJob API недоступен: %s', exc)
            return []

        result = []
        for item in payload.get('objects', []):
            result.append({
                'external_id': str(item.get('id')),
                'title': item.get('profession', ''),
                'description': item.get('candidat', '') or item.get('work', ''),
                'keywords': [],
                'url': item.get('link', ''),
                'salary_from': item.get('payment_from'),
                'salary_to': item.get('payment_to'),
                'employer': (item.get('client') or {}).get('title', ''),
            })
        return result[:limit]
