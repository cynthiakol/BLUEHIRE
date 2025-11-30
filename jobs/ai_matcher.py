from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_applicants(job, applicants):
    """
    Rank applicants for a given job based on similarity between
    job.description and jobseeker.skills/experience fields.
    """
    job_text = f"{job.title} {job.description or ''} {job.category or ''}".lower()

    seeker_texts = []
    seekers = []
    for app in applicants:
        # handle either jobseeker or applicant field names
        seeker = getattr(app, "jobseeker", None) or getattr(app, "applicant", None)
        if not seeker:
            continue
        combined = f"{getattr(seeker, 'skills', '')} {getattr(seeker, 'experience', '')}".lower()
        seeker_texts.append(combined)
        seekers.append(seeker)

    if not seeker_texts:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([job_text] + seeker_texts)
    scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    ranked = sorted(zip(seekers, scores), key=lambda x: x[1], reverse=True)

    results = []
    for seeker, score in ranked[:5]:
        if score > 0.1:
            results.append({
                "seeker": seeker,
                "score": round(score * 100, 1),
            })
    return results
