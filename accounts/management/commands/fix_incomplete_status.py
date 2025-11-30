from django.core.management.base import BaseCommand
from accounts.models import JobSeeker, Employer

class Command(BaseCommand):
    help = 'Updates existing users without complete documents to Incomplete status'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🔧 Fixing incomplete user statuses...'))
        
        # ========================================
        # FIX JOBSEEKERS
        # ========================================
        seekers = JobSeeker.objects.all()
        updated_seekers = 0
        kept_seekers = 0
        
        self.stdout.write('\n📋 Checking JobSeekers...')
        
        for seeker in seekers:
            has_all_docs = all([
                seeker.barangay_clearance,
                seeker.police_clearance,
                seeker.nbi_clearance,
                seeker.valid_id
            ])
            
            if not has_all_docs:
                # Missing documents - set to Incomplete
                if seeker.approval_status != "Incomplete":
                    old_status = seeker.approval_status
                    seeker.approval_status = "Incomplete"
                    seeker.verification_status = "Incomplete"
                    seeker.save()
                    updated_seekers += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  🔄 {seeker.user.username}: {old_status} → Incomplete (missing docs)"
                        )
                    )
            else:
                # Has all documents - keep current status
                kept_seekers += 1
                self.stdout.write(
                    f"  ✓ {seeker.user.username}: {seeker.approval_status} (has all docs)"
                )
        
        # ========================================
        # FIX EMPLOYERS
        # ========================================
        employers = Employer.objects.all()
        updated_employers = 0
        kept_employers = 0
        
        self.stdout.write('\n📋 Checking Employers...')
        
        for employer in employers:
            if employer.employer_type == "Company":
                has_all_docs = all([
                    employer.business_permit,
                    employer.company_id_file
                ])
            else:
                has_all_docs = all([
                    employer.barangay_clearance,
                    employer.police_clearance,
                    employer.nbi_clearance,
                    employer.valid_id
                ])
            
            if not has_all_docs:
                # Missing documents - set to Incomplete
                if employer.approval_status != "Incomplete":
                    old_status = employer.approval_status
                    employer.approval_status = "Incomplete"
                    employer.save()
                    updated_employers += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  🔄 {employer.user.username}: {old_status} → Incomplete (missing docs)"
                        )
                    )
            else:
                # Has all documents - keep current status
                kept_employers += 1
                self.stdout.write(
                    f"  ✓ {employer.user.username}: {employer.approval_status} (has all docs)"
                )
        
        # ========================================
        # SUMMARY
        # ========================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ SUMMARY:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f"JobSeekers:")
        self.stdout.write(f"  - Updated to Incomplete: {updated_seekers}")
        self.stdout.write(f"  - Kept current status: {kept_seekers}")
        self.stdout.write(f"\nEmployers:")
        self.stdout.write(f"  - Updated to Incomplete: {updated_employers}")
        self.stdout.write(f"  - Kept current status: {kept_employers}")
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'✅ Total updated: {updated_seekers + updated_employers} users'))