from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
import random


# ---------------------------------------------------------------------
# CUSTOM USER MANAGER
# ---------------------------------------------------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "Admin")
        return self.create_user(username, email, password, **extra_fields)


# ---------------------------------------------------------------------
# USERS TABLE
# ---------------------------------------------------------------------
class Users(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('JobSeeker', 'Job Seeker'),
            ('Employer', 'Employer'),
            ('Admin', 'System Admin'),
        ],
        blank=True,  # ✅ ADD THIS
        null=True,   # ✅ ADD THIS
    )
    
    is_verified = models.BooleanField(default=False)
    email_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'


# ---------------------------------------------------------------------
# JOB SEEKER TABLE
# ---------------------------------------------------------------------
# REPLACE the entire JobSeeker class in accounts/models.py (starting around line 50)
# Keep everything else in models.py the same

class JobSeeker(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    VALID_ID_CHOICES = [
        ('National ID', 'National ID'),
        ('Passport', 'Passport'),
        ('Driver\'s License', 'Driver\'s License'),
        ('UMID', 'UMID'),
        ('Voter\'s ID', 'Voter\'s ID'),
        ('PhilHealth', 'PhilHealth'),
    ]

    seeker_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id")

    # --- Basic info ---
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    # --- Documents ---
    barangay_clearance = models.FileField(upload_to="clearances/barangay/", blank=True, null=True)
    police_clearance = models.FileField(upload_to="clearances/police/", blank=True, null=True)
    nbi_clearance = models.FileField(upload_to="clearances/nbi/", blank=True, null=True)
    nc2_certificate = models.FileField(upload_to="certificates/nc2/", blank=True, null=True)
    valid_id_type = models.CharField(max_length=100, choices=VALID_ID_CHOICES, blank=True, null=True)
    valid_id = models.FileField(upload_to="ids/", blank=True, null=True)
    valid_id_back = models.FileField(upload_to="ids/", blank=True, null=True)  # ✅ NEW FIELD

    # --- System fields ---
    verification_status = models.CharField(max_length=50, default="Pending")
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
        ],
        default="Pending",
    )
    profile_completion = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    # ---- AI Matching Fields ----
    skills = models.JSONField(default=list, blank=True, null=True)
    preferred_job_types = models.JSONField(default=list, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    certifications = models.JSONField(default=list, blank=True, null=True)

    # --- Preferred Job Type (manual selection for AI recommendation) ---
    job_type = models.CharField(
        max_length=50,
        choices=[
            ("Construction", "Construction"),
            ("Manufacturing", "Manufacturing"),
            ("Maintenance", "Maintenance"),
            ("Transportation", "Transportation"),
            ('Plumber', 'Plumber'),
            ("Customer Service", "Customer Service"),
            ('Carpentry', 'Carpentry'),
            ("Driver", "Driver"),
            ("Technician", "Technician"),
            ("Electrician", "Electrician"),
            ("Mechanic", "Mechanic"),
            ("Laborer", "Laborer"),
            ("Other", "Other"),
        ],
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "jobseeker"
        verbose_name_plural = "Job Seekers"
        managed = True

    def __str__(self):
        if hasattr(self, "user") and self.user:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            return full_name if full_name else self.user.username
        return f"JobSeeker #{self.seeker_id}"


# ---------------------------------------------------------------------
# EMPLOYER TABLE
# ---------------------------------------------------------------------
class Employer(models.Model):
    employer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)

    EMPLOYER_TYPE_CHOICES = [
        ("Personal", "Personal"),
        ("Company", "Company"),
    ]
    employer_type = models.CharField(
        max_length=20,
        choices=EMPLOYER_TYPE_CHOICES,
        default="Personal",
        blank=True,
        null=True,
    )

    profile_completion = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=50, default="Pending")

    # -------------------------------
    # Company employer fields
    # -------------------------------
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    business_permit = models.FileField(upload_to="company_docs/permits/", blank=True, null=True)
    company_id_file = models.FileField(upload_to="company_docs/ids/", blank=True, null=True)
    # ✅ CHANGED: Remove default="Pending", use None instead
    business_permit_status = models.CharField(max_length=20, blank=True, null=True)
    company_id_status = models.CharField(max_length=20, blank=True, null=True)

    # -------------------------------
    # Personal employer fields
    # -------------------------------
    personal_address = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to="employer_photos/", blank=True, null=True)
    barangay_clearance = models.FileField(upload_to="employer_docs/barangay/", blank=True, null=True)
    police_clearance = models.FileField(upload_to="employer_docs/police/", blank=True, null=True)
    nbi_clearance = models.FileField(upload_to="employer_docs/nbi/", blank=True, null=True)
    valid_id = models.FileField(upload_to="employer_docs/valid_id/", blank=True, null=True)
    valid_id_back = models.FileField(upload_to="employer_docs/valid_id/", blank=True, null=True)  # ✅ ADD THIS
    valid_id_type = models.CharField(max_length=100, blank=True, null=True)
    # ✅ CHANGED: Remove default="Pending", use None instead
    barangay_status = models.CharField(max_length=20, blank=True, null=True)
    police_status = models.CharField(max_length=20, blank=True, null=True)
    nbi_status = models.CharField(max_length=20, blank=True, null=True)
    valid_id_status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.employer_type or 'N/A'})"


# ---------------------------------------------------------------------
# PHONE OTP
# ---------------------------------------------------------------------
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "phone_otp"
        managed = True

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone} - {self.otp}"


# ---------------------------------------------------------------------
# SYSTEM LOG
# ---------------------------------------------------------------------
class SystemLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="account_logs")
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "systemlog"
        managed = True

    def __str__(self):
        return f"{self.user.username} - {self.action}"


# ---------------------------------------------------------------------
# EMPLOYER DOCUMENTS
# ---------------------------------------------------------------------
class EmployerDocuments(models.Model):
    doc_id = models.AutoField(primary_key=True)
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name="accounts_documents",
    )
    document_type = models.CharField(max_length=50)
    document_file = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending")
    expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "employerdocuments"
        verbose_name_plural = "Employer Documents"
        managed = True

    def __str__(self):
        return f"{self.employer.user.username} - {self.document_type}"


# ---------------------------------------------------------------------
# JOB SEEKER CERTIFICATE
# ---------------------------------------------------------------------
class JobSeekerCertificate(models.Model):
    jobseeker = models.ForeignKey("JobSeeker", on_delete=models.CASCADE, related_name="certificates")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/certificates/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.jobseeker.user.username})"


# ---------------------------------------------------------------------
# DOCUMENT VERIFICATION
# ---------------------------------------------------------------------
class DocumentVerification(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
        ("Suspicious", "Suspicious"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=100)
    file = models.FileField(upload_to="doc_verifications/")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    ai_confidence = models.FloatField(default=0.0)
    reason = models.TextField(blank=True, null=True)
    hash_signature = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} | {self.doc_type} | {self.status}"