from django.core.management.base import BaseCommand
from accounts.models import JobSeeker
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Remove missing file references from JobSeeker documents"

    def handle(self, *args, **options):
        count = 0
        for seeker in JobSeeker.objects.all():
            for field in ['barangay_clearance','police_clearance','nbi_clearance','nc2_certificate']:
                file_field = getattr(seeker, field)
                if file_field and not os.path.exists(os.path.join(settings.MEDIA_ROOT, file_field.name)):
                    self.stdout.write(f"🗑 Removing missing: {file_field.name}")
                    setattr(seeker, field, None)
                    count += 1
            seeker.save()
        self.stdout.write(self.style.SUCCESS(f"Cleanup complete — {count} broken file references removed."))
