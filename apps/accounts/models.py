"""Модели пользователей и ролей UnitcodeHR."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Справочник ролей в системе UnitcodeHR."""

    CODE_ADMIN = 'admin'
    CODE_HR = 'hr'
    CODE_HIRING_MANAGER = 'hiring_manager'

    CODE_CHOICES = [
        (CODE_ADMIN, 'Администратор'),
        (CODE_HR, 'HR-менеджер'),
        (CODE_HIRING_MANAGER, 'Нанимающий менеджер'),
    ]

    code = models.CharField('Код', max_length=32, unique=True, choices=CODE_CHOICES)
    name = models.CharField('Наименование', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Расширенная модель пользователя с ролью и подразделением."""
    role = models.ForeignKey(
        Role, verbose_name='Роль', on_delete=models.RESTRICT,
        related_name='users', null=True, blank=True,
    )
    department = models.ForeignKey(
        'catalog.Department', verbose_name='Отдел',
        on_delete=models.SET_NULL, related_name='members', null=True, blank=True,
    )
    phone = models.CharField('Телефон', max_length=20, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', null=True, blank=True)
    notify_email = models.BooleanField('Уведомления по почте', default=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full = f'{self.last_name} {self.first_name}'.strip()
        return full or self.username

    @property
    def is_hr(self) -> bool:
        return self.role and self.role.code in (Role.CODE_HR, Role.CODE_ADMIN)

    @property
    def is_hiring_manager(self) -> bool:
        return self.role and self.role.code in (Role.CODE_HIRING_MANAGER, Role.CODE_ADMIN)

    @property
    def is_administrator(self) -> bool:
        return self.role and self.role.code == Role.CODE_ADMIN
