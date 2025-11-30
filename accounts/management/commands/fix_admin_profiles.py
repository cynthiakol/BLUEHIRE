# Create this file: accounts/management/commands/fix_admin_profiles.py

from django.core.management.base import BaseCommand
from accounts.models import Users, Employer, JobSeeker


class Command(BaseCommand):
    help = 'Fix admin users who have incorrect profiles or roles'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Checking all admin users...'))
        
        # Find all admin users
        admin_users = Users.objects.filter(
            is_superuser=True
        ) | Users.objects.filter(
            is_staff=True
        )
        
        for user in admin_users:
            self.stdout.write(f'\nChecking user: {user.username}')
            self.stdout.write(f'  Current role: {user.role}')
            self.stdout.write(f'  is_superuser: {user.is_superuser}')
            self.stdout.write(f'  is_staff: {user.is_staff}')
            
            fixed = False
            
            # Check for Employer profile
            try:
                employer = Employer.objects.get(user=user)
                self.stdout.write(self.style.ERROR(f'  ❌ Admin has Employer profile - DELETING'))
                employer.delete()
                fixed = True
            except Employer.DoesNotExist:
                self.stdout.write(self.style.SUCCESS(f'  ✅ No Employer profile'))
            
            # Check for JobSeeker profile
            try:
                jobseeker = JobSeeker.objects.get(user=user)
                self.stdout.write(self.style.ERROR(f'  ❌ Admin has JobSeeker profile - DELETING'))
                jobseeker.delete()
                fixed = True
            except JobSeeker.DoesNotExist:
                self.stdout.write(self.style.SUCCESS(f'  ✅ No JobSeeker profile'))
            
            # Fix role
            if user.role != 'Admin':
                self.stdout.write(self.style.ERROR(f'  ❌ Role is "{user.role}" - FIXING to "Admin"'))
                user.role = 'Admin'
                user.save()
                fixed = True
            else:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Role is correct'))
            
            if fixed:
                self.stdout.write(self.style.SUCCESS(f'✅ Fixed admin user: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Admin user is already correct: {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Done checking all admin users'))