from django.contrib import admin
from .models import Subject, LessonRequest


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'tutor', 'subject', 'start_time', 'duration_minutes', 'status', 'created_at']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['student__email', 'tutor__email', 'subject__name']
    date_hierarchy = 'created_at'
