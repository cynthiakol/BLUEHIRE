from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display    = ('id', 'reviewer', 'get_target', 'score', 'is_visible', 'get_job', 'created_at')
    list_filter     = ('score', 'is_visible', 'created_at')
    list_editable   = ('is_visible',)
    readonly_fields = ('created_at',)
    search_fields   = ('reviewer__username', 'rated_jobseeker__user__username',
                       'rated_employer__user__username', 'comment')

    def get_target(self, obj):
        if obj.rated_jobseeker:
            return f"Worker: {obj.rated_jobseeker.user.username}"
        if obj.rated_employer:
            return f"Employer: {obj.rated_employer.user.username}"
        return '—'
    get_target.short_description = 'Rated'

    def get_job(self, obj):
        return obj.application.job.title if obj.application else '—'
    get_job.short_description = 'Job'