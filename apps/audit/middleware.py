"""Middleware для журналирования значимых HTTP-запросов авторизованных пользователей."""
import logging

logger = logging.getLogger(__name__)

# Какие методы / пути логировать (избегаем шума от статики и GET)
_LOGGED_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')
_SKIPPED_PREFIXES = ('/static/', '/media/', '/admin/jsi18n', '/healthz')


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (request.user.is_authenticated
                and request.method in _LOGGED_METHODS
                and not any(request.path.startswith(p) for p in _SKIPPED_PREFIXES)):
            try:
                from .models import ActionLog
                ActionLog.objects.create(
                    user=request.user,
                    action=f'{request.method} {request.path}',
                    ip_address=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                )
            except Exception as exc:  # не блокируем основной ответ
                logger.warning('Не удалось залогировать действие: %s', exc)
        return response

    @staticmethod
    def _get_ip(request) -> str | None:
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
