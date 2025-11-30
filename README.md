# BlueHire

**BlueHire** is an open-source AI-powered recruitment system focused on **blue-collar jobs** in the Philippines.

## 🚀 Features
- Role-based dashboards (Job Seeker / Employer / Admin)
- Document upload & AI fraud detection
- AI-based job recommendations (TF-IDF + Cosine Similarity)
- Auto document verification with OCR hooks
- Admin monitoring, logs, and reporting system

## 🧠 Tech Stack
- Python 3.13 | Django 5 | MySQL 8  
- scikit-learn | OpenCV | Tesseract (OCR)  
- HTML | CSS | Vanilla JS  

## 🛠 Setup
```bash
git clone https://github.com/Augustine/BlueHire.git
cd BlueHire
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
