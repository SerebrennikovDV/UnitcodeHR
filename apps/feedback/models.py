from django.db import models


class Feedback(models.Model):
    """Сообщение с публичной формы обратной связи."""
    name = models.CharField('Имя', max_length=150)
    email = models.EmailField('E-mail')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    is_processed = models.BooleanField('Обработано', default=False)
    processed_by = models.ForeignKey(
        'accounts.User', verbose_name='Кем обработано',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_feedback',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    processed_at = models.DateTimeField('Дата обработки', null=True, blank=True)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.subject}'
