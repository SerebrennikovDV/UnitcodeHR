"""Офферы и факты найма."""
from django.db import models


class Offer(models.Model):
    """Предложение о работе."""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('approved', 'Согласован'),
        ('sent', 'Направлен кандидату'),
        ('accepted', 'Принят'),
        ('declined', 'Отклонён'),
        ('expired', 'Истёк срок'),
    ]
    application = models.OneToOneField(
        'pipeline.Application', verbose_name='Отклик',
        on_delete=models.CASCADE, related_name='offer',
    )
    salary = models.DecimalField('Зарплата, ₽', max_digits=10, decimal_places=2)
    start_date = models.DateField('Дата выхода')
    probation_months = models.PositiveSmallIntegerField('Испытательный срок (мес.)', default=3)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='draft')
    document = models.FileField('Файл оффера (.docx)', upload_to='offers/%Y/%m/', null=True, blank=True)
    sent_at = models.DateTimeField('Дата отправки', null=True, blank=True)
    responded_at = models.DateTimeField('Дата ответа', null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Оффер для {self.application.candidate}'


class Hire(models.Model):
    """Факт оформления кандидата на работу + испытательный срок."""
    EMPLOYMENT_TYPES = [
        ('full_time', 'Штат (трудовой договор)'),
        ('self_employed', 'Самозанятый (НПД)'),
        ('individual', 'ИП (ГПХ)'),
        ('other', 'Иное'),
    ]
    offer = models.OneToOneField(Offer, verbose_name='Оффер',
                                   on_delete=models.CASCADE, related_name='hire')
    employment_type = models.CharField('Форма трудоустройства', max_length=20,
                                        choices=EMPLOYMENT_TYPES, default='self_employed')
    probation_end = models.DateField('Окончание испытательного срока')
    probation_passed = models.BooleanField('Испытательный срок пройден', null=True, blank=True)
    probation_notes = models.TextField('Заметки по испытательному сроку', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Найм'
        verbose_name_plural = 'Наймы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Найм {self.offer.application.candidate}'
