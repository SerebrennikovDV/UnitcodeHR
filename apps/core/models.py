"""Общие модели и абстрактные базовые классы для других приложений."""
from django.db import models


class TimeStampedModel(models.Model):
    """Базовая модель с автоматическими полями created_at/updated_at."""
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Модель с поддержкой мягкого удаления."""
    is_deleted = models.BooleanField('Удалено', default=False)
    deleted_at = models.DateTimeField('Дата удаления', null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
