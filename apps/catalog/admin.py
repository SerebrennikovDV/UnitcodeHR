from django.contrib import admin

from .models import Department, Position, Source, Stage, Skill


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'grade', 'department', 'salary_min', 'salary_max', 'is_active')
    list_filter = ('grade', 'department', 'is_active')
    search_fields = ('title',)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'cost_per_month', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'is_terminal', 'color')
    list_editable = ('color',)
    ordering = ('order',)
    search_fields = ('name',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'lemma', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'lemma')
