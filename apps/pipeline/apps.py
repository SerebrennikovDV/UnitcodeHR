from django.apps import AppConfig


class PipelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pipeline'
    verbose_name = 'Воронка подбора'

    def ready(self):
        from . import signals  # noqa: F401
