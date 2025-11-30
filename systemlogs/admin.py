from django.contrib import admin
from .models import SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'user', 'action', 'timestamp')
    search_fields = ('user__name', 'action')
    list_filter = ('timestamp',)
