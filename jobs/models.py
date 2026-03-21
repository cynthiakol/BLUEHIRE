from django.db import models
from django.utils import timezone
from accounts.models import Employer, JobSeeker
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

Users = get_user_model()

# Update in jobs/models.py

class Job(models.Model):
    CATEGORY_CHOICES = [
        ("Construction", "Construction"),
        ("Manufacturing", "Manufacturing"),
        ("Maintenance", "Maintenance"),
        ("Transportation", "Transportation"),
        ("Plumber", "Plumber"),
        ("Customer Service", "Customer Service"),
        ("Carpentry", "Carpentry"),
        ("Driver", "Driver"),
        ("Technician", "Technician"),
        ("Electrician", "Electrician"),
        ("Mechanic", "Mechanic"),
        ("Laborer", "Laborer"),
        ("Other", "Other"),
    ]
    
    # ✅ UPDATED: Added Contract type for Philippine context
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),      # Regular employment
        ('Part-time', 'Part-time'),      # Part-time work
        ('Contract', 'Contract'),        # Contract-based (project-based, fixed-term)
        ('Commission', 'Commission'),    # Commission-based (sales, agents, etc.)
    ]

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255, default="Surigao City")
    salary = models.CharField(max_length=100, blank=True, null=True)
    
    # ✅ UPDATED: Job Type now includes Contract
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Employment type (Full-time, Part-time, Contract, or Commission-based)"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # Hiring timeline fields
    application_deadline = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Applications will close automatically after this date/time"
    )
    hiring_quota = models.IntegerField(
        default=1, 
        help_text="Number of workers to hire"
    )
    auto_close_on_quota = models.BooleanField(
        default=False, 
        help_text="Automatically mark as unavailable when quota is met"
    )

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.title} - {self.employer.user.username} ({status})"
    
    def get_hired_count(self):
        """Returns number of applicants hired for this job"""
        return self.job_applications.filter(status="Hired").count()
    
    def get_rejected_count(self):
        """Returns number of applicants rejected for this job"""
        return self.job_applications.filter(status="Rejected").count()
    
    def get_total_applicants(self):
        """Returns total number of applicants"""
        return self.job_applications.count()
    
    def is_past_deadline(self):
        """Check if application deadline has passed"""
        if self.application_deadline:
            return timezone.now() > self.application_deadline
        return False
    
    def get_deadline_status(self):
        """Get human-readable deadline status"""
        if not self.application_deadline:
            return "No deadline set"
        
        now = timezone.now()
        
        if now > self.application_deadline:
            return "Expired"
        
        time_left = self.application_deadline - now
        days = time_left.days
        hours = time_left.seconds // 3600
        
        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} left"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} left"
        else:
            return "Less than 1 hour left"
    
    def get_time_remaining(self):
        """Get detailed time remaining"""
        if not self.application_deadline:
            return None
        
        now = timezone.now()
        if now > self.application_deadline:
            return {"expired": True}
        
        time_left = self.application_deadline - now
        return {
            "expired": False,
            "days": time_left.days,
            "hours": time_left.seconds // 3600,
            "minutes": (time_left.seconds % 3600) // 60
        }


class Application(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Hired", "Hired"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
        ("Not Completed", "Not Completed"),
    ]

    application_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_applications")
    applicant = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name="jobseeker_applications")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Pending")
    applied_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.applicant} applied for {self.job}"


class Notification(models.Model):
    receiver = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.receiver.username if self.receiver else 'Unknown'} - {self.message[:30]}"


# ============================================================
# SIGNALS
# ============================================================

@receiver(post_save, sender=Job)
def notify_admin_on_new_job(sender, instance, created, **kwargs):
    """Notify admin when new job is posted"""
    if created:
        Notification.objects.create(
            receiver=None,
            message=f"New job '{instance.title}' posted by {instance.employer.user.username} pending admin approval.",
        )