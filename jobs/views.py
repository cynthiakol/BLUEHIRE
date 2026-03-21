from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Employer, JobSeeker
from accounts.utils import check_verification
from .models import Job, Notification 
from systemlogs.models import SystemLog
from datetime import timedelta
from .models import Job
from .models import Employer, Job 
# ---------------------------------------------------------------------
# EMPLOYER — CREATE JOB
# ---------------------------------------------------------------------

@check_verification
@login_required
def post_job(request):
    employer = Employer.objects.filter(user=request.user).first()
    if not employer:
        messages.error(request, "Employer profile not found.")
        return redirect("employer_dashboard")

    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        salary = request.POST.get("salary")
        location = request.POST.get("location", "Surigao City")  # ✅ NEW
        job_type = request.POST.get("job_type")  # ✅ NEW
        deadline = request.POST.get("application_deadline")
        hiring_quota = request.POST.get("hiring_quota", 1)
        auto_close = request.POST.get("auto_close_on_quota") == "on"
        
        from django.utils import timezone
        from datetime import datetime
        
        # Parse deadline if provided
        application_deadline = None
        if deadline:
            try:
                application_deadline = timezone.make_aware(
                    datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                )
            except ValueError:
                messages.error(request, "Invalid deadline format.")
                return redirect("post_job")

        Job.objects.create(
            employer=employer,
            title=title,
            category=category,
            description=description,
            salary=salary,
            location=location,  # ✅ NEW
            job_type=job_type,  # ✅ NEW
            application_deadline=application_deadline,
            hiring_quota=int(hiring_quota),
            auto_close_on_quota=auto_close,
            is_approved=False,
        )

        messages.success(request, "Job posted successfully! Awaiting admin approval.")
        return redirect("employer_dashboard")

    return render(request, "core/post_job.html")

# ---------------------------------------------------------------------
# JOB SEEKER — APPLY TO JOB
# ---------------------------------------------------------------------
@login_required
@check_verification
def apply_job(request, job_id):
    try:
        jobseeker = JobSeeker.objects.get(user=request.user)
    except JobSeeker.DoesNotExist:
        messages.error(request, "Job Seeker profile not found. Please register as a job seeker.")
        return redirect('/register/')

    job = get_object_or_404(Job, pk=job_id)

    # Application handling (uncomment when Application model exists)
    # if Application.objects.filter(job=job, jobseeker=jobseeker).exists():
    #     messages.warning(request, "You already applied to this job.")
    #     return redirect('job_detail', job_id=job.id)

    # Application.objects.create(job=job, jobseeker=jobseeker, applied_at=timezone.now())

    messages.success(request, "Your application has been submitted successfully!")
    return redirect('jobseeker_dashboard')


# ---------------------------------------------------------------------
# EMPLOYER — VIEW THEIR JOBS
# ---------------------------------------------------------------------
@login_required
def view_applications(request):
    if request.user.role != "Employer":
        messages.error(request, "Only employers can view applications.")
        return redirect("homepage")

    employer = Employer.objects.filter(user=request.user).first()
    if not employer:
        messages.error(request, "Employer profile not found.")
        return redirect("signin_register")

    jobs = Job.objects.filter(employer=employer).order_by("-created_at")
    context = {
        "employer": employer,
        "jobs": jobs,
    }
    return render(request, "core/view_applications.html", context)


# ---------------------------------------------------------------------
# SYSTEM ADMIN — VIEW PENDING JOBS
# ---------------------------------------------------------------------
@login_required
def pending_jobs_systemadmin(request):
    # restrict access
    if not hasattr(request.user, "role") or request.user.role != "Admin":
        messages.error(request, "Access denied.")
        return redirect("homepage")

    # get all pending jobs posted by verified employers
    pending_jobs = Job.objects.filter(
        is_approved=False,
        employer__employer_type__in=["Personal", "Company"],
        employer__is_verified=True
    ).select_related("employer").order_by("-created_at")

    # counts for top display
    verified_employers = Employer.objects.filter(is_verified=True).count()
    verified_seekers = JobSeeker.objects.filter(verification_status="Verified").count()
    pending_count = pending_jobs.count()

    context = {
        "title": "Pending Job Approvals",
        "pending_jobs": pending_jobs,
        "verified_employers": verified_employers,
        "verified_seekers": verified_seekers,
        "pending_count": pending_count,
    }

    return render(request, "core/pending_jobs.html", context)


# ---------------------------------------------------------------------
# SYSTEM ADMIN — APPROVE / REJECT JOBS
# ---------------------------------------------------------------------
@login_required
def approve_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # mark job as approved
    job.is_approved = True
    job.save()

    # log system action
    SystemLog.objects.create(
        user=request.user,
        action=f"Job '{job.title}' approved by {request.user.username}"
    )

    # send notification to employer (if jobseeker object exists)
    try:
        Notification.objects.create(
            receiver=job.employer.user.jobseeker_set.first(),  # ✅ this expects a JobSeeker object
            message=f"Your job '{job.title}' has been approved by admin."
        )
    except Exception as e:
        print("Notification error:", e)

    messages.success(request, f"Job '{job.title}' approved successfully.")
    return redirect("pending_jobs_systemadmin")

@login_required
def reject_job(request, job_id):
    if not hasattr(request.user, "role") or request.user.role != "Admin":
        messages.error(request, "Access denied.")
        return redirect("homepage")

    job = get_object_or_404(Job, id=job_id)

    # ✅ fix: remove 'details' and use only 'action'
    SystemLog.objects.create(
        user=request.user,
        action=f"Job '{job.title}' rejected by {request.user.username}"
    )

    job.delete()
    messages.success(request, f"Job '{job.title}' rejected and removed.")
    return redirect("pending_jobs_systemadmin")

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer__user=request.user)

    # ✅ updated categories
    categories = [
        "Construction",
        "Manufacturing",
        "Maintenance",
        "Transportation",
        "Carpentry",
        "Customer Service",
        "Plumber",
        "Driver",
        "Technician",
        "Electrician",
        "Mechanic",
        "Laborer",
        "Other",
    ]

    if request.method == "POST":
        job.title = request.POST.get("title")
        job.description = request.POST.get("description")
        job.category = request.POST.get("category")
        job.location = request.POST.get("location")
        job.salary = request.POST.get("salary")
        job.job_type = request.POST.get("job_type")  # ✅ NEW - Add this line
        
        # ✅ NEW: Handle deadline updates
        deadline = request.POST.get("application_deadline")
        if deadline:
            from django.utils import timezone
            from datetime import datetime
            try:
                job.application_deadline = timezone.make_aware(
                    datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                )
            except ValueError:
                messages.error(request, "Invalid deadline format.")
                return redirect("edit_job", job_id=job_id)
        else:
            job.application_deadline = None
        
        # ✅ NEW: Handle quota updates
        hiring_quota = request.POST.get("hiring_quota", 1)
        job.hiring_quota = int(hiring_quota)
        job.auto_close_on_quota = request.POST.get("auto_close_on_quota") == "on"
        
        job.save()

        messages.success(request, "✅ Job listing updated successfully!")
        return redirect("employer_dashboard")

    return render(request, "core/edit_job.html", {"job": job, "categories": categories})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job

@login_required
def view_job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Fix stats — annotate counts directly on the job object
    from applications.models import Application
    from django.db.models import Count, Q

    job.total_applicants = Application.objects.filter(job=job).count()
    job.hired_count = Application.objects.filter(job=job, status="Hired").count()

    has_applied = False
    application_status = None

    if hasattr(request.user, 'role') and request.user.role == 'JobSeeker':
        try:
            from accounts.models import JobSeeker
            jobseeker = JobSeeker.objects.get(user=request.user)
            application = Application.objects.filter(job=job, applicant=jobseeker).first()
            if application:
                has_applied = True
                application_status = application.status
        except Exception:
            pass

    return render(request, "core/view_job_details.html", {
        "job": job,
        "has_applied": has_applied,
        "application_status": application_status,
    })

@login_required
def employer_job_list(request):
    """
    Display all jobs posted by this employer
    Shows: Pending, Approved, Rejected status
    """
    try:
        employer = Employer.objects.get(user=request.user)
    except Employer.DoesNotExist:
        messages.error(request, "Employer profile not found.")
        return redirect("signin_register")
    
    from django.db.models import Count, Q
    
    # Get all jobs with application stats
    jobs = Job.objects.filter(employer=employer).annotate(
        total_applicants=Count('job_applications'),
        hired_count=Count('job_applications', filter=Q(job_applications__status='Hired')),
        pending_count=Count('job_applications', filter=Q(job_applications__status='Pending'))
    ).order_by("-created_at")
    
    # Categorize jobs
    pending_jobs = jobs.filter(is_approved=False)
    approved_jobs = jobs.filter(is_approved=True, is_available=True)
    closed_jobs = jobs.filter(is_approved=True, is_available=False)
    
    context = {
        "employer": employer,
        "all_jobs": jobs,
        "pending_jobs": pending_jobs,
        "approved_jobs": approved_jobs,
        "closed_jobs": closed_jobs,
    }
    return render(request, "core/employer_job_list.html", context)
