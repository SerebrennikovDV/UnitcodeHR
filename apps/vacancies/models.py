"""Модели заявок на найм и опубликованных вакансий."""
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode


class HiringRequest(models.Model):
    """Заявка на найм от нанимающего менеджера."""

    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending_approval'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PENDING, 'На согласовании'),
        (STATUS_APPROVED, 'Согласована'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    title = models.CharField('Название позиции', max_length=200)
    description = models.TextField('Описание задач')
    department = models.ForeignKey(
        'catalog.Department', verbose_name='Отдел',
        on_delete=models.PROTECT, related_name='hiring_requests',
    )
    position = models.ForeignKey(
        'catalog.Position', verbose_name='Должность',
        on_delete=models.PROTECT, related_name='hiring_requests',
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Инициатор',
        on_delete=models.PROTECT, related_name='created_requests',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Согласовал',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_requests',
    )
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    salary_min = models.DecimalField('ЗП мин., ₽', max_digits=10, decimal_places=2)
    salary_max = models.DecimalField('ЗП макс., ₽', max_digits=10, decimal_places=2)
    urgency = models.CharField('Срочность', max_length=20, default='normal',
                                choices=[('low', 'Низкая'), ('normal', 'Обычная'),
                                         ('high', 'Высокая'), ('critical', 'Критическая')])
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    approved_at = models.DateTimeField('Дата согласования', null=True, blank=True)

    class Meta:
        verbose_name = 'Заявка на найм'
        verbose_name_plural = 'Заявки на найм'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.title}'


class Vacancy(models.Model):
    """Опубликованная вакансия — производный объект от утверждённой заявки."""

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CLOSED = 'closed'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PUBLISHED, 'Опубликована'),
        (STATUS_CLOSED, 'Закрыта'),
        (STATUS_ARCHIVED, 'В архиве'),
    ]

    request = models.ForeignKey(
        HiringRequest, verbose_name='Заявка',
        on_delete=models.CASCADE, related_name='vacancies',
    )
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL-идентификатор', max_length=220, unique=True, blank=True)
    description = models.TextField('Описание')
    requirements = models.TextField('Требования')
    benefits = models.TextField('Условия', blank=True)
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Рекрутёр',
        on_delete=models.PROTECT, related_name='led_vacancies',
    )
    hiring_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Нанимающий менеджер',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_vacancies',
    )
    skills = models.ManyToManyField(
        'catalog.Skill', verbose_name='Требуемые навыки',
        through='VacancySkill', related_name='vacancies',
    )
    min_experience_years = models.PositiveSmallIntegerField('Минимальный опыт, лет', default=0)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    deadline = models.DateField('Срок закрытия', null=True, blank=True)
    published_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    closed_at = models.DateTimeField('Дата закрытия', null=True, blank=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-published_at', '-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.title))[:200] or f'vacancy-{self.pk}'
            self.slug = base
            # уникализация slug
            i = 1
            while Vacancy.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                i += 1
                self.slug = f'{base}-{i}'
        super().save(*args, **kwargs)


class VacancySkill(models.Model):
    """Связующая таблица «Вакансия — требуемый навык» с весом."""
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='vacancy_skills')
    skill = models.ForeignKey('catalog.Skill', on_delete=models.PROTECT,
                                related_name='skill_vacancies')
    weight = models.DecimalField('Вес требования', max_digits=4, decimal_places=2, default=1.0,
                                  help_text='Используется при расчёте score (по умолчанию 1.0)')
    is_required = models.BooleanField('Обязательное', default=True)

    class Meta:
        verbose_name = 'Навык вакансии'
        verbose_name_plural = 'Навыки вакансий'
        unique_together = [('vacancy', 'skill')]

    def __str__(self):
        return f'{self.vacancy} — {self.skill}'
