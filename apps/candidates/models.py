"""Кандидаты и прикреплённые к ним резюме."""
from django.db import models


class Candidate(models.Model):
    """Карточка кандидата."""
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('E-mail', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    telegram = models.CharField('Telegram', max_length=50, blank=True)
    expected_salary = models.DecimalField('Ожидаемая ЗП, ₽', max_digits=10, decimal_places=2, null=True, blank=True)
    source = models.ForeignKey(
        'catalog.Source', verbose_name='Источник',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates',
    )
    skills = models.ManyToManyField(
        'catalog.Skill', verbose_name='Навыки',
        through='CandidateSkill', related_name='candidates', blank=True,
    )
    is_blacklisted = models.BooleanField('В чёрном списке', default=False)
    notes = models.TextField('Заметки HR', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Кандидат'
        verbose_name_plural = 'Кандидаты'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email'], name='cand_email_idx'),
            models.Index(fields=['phone'], name='cand_phone_idx'),
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def full_name(self) -> str:
        return f'{self.last_name} {self.first_name}'.strip()


class Resume(models.Model):
    """Файл резюме, прикреплённый к карточке кандидата."""
    candidate = models.ForeignKey(
        Candidate, verbose_name='Кандидат',
        on_delete=models.CASCADE, related_name='resumes',
    )
    file = models.FileField('Файл резюме', upload_to='resumes/%Y/%m/')
    original_filename = models.CharField('Исходное имя файла', max_length=255, blank=True)
    file_size = models.PositiveIntegerField('Размер, байт', default=0)
    is_primary = models.BooleanField('Основное резюме', default=False)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Резюме'
        verbose_name_plural = 'Резюме'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Резюме {self.candidate} ({self.original_filename})'


class CandidateSkill(models.Model):
    """Связующая таблица «Кандидат — навык» с уровнем владения."""
    LEVEL_CHOICES = [
        (1, 'Начальный'),
        (2, 'Базовый'),
        (3, 'Уверенный'),
        (4, 'Продвинутый'),
        (5, 'Экспертный'),
    ]
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                    related_name='candidate_skills')
    skill = models.ForeignKey('catalog.Skill', on_delete=models.PROTECT,
                                related_name='skill_candidates')
    level = models.PositiveSmallIntegerField('Уровень', choices=LEVEL_CHOICES, default=3)

    class Meta:
        verbose_name = 'Навык кандидата'
        verbose_name_plural = 'Навыки кандидатов'
        unique_together = [('candidate', 'skill')]
