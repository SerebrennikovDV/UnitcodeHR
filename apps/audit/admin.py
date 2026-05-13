from django.contrib import admin
from .models import ActionLog


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'object_type', 'object_id', 'ip_address')
    list_filter = ('action', 'object_type')
    search_fields = ('user__username', 'action', 'object_type')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
