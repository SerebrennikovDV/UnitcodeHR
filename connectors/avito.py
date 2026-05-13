"""Коннектор к Avito API (бизнес-аккаунт через developers.avito.ru).

Требует OAuth client_id/client_secret, выдаваемых после подключения Avito
Бизнес-аккаунта. В режиме mock — возвращает данные из
connectors/fixtures/avito_sample.json.
"""
import logging
import requests
from django.conf import settings

from .base import BaseVacancyConnector

logger = logging.getLogger(__name__)


class AvitoConnector(BaseVacancyConnector):
    source = 'avito'
    display_name = 'Avito'
    mock_filename = 'avito_sample.json'

    OAUTH_URL = 'https://api.avito.ru/token'
    SEARCH_URL = 'https://api.avito.ru/job/v2/vacancies'

    def _real_search(self, query: str, limit: int) -> list[dict]:
        client_id = settings.CONNECTORS['AVITO_CLIENT_ID']
        client_secret = settings.CONNECTORS['AVITO_CLIENT_SECRET']
        if not (client_id and client_secret):
            logger.warning('Учётные данные Avito не заданы — пропускаем источник')
            return []

        # 1. Получение access token через OAuth Client Credentials Grant
        try:
            token_response = requests.post(
                self.OAUTH_URL,
                data={'grant_type': 'client_credentials',
                      'client_id': client_id, 'client_secret': client_secret},
                timeout=10,
            )
            token_response.raise_for_status()
            access_token = token_response.json().get('access_token')
        except Exception as exc:
            logger.warning('Avito OAuth недоступен: %s', exc)
            return []

        # 2. Запрос вакансий
        try:
            response = requests.get(
                self.SEARCH_URL,
                params={'query': query, 'per_page': min(limit, 50)},
                headers={'Authorization': f'Bearer {access_token}',
                         'User-Agent': 'UnitcodeHR/1.0'},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning('Avito API недоступен: %s', exc)
            return []

        result = []
        for item in payload.get('items', []):
            result.append({
                'external_id': str(item.get('id')),
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'keywords': [],
                'url': item.get('url', ''),
                'salary_from': (item.get('salary') or {}).get('from'),
                'salary_to': (item.get('salary') or {}).get('to'),
                'employer': (item.get('company') or {}).get('name', ''),
            })
        return result[:limit]
