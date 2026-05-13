"""
Точка входа в приложение UnitcodeHR.

Этот файл — обёртка над стандартным Django-CLI manage.py, предусмотренная
требованиями рубрики оценивания преддипломной практики (наличие файла
main.py в корне репозитория).

Запуск:
    python main.py runserver      — запуск отладочного сервера
    python main.py migrate        — применение миграций БД
    python main.py createsuperuser — создание суперпользователя
    python main.py shell           — интерактивная оболочка Django
"""
import os
import sys


def main() -> None:
    """Делегирует управление стандартному Django-CLI."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unitcode_hr.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Django не установлен. Создайте виртуальное окружение и '
            'выполните: pip install -r requirements.txt'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
