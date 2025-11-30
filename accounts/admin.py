from django.contrib import admin
from jobs.models import Notification
from django.utils import timezone
from .models import DocumentVerification
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from applications.models import Application 
from django.utils.translation import gettext_lazy as _
from .models import (
    Users,
    JobSeeker,
    Employer,
    PhoneOTP,
    SystemLog,
    EmployerDocuments,
    JobSeekerCertificate,
    DocumentVerification,
)

# -------------------------
# Users admin
# -------------------------
@admin.register(Users)
class UsersAdmin(DjangoUserAdmin):
    # use the custom primary key field name if you prefer
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_superuser", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "role",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "email_verified_at")}),
        (_("Tokens"), {"fields": ("email_token",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

# -------------------------
# JobSeeker admin
# -------------------------
@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "region", "city", "profile_completion", "approval_status")
    search_fields = ("user__username", "user__first_name", "user__last_name", "region", "city")
    readonly_fields = ("date_created", "last_updated")
    list_filter = ("approval_status", "verification_status", "region", "job_type")

# -------------------------
# Employer admin
# -------------------------
@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "employer_type",
        "is_verified",
        "profile_completion",
    )
    list_filter = ("employer_type", "is_verified")
    search_fields = ("user__username", "user__email")
    actions = ["approve_documents", "reject_documents"]

    # ✅ approve selected employers
    def approve_documents(self, request, queryset):

        for employer in queryset:
            employer.is_verified = True

            # mark all docs approved depending on employer type
            if employer.employer_type == "Company":
                employer.business_permit_status = "Approved"
                employer.company_id_status = "Approved"
            else:
                employer.barangay_status = "Approved"
                employer.police_status = "Approved"
                employer.nbi_status = "Approved"
                employer.valid_id_status = "Approved"

            employer.save()

            # ✅ clear any suspicious AI alerts for this user
            DocumentVerification.objects.filter(user=employer.user, status="Suspicious").update(
                status="Verified",
                reason="Manually approved by system admin",
                ai_confidence=1.0,
            )

            # ✅ create a notification
            Notification.objects.create(
                receiver=employer.user,
                message=(
                    f"✅ Congratulations {employer.user.first_name}, your verification is complete! "
                    f"Your documents were successfully reviewed and your account is now verified on BlueHire."
                ),
                created_at=timezone.now(),
            )

        self.message_user(request, "Selected employer(s) approved and notified.")
    approve_documents.short_description = "Approve selected employer documents"

    # ✅ reject selected employers
    def reject_documents(self, request, queryset):


        for employer in queryset:
            employer.is_verified = False

            if employer.employer_type == "Company":
                employer.business_permit_status = "Rejected"
                employer.company_id_status = "Rejected"
            else:
                employer.barangay_status = "Rejected"
                employer.police_status = "Rejected"
                employer.nbi_status = "Rejected"
                employer.valid_id_status = "Rejected"

            employer.save()

            # ❌ mark all AI records as rejected for this user
            DocumentVerification.objects.filter(user=employer.user).update(
                status="Rejected",
                reason="Documents rejected by system admin",
                ai_confidence=0.0,
            )

            # ❌ create rejection notification
            Notification.objects.create(
                receiver=employer.user,
                message=(
                    f"❌ Hi {employer.user.first_name}, unfortunately your uploaded verification documents "
                    f"did not meet the requirements. Please re-upload clear and valid files for review."
                ),
                created_at=timezone.now(),
            )

        self.message_user(request, "Selected employer(s) rejected and notified.")
    reject_documents.short_description = "Reject selected employer documents"

    

# -------------------------
# Other simple models
# -------------------------
@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "otp", "created_at")
    readonly_fields = ("created_at",)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ("log_id", "user", "action", "timestamp")
    search_fields = ("user__username", "action")

@admin.register(EmployerDocuments)
class EmployerDocumentsAdmin(admin.ModelAdmin):
    list_display = ("doc_id", "employer", "document_type", "status", "expiry_date")
    list_filter = ("status",)

@admin.register(JobSeekerCertificate)
class JobSeekerCertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "jobseeker", "name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

@admin.register(DocumentVerification)
class DocumentVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "doc_type", "status", "ai_confidence", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "doc_type")

#class ApplicationAdmin(admin.ModelAdmin):
   # list_display = ('application_id', 'job', 'applicant', 'status', 'applied_date')
   # list_filter = ('status', 'applied_date')
   # search_fields = ('job__title', 'applicant__user__username', 'applicant__user__first_name', 'applicant__user__last_name')
   # list_editable = ('status',)
   # readonly_fields = ('applied_date',)
   # ordering = ('-applied_date',)
    
   # def get_queryset(self, request):
        #qs = super().get_queryset(request)
        #return qs.select_related('job', 'applicant__user')

# Register using this method only (no decorator above)
#admin.site.register(Application, ApplicationAdmin)