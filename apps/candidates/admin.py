from django.contrib import admin
from .models import Candidate, Resume, CandidateSkill


class ResumeInline(admin.TabularInline):
    model = Resume
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size')


class CandidateSkillInline(admin.TabularInline):
    model = CandidateSkill
    extra = 1
    autocomplete_fields = ('skill',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'source', 'expected_salary',
                    'is_blacklisted', 'created_at')
    list_filter = ('source', 'is_blacklisted')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'telegram')
    inlines = [CandidateSkillInline, ResumeInline]
    actions = ['archive_inactive']

    @admin.action(description='Архивировать неактивных кандидатов (без откликов)')
    def archive_inactive(self, request, queryset):
        qs = queryset.filter(applications__isnull=True)
        count = qs.count()
        # softdelete нет, просто помечаем blacklisted
        qs.update(is_blacklisted=True)
        self.message_user(request, f'Архивировано: {count}')


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'original_filename', 'file_size', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary',)
    search_fields = ('candidate__first_name', 'candidate__last_name', 'original_filename')


@admin.register(CandidateSkill)
class CandidateSkillAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'skill', 'level')
    list_filter = ('level',)
    autocomplete_fields = ('candidate', 'skill')
