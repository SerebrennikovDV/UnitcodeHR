from django.contrib import admin
from .models import HiringRequest, Vacancy, VacancySkill


class VacancySkillInline(admin.TabularInline):
    model = VacancySkill
    extra = 1


@admin.register(HiringRequest)
class HiringRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department', 'position', 'requested_by',
                    'status', 'urgency', 'created_at')
    list_filter = ('status', 'urgency', 'department')
    search_fields = ('title', 'description')
    autocomplete_fields = ('requested_by', 'approved_by', 'department', 'position')


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'recruiter', 'hiring_manager',
                    'min_experience_years', 'deadline', 'published_at')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'requirements')
    inlines = [VacancySkillInline]
    autocomplete_fields = ('recruiter', 'hiring_manager', 'request')
    actions = ['publish_selected', 'archive_selected']

    @admin.action(description='Опубликовать выбранные вакансии')
    def publish_selected(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='draft').update(
            status='published', published_at=timezone.now()
        )
        self.message_user(request, f'Опубликовано вакансий: {updated}')

    @admin.action(description='Архивировать выбранные вакансии')
    def archive_selected(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'В архив отправлено: {updated}')


@admin.register(VacancySkill)
class VacancySkillAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'skill', 'weight', 'is_required')
    list_filter = ('is_required',)
    autocomplete_fields = ('vacancy', 'skill')
