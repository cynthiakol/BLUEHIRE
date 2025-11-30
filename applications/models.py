from django.db import models
from accounts.models import JobSeeker
from jobs.models import Job
from jobs.models import Notification

class Application(models.Model):
    application_id = models.AutoField(primary_key=True)
    applicant = models.ForeignKey(
        JobSeeker,
        on_delete=models.CASCADE,
        db_column='applicant_id'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        db_column='job_id'
    )
    status = models.CharField(max_length=8, blank=True, null=True, default="Pending")
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'applications_application'

def mark_as_hired(application):
    application.status = "Hired"
    application.save()

    Notification.objects.create(
        user=application.applicant.user,
        message="🎉 Your application has been approved! Please check your email for next steps."
    )
