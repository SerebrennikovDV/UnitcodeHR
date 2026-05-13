"""Модели подсистемы скрининга резюме."""
from django.db import models


class ResumeParse(models.Model):
    """Результаты парсинга файла резюме."""
    resume = models.OneToOneField(
        'candidates.Resume', verbose_name='Резюме',
        on_delete=models.CASCADE, related_name='parsed',
    )
    raw_text = models.TextField('Извлечённый текст', blank=True)
    normalized_text = models.TextField('Лемматизированный текст', blank=True)
    years_experience = models.DecimalField('Извлечённый опыт работы, лет',
                                            max_digits=4, decimal_places=1, null=True, blank=True)
    parser_version = models.CharField('Версия парсера', max_length=20, default='1.0')
    parsed_at = models.DateTimeField('Дата парсинга', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат парсинга резюме'
        verbose_name_plural = 'Результаты парсинга резюме'

    def __str__(self):
        return f'Парс резюме {self.resume.candidate}'


class Match(models.Model):
    """Результат скоринга резюме под конкретную вакансию."""

    VERDICT_CHOICES = [
        ('recommended', 'Рекомендован (≥ 70 %)'),
        ('match', 'Подходит (50–70 %)'),
        ('review', 'На решение HR'),
        ('auto_rejected', 'Авто-отклонено (< 50 %)'),
    ]

    application = models.OneToOneField(
        'pipeline.Application', verbose_name='Отклик',
        on_delete=models.CASCADE, related_name='match',
    )
    score = models.DecimalField('Балл, %', max_digits=5, decimal_places=2,
                                 help_text='Интегральный показатель соответствия (0-100)')
    verdict = models.CharField('Вердикт', max_length=20, choices=VERDICT_CHOICES)
    matched_keywords = models.JSONField('Найденные ключевые слова', default=list)
    missing_keywords = models.JSONField('Недостающие ключевые слова', default=list)
    experience_match = models.BooleanField('Соответствие по опыту', default=False)
    extracted_experience_years = models.DecimalField(
        'Извлечённый опыт работы', max_digits=4, decimal_places=1, null=True, blank=True,
    )
    reasons = models.TextField('Описание причин', blank=True)
    calculated_at = models.DateTimeField('Дата расчёта', auto_now_add=True)

    candidate = models.ForeignKey(
        'candidates.Candidate', verbose_name='Кандидат',
        on_delete=models.CASCADE, related_name='screening_matches',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Скоринг резюме'
        verbose_name_plural = 'Скоринги резюме'
        ordering = ['-calculated_at']
        indexes = [
            models.Index(fields=['verdict'], name='match_verdict_idx'),
        ]

    def __str__(self):
        return f'{self.application} — {self.score} % ({self.get_verdict_display()})'

    @property
    def color(self) -> str:
        """Bootstrap-цвет для индикации в UI."""
        return {
            'recommended': 'success',
            'match': 'primary',
            'review': 'warning',
            'auto_rejected': 'danger',
        }.get(self.verdict, 'secondary')


class ExternalVacancy(models.Model):
    """Закэшированные данные вакансии с внешней площадки (HH / SuperJob / Avito)."""
    SOURCE_CHOICES = [
        ('hh', 'hh.ru'),
        ('superjob', 'SuperJob'),
        ('avito', 'Avito'),
    ]
    source = models.CharField('Источник', max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField('ID на внешнем источнике', max_length=50)
    query = models.CharField('Поисковый запрос', max_length=200)
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание', blank=True)
    raw_payload = models.JSONField('Сырой ответ API', default=dict)
    extracted_keywords = models.JSONField('Извлечённые ключевые слова', default=list)
    fetched_at = models.DateTimeField('Дата получения', auto_now_add=True)

    class Meta:
        verbose_name = 'Внешняя вакансия'
        verbose_name_plural = 'Внешние вакансии'
        unique_together = [('source', 'external_id')]
        ordering = ['-fetched_at']

    def __str__(self):
        return f'[{self.get_source_display()}] {self.title}'
