from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, TutorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'grade_level', 'created_at']
    search_fields = ['user__email', 'grade_level']
    list_filter = ['grade_level']


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'hourly_rate', 'bio', 'rating', 'created_at']
    search_fields = ['user__email', 'bio']
    list_filter = ['rating', 'subjects']
    filter_horizontal = ['subjects']