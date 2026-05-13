"""Коннектор к открытому API hh.ru.

В режиме mock возвращает данные из connectors/fixtures/hh_sample.json.
В боевом режиме обращается к https://api.hh.ru/vacancies?text=<query>.
"""
import logging
import requests
from django.conf import settings

from .base import BaseVacancyConnector

logger = logging.getLogger(__name__)


class HHConnector(BaseVacancyConnector):
    source = 'hh'
    display_name = 'hh.ru'
    mock_filename = 'hh_sample.json'

    def _real_search(self, query: str, limit: int) -> list[dict]:
        base = settings.CONNECTORS['HH_API_BASE']
        url = f'{base}/vacancies'
        params = {'text': query, 'per_page': min(limit, 100),
                  'area': 1, 'only_with_salary': False}
        try:
            response = requests.get(url, params=params, timeout=10,
                                    headers={'User-Agent': 'UnitcodeHR/1.0'})
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning('HH API недоступен: %s', exc)
            return []

        result = []
        for item in payload.get('items', []):
            result.append({
                'external_id': str(item.get('id')),
                'title': item.get('name', ''),
                'description': (item.get('snippet') or {}).get('requirement') or '',
                'keywords': self._extract_keywords(item),
                'url': item.get('alternate_url', ''),
                'salary_from': (item.get('salary') or {}).get('from'),
                'salary_to':   (item.get('salary') or {}).get('to'),
                'employer': (item.get('employer') or {}).get('name', ''),
            })
        return result[:limit]

    @staticmethod
    def _extract_keywords(item: dict) -> list[str]:
        """Извлекает ключевые слова из текста вакансии."""
        text = ' '.join(filter(None, [
            item.get('name', ''),
            (item.get('snippet') or {}).get('requirement') or '',
            (item.get('snippet') or {}).get('responsibility') or '',
        ]))
        # Список самых частых IT-навыков (стартовый словарь)
        common = ['python', 'django', 'flask', 'fastapi', 'postgresql', 'mysql',
                  'redis', 'docker', 'kubernetes', 'git', 'rest', 'graphql',
                  'react', 'vue', 'typescript', 'javascript', 'sql', 'linux',
                  'aws', 'azure', 'celery', 'rabbitmq', 'pytest', 'CI/CD']
        lowered = text.lower()
        return [k for k in common if k.lower() in lowered]
