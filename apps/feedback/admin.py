from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_processed', 'created_at')
    list_filter = ('is_processed',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_processed']

    @admin.action(description='Пометить как обработанное')
    def mark_processed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_processed=True, processed_by=request.user,
                                   processed_at=timezone.now())
        self.message_user(request, f'Обработано: {updated}')
