"""Сигналы воронки подбора: фиксация истории этапов, запуск скрининга."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Application, StageHistory

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Application)
def detect_stage_change(sender, instance, **kwargs):
    """Запоминает старый этап перед сохранением (для сравнения в post_save)."""
    if instance.pk:
        try:
            old = Application.objects.get(pk=instance.pk)
            instance._old_stage_id = old.current_stage_id
        except Application.DoesNotExist:
            instance._old_stage_id = None
    else:
        instance._old_stage_id = None


@receiver(post_save, sender=Application)
def fix_stage_history(sender, instance, created, **kwargs):
    """Фиксирует историю каждого перехода в StageHistory."""
    old_stage_id = getattr(instance, '_old_stage_id', None)
    if created or old_stage_id != instance.current_stage_id:
        if instance.current_stage_id:
            StageHistory.objects.create(
                application=instance,
                stage_id=instance.current_stage_id,
                comment='Начальный этап' if created else 'Переход по воронке',
            )

    if created:
        # Запускаем автоматический скрининг резюме нового отклика
        try:
            from apps.screening.services import schedule_screening
            schedule_screening(instance)
        except ImportError:
            logger.warning('Модуль screening не загружен, скрининг пропущен')
        except Exception as exc:
            logger.error('Ошибка запуска скрининга для отклика %s: %s', instance.pk, exc)
