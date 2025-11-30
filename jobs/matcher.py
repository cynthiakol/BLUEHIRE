# jobs/matcher.py
# AI Matching System for BlueHire
# Matches job seekers to jobs based on skills, preferences, NC2 certificates, and experience

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_similarity(seekers, job):
    """
    Enhanced AI matching algorithm that ranks job seekers for a specific job.
    
    Scoring Breakdown:
    - Skills match: 40% weight (TF-IDF similarity)
    - Preferred job types: 30% weight (exact/partial category match)
    - NC2 Certificate: 20% weight (HUGE BONUS for verified skills)
    - Experience years: 10% weight (scaled 0-5+ years)
    
    Args:
        seekers: QuerySet or list of JobSeeker objects
        job: Job object to match against
    
    Returns:
        List of (seeker, similarity_score) tuples sorted by score (highest first)
        similarity_score is between 0.0 and 1.0
    """
    results = []
    
    # Prepare job text for comparison
    job_text = f"{job.title} {job.category} {job.description}".lower()
    
    for seeker in seekers:
        score_components = {
            'skills': 0.0,
            'job_types': 0.0,
            'nc2_bonus': 0.0,
            'experience': 0.0
        }
        
        # ===============================================
        # 1. SKILLS MATCHING (40% weight)
        # ===============================================
        seeker_skills = ""
        if seeker.skills:
            skills_list = seeker.skills if isinstance(seeker.skills, list) else [str(seeker.skills)]
            seeker_skills = " ".join([str(s).lower() for s in skills_list])
        
        if seeker_skills and job_text:
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                vectors = vectorizer.fit_transform([seeker_skills, job_text])
                skills_similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                score_components['skills'] = skills_similarity * 0.40  # 40% weight
            except Exception as e:
                print(f"Skills matching error for {seeker.user.username}: {e}")
                score_components['skills'] = 0.0
        
        # ===============================================
        # 2. PREFERRED JOB TYPES MATCHING (30% weight)
        # ===============================================
        if seeker.preferred_job_types:
            job_types_list = seeker.preferred_job_types if isinstance(seeker.preferred_job_types, list) else [str(seeker.preferred_job_types)]
            
            # Check for exact category match
            if job.category in job_types_list:
                score_components['job_types'] = 0.30  # Perfect match = 30%
            else:
                # Check for partial match
                job_category_lower = job.category.lower()
                for pref in job_types_list:
                    pref_lower = str(pref).lower()
                    if pref_lower in job_category_lower or job_category_lower in pref_lower:
                        score_components['job_types'] = 0.20  # Partial match = 20%
                        break
        
        # ===============================================
        # 3. NC2 CERTIFICATE VERIFICATION (20% weight) - HUGE BONUS!
        # ===============================================
        nc2_verified = False
        
        # Check if seeker has uploaded NC2 certificate (direct field)
        if hasattr(seeker, 'nc2_certificate') and seeker.nc2_certificate:
            nc2_verified = True
            score_components['nc2_bonus'] = 0.20  # Full 20% bonus for having NC2
            print(f"[NC2 BOOST] {seeker.user.username} has NC2 certificate (field)")
        
        # Alternative: Check if they have certificates in the certifications JSON field
        if not nc2_verified and hasattr(seeker, 'certifications') and seeker.certifications:
            certs_list = seeker.certifications if isinstance(seeker.certifications, list) else []
            # Check if any certification mentions NC2, TESDA, or relevant trade
            for cert in certs_list:
                cert_lower = str(cert).lower()
                if any(keyword in cert_lower for keyword in ['nc2', 'nc ii', 'tesda', 'national certificate']):
                    nc2_verified = True
                    score_components['nc2_bonus'] = 0.20
                    print(f"[NC2 BOOST] {seeker.user.username} has NC2 in certifications field")
                    break
        
        # Alternative: Check JobSeekerCertificate model (uploaded certificate files)
        if not nc2_verified:
            try:
                from accounts.models import JobSeekerCertificate
                has_certificates = JobSeekerCertificate.objects.filter(
                    jobseeker=seeker
                ).exists()
                if has_certificates:
                    # If they uploaded any certificates, give partial bonus
                    score_components['nc2_bonus'] = 0.15  # 15% for having certificates
                    nc2_verified = True
                    print(f"[NC2 BOOST] {seeker.user.username} has uploaded certificates")
            except Exception as e:
                print(f"Certificate check error: {e}")
        
        # ===============================================
        # 4. EXPERIENCE MATCHING (10% weight)
        # ===============================================
        if hasattr(seeker, 'experience_years') and seeker.experience_years:
            try:
                years = int(seeker.experience_years)
                # Scale: 0 years = 0%, 5+ years = 10% (full weight)
                experience_score = min(years / 5.0, 1.0) * 0.10
                score_components['experience'] = experience_score
            except Exception as e:
                print(f"Experience parsing error: {e}")
                score_components['experience'] = 0.0
        
        # ===============================================
        # CALCULATE FINAL SCORE
        # ===============================================
        final_score = sum(score_components.values())
        
        # Ensure score is between 0 and 1
        final_score = max(0.0, min(1.0, final_score))
        
        # Debug logging (comment out in production)
        print(f"[AI MATCHER] {seeker.user.username}: "
              f"Skills={score_components['skills']:.2f}, "
              f"JobTypes={score_components['job_types']:.2f}, "
              f"NC2={score_components['nc2_bonus']:.2f}, "
              f"Experience={score_components['experience']:.2f}, "
              f"FINAL={final_score:.2f}")
        
        results.append((seeker, final_score))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def recommend_jobs_for_seeker(seeker, available_jobs):
    """
    Recommend jobs for a specific job seeker based on their profile.
    Same algorithm but reversed (seeker → jobs instead of jobs → seekers)
    
    Scoring Breakdown:
    - Skills/text similarity: 50% weight
    - Category match: 30% weight
    - NC2 bonus: 20% weight (if seeker has NC2, boost ALL job matches)
    
    Args:
        seeker: JobSeeker object
        available_jobs: QuerySet or list of Job objects
    
    Returns:
        List of (job, similarity_score) tuples sorted by score (highest first)
        similarity_score is between 0.0 and 1.0
    """
    results = []
    
    # Prepare seeker profile text
    seeker_text = ""
    
    if seeker.skills:
        skills_list = seeker.skills if isinstance(seeker.skills, list) else [str(seeker.skills)]
        seeker_text += " ".join([str(s).lower() for s in skills_list])
    
    if seeker.preferred_job_types:
        job_types_list = seeker.preferred_job_types if isinstance(seeker.preferred_job_types, list) else [str(seeker.preferred_job_types)]
        seeker_text += " " + " ".join([str(jt).lower() for jt in job_types_list])
    
    if not seeker_text.strip():
        print(f"[RECOMMEND] No skills/preferences for {seeker.user.username}")
        return []  # Can't match without any data
    
    # Check if seeker has NC2 (this boosts ALL job recommendations)
    seeker_has_nc2 = False
    if hasattr(seeker, 'nc2_certificate') and seeker.nc2_certificate:
        seeker_has_nc2 = True
    elif hasattr(seeker, 'certifications') and seeker.certifications:
        certs_list = seeker.certifications if isinstance(seeker.certifications, list) else []
        for cert in certs_list:
            cert_lower = str(cert).lower()
            if any(keyword in cert_lower for keyword in ['nc2', 'nc ii', 'tesda', 'national certificate']):
                seeker_has_nc2 = True
                break
    
    if seeker_has_nc2:
        print(f"[RECOMMEND] {seeker.user.username} has NC2 - boosting all matches")
    
    for job in available_jobs:
        score_components = {
            'skills': 0.0,
            'category': 0.0,
            'nc2_bonus': 0.0,
        }
        
        # Job text for comparison
        job_text = f"{job.title} {job.category} {job.description}".lower()
        
        # 1. Text similarity (50% weight)
        if seeker_text and job_text:
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                vectors = vectorizer.fit_transform([seeker_text, job_text])
                text_similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                score_components['skills'] = text_similarity * 0.50
            except Exception as e:
                print(f"Text similarity error: {e}")
                score_components['skills'] = 0.0
        
        # 2. Category match (30% weight)
        if seeker.preferred_job_types:
            job_types_list = seeker.preferred_job_types if isinstance(seeker.preferred_job_types, list) else []
            if job.category in job_types_list:
                score_components['category'] = 0.30
            else:
                job_category_lower = job.category.lower()
                for pref in job_types_list:
                    pref_lower = str(pref).lower()
                    if pref_lower in job_category_lower or job_category_lower in pref_lower:
                        score_components['category'] = 0.20
                        break
        
        # 3. NC2 bonus (20% weight) - if seeker has NC2, boost all job matches
        if seeker_has_nc2:
            score_components['nc2_bonus'] = 0.20
        
        final_score = sum(score_components.values())
        final_score = max(0.0, min(1.0, final_score))
        
        results.append((job, final_score))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    print(f"[RECOMMEND] Top 3 jobs for {seeker.user.username}:")
    for job, score in results[:3]:
        print(f"  - {job.title}: {score:.2f}")
    
    return results


def rank_applicants(job):
    """
    Convenience function to rank all applicants for a specific job.
    
    Args:
        job: Job object
    
    Returns:
        List of (applicant, score) tuples sorted by score
    """
    from applications.models import Application
    
    # Get all applicants for this job
    applications = Application.objects.filter(job=job).select_related('applicant', 'applicant__user')
    applicants = [app.applicant for app in applications]
    
    if not applicants:
        return []
    
    # Use compute_similarity to rank them
    return compute_similarity(applicants, job)