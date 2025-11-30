"""
Enhanced AI Job Recommendation System for BlueHire
Multi-factor scoring with CERTIFICATES support
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def normalize_text(text):
    """Clean and normalize text for matching"""
    if not text:
        return ""
    
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)
    
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def compute_enhanced_match_score(seeker, job):
    """
    Enhanced matching algorithm with CERTIFICATES support
    Returns a score from 0-100 representing match quality
    """
    
    total_score = 0
    
    # ================================
    # 1. SKILLS MATCHING (35 points max) - REDUCED from 40
    # ================================
    skills_score = 0
    seeker_skills = normalize_text(seeker.skills)
    
    job_title = normalize_text(job.title)
    job_category = normalize_text(job.category)
    job_description = normalize_text(job.description)
    
    if seeker_skills:
        # Direct category match (12 points)
        if job_category and job_category in seeker_skills:
            skills_score += 12
        
        # Title keywords in skills (13 points)
        title_words = set(job_title.split())
        skill_words = set(seeker_skills.split())
        
        title_matches = len(title_words & skill_words)
        if title_matches > 0:
            skills_score += min(13, title_matches * 5)
        
        # TF-IDF semantic similarity (10 points)
        if job_description:
            try:
                vectorizer = TfidfVectorizer(
                    max_features=100,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                vectors = vectorizer.fit_transform([seeker_skills, job_description])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                skills_score += similarity * 10
            except:
                pass
    
    total_score += min(35, skills_score)
    
    # ================================
    # 2. CERTIFICATES & CERTIFICATIONS (15 points max) - NEW!
    # ================================
    cert_score = 0
    
    # Get certificates from JobSeekerCertificate model
    try:
        from accounts.models import JobSeekerCertificate
        certificates = JobSeekerCertificate.objects.filter(jobseeker=seeker)
        cert_names = " ".join([normalize_text(cert.name) for cert in certificates])
    except:
        cert_names = ""
    
    # Get certifications from JSONField
    if hasattr(seeker, 'certifications') and seeker.certifications:
        cert_list = seeker.certifications if isinstance(seeker.certifications, list) else []
        cert_names += " " + normalize_text(" ".join(cert_list))
    
    if cert_names.strip():
        # Check if any certificate matches job category/title
        if job_category and job_category in cert_names:
            cert_score += 10
        
        # Check for common certifications (NC2, TESDA, etc.)
        job_keywords = set(job_title.split() + job_category.split())
        cert_words = set(cert_names.split())
        cert_matches = len(job_keywords & cert_words)
        
        if cert_matches > 0:
            cert_score += min(5, cert_matches * 2)
        
        # Bonus for having any certificates
        cert_score += 3
    
    total_score += min(15, cert_score)
    
    # ================================
    # 3. JOB TYPE PREFERENCE (20 points max) - REDUCED from 25
    # ================================
    preference_score = 0
    
    preferred_types = seeker.preferred_job_types
    if isinstance(preferred_types, list):
        preferred_text = normalize_text(" ".join(preferred_types))
    else:
        preferred_text = normalize_text(preferred_types)
    
    seeker_job_type = normalize_text(seeker.job_type)
    
    if job_category:
        # Exact category match in preferences (12 points)
        if job_category in preferred_text:
            preference_score += 12
        
        # Category match in seeker's job_type field (8 points)
        if job_category in seeker_job_type:
            preference_score += 8
    
    total_score += min(20, preference_score)
    
    # ================================
    # 4. EXPERIENCE (15 points max)
    # ================================
    experience_score = 0
    
    requires_experience = any(word in job_description for word in 
                            ['experience', 'experienced', 'years', 'background'])
    
    if hasattr(seeker, 'experience_years') and seeker.experience_years:
        if seeker.experience_years >= 5:
            experience_score = 15
        elif seeker.experience_years >= 3:
            experience_score = 12
        elif seeker.experience_years >= 1:
            experience_score = 8
        else:
            experience_score = 5
    else:
        if not requires_experience:
            experience_score = 8
        else:
            experience_score = 3
    
    total_score += experience_score
    
    # ================================
    # 5. LOCATION MATCHING (10 points max)
    # ================================
    location_score = 0
    
    job_location = normalize_text(job.location)
    seeker_city = normalize_text(seeker.city)
    seeker_region = normalize_text(seeker.region)
    
    if job_location and (seeker_city or seeker_region):
        if seeker_city and seeker_city in job_location:
            location_score = 10
        elif seeker_region and seeker_region in job_location:
            location_score = 7
        else:
            location_score = 5
    else:
        location_score = 5
    
    total_score += location_score
    
    # ================================
    # 6. PROFILE COMPLETENESS (5 points max) - REDUCED from 10
    # ================================
    profile_score = 0
    
    if hasattr(seeker, 'profile_completion'):
        completion = seeker.profile_completion
        if completion >= 90:
            profile_score = 5
        elif completion >= 70:
            profile_score = 4
        elif completion >= 50:
            profile_score = 3
        else:
            profile_score = 2
    
    total_score += profile_score
    
    # ================================
    # FINAL ADJUSTMENTS
    # ================================
    
    # Ensure minimum score of 10
    if total_score < 10 and (seeker_skills or preferred_text or cert_names):
        total_score = 10
    
    # Cap at 100
    total_score = min(100, round(total_score, 1))
    
    return total_score


def recommend_jobs_for_seeker(seeker, available_jobs, top_n=10):
    """
    Recommend top N jobs for a job seeker
    """
    
    recommendations = []
    
    for job in available_jobs:
        score = compute_enhanced_match_score(seeker, job)
        
        if score >= 20:
            recommendations.append((job, score))
    
    recommendations.sort(key=lambda x: x[1], reverse=True)
    
    return recommendations[:top_n]


def rank_applicants_for_job(job, applicants):
    """
    Rank applicants for a specific job posting
    """
    
    rankings = []
    
    for applicant in applicants:
        score = compute_enhanced_match_score(applicant, job)
        rankings.append((applicant, score))
    
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    return rankings