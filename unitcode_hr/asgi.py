"""ASGI-конфигурация UnitcodeHR (для асинхронного развёртывания)."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unitcode_hr.settings')
application = get_asgi_application()
