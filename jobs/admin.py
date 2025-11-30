from django.contrib import admin
from .models import Job, Notification

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'employer', 'category', 'salary', 'is_approved', 'is_available', 'created_at')
    list_filter = ('is_approved', 'is_available', 'category', 'created_at')
    search_fields = ('title', 'description', 'employer__user__username', 'employer__company_name')
    list_editable = ('is_approved', 'is_available')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'receiver', 'message_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('receiver__username', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'