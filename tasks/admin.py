from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Task

class TaskInline(admin.TabularInline):
    """Shows all tasks created by a specific user directly on their user admin page."""
    model = Task
    extra = 0
    fields = ('task_title', 'name', 'date', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    ordering = ('-date', '-created_at')

# Re-register User with TaskInline
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Django Admin customization for Task model.
    - Displays Name, Date, Task Title, and Creation Date.
    - Adds search by Name, Task Title, and Description.
    - Adds date filters and date hierarchy.
    - Configures ordering by date and created_at.
    """
    list_display = ('task_title', 'user', 'name', 'date', 'created_at', 'updated_at')
    list_filter = ('user', 'date', 'created_at')
    search_fields = ('task_title', 'name', 'description', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Owner', {
            'fields': ('user',)
        }),
        ('Task Details', {
            'fields': ('task_title', 'name', 'date', 'description')
        }),
        ('System Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize Admin Site branding
admin.site.site_header = "TaskFlow Administration"
admin.site.site_title = "TaskFlow Admin Portal"
admin.site.index_title = "TaskFlow Management Dashboard"
