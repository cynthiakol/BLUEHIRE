from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import Job, Notification

class Command(BaseCommand):
    help = 'Close job listings that have passed their application deadline'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find jobs that are still available but past deadline
        expired_jobs = Job.objects.filter(
            is_available=True,
            application_deadline__lt=now
        ).select_related('employer__user')
        
        count = 0
        for job in expired_jobs:
            job.is_available = False
            job.save(update_fields=['is_available'])
            count += 1
            
            # Notify employer
            Notification.objects.create(
                receiver=job.employer.user,
                message=f"⏰ Your job listing '{job.title}' has been automatically closed due to the application deadline being reached."
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"Closed job '{job.title}' (ID: {job.id})")
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully closed {count} expired job listing(s)')
        )