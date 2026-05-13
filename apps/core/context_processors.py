"""Глобальный контекст для всех шаблонов."""
from django.conf import settings


def site_info(request):
    """Передаёт в шаблоны информацию о системе (для footer, заголовков и т.п.)."""
    return {
        'SITE_NAME': 'UnitcodeHR',
        'SITE_AUTHOR': 'Серебренников Дмитрий Валерьевич',
        'SITE_VERSION': '1.0',
        'COMPANY_NAME': 'ООО «Юниткод»',
        'COMPANY_URL': 'https://unitcode.ru',
        'SCREENING_THRESHOLD': settings.SCREENING['AUTO_REJECT_THRESHOLD'],
    }
