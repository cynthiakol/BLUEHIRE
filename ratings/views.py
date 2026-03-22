from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from applications.models import Application
from accounts.models import JobSeeker, Employer
from jobs.models import Notification
from .models import Rating


@login_required
def rate_jobseeker(request, application_id):
    if request.user.role != 'Employer':
        messages.error(request, "Only employers can rate job seekers.")
        return redirect('employer_dashboard')

    application = get_object_or_404(
        Application,
        pk=application_id,
        job__employer__user=request.user,
        status__in=['Completed', 'Not Completed'],
    )
    jobseeker = application.applicant
    already_rated = Rating.objects.filter(
        reviewer=request.user,
        application=application,
        rated_jobseeker=jobseeker,
    ).first()

    if request.method == 'POST':
        if already_rated:
            messages.warning(request, "You already rated this worker.")
            return redirect('employer_dashboard')
        score = request.POST.get('score', '')
        comment = request.POST.get('comment', '').strip()
        if not score.isdigit() or not (1 <= int(score) <= 5):
            messages.error(request, "Please select a valid rating (1–5 stars).")
            return redirect(request.path)

        Rating.objects.create(
            reviewer=request.user,
            application=application,
            rated_jobseeker=jobseeker,
            score=int(score),
            comment=comment or None,
            is_visible=True,
        )

        # Notify the jobseeker
        try:
            employer = request.user.employer
            employer_name = employer.company_name or request.user.get_full_name() or request.user.username
        except:
            employer_name = request.user.get_full_name() or request.user.username

        star_label = f"{score} star{'s' if int(score) != 1 else ''}"
        Notification.objects.create(
            receiver=jobseeker.user,
            message=f"⭐ {employer_name} rated you {star_label} for \"{application.job.title}\". You can now rate them back!"
        )

        messages.success(request, "Rating submitted!")
        return redirect('employer_dashboard')

    return render(request, 'ratings/rate_jobseeker.html', {
        'application': application,
        'jobseeker': jobseeker,
        'job': application.job,
        'already_rated': already_rated,
        'is_no_show': application.status == 'Not Completed',
    })


@login_required
def rate_employer(request, application_id):
    if request.user.role != 'JobSeeker':
        messages.error(request, "Only job seekers can rate employers.")
        return redirect('jobseeker_dashboard')

    jobseeker = get_object_or_404(JobSeeker, user=request.user)
    application = get_object_or_404(
        Application,
        pk=application_id,
        applicant=jobseeker,
        status='Completed',
    )
    employer = application.job.employer
    already_rated = Rating.objects.filter(
        reviewer=request.user,
        application=application,
        rated_employer=employer,
    ).first()

    if request.method == 'POST':
        if already_rated:
            messages.warning(request, "You already rated this employer.")
            return redirect('jobseeker_dashboard')
        score = request.POST.get('score', '')
        comment = request.POST.get('comment', '').strip()
        if not score.isdigit() or not (1 <= int(score) <= 5):
            messages.error(request, "Please select a valid rating (1–5 stars).")
            return redirect(request.path)

        Rating.objects.create(
            reviewer=request.user,
            application=application,
            rated_employer=employer,
            score=int(score),
            comment=comment or None,
            is_visible=True,
        )

        # Notify the employer
        try:
            seeker_name = jobseeker.user.get_full_name() or jobseeker.user.username
        except:
            seeker_name = request.user.username

        star_label = f"{score} star{'s' if int(score) != 1 else ''}"
        Notification.objects.create(
            receiver=employer.user,
            message=f"⭐ {seeker_name} rated you {star_label} for \"{application.job.title}\"."
        )

        messages.success(request, "Rating submitted!")
        return redirect('jobseeker_dashboard')

    return render(request, 'ratings/rate_employer.html', {
        'application': application,
        'employer': employer,
        'job': application.job,
        'already_rated': already_rated,
    })


def jobseeker_ratings(request, jobseeker_id):
    jobseeker = get_object_or_404(JobSeeker, pk=jobseeker_id)
    ratings = Rating.objects.filter(
        rated_jobseeker=jobseeker, is_visible=True
    ).select_related('reviewer', 'application__job')
    stats = ratings.aggregate(avg=Avg('score'), total=Count('id'))
    avg_score = round(stats['avg'] or 0, 1)
    total = stats['total']
    distribution = {i: ratings.filter(score=i).count() for i in range(5, 0, -1)}
    return render(request, 'ratings/jobseeker_ratings.html', {
        'jobseeker': jobseeker,
        'ratings': ratings,
        'avg_score': avg_score,
        'total': total,
        'distribution': distribution,
        'filled_stars': range(1, round(avg_score) + 1),
        'empty_stars': range(round(avg_score) + 1, 6),
    })


def employer_ratings(request, employer_id):
    employer = get_object_or_404(Employer, pk=employer_id)
    ratings = Rating.objects.filter(
        rated_employer=employer, is_visible=True
    ).select_related('reviewer', 'application__job')
    stats = ratings.aggregate(avg=Avg('score'), total=Count('id'))
    avg_score = round(stats['avg'] or 0, 1)
    total = stats['total']
    distribution = {i: ratings.filter(score=i).count() for i in range(5, 0, -1)}
    return render(request, 'ratings/employer_ratings.html', {
        'employer': employer,
        'ratings': ratings,
        'avg_score': avg_score,
        'total': total,
        'distribution': distribution,
        'filled_stars': range(1, round(avg_score) + 1),
        'empty_stars': range(round(avg_score) + 1, 6),
    })