from django.contrib import admin
from .models import Application, StageHistory, Interview


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate', 'vacancy', 'current_stage', 'created_at', 'closed_at')
    list_filter = ('current_stage', 'vacancy')
    search_fields = ('candidate__first_name', 'candidate__last_name',
                     'vacancy__title')
    autocomplete_fields = ('candidate', 'vacancy', 'current_stage')


@admin.register(StageHistory)
class StageHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'stage', 'changed_by', 'changed_at')
    list_filter = ('stage',)
    readonly_fields = ('changed_at',)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'kind', 'interviewer', 'scheduled_at', 'result', 'rating')
    list_filter = ('kind', 'result')
    autocomplete_fields = ('application', 'interviewer')
