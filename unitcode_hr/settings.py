"""
Настройки Django-проекта UnitcodeHR.
Документация: https://docs.djangoproject.com/en/5.1/topics/settings/
"""
from pathlib import Path
import os
import environ

# Корневой каталог проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из файла .env (если присутствует)
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CONNECTORS_MOCK_MODE=(bool, True),
    SCREENING_AUTO_REJECT_THRESHOLD=(float, 50.0),
    SCREENING_RECOMMEND_THRESHOLD=(float, 70.0),
)
environ.Env.read_env(BASE_DIR / '.env')

# --- Безопасность ---
SECRET_KEY = env('DJANGO_SECRET_KEY', default='dev-secret-replace-in-prod')
DEBUG = env('DJANGO_DEBUG')
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')

# --- Установленные приложения ---
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.catalog',
    'apps.vacancies',
    'apps.candidates',
    'apps.pipeline',
    'apps.offers',
    'apps.screening',
    'apps.analytics',
    'apps.feedback',
    'apps.audit',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Пользовательская модель
AUTH_USER_MODEL = 'accounts.User'

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'unitcode_hr.urls'

# --- Шаблоны ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'unitcode_hr.wsgi.application'

# --- База данных ---
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
    )
}

# --- Валидаторы пароля ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Локализация ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# --- Статика и медиа ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Аутентификация ---
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# --- Crispy Forms ---
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# --- Электронная почта ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if DEBUG \
    else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='no-reply@unitcode.ru')

# --- Параметры подсистемы скрининга ---
SCREENING = {
    'AUTO_REJECT_THRESHOLD': env('SCREENING_AUTO_REJECT_THRESHOLD'),
    'RECOMMEND_THRESHOLD': env('SCREENING_RECOMMEND_THRESHOLD'),
    'PARSER_VERSION': '1.0',
}

# --- Коннекторы внешних источников ---
CONNECTORS = {
    'MOCK_MODE': env('CONNECTORS_MOCK_MODE'),
    'HH_API_BASE': env('HH_API_BASE', default='https://api.hh.ru'),
    'SUPERJOB_API_KEY': env('SUPERJOB_API_KEY', default=''),
    'AVITO_CLIENT_ID': env('AVITO_CLIENT_ID', default=''),
    'AVITO_CLIENT_SECRET': env('AVITO_CLIENT_SECRET', default=''),
    'FIXTURES_PATH': BASE_DIR / 'connectors' / 'fixtures',
}

# --- Тип первичного ключа по умолчанию ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Логирование ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.screening': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.audit': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
