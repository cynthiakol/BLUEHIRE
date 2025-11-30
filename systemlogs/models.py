from django.db import models
from accounts.models import Users
from accounts.models import JobSeeker

class SystemLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='system_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'systemlog'
        verbose_name_plural = "System Logs"

    def __str__(self):
        return f"{self.user.name} - {self.action[:50]}"
    
class AIDocumentCheck(models.Model):
    jobseeker = models.ForeignKey(
        JobSeeker, on_delete=models.CASCADE, related_name="ai_document_checks"
    )
    document_type = models.CharField(max_length=100)  # e.g. Barangay Clearance
    detected_text = models.TextField(blank=True, null=True)  # OCR-extracted text
    confidence_score = models.FloatField(default=0.0)  # AI confidence %
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW FIELD — tells whether the alert was handled
    status = models.CharField(
        max_length=20,
        choices=[
            ("Flagged", "Flagged"),     # AI found something suspicious
            ("Cleared", "Cleared"),     # Admin approved the user/docs
            ("Rejected", "Rejected"),   # Admin rejected the user/docs
        ],
        default="Flagged",
    )

    def __str__(self):
        return f"{self.document_type} check ({self.confidence_score:.2f}%)"
