"""Воронка подбора: отклики, история этапов, интервью."""
from django.conf import settings
from django.db import models


class Application(models.Model):
    """Отклик кандидата на вакансию."""
    candidate = models.ForeignKey(
        'candidates.Candidate', verbose_name='Кандидат',
        on_delete=models.CASCADE, related_name='applications',
    )
    vacancy = models.ForeignKey(
        'vacancies.Vacancy', verbose_name='Вакансия',
        on_delete=models.CASCADE, related_name='applications',
    )
    current_stage = models.ForeignKey(
        'catalog.Stage', verbose_name='Текущий этап',
        on_delete=models.PROTECT, related_name='applications', null=True, blank=True,
    )
    rejection_reason = models.CharField('Причина отказа', max_length=200, blank=True)
    cover_letter = models.TextField('Сопроводительное письмо', blank=True)
    created_at = models.DateTimeField('Дата отклика', auto_now_add=True)
    closed_at = models.DateTimeField('Дата закрытия', null=True, blank=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['-created_at']
        unique_together = [('candidate', 'vacancy')]
        indexes = [
            models.Index(fields=['vacancy', 'current_stage'], name='app_vac_stage_idx'),
        ]

    def __str__(self):
        return f'{self.candidate} → {self.vacancy}'


class StageHistory(models.Model):
    """История переходов отклика по этапам воронки."""
    application = models.ForeignKey(Application, verbose_name='Отклик',
                                      on_delete=models.CASCADE, related_name='stage_history')
    stage = models.ForeignKey('catalog.Stage', verbose_name='Этап',
                                on_delete=models.PROTECT, related_name='history_records')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Кем изменено',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='stage_changes',
    )
    comment = models.TextField('Комментарий', blank=True)
    changed_at = models.DateTimeField('Дата изменения', auto_now_add=True)

    class Meta:
        verbose_name = 'История этапа'
        verbose_name_plural = 'История этапов'
        ordering = ['changed_at']
        indexes = [
            models.Index(fields=['application', 'changed_at'], name='hist_app_time_idx'),
        ]

    def __str__(self):
        return f'{self.application} → {self.stage} ({self.changed_at:%d.%m.%Y})'


class Interview(models.Model):
    """Интервью с кандидатом."""
    KIND_CHOICES = [
        ('hr', 'HR-интервью'),
        ('tech', 'Техническое интервью'),
        ('final', 'Финальное интервью'),
        ('reference', 'Сбор рекомендаций'),
    ]
    RESULT_CHOICES = [
        ('pending', 'Не проведено'),
        ('passed', 'Прошёл'),
        ('failed', 'Не прошёл'),
        ('canceled', 'Отменено'),
    ]

    application = models.ForeignKey(Application, verbose_name='Отклик',
                                      on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Интервьюер',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='led_interviews',
    )
    kind = models.CharField('Тип интервью', max_length=20, choices=KIND_CHOICES)
    scheduled_at = models.DateTimeField('Запланировано на')
    duration_minutes = models.PositiveSmallIntegerField('Длительность, мин.', default=60)
    meeting_link = models.URLField('Ссылка на встречу', blank=True)
    result = models.CharField('Результат', max_length=20, choices=RESULT_CHOICES, default='pending')
    rating = models.PositiveSmallIntegerField('Оценка (1-5)', null=True, blank=True)
    notes = models.TextField('Заметки', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Интервью'
        verbose_name_plural = 'Интервью'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.get_kind_display()} — {self.application}'
