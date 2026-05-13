from django.contrib import admin
from .models import Offer, Hire


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'salary', 'start_date', 'status', 'sent_at')
    list_filter = ('status',)
    autocomplete_fields = ('application',)
    actions = ['regenerate_docx']

    @admin.action(description='Перегенерировать .docx файл оффера')
    def regenerate_docx(self, request, queryset):
        from .services import generate_offer_docx
        for offer in queryset:
            generate_offer_docx(offer)
        self.message_user(request, f'Сгенерировано офферов: {queryset.count()}')


@admin.register(Hire)
class HireAdmin(admin.ModelAdmin):
    list_display = ('offer', 'employment_type', 'probation_end', 'probation_passed')
    list_filter = ('employment_type', 'probation_passed')
