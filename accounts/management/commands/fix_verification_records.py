from django.core.management.base import BaseCommand
from accounts.models import JobSeeker, DocumentVerification
from django.utils import timezone

class Command(BaseCommand):
    help = 'Fix missing or incorrect document verification records for approved jobseekers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Fixing verification records...'))
        
        # Get all approved jobseekers
        approved_seekers = JobSeeker.objects.filter(approval_status="Approved")
        
        fixed_count = 0
        created_count = 0
        
        for seeker in approved_seekers:
            self.stdout.write(f"\n📋 Checking {seeker.user.username}...")
            
            doc_types = [
                ("Barangay Clearance", seeker.barangay_clearance),
                ("Police Clearance", seeker.police_clearance),
                ("Nbi Clearance", seeker.nbi_clearance),
                ("Valid Id", seeker.valid_id),
            ]
            
            for doc_name, doc_file in doc_types:
                if doc_file:  # Only process if document exists
                    verification, created = DocumentVerification.objects.update_or_create(
                        user=seeker.user,
                        doc_type=doc_name,
                        defaults={
                            "file": doc_file,
                            "status": "Verified",  # Set to Verified since jobseeker is approved
                            "ai_confidence": 1.0,
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"  ✅ Created verification record for {doc_name}"))
                        created_count += 1
                    elif verification.status != "Verified":
                        self.stdout.write(self.style.WARNING(f"  🔄 Updated {doc_name} status to Verified"))
                        fixed_count += 1
                    else:
                        self.stdout.write(f"  ✓ {doc_name} already verified")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created {created_count} records, Fixed {fixed_count} records'))