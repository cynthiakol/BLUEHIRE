from django.urls import path
from . import views

urlpatterns = [
    path("post/", views.post_job, name="post_job"),
    path("system-admin/pending-jobs/", views.pending_jobs_systemadmin, name="pending_jobs_systemadmin"),
    path("pending-jobs/", views.pending_jobs_systemadmin, name="pending_jobs_systemadmin"),
    path("approve/<int:job_id>/", views.approve_job, name="approve_job"),
    path("reject/<int:job_id>/", views.reject_job, name="reject_job"),
    path("employer/job/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("job/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("view/<int:job_id>/", views.view_job_details, name="view_job_details"),
]