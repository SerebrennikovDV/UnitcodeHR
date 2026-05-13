"""Справочники: подразделения, должности, источники найма, этапы, навыки."""
from django.db import models


class Department(models.Model):
    """Подразделение ООО «Юниткод» (поддерживает иерархию)."""
    name = models.CharField('Наименование', max_length=150)
    parent = models.ForeignKey(
        'self', verbose_name='Родительское подразделение',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
    )
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    """Должность с грейдом и вилкой ЗП."""
    GRADE_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Team Lead'),
        ('manager', 'Менеджер'),
        ('other', 'Иное'),
    ]
    title = models.CharField('Должность', max_length=150)
    grade = models.CharField('Грейд', max_length=20, choices=GRADE_CHOICES, default='middle')
    department = models.ForeignKey(
        Department, verbose_name='Отдел',
        on_delete=models.RESTRICT, related_name='positions',
    )
    salary_min = models.DecimalField('ЗП мин., ₽', max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField('ЗП макс., ₽', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['department', 'title']

    def __str__(self):
        return f'{self.title} ({self.get_grade_display()})'


class Source(models.Model):
    """Источник найма (откуда приходят кандидаты)."""
    TYPE_CHOICES = [
        ('jobboard', 'Доска вакансий'),
        ('social', 'Соц. сеть / мессенджер'),
        ('referral', 'Реферал'),
        ('event', 'Мероприятие'),
        ('other', 'Иное'),
    ]
    name = models.CharField('Наименование', max_length=100, unique=True)
    type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default='jobboard')
    cost_per_month = models.DecimalField('Стоимость в месяц, ₽', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Источник найма'
        verbose_name_plural = 'Источники найма'
        ordering = ['name']

    def __str__(self):
        return self.name


class Stage(models.Model):
    """Этап воронки подбора."""
    name = models.CharField('Наименование', max_length=100)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_terminal = models.BooleanField('Терминальный', default=False,
                                       help_text='Этап завершает воронку (оффер принят / отказ / авто-отклонено)')
    color = models.CharField('Цвет (HEX)', max_length=7, default='#0d6efd',
                              help_text='Например, #0d6efd для синего')

    class Meta:
        verbose_name = 'Этап воронки'
        verbose_name_plural = 'Этапы воронки'
        ordering = ['order']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Справочник навыков (используется и в требованиях вакансий, и в карточках кандидатов)."""
    CATEGORY_CHOICES = [
        ('language', 'Язык программирования'),
        ('framework', 'Фреймворк'),
        ('database', 'СУБД'),
        ('tool', 'Инструмент'),
        ('soft', 'Soft skill'),
        ('domain', 'Предметная область'),
        ('other', 'Иное'),
    ]
    name = models.CharField('Навык', max_length=100, unique=True)
    lemma = models.CharField('Лемма (нормальная форма)', max_length=100, blank=True,
                              help_text='Используется модулем скрининга. Заполняется автоматически.')
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='other')
    aliases = models.JSONField('Синонимы', default=list, blank=True,
                                help_text='Список альтернативных написаний для поиска')
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Навык / ключевое слово'
        verbose_name_plural = 'Навыки / ключевые слова'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
