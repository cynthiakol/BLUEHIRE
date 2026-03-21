from django.urls import path
from . import views

urlpatterns = [
    path('rate/jobseeker/<int:application_id>/', views.rate_jobseeker,    name='rate_jobseeker'),
    path('rate/employer/<int:application_id>/',  views.rate_employer,     name='rate_employer'),
    path('ratings/jobseeker/<int:jobseeker_id>/', views.jobseeker_ratings, name='jobseeker_ratings'),
    path('ratings/employer/<int:employer_id>/',   views.employer_ratings,  name='employer_ratings'),
]