"""
Корневая URL-конфигурация UnitcodeHR.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Публичные страницы
    path('', core_views.home, name='home'),
    path('healthz/', core_views.healthz, name='healthz'),
    path('about/', core_views.about, name='about'),
    path('help/', core_views.help_page, name='help'),

    # Аутентификация и личные кабинеты
    path('accounts/', include('apps.accounts.urls')),

    # Основной функционал (требует авторизации)
    path('dashboard/', include('apps.core.urls_dashboard')),
    path('catalog/', include('apps.catalog.urls')),
    path('vacancies/', include('apps.vacancies.urls')),
    path('candidates/', include('apps.candidates.urls')),
    path('pipeline/', include('apps.pipeline.urls')),
    path('offers/', include('apps.offers.urls')),
    path('screening/', include('apps.screening.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('feedback/', include('apps.feedback.urls')),
]

# В отладочном режиме раздаём media через Django
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
