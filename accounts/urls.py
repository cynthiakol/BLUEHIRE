from django.urls import path
from . import views
from .views import generate_report

urlpatterns = [

    # ====================================================
    # 🔹 AUTH ROUTES
    # ====================================================
    path("signin_register/", views.signin_register, name="signin_register"),
    path("logout/", views.logout_view, name="logout_view"),

    # ====================================================
    # 🔹 OTP ROUTES (✅ ADD THESE TWO LINES)
    # ====================================================
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),

    # ====================================================
    # 🔹 PROFILE ROUTES
    # ====================================================
    path("profile/", views.profile_view, name="profile"),

    # ====================================================
    # 🔹 JOBSEEKER ROUTES
    # ====================================================
    path("jobseeker/profile/", views.jobseeker_profile, name="jobseeker_profile"),
    path("jobseeker/profile/update/", views.update_jobseeker_profile, name="update_jobseeker_profile"),
    path("jobseeker/documents/upload/", views.upload_jobseeker_documents, name="upload_jobseeker_documents"),
    path("jobseeker/certificates/upload/", views.upload_jobseeker_certificates, name="upload_jobseeker_certificates"),
    path("jobseeker/dashboard/", views.jobseeker_dashboard, name="jobseeker_dashboard"),
    path("job/apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("jobseeker/<int:jobseeker_id>/profile/", views.jobseeker_public_profile, name="jobseeker_public_profile"),
    path("jobseeker/recommendations/", views.jobseeker_recommendations, name="jobseeker_recommendations"),
    path("jobseeker/update-skills/", views.update_skills, name="update_skills"),

    # ====================================================
    # 🔹 SYSTEM ADMIN ROUTES
    # ====================================================
    path("dashboard/", views.system_admin_dashboard, name="system_admin_dashboard"),
    path("verify/<str:user_type>/<int:user_id>/<str:doc_type>/", views.verify_document, name="verify_document"),
    path("toggle/<int:user_id>/", views.toggle_verification, name="toggle_verification"),
    path('system-admin/clear-logs/', views.clear_old_logs, name='clear_old_logs'),

    # ✅ jobseeker actions
    path("jobseeker/approve/<int:seeker_id>/", views.approve_jobseeker, name="approve_jobseeker"),
    path("jobseeker/reject/<int:seeker_id>/", views.reject_jobseeker, name="reject_jobseeker"),
    path("jobseeker/reupload/<int:seeker_id>/", views.reupload_jobseeker, name="reupload_jobseeker"),
    path("employer/applications/", views.view_applications, name="view_applications"),
    
    # ✅ Employer ACTIONS
    path("employer/approve/<int:emp_id>/", views.approve_employer, name="approve_employer"),
    path("employer/reject/<int:emp_id>/", views.reject_employer, name="reject_employer"),
    path("employer/reupload/<int:emp_id>/", views.reupload_employer, name="reupload_employer"),

    # ✅ report & jobs
    path("report/", generate_report, name="generate_report"),
    path("generate-report/", generate_report, name="generate_report"),
    path("jobs/pending/", views.pending_jobs, name="pending_jobs"),
    path("jobs/approve/<int:job_id>/", views.approve_job, name="approve_job"),
    path("admin/jobs/reject/<int:job_id>/", views.reject_job, name="reject_job"),

    # ✅ document viewer
    path("view-document/<int:seeker_id>/<str:doc_type>/", views.view_document, name="view_document"),

    # ✅ jobseeker profile view for admin
    path("employer/jobseeker/<int:jobseeker_id>/", views.jobseeker_public_profile, name="system_admin_jobseeker_profile"),

    # ✅ application status updates
    path("employer/applications/update/<str:app_id>/", views.update_application_status, name="update_application_status"),
    
    path("jobs/search/", views.public_job_search, name="public_job_search"),

    # ====================================================
    # 🔹 EMPLOYER ROUTES
    # ====================================================
    path("employer/dashboard/", views.employer_dashboard, name="employer_dashboard"),
    path("employer/profile/", views.employer_profile, name="employer_profile"),
    path("employer/profile/update/", views.update_employer_profile, name="update_employer_profile"),
    path("employer/documents/upload/", views.upload_employer_documents, name="upload_employer_documents"),
    path("employer/<int:employer_id>/profile/", views.employer_public_profile, name="employer_public_profile"),
    path("employer/applications/", views.view_applications, name="view_applications"),
    path("employer/job/<int:job_id>/recommendations/", views.ai_recommend_seekers, name="ai_recommend_seekers"),
    path("employer/job/<int:job_id>/availability/", views.toggle_job_availability, name="toggle_job_availability"),

    # ====================================================
    # 🔹 NOTIFICATIONS
    # ====================================================
    path("notifications/", views.get_notifications, name="get_notifications"),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),

    # ====================================================
    # 🔹 EMAIL VERIFICATION
    # ====================================================
    path("verify-email/", views.verify_email, name="verify_email"),
    path("verify-email/<uuid:token>/", views.verify_email_token, name="verify_email_token"),
    path("resend-verification/", views.resend_verification, name="resend_verification"),
]