from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employer, JobSeeker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobs.models import Job
from accounts.models import JobSeeker
from django.contrib.auth.decorators import login_required

def check_verification(view_func):
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not user or not hasattr(user, "email"):
            messages.error(request, "Please sign in first.")
            return redirect("signin_register")

        try:
            if user.role == "Employer":
                employer = Employer.objects.get(user_id=user.user_id)
                if not employer.is_verified:
                    messages.warning(request, "You need to verify your documents before posting a job.")
                    return redirect("employer_profile")  # ✅ fixed redirect

            elif user.role == "JobSeeker":
                seeker = JobSeeker.objects.get(user_id=user.user_id)
                if not (seeker.barangay_verified and seeker.nbi_verified and seeker.police_verified):
                    messages.warning(request, "Please complete your verification documents first.")
                    return redirect("jobseeker_profile")  # ✅ fixed redirect

        except (Employer.DoesNotExist, JobSeeker.DoesNotExist):
            messages.error(request, "Account record not found.")
            return redirect("signin_register")

        return view_func(request, *args, **kwargs)
    return wrapper


def get_recommended_jobs_for_seeker(seeker, top_n=5):
    """Improved AI job matcher with lower threshold and better field merging"""
    jobs = Job.objects.filter(is_available=True)
    if not jobs.exists():
        return []

    # Build seeker profile text
    seeker_text_parts = []

    # Add skills
    if seeker.skills:
        if isinstance(seeker.skills, list):
            seeker_text_parts.extend(seeker.skills)
        elif isinstance(seeker.skills, str):
            seeker_text_parts.append(seeker.skills)

    # Add preferred job types
    if hasattr(seeker, "preferred_job_types") and seeker.preferred_job_types:
        if isinstance(seeker.preferred_job_types, list):
            seeker_text_parts.extend(seeker.preferred_job_types)
        elif isinstance(seeker.preferred_job_types, str):
            seeker_text_parts.append(seeker.preferred_job_types)

    seeker_text = " ".join(seeker_text_parts).strip()
    if not seeker_text:
        return []

    # Build job texts
    job_texts = [
        f"{job.title or ''} {job.category or ''} {job.description or ''}"
        for job in jobs
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([seeker_text] + job_texts)
    scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    # Sort and filter
    ranked = sorted(zip(jobs, scores), key=lambda x: x[1], reverse=True)
    recommendations = []

    for job, score in ranked[:top_n]:
        if score > 0.05:  # lowered threshold to 5%
            recommendations.append((job, round(score * 100, 1)))

    return recommendations