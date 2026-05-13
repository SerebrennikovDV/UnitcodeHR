from django.conf import settings
from django.db import models


class ActionLog(models.Model):
    """Журнал значимых действий пользователей."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Пользователь',
        on_delete=models.SET_NULL, null=True, related_name='action_logs',
    )
    action = models.CharField('Действие', max_length=50)
    object_type = models.CharField('Тип объекта', max_length=50, blank=True)
    object_id = models.PositiveBigIntegerField('ID объекта', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.CharField('User-Agent', max_length=255, blank=True)
    payload = models.JSONField('Доп. данные', default=dict, blank=True)
    created_at = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Журнал действий'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='audit_user_time_idx'),
        ]

    def __str__(self):
        return f'{self.user} → {self.action} @ {self.created_at:%d.%m.%Y %H:%M}'
