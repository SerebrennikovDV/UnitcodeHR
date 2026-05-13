from django.contrib import admin
from .models import ResumeParse, Match, ExternalVacancy


@admin.register(ResumeParse)
class ResumeParseAdmin(admin.ModelAdmin):
    list_display = ('resume', 'years_experience', 'parser_version', 'parsed_at')
    readonly_fields = ('parsed_at',)
    search_fields = ('resume__candidate__first_name', 'resume__candidate__last_name')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('application', 'score', 'verdict', 'experience_match', 'calculated_at')
    list_filter = ('verdict',)
    search_fields = ('application__candidate__first_name', 'application__candidate__last_name',
                     'application__vacancy__title')
    readonly_fields = ('calculated_at',)
    actions = ['recalculate_match']

    @admin.action(description='Пересчитать скоринг резюме')
    def recalculate_match(self, request, queryset):
        from .services import score_application
        count = 0
        for match in queryset.select_related('application'):
            score_application(match.application)
            count += 1
        self.message_user(request, f'Пересчитано: {count}')


@admin.register(ExternalVacancy)
class ExternalVacancyAdmin(admin.ModelAdmin):
    list_display = ('source', 'external_id', 'title', 'query', 'fetched_at')
    list_filter = ('source',)
    search_fields = ('title', 'description', 'query')
