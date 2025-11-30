import os
import hashlib
import pytesseract
from PIL import Image
from django.conf import settings
from jobs.models import Notification
from accounts.models import DocumentVerification
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_file_hash(file_path):
    """Compute SHA256 hash for duplicate detection"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def extract_text_from_image(file_path):
    """Use OCR to extract visible text"""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text.lower()
    except Exception as e:
        print("OCR error:", e)
        return ""


def check_document_validity(user, file_path, doc_type):
    results = {"status": "Verified", "reason": "", "confidence": 1.0}

    text = extract_text_from_image(file_path)
    if user.first_name.lower() not in text or user.last_name.lower() not in text:
        results["status"] = "Suspicious"
        results["reason"] = "Name not found in document."
        results["confidence"] = 0.3

    file_hash = generate_file_hash(file_path)
    if DocumentVerification.objects.filter(hash_signature=file_hash).exists():
        results["status"] = "Suspicious"
        results["reason"] += " Duplicate document detected."
        results["confidence"] = 0.2

    results["hash_signature"] = file_hash
    return results


def run_ai_verification_for_user(user, uploaded_files):
    """AI doc check for both jobseekers and employers"""
    for field_name, file in uploaded_files.items():
        upload_dir = os.path.join(settings.MEDIA_ROOT, "ai_scans")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.name)

        with open(file_path, "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        result = check_document_validity(user, file_path, field_name)

        # log verification result
        DocumentVerification.objects.create(
            user=user,
            doc_type=field_name,
            file=file,
            status=result["status"],
            reason=result["reason"],
            ai_confidence=result["confidence"],
            hash_signature=result["hash_signature"],
        )

        # notify all admins if suspicious
        if result["status"] == "Suspicious":
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    receiver=admin,
                    message=f"⚠️ Suspicious {field_name} uploaded by {user.username}. Confidence: {result['confidence']}",
                    created_at=timezone.now(),
                )
